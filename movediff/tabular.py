"""Use the tool on position data that didn't come from video.

Headset logs, motion capture and tablet recordings already give positions,
so the pose and normalisation steps are skipped. The input is one long CSV:

    condition,trial,t,joint,x,y
    baseline,1,0.00,wrist,12.31,4.02
    baseline,1,0.01,wrist,12.35,4.03
    ...

t is in seconds and x, y are in any unit you name with --unit. Each trial
can include rest before and after the movement. The movement is cut out with
the same rule the video path uses (speed along the main direction crossing
10% of its peak), unless you pass --no-cut.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from .segment import Reps, _bounds
from .signal import lowpass, to_uniform


def cut_trial(traj: np.ndarray, fps: float, e: int, onset_frac: float = 0.1) -> tuple[int, int] | None:
    """Onset and offset of the one movement in a trial, or None if it runs off either end."""
    vel = np.gradient(traj[:, e], axis=0) * fps
    speed = np.linalg.norm(vel, axis=1)
    p, last = int(np.argmax(speed)), len(speed) - 1
    on, off, cut_a, cut_b = _bounds(speed, onset_frac * speed[p], 0, p, last)
    axis = traj[off, e] - traj[on, e]
    if off > on and np.linalg.norm(axis) > 0:
        along = np.abs(vel @ (axis / np.linalg.norm(axis)))
        on, off, cut_a, cut_b = _bounds(along, onset_frac * along[p], 0, p, last)
    if cut_a or cut_b or off - on < 3:
        return None
    return on, off


def reps_from_trials(name: str, trials: list[tuple[np.ndarray, np.ndarray]], joints: list[str],
                     effector: str, unit: str, *, cut: bool = True, onset_frac: float = 0.1,
                     cutoff: float | None = None, trial_ids: list[int] | None = None) -> tuple[Reps, list[int]]:
    """Build Reps from (t seconds, positions (n, J, 2)) trials. Returns (reps, ids of trials dropped)."""
    e = joints.index(effector)
    pieces, onsets, offsets, ids, dropped, fps_all = [], [], [], [], [], []
    for k, (t, traj) in enumerate(trials):
        tid = trial_ids[k] if trial_ids else k + 1
        t, traj, fps = to_uniform(np.asarray(t, float), np.asarray(traj, float))
        if np.isnan(traj).any():
            dropped.append(tid)
            continue
        traj = lowpass(traj, fps, cutoff)
        window = cut_trial(traj, fps, e, onset_frac) if cut else (0, len(traj) - 1)
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
               onset_frac: float = 0.1, cutoff: float | None = None) -> dict[str, Path]:
    data, joints = read_csv(path)
    effector = effector or joints[0]
    if effector not in joints:
        raise SystemExit(f"effector {effector!r} not in joints {joints}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for cond, trials in data.items():
        ids = sorted(trials)
        reps, dropped = reps_from_trials(cond, [trials[i] for i in ids], joints, effector, unit, cut=cut,
                                         onset_frac=onset_frac, cutoff=cutoff, trial_ids=ids)
        reps.save(out_dir / f"{cond}.reps.npz")
        written[cond] = out_dir / f"{cond}.reps.npz"
        note = f", dropped trials {dropped}" if dropped else ""
        print(f"{cond}: {len(reps)} reps{note}")
    return written
