"""Real VR data: does the tool find a mid-reach change where it actually happened?

Data: Furmanek et al. (2022), Scientific Data 9:23, CC0, figshare
doi:10.6084/m9.figshare.13377506. People reached to grasp a virtual object
in an Oculus Rift while markers on the wrist, thumb and index finger were
tracked (75 Hz, released resampled to 100 Hz). On some trials the object
jumped from 20 cm to 40 cm away at 100, 200 or 300 ms after movement onset.

The check: jumped reaches against reaches to the near object, which start
the same way. The shift should stay at the noise floor until after the
jump, and rise later for later jumps. The raw data, compared in plain
milliseconds with no alignment and no cutting, gives the reference time.
The tool is run both ways: the default DTW timeline and clock time from
onset (--align-on onset).

Usage, from the repo root:
  python validation/furmanek2022.py data/furmanek2022/Small_Subset/Dist_Pert/P1
Writes results/furmanek2022/<participant>/. No network, no paid APIs.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from movediff import plots  # noqa: E402
from movediff.analyse import analyse  # noqa: E402
from movediff.metrics import build_conditions, compare, phase_masks  # noqa: E402
from movediff.segment import Reps  # noqa: E402
from movediff.tabular import import_csv  # noqa: E402

# Condition order from Table 4 of the paper (distance experiment), checked
# against Final_Object_Position: each group of three ends at the right distance.
DIST = ["N", "NM", "M", "MF", "F"]  # 20, 25, 30, 35, 40 cm
JUMPS = [("N", "NM"), ("N", "M"), ("N", "MF"), ("N", "F"), ("NM", "M"), ("NM", "MF"), ("NM", "F"),
         ("M", "MF"), ("M", "F"), ("MF", "F")]
NAMES = DIST + [f"{a}-to-{b}-{ms}" for a, b in JUMPS for ms in (100, 200, 300)]
JOINTS = ["wrist", "thumb", "index"]
RUN = 5  # samples a curve must stay above the noise band to count as a divergence (50 ms at 100 Hz)


def load(pdir: Path):
    import scipy.io as sio

    m = sio.loadmat(pdir / "Trajectories.mat", squeeze_me=True, struct_as_record=False)
    res, obj = m["Resampled"], m["Final_Object_Position"]
    if len(res) != len(NAMES):
        raise SystemExit(f"expected {len(NAMES)} conditions, found {len(res)}")
    near, far = np.asarray(obj[0], float), np.asarray(obj[4], float)
    depth = (far - near)[:2] / np.linalg.norm((far - near)[:2])  # reach direction across the table
    trials = {n: [np.asarray(t, float) for t in np.atleast_1d(res[i])] for i, n in enumerate(NAMES)}
    origin = np.median([t[0, 1:4] for ts in trials.values() for t in ts], axis=0)

    def project(tr):
        """(n, 10) [ms, wrist xyz, thumb xyz, index xyz] -> t in s, (n, 3, 2) [depth, height] in cm."""
        pts = tr[:, 1:10].reshape(len(tr), 3, 3) - origin
        return tr[:, 0] / 1000.0, np.stack([pts[..., :2] @ depth, pts[..., 2]], axis=-1)

    return {n: [project(t) for t in ts] for n, ts in trials.items()}


def write_csv(data, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["condition", "trial", "t", "joint", "x", "y"])
        for cond, trials in data.items():
            for k, (t, pos) in enumerate(trials, 1):
                for i in range(len(t)):
                    for j, joint in enumerate(JOINTS):
                        w.writerow([cond, k, f"{t[i]:.3f}", joint, f"{pos[i, j, 0]:.3f}", f"{pos[i, j, 1]:.3f}"])


def first_run(above: np.ndarray, start: int = 0) -> int | None:
    count = 0
    for i in range(start, len(above)):
        count = count + 1 if above[i] else 0
        if count == RUN:
            return i - RUN + 1
    return None


def raw_divergence(data, base: str, other: str, rng, n_perm: int = 2000) -> float | None:
    """When do wrist depth positions separate, in plain ms after onset, with no alignment at all?"""
    a, b = data[base], data[other]
    t0 = a[0][0]
    n = min(len(t) for t, _ in a + b)
    A = np.array([p[:n, 0, 0] for _, p in a])
    B = np.array([p[:n, 0, 0] for _, p in b])
    obs = np.abs(B.mean(0) - A.mean(0))
    pooled, na = np.concatenate([A, B]), len(A)
    null = np.empty((n_perm, n))
    for k in range(n_perm):
        idx = rng.permutation(len(pooled))
        null[k] = np.abs(pooled[idx[na:]].mean(0) - pooled[idx[:na]].mean(0))
    start = int(np.searchsorted(t0[:n], 0.0))
    i = first_run(obs > np.percentile(null, 95, axis=0), start)
    return None if i is None else float(t0[i] * 1000)


def tool_divergence(reps: dict[str, Reps], base: str, other: str, rng, mode: str) -> tuple[float | None, dict]:
    conds, aligner, joints = build_conditions({"baseline": reps[base], "test": reps[other]}, "wrist", 101,
                                              mode, 0.1, 1.0)
    c = compare(conds["baseline"], conds["test"], phase_masks([1 / 3, 2 / 3], 101), rng, 2000, 10)
    e = joints.index("wrist")
    i = first_run(c["shift_curve"][:, e] > c["null95_curve"][:, e])
    # Convert the timeline back to ms in the trial clock (0 = switch release,
    # which is what the jump times are measured from). With DTW the baseline
    # timeline is retimed to average baseline timing, so u maps to mean onset +
    # u * mean duration. With onset mode it is clock time already.
    b = reps[base]
    onset_ms = 1000 * float(np.mean(b.onset_t))
    dur_ms = 1000 * (aligner.span_s if mode == "onset" else float(np.mean(b.offset_t - b.onset_t)))
    ms = None if i is None else onset_ms + i / 100 * dur_ms
    curve = dict(ms=(onset_ms + np.linspace(0, 1, 101) * dur_ms).tolist(),
                 shift=c["shift_curve"][:, e].tolist(), null95=c["null95_curve"][:, e].tolist())
    return ms, curve


def plot_timing(curves: dict, rows: list[dict], path: Path) -> None:
    import matplotlib.pyplot as plt

    plots._style()
    shades = {100: "#86b6ef", 200: "#2a78d6", 300: "#104281"}  # one hue, light to dark = early to late jump
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    c200 = curves[200]
    ax.fill_between(c200["ms"], 0, c200["null95"], color=plots.NULL, lw=0, label="noise band (200 ms jump)")
    for r in rows:
        jump, c = r["jump_ms"], curves[r["jump_ms"]]
        ax.plot(c["ms"], c["shift"], color=shades[jump], label=f"jump at {jump} ms")
        ax.axvline(jump, color=shades[jump], lw=1, ls=(0, (2, 2)))
        if r["tool_ms"] is not None:
            ax.plot(r["tool_ms"], np.interp(r["tool_ms"], c["ms"], c["shift"]), "o", ms=7,
                    color=shades[jump], mec=plots.SURFACE, mew=1.5)
    ax.set_xlim(0, max(c["ms"][-1] for c in curves.values()))
    ax.set_ylim(bottom=0)
    ax.set_xlabel("ms after movement onset (dotted lines = when the object jumped)")
    ax.set_ylabel("wrist shift from near reaches (cm)")
    ax.set_title("Real VR reaches: when the shift rises above noise (dots), by jump time")
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    pdir = Path(sys.argv[1])
    who = pdir.name
    data = load(pdir)
    work = ROOT / "work" / "furmanek2022" / who
    write_csv(data, work / "positions.csv")
    reps_paths = import_csv(work / "positions.csv", work / "trajectories", unit="cm", effector="wrist")
    reps = {k: Reps.load(p) for k, p in reps_paths.items()}

    out = ROOT / "results" / "furmanek2022" / who
    rng = np.random.default_rng(0)
    rows, curves = [], {}
    for jump in (100, 200, 300):
        name = f"N-to-F-{jump}"
        dtw_ms, _ = tool_divergence(reps, "N", name, rng, "velocity")
        onset_ms, curves[jump] = tool_divergence(reps, "N", name, rng, "onset")
        rows.append(dict(jump_ms=jump, n_jump=len(reps[name]), n_near=len(reps["N"]),
                         raw_ms=raw_divergence(data, "N", name, rng), tool_onset_ms=onset_ms, tool_dtw_ms=dtw_ms,
                         duration_near_ms=1000 * float(np.median(reps["N"].offset_t - reps["N"].onset_t)),
                         duration_jump_ms=1000 * float(np.median(reps[name].offset_t - reps[name].onset_t))))
    out.mkdir(parents=True, exist_ok=True)
    plot_timing(curves, [dict(r, tool_ms=r["tool_onset_ms"]) for r in rows], out / "timing.png")

    # The standard pipeline on the 200 ms jump. Durations differ by about 2x,
    # so it compares at the same ms after onset (the tool warns otherwise).
    analyse(dict(baseline=reps_paths["N"], test=reps_paths["N-to-F-200"]), out / "near_vs_jump200",
            align_on="onset")
    summary = dict(participant=who, source="Furmanek et al. 2022, Sci Data 9:23, CC0", timing=rows)
    (out / "check.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
