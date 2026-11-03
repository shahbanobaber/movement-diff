"""Use the tool on position data that didn't come from video.

Headset logs, motion capture and tablet recordings already give positions,
so the pose and normalisation steps are skipped. The input is one long CSV:

    condition,trial,t,joint,x,y
    baseline,1,0.00,wrist,12.31,4.02
    baseline,1,0.01,wrist,12.35,4.03
    ...

t is in seconds and x, y are in any unit you name with --unit. Each trial
can include rest before and after the movement. The movement is cut out where
speed along its main direction crosses one threshold, 10% of the median peak
speed over every trial in the file. If t=0 already marks movement onset (a
start switch, a logged event), --onset-at-zero uses it and only the end is
found. --no-cut keeps whole trials.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from .segment import Reps, _bounds
from .signal import lowpass, to_uniform


def _prepare(t, traj, cutoff):
    t, traj, fps = to_uniform(np.asarray(t, float), np.asarray(traj, float))
    if np.isnan(traj).any():
        return None
    return t, lowpass(traj, fps, cutoff), fps


def main_axis_speed(traj: np.ndarray, fps: float, e: int, onset_frac: float = 0.1) -> np.ndarray:
    """Effector speed along the main direction of the trial's movement, so sideways wobble can't move the cut."""
    vel = np.gradient(traj[:, e], axis=0) * fps
    speed = np.linalg.norm(vel, axis=1)
    p = int(np.argmax(speed))
    on, off, _, _ = _bounds(speed, onset_frac * speed[p], 0, p, len(speed) - 1)
    axis = traj[off, e] - traj[on, e]
    n = float(np.linalg.norm(axis))
    return np.abs(vel @ (axis / n)) if off > on and n > 0 else speed


def cut_trial(along: np.ndarray, thr: float, onset: int | None = None) -> tuple[int, int] | None:
    """Onset and offset where `along` crosses thr, or None if the movement runs off either end.

    thr must be the same for every trial. Scaled to each trial's own peak, it
    puts the onset later in trials with a large second movement (a
    correction), and on a clock-time comparison that alone looks like a
    change in path.
    """
    big = np.flatnonzero(along > max(0.5 * along.max(), thr))
    if not big.size:
        return None
    first, last = int(big[0]), int(big[-1])
    if onset is None:
        below = np.flatnonzero(along[: first + 1] < thr)
        if not below.size:
            return None
        onset = int(below[-1])
    after = np.flatnonzero(along[last:] < thr)
    if not after.size or last + int(after[0]) - onset < 3:
        return None
    return onset, last + int(after[0])


def onset_threshold(trials, e: int, onset_frac: float = 0.1, cutoff: float | None = None) -> float:
    """onset_frac times the median peak main-axis speed over the trials."""
    peaks = []
    for t, traj in trials:
        prep = _prepare(t, traj, cutoff)
        if prep is not None:
            peaks.append(main_axis_speed(prep[1], prep[2], e, onset_frac).max())
    if not peaks:
        raise SystemExit("no usable trials")
    return onset_frac * float(np.median(peaks))


def reps_from_trials(name: str, trials: list[tuple[np.ndarray, np.ndarray]], joints: list[str],
                     effector: str, unit: str, *, cut: bool = True, onset_frac: float = 0.1,
                     thr: float | None = None, onset_at_zero: bool = False, cutoff: float | None = None,
                     trial_ids: list[int] | None = None) -> tuple[Reps, list[int]]:
    """Build Reps from (t seconds, positions (n, J, 2)) trials. Returns (reps, ids of trials dropped).

    thr is the onset threshold in units/s. Leave it out to take it from these
    trials; import_csv passes one value for every condition in the file.
    """
    e = joints.index(effector)
    if cut and thr is None:
        thr = onset_threshold(trials, e, onset_frac, cutoff)
    pieces, onsets, offsets, ids, dropped, fps_all = [], [], [], [], [], []
    for k, (t, traj) in enumerate(trials):
        tid = trial_ids[k] if trial_ids else k + 1
        prep = _prepare(t, traj, cutoff)
        if prep is None:
            dropped.append(tid)
            continue
        t, traj, fps = prep
        if cut:
            zero = int(np.searchsorted(t, 0.0)) if onset_at_zero else None
            window = cut_trial(main_axis_speed(traj, fps, e, onset_frac), thr, zero)
        else:
            window = (0, len(traj) - 1)
        if window is None:
            dropped.append(tid)
            continue
        on, off = window
        pieces.append(traj[on : off + 1])
        onsets.append(t[on])
        offsets.append(t[off])
        ids.append(tid)
        fps_all.append(fps)
    if not pieces:
        raise SystemExit(f"{name}: no usable trials")
    fps = float(np.median(fps_all))
    if np.ptp(fps_all) > 0.01 * fps:
        raise SystemExit(f"{name}: trials have different sampling rates ({min(fps_all):.1f}-{max(fps_all):.1f} Hz)")
    lengths = np.array([len(p) for p in pieces])
    reps = Reps(name=name, fps=fps, side="n/a", joints=list(joints), effector=effector, unit=unit, scale_px=1.0,
                frames=np.concatenate(pieces), starts=np.concatenate([[0], np.cumsum(lengths)[:-1]]),
                lengths=lengths, onset_t=np.array(onsets), offset_t=np.array(offsets), rep_ids=np.array(ids))
    return reps, dropped


def read_csv(path: Path) -> tuple[dict[str, dict[int, tuple[np.ndarray, np.ndarray]]], list[str]]:
    """Long CSV -> {condition: {trial: (t, positions (n, J, 2))}}, joint names in first-seen order."""
    rows: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    joints: list[str] = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        missing = {"condition", "trial", "t", "joint", "x", "y"} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{path}: missing columns {sorted(missing)}")
        for r in reader:
            if r["joint"] not in joints:
                joints.append(r["joint"])
            rows[r["condition"]][int(r["trial"])][r["joint"]].append((float(r["t"]), float(r["x"]), float(r["y"])))
    out = {}
    for cond, trials in rows.items():
        out[cond] = {}
        for tid, by_joint in trials.items():
            series = [np.array(sorted(by_joint[j])) for j in joints if j in by_joint]
            if len(series) != len(joints) or len({len(s) for s in series}) != 1:
                raise SystemExit(f"{path}: condition {cond} trial {tid} is missing samples for some joints")
            t = series[0][:, 0]
            out[cond][tid] = (t, np.stack([s[:, 1:] for s in series], axis=1))
    return out, joints


def import_csv(path: Path, out_dir: Path, *, unit: str, effector: str | None = None, cut: bool = True,
               onset_frac: float = 0.1, onset_at_zero: bool = False, cutoff: float | None = None) -> dict[str, Path]:
    data, joints = read_csv(path)
    effector = effector or joints[0]
    if effector not in joints:
        raise SystemExit(f"effector {effector!r} not in joints {joints}")
    thr = None
    if cut:
        every = [tr for trials in data.values() for tr in trials.values()]
        thr = onset_threshold(every, joints.index(effector), onset_frac, cutoff)
        print(f"onset threshold: {thr:.3g} {unit}/s ({100 * onset_frac:.0f}% of the median peak speed, all trials)")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for cond, trials in data.items():
        ids = sorted(trials)
        reps, dropped = reps_from_trials(cond, [trials[i] for i in ids], joints, effector, unit, cut=cut,
                                         onset_frac=onset_frac, thr=thr, onset_at_zero=onset_at_zero,
                                         cutoff=cutoff, trial_ids=ids)
        reps.save(out_dir / f"{cond}.reps.npz")
        written[cond] = out_dir / f"{cond}.reps.npz"
        note = f", dropped trials {dropped}" if dropped else ""
        print(f"{cond}: {len(reps)} reps{note}")
    return written
