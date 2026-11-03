"""Command line: python -m movediff {extract,segment,import,analyse,demo} ..."""

from __future__ import annotations

import argparse
from pathlib import Path

from .extract import DEFAULT_MODEL


def _csv(s: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in s.split(",") if x.strip())


def _ints(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in _csv(s))


def _floats(s: str) -> tuple[float, ...]:
    return tuple(float(x) for x in _csv(s))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="movediff", description="Compare one person's movement across conditions.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("extract", help="video -> pose landmarks (.pose.npz)")
    p.add_argument("videos", nargs="+", type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("work"))
    p.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    p.add_argument("--overlay", action="store_true", help="also write a skeleton overlay video to check tracking")

    p = sub.add_parser("segment", help="pose landmarks -> normalised per-rep trajectories (.reps.npz + .csv)")
    p.add_argument("pose", type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("trajectories"))
    p.add_argument("--side", choices=("left", "right"), default="right", help="the moving arm")
    p.add_argument("--effector", default="wrist", help="landmark whose speed defines reps (default wrist)")
    p.add_argument("--joints", type=_csv, default=("elbow", "wrist", "index"))
    p.add_argument("--centre", default="shoulder", help="landmark subtracted every frame")
    p.add_argument("--scale", choices=("auto", "torso", "arm"), default="auto")
    p.add_argument("--stroke", choices=("forward", "backward", "up", "down", "any"), default="forward",
                   help="which speed peaks count as reps")
    p.add_argument("--flip", choices=("auto", "yes", "no"), default="auto", help="flip x so +x = facing direction")
    p.add_argument("--cutoff", type=float, default=6.0, help="low-pass cutoff in Hz (raise for fast throws)")
    p.add_argument("--min-peak", type=float, default=0.25, help="peak height as a fraction of the 99th pct speed")
    p.add_argument("--onset-frac", type=float, default=0.1, help="rep starts/ends where speed < this x peak")
    p.add_argument("--pad-before", type=float, default=0.0, help="seconds added before onset (e.g. a backswing)")
    p.add_argument("--pad-after", type=float, default=0.0)
    p.add_argument("--start", type=float, help="ignore video before this time (s)")
    p.add_argument("--end", type=float, help="ignore video after this time (s)")
    p.add_argument("--drop", type=_ints, default=(), help="candidate numbers to drop, as shown on the plot")
    p.add_argument("--expect", type=int, help="warn if the number of reps differs")

    p = sub.add_parser("import", help="CSV of positions (headset, mocap, tablet) -> per-rep trajectories")
    p.add_argument("csv", type=Path, help="columns: condition,trial,t,joint,x,y (t in seconds)")
    p.add_argument("--unit", required=True, help="unit of x and y, e.g. cm")
    p.add_argument("--out-dir", type=Path, default=Path("trajectories"))
    p.add_argument("--effector", help="joint that defines the movement (default: first joint in the file)")
    p.add_argument("--no-cut", action="store_true", help="trials already start and end with the movement")
    p.add_argument("--onset-frac", type=float, default=0.1,
                   help="onset threshold as a fraction of the median peak speed over all trials")
    p.add_argument("--onset-at-zero", action="store_true",
                   help="t=0 in each trial is movement onset (start switch, logged event); find only the end")
    p.add_argument("--cutoff", type=float, help="optional low-pass cutoff in Hz")

    p = sub.add_parser("analyse", help="compare sessions -> metrics.json, summary.md, figures")
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--test", type=Path, required=True)
    p.add_argument("--practice", type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("results"))
    p.add_argument("--effector", help="joint for the endpoint, speed and summary tables (default: from segment)")
    p.add_argument("--phases", type=_floats, default=(1 / 3, 2 / 3), help="phase boundaries, e.g. 0.33,0.67")
    p.add_argument("--phase-names", type=_csv, default=("early", "mid", "late"))
    p.add_argument("--align-on", choices=("velocity", "speed", "position", "none", "onset"), default="velocity",
                   help="velocity = DTW (default); onset = compare at the same ms after onset, for conditions "
                        "that differ a lot in duration")
    p.add_argument("--band", type=float, default=0.1, help="DTW warping limit, fraction of the movement")
    p.add_argument("--unit-cm", type=float, help="your measured scale length in cm (shoulder to hip for torso)")
    p.add_argument("--n-perm", type=int, default=2000)
    p.add_argument("--n-boot", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)

    p = sub.add_parser("demo", help="synthetic sessions with known changes -> full pipeline")
    p.add_argument("--out-dir", type=Path, default=Path("results/synthetic"))
    p.add_argument("--scenario", choices=("bulge", "undershoot"), default="bulge")
    p.add_argument("--n-perm", type=int, default=2000)

    a = ap.parse_args(argv)
    if a.cmd == "extract":
        from .extract import extract

        for v in a.videos:
            stem = v.stem
            extract(v, a.out_dir / f"{stem}.pose.npz", a.model,
                    a.out_dir / f"{stem}.overlay.mp4" if a.overlay else None)
    elif a.cmd == "segment":
        _segment(a.pose, a.out_dir, a.expect, side=a.side, effector=a.effector, joints=a.joints,
                 centre=a.centre, scale=a.scale, stroke=a.stroke, flip=a.flip, cutoff=a.cutoff,
                 min_peak=a.min_peak, onset_frac=a.onset_frac, pad_before_s=a.pad_before,
                 pad_after_s=a.pad_after, start_s=a.start, end_s=a.end, drop=a.drop)
    elif a.cmd == "import":
        from .tabular import import_csv

        import_csv(a.csv, a.out_dir, unit=a.unit, effector=a.effector, cut=not a.no_cut,
                   onset_frac=a.onset_frac, onset_at_zero=a.onset_at_zero, cutoff=a.cutoff)
    elif a.cmd == "analyse":
        from .analyse import analyse

        analyse(dict(baseline=a.baseline, practice=a.practice, test=a.test), a.out_dir, effector=a.effector,
                bounds=a.phases, names=a.phase_names, align_on=a.align_on, band=a.band, unit_cm=a.unit_cm,
                n_perm=a.n_perm, n_boot=a.n_boot, seed=a.seed)
    elif a.cmd == "demo":
        demo(a.out_dir, a.n_perm, a.scenario)


