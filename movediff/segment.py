"""Step 2: landmark stream -> normalised per-rep trajectories.

1. Drop low-visibility landmarks, resample to a uniform frame rate, fill short
   gaps, low-pass filter (zero-lag Butterworth, 6 Hz by default).
2. Normalise: subtract the centre landmark (moving-side shoulder) every frame,
   divide by one body length per session (median shoulder-to-hip, or upper arm
   plus forearm when the hip is hidden), and flip x so +x is the direction the
   person faces. Units after this step are "torso lengths" or "arm lengths".
3. Segment: peaks in effector speed, keep peaks moving in the chosen direction,
   walk out from each peak to where speed falls below 10% of that peak, then
   redo that walk on speed along the rep's main direction (so sideways wobble
   cannot move the cut), and reject candidates that travel less than half the
   session's median path.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

from .landmarks import lm
from .signal import fill_gaps, lowpass, to_uniform


@dataclass
class Reps:
    name: str
    fps: float
    side: str
    joints: list[str]
    effector: str
    unit: str            # "torso" or "arm": what 1.0 means
    scale_px: float      # pixels per unit in this session
    frames: np.ndarray   # (N, J, 2) all reps concatenated
    starts: np.ndarray   # (R,) offset of each rep in `frames`
    lengths: np.ndarray  # (R,)
    onset_t: np.ndarray  # (R,) seconds into the video
    offset_t: np.ndarray
    rep_ids: np.ndarray  # (R,) candidate number from segmentation (gaps = dropped)

    def __len__(self) -> int:
        return len(self.starts)

    def rep(self, k: int) -> np.ndarray:
        s = int(self.starts[k])
        return self.frames[s : s + int(self.lengths[k])]

    def save(self, path: Path) -> None:
        np.savez_compressed(
            path, name=self.name, fps=self.fps, side=self.side, joints=np.array(self.joints),
            effector=self.effector, unit=self.unit, scale_px=self.scale_px, frames=self.frames,
            starts=self.starts, lengths=self.lengths, onset_t=self.onset_t, offset_t=self.offset_t,
            rep_ids=self.rep_ids,
        )

    @classmethod
    def load(cls, path: Path) -> "Reps":
        d = np.load(path)
        return cls(
            name=str(d["name"]), fps=float(d["fps"]), side=str(d["side"]),
            joints=[str(j) for j in d["joints"]], effector=str(d["effector"]), unit=str(d["unit"]),
            scale_px=float(d["scale_px"]), frames=d["frames"], starts=d["starts"],
            lengths=d["lengths"], onset_t=d["onset_t"], offset_t=d["offset_t"], rep_ids=d["rep_ids"],
        )

    def to_csv(self, path: Path) -> None:
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["rep", "frame", "t", "joint", "x", "y"])
            for k in range(len(self)):
                traj = self.rep(k)
                for f in range(len(traj)):
                    for j, joint in enumerate(self.joints):
                        w.writerow([int(self.rep_ids[k]), f, f"{f / self.fps:.4f}", joint,
                                    f"{traj[f, j, 0]:.5f}", f"{traj[f, j, 1]:.5f}"])


def _bounds(sig: np.ndarray, thr: float, prev: int, p: int, nxt: int) -> tuple[int, int, bool, bool]:
    """Walk out from peak p to where `sig` drops below thr, staying between the neighbouring peaks.

    Returns (onset, offset, cut_at_start, cut_at_end); the flags mean the
    movement runs off the start or end of the video.
    """
    before, after = sig[prev : p + 1], sig[p : nxt + 1]
    b, a = np.flatnonzero(before < thr), np.flatnonzero(after < thr)
    on = prev + (int(b[-1]) if b.size else int(np.argmin(before)))
    off = p + (int(a[0]) if a.size else int(np.argmin(after)))
    return on, off, (not b.size and on == 0), (not a.size and off == len(sig) - 1)


@dataclass
class Diagnostics:
    t: np.ndarray
    speed: np.ndarray
    effector_xy: np.ndarray
    threshold: float
    candidates: list[dict] = field(default_factory=list)


def segment(
    pose_path: Path,
    *,
    name: str | None = None,
    side: str = "right",
    effector: str = "wrist",
    joints: tuple[str, ...] = ("elbow", "wrist", "index"),
    centre: str = "shoulder",
    scale: str = "auto",
    stroke: str = "forward",
    flip: str = "auto",
    cutoff: float = 6.0,
    min_vis: float = 0.5,
    max_gap_s: float = 0.25,
    min_peak: float = 0.25,
    min_sep_s: float = 0.3,
    onset_frac: float = 0.1,
    onset_axis: str = "main",
    pad_before_s: float = 0.0,
    pad_after_s: float = 0.0,
    min_dur_s: float = 0.15,
    max_dur_s: float = 4.0,
    min_path_frac: float = 0.5,
    start_s: float | None = None,
    end_s: float | None = None,
    drop: tuple[int, ...] = (),
) -> tuple[Reps, Diagnostics]:
    d = np.load(pose_path)
    xy_all = d["xy"].astype(float)
    vis = d["vis"].astype(float)
    t = d["t"].astype(float)
    name = name or Path(pose_path).name.split(".")[0]

    keep = np.ones(len(t), dtype=bool)
    if start_s is not None:
        keep &= t >= start_s
    if end_s is not None:
        keep &= t <= end_s
    xy_all, vis, t = xy_all[keep], vis[keep], t[keep]
    xy_all[vis < min_vis] = np.nan

    joints = tuple(joints) if effector in joints else tuple(joints) + (effector,)
    tracked = [centre, *joints]
    xy = xy_all[:, [lm(side, j) for j in tracked]]
    t, xy, fps = to_uniform(t, xy)
    xy, missing = fill_gaps(xy, int(round(max_gap_s * fps)))
    xy = lowpass(xy, fps, cutoff)

    # One length per session, from unfiltered points (median is robust to jitter).
    def seg_len(a: str, b: str) -> float:
        diff = xy_all[:, lm(side, a)] - xy_all[:, lm(side, b)]
        return float(np.nanmedian(np.linalg.norm(diff, axis=1)))

    if scale == "auto":
        hip_vis = np.nanmedian(vis[:, lm(side, "hip")])
        scale = "torso" if hip_vis >= min_vis else "arm"
    if scale == "torso":
        scale_px = seg_len("shoulder", "hip")
    elif scale == "arm":
        scale_px = seg_len("shoulder", "elbow") + seg_len("elbow", "wrist")
    else:
        raise ValueError(f"scale must be torso, arm or auto, not {scale!r}")
    if not np.isfinite(scale_px) or scale_px <= 0:
        raise SystemExit(f"{name}: could not measure body scale ({scale}); try --scale arm")

    norm = (xy[:, 1:] - xy[:, :1]) / scale_px  # (T, J, 2) relative to centre
    if flip == "auto":
        facing = np.nanmedian(xy_all[:, lm(side, "nose"), 0] - xy_all[:, lm(side, "shoulder"), 0])
        do_flip = bool(facing < 0)
    else:
        do_flip = flip == "yes"
    if do_flip:
        norm[..., 0] *= -1

    e = joints.index(effector)
    vel = np.gradient(norm[:, e], axis=0) * fps
    speed = np.linalg.norm(vel, axis=1)

    ref = float(np.percentile(speed, 99))
    height = min_peak * ref
    peaks, _ = find_peaks(speed, height=height, prominence=0.5 * height,
                          distance=max(1, int(round(min_sep_s * fps))))

    def right_way(p):
        v = vel[max(p - 2, 0) : p + 3].mean(axis=0)
        return {"forward": v[0] > 0, "backward": v[0] < 0, "up": v[1] > 0, "down": v[1] < 0, "any": True}[stroke]

    # One onset threshold for every rep in the session. Scaled to each rep's own
    # peak, it would cut faster reps later into their movement, and that alone
    # looks like a change in path (seen on real data, see validation/README.md).
    strokes = [p for p in peaks if right_way(p)]
    cut_thr = onset_frac * float(np.median(speed[strokes])) if strokes else 0.0

    diag = Diagnostics(t=t, speed=speed, effector_xy=norm[:, e], threshold=height)
    T = len(t)
    number = 0
    for k, p in enumerate(peaks):
        if not right_way(p):
            continue
        number += 1
        prev = peaks[k - 1] if k > 0 else 0
        nxt = peaks[k + 1] if k + 1 < len(peaks) else T - 1
        status, reason = "kept", ""

        onset, offset, cut_start, cut_end = _bounds(speed, cut_thr, prev, p, nxt)
        if onset_axis == "main" and offset > onset:
            # Second pass on speed along the rep's main direction, so sideways
            # wobble at the start or end (which is what more variability looks
            # like) cannot move where the rep is cut.
            axis = norm[offset, e] - norm[onset, e]
            if np.linalg.norm(axis) > 0:
                along = np.abs(vel @ (axis / np.linalg.norm(axis)))
                onset, offset, cut_start, cut_end = _bounds(along, cut_thr, prev, p, nxt)
        if cut_start:
            status, reason = "rejected", "starts before the video"
        if cut_end:
            status, reason = "rejected", "runs past the end of the video"

        onset = max(0, onset - int(round(pad_before_s * fps)))
        offset = min(T - 1, offset + int(round(pad_after_s * fps)))
        dur = (offset - onset) / fps
        if status == "kept":
            if dur < min_dur_s:
                status, reason = "rejected", f"too short ({dur:.2f}s)"
            elif dur > max_dur_s:
                status, reason = "rejected", f"too long ({dur:.2f}s)"
            elif missing[onset : offset + 1].any():
                status, reason = "rejected", "tracking lost"
            elif number in drop:
                status, reason = "dropped", "--drop"
        diag.candidates.append(dict(number=number, onset=int(onset), offset=int(offset),
                                    peak=int(p), status=status, reason=reason))

    # Fidgets and tracking blips pass the speed threshold but travel much less
    # than a real rep. Compare each candidate's path length to the session median.
    def path_len(c):
        seg = norm[c["onset"] : c["offset"] + 1, e]
        return float(np.linalg.norm(np.diff(seg, axis=0), axis=1).sum())

    ok = [c for c in diag.candidates if c["status"] == "kept"]
    if ok:
        median = np.median([path_len(c) for c in ok])
        for c in ok:
            if path_len(c) < min_path_frac * median:
                c["status"], c["reason"] = "rejected", f"small ({path_len(c) / median:.0%} of median path)"
    kept = [(c["number"], c["onset"], c["offset"]) for c in diag.candidates if c["status"] == "kept"]

    if not kept:
        raise SystemExit(f"{name}: no reps found; check the segmentation plot and thresholds")

    pieces = [norm[on : off + 1, :] for _, on, off in kept]
    lengths = np.array([len(p) for p in pieces])
    reps = Reps(
        name=name, fps=fps, side=side, joints=list(joints), effector=effector, unit=scale,
        scale_px=scale_px, frames=np.concatenate(pieces), starts=np.concatenate([[0], np.cumsum(lengths)[:-1]]),
        lengths=lengths, onset_t=np.array([t[on] for _, on, _ in kept]),
        offset_t=np.array([t[off] for _, _, off in kept]), rep_ids=np.array([n for n, _, _ in kept]),
    )
    return reps, diag