def _segment(pose: Path, out_dir: Path, expect: int | None = None, **kw):
    from .plots import plot_segmentation
    from .segment import segment

    reps, diag = segment(pose, **kw)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = reps.name
    reps.save(out_dir / f"{stem}.reps.npz")
    reps.to_csv(out_dir / f"{stem}.reps.csv")
    plot_segmentation(diag, stem, out_dir / f"{stem}.segmentation.png")
    rejected = [f"#{c['number']} {c['reason']}" for c in diag.candidates if c["status"] != "kept"]
    msg = f"{stem}: {len(reps)} reps kept"
    if rejected:
        msg += f" (not kept: {', '.join(rejected)})"
    print(msg + f". Check {out_dir / (stem + '.segmentation.png')}")
    if expect is not None and expect != len(reps):
        print(f"WARNING: expected {expect} reps, found {len(reps)}. Look at the plot before analysing.")
    return out_dir / f"{stem}.reps.npz"


def demo(out_dir: Path, n_perm: int = 2000, scenario: str = "bulge") -> dict:
    from .analyse import analyse
    from .synth import write_sessions

    out_dir = Path(out_dir)
    poses = write_sessions(out_dir / "pose", scenario=scenario)
    reps = {k: _segment(p, out_dir / "trajectories", side="right") for k, p in poses.items()}
    return analyse(reps, out_dir, n_perm=n_perm, n_boot=n_perm)


if __name__ == "__main__":
    main()
