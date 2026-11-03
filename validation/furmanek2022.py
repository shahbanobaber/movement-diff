"""Real VR data: does the tool find a mid-reach change when it actually happened?

Data: Furmanek et al. (2022), Scientific Data 9:23, CC0, figshare
doi:10.6084/m9.figshare.13377506. People reached to grasp a virtual object
in an Oculus Rift while markers on the wrist, thumb and index finger were
tracked (75 Hz, released resampled to 100 Hz). On some trials the object
jumped from 20 cm to 40 cm away at 100, 200 or 300 ms after movement onset.

The check: jumped reaches against reaches to the near object, which start
the same way. A response to the jump can only start after it, and should
start later for later jumps.

Reference: the raw wrist positions (depth and height, what the tool sees)
compared in plain ms from the dataset's own movement onset, with no cutting
and no alignment. The tool runs three ways:

  given onsets  import --onset-at-zero, then --align-on onset. The pipeline alone.
  own onsets    import finds each reach's onset, then --align-on onset. As with video.
  DTW           own onsets, then the default --align-on velocity.

Every method uses the same statistic and rule. At each time step, label
shuffles give a 95% noise band for the distance between condition means.
The change starts where the distance rises above the band and stays above
it to the end of the window. Random splits of near reaches, where nothing
changed, measure how often the rule fires by chance.

Usage, from the repo root:
  python validation/furmanek2022.py data/furmanek2022/Full_Dataset/Dist_Pert/P*
Writes results/furmanek2022/<participant>/ and, for more than one
participant, results/furmanek2022/summary.md and timing_all.png. The first
participant also gets a full `analyse` run. No network, no paid APIs.
"""

from __future__ import annotations

import contextlib
import csv
import io
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
JUMP_MS = (100, 200, 300)
RUN = 5            # samples the distance must stay above the band, at minimum
N_PERM = 2000
N_SPLITS, SPLIT_SIZE, SPLIT_PERM = 20, 13, 500   # null check: near reaches split 13 vs the rest
METHODS = {"raw": "raw data", "given": "tool, given onsets", "own": "tool, own onsets", "dtw": "tool, DTW"}


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


def sustained(above: np.ndarray) -> int | None:
    """Start of the run above the band that lasts to the end of the window, if it is at least RUN long."""
    if not above[-1]:
        return None
    i = len(above) - 1
    while i > 0 and above[i - 1]:
        i -= 1
    return i if len(above) - i >= RUN else None


def _band(A: np.ndarray, B: np.ndarray, rng, n_perm: int) -> tuple[np.ndarray, np.ndarray]:
    """Distance between condition means and its pointwise 95% shuffle band. A, B: (n, T, 2).

    The same statistic as the shift curve and noise band in metrics.compare.
    """
    obs = np.linalg.norm(B.mean(0) - A.mean(0), axis=-1)
    pooled, na, nb = np.concatenate([A, B]), len(A), len(B)
    total, null = pooled.sum(0), np.empty((n_perm, A.shape[1]))
    for k in range(n_perm):
        sb = pooled[rng.permutation(na + nb)[:nb]].sum(0)
        null[k] = np.linalg.norm(sb / nb - (total - sb) / na, axis=-1)
    return obs, np.percentile(null, 95, axis=0)


def raw_divergence(data, a: str, b: str, rng, n_perm: int = N_PERM, split=None) -> float | None:
    """Wrist positions from the dataset's own onset (t=0), no cutting, no alignment."""
    def from_zero(trials):
        return [p[np.searchsorted(t, 0.0):, 0] for t, p in trials]

    A, B = from_zero(data[a]), from_zero(data[b])
    if split is not None:
        A, B = [A[i] for i in split[0]], [A[i] for i in split[1]]
    n = min(len(x) for x in A + B)
    obs, thr = _band(np.array([x[:n] for x in A]), np.array([x[:n] for x in B]), rng, n_perm)
    i = sustained(obs > thr)
    return None if i is None else 10.0 * i  # 100 Hz


def tool_curve(reps: dict[str, Reps], a: str, b: str, rng, mode: str, n_perm: int = N_PERM, split=None):
    """The tool's wrist shift curve and noise band, on the trial clock (ms after the dataset's onset)."""
    if split is None:
        conds, aligner, joints = build_conditions({"baseline": reps[a], "test": reps[b]}, "wrist", 101,
                                                  mode, 0.1, 1.0)
        ref, other = conds["baseline"], conds["test"]
    else:
        conds, aligner, joints = build_conditions({"baseline": reps[a]}, "wrist", 101, mode, 0.1, 1.0)
        ref, other = conds["baseline"].subset(split[0], "a"), conds["baseline"].subset(split[1], "b")
    c = compare(ref, other, phase_masks([1 / 3, 2 / 3], 101), rng, n_perm, 10)
    e = joints.index("wrist")
    # With onset mode the timeline is clock time from each rep's onset. With
    # DTW it is the baseline retimed to average baseline timing, so step u
    # sits at mean onset + u * mean duration.
    base = reps[a]
    onset_ms = 1000 * float(np.mean(base.onset_t))
    dur_ms = 1000 * (aligner.span_s if mode == "onset" else float(np.mean(base.offset_t - base.onset_t)))
    return dict(ms=(onset_ms + np.linspace(0, 1, 101) * dur_ms).tolist(),
                shift=c["shift_curve"][:, e].tolist(), null95=c["null95_curve"][:, e].tolist())


def divergence(curve: dict) -> float | None:
    i = sustained(np.asarray(curve["shift"]) > np.asarray(curve["null95"]))
    return None if i is None else float(curve["ms"][i])


def import_quietly(csv_path: Path, out: Path, **kw) -> dict[str, Reps]:
    with contextlib.redirect_stdout(io.StringIO()):
        paths = import_csv(csv_path, out, unit="cm", effector="wrist", **kw)
    return {k: Reps.load(p) for k, p in paths.items()}


def check_participant(pdir: Path, rng) -> tuple[dict, dict]:
    who = pdir.name
    data = load(pdir)
    work = ROOT / "work" / "furmanek2022" / who
    write_csv(data, work / "positions.csv")
    own = import_quietly(work / "positions.csv", work / "trajectories")
    given = import_quietly(work / "positions.csv", work / "trajectories_t0", onset_at_zero=True)

    rows, curves = [], {}
    for jump in JUMP_MS:
        b = f"N-to-F-{jump}"
        curves[jump] = tool_curve(own, "N", b, rng, "onset")
        rows.append(dict(jump_ms=jump, n_near=len(own["N"]), n_jump=len(own[b]),
                         raw=raw_divergence(data, "N", b, rng),
                         given=divergence(tool_curve(given, "N", b, rng, "onset")),
                         own=divergence(curves[jump]),
                         dtw=divergence(tool_curve(own, "N", b, rng, "velocity")),
                         duration_near_ms=1000 * float(np.median(own["N"].offset_t - own["N"].onset_t)),
                         duration_jump_ms=1000 * float(np.median(own[b].offset_t - own[b].onset_t))))

    # Nothing changed between two random halves of the near reaches.
    fired = {"raw": 0, "own": 0}
    for _ in range(N_SPLITS):
        p = rng.permutation(len(data["N"]))
        fired["raw"] += raw_divergence(data, "N", "N", rng, SPLIT_PERM, (p[SPLIT_SIZE:], p[:SPLIT_SIZE])) is not None
        q = rng.permutation(len(own["N"]))
        curve = tool_curve(own, "N", "N", rng, "onset", SPLIT_PERM, (q[SPLIT_SIZE:], q[:SPLIT_SIZE]))
        fired["own"] += divergence(curve) is not None
    return dict(participant=who, timing=rows, null_splits=N_SPLITS, null_fired=fired), curves


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
        if r["own"] is not None:
            ax.plot(r["own"], np.interp(r["own"], c["ms"], c["shift"]), "o", ms=7,
                    color=shades[jump], mec=plots.SURFACE, mew=1.5)
    ax.set_xlim(0, max(c["ms"][-1] for c in curves.values()))
    ax.set_ylim(bottom=0)
    ax.set_xlabel("ms after movement onset (dotted lines = when the object jumped)")
    ax.set_ylabel("wrist shift from near reaches (cm)")
    ax.set_title("Real VR reaches: when the shift rises above noise for good (dots), by jump time")
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_all(results: list[dict], path: Path) -> None:
    """One dot per participant and method: when the change starts, by jump time."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    plots._style()
    colors = {"raw": plots.INK2, "own": plots.COLORS["baseline"], "dtw": plots.COLORS["test"]}
    offset = {"raw": -0.24, "own": 0.0, "dtw": 0.24}
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    n = len(results)
    jitter = np.linspace(-0.07, 0.07, n)
    for g, jump in enumerate(JUMP_MS):
        ax.add_patch(plt.Rectangle((g - 0.42, 0), 0.84, jump, color=plots.NULL, lw=0, zorder=0))
        ax.plot([g - 0.42, g + 0.42], [jump, jump], color=plots.MUTED, lw=1, ls=(0, (2, 2)), zorder=1)
        for m in offset:
            ys = [next(r for r in res["timing"] if r["jump_ms"] == jump)[m] for res in results]
            xs = [g + offset[m] + jitter[k] for k, y in enumerate(ys) if y is not None]
            ax.plot(xs, [y for y in ys if y is not None], "o", ms=7, color=colors[m], mec=plots.SURFACE,
                    mew=1.5, ls="none", zorder=3, label=METHODS[m] if g == 0 else None)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(color=plots.NULL, lw=0))
    labels.append("before the object moved")
    ax.legend(handles, labels, loc="upper left", fontsize=8.5, ncol=2)
    ax.set_xticks(range(len(JUMP_MS)), [f"object jumped at {j} ms" for j in JUMP_MS])
    ax.set_xlim(-0.5, len(JUMP_MS) - 0.5)
    ax.set_ylim(0, 800)
    ax.set_ylabel("when the change starts (ms after onset)")
    ax.set_title(f"Real VR reaches, {n} people: when each method says the hand changed course")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _ms(v):
    return "not found" if v is None else f"{v:.0f}"


def summarise(results: list[dict]) -> str:
    rows = [(res["participant"], r) for res in results for r in res["timing"]]
    n = len(rows)

    def found(m):
        return [r for _, r in rows if r[m] is not None]

    def early(m):
        return sum(r[m] < r["jump_ms"] for r in found(m))

    def ordered(m):
        ok = 0
        for res in results:
            v = [r[m] for r in res["timing"]]
            ok += all(x is not None for x in v) and v[0] < v[1] < v[2]
        return ok

    def vs_raw(m):
        return [r[m] - r["raw"] for r in found(m) if r["raw"] is not None]

    lines = [
        "# Real VR reaches, all participants",
        "",
        "Generated by `validation/furmanek2022.py`. Furmanek et al. (2022), distance experiment: reaches to the "
        "near object (20 cm) against reaches where it jumped to 40 cm. Times are ms after the dataset's movement "
        "onset, when the wrist shift rises above the 95% noise band and stays above it.",
        "",
        "| participant | jump at | near / jumped trials | " + " | ".join(METHODS.values()) + " |",
        "|---|---|---|---|---|---|---|",
    ]
    for who, r in rows:
        lines.append(f"| {who} | {r['jump_ms']} | {r['n_near']} / {r['n_jump']} | {_ms(r['raw'])} | "
                     f"{_ms(r['given'])} | {_ms(r['own'])} | {_ms(r['dtw'])} |")
    lines += ["", "| | raw data | tool, given onsets | tool, own onsets | tool, DTW |", "|---|---|---|---|---|"]
    lines.append("| found | " + " | ".join(f"{len(found(m))}/{n}" for m in METHODS) + " |")
    lines.append("| before the object moved | " + " | ".join(str(early(m)) for m in METHODS) + " |")
    lines.append("| order 100 < 200 < 300 ms | " + " | ".join(f"{ordered(m)}/{len(results)}" for m in METHODS) + " |")
    diffs = {m: vs_raw(m) for m in METHODS if m != "raw"}
    lines.append("| median difference from raw (ms), range | | " + " | ".join(
        f"{round(np.median(d)):+d} [{round(min(d)):+d}, {round(max(d)):+d}]" for d in diffs.values()) + " |")
    total = sum(res["null_splits"] for res in results)
    fired = {m: sum(res["null_fired"][m] for res in results) for m in ("raw", "own")}
    lines += ["", f"Random splits of near reaches ({SPLIT_SIZE} against the rest, {total} splits), where nothing "
              f"changed. The rule fired in {fired['raw']} for the raw data ({100 * fired['raw'] / total:.0f}%) and "
              f"{fired['own']} for the tool with its own onsets ({100 * fired['own'] / total:.0f}%).", ""]
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    dirs = sorted((Path(p) for p in sys.argv[1:]), key=lambda p: (len(p.name), p.name))
    out = ROOT / "results" / "furmanek2022"
    results = []
    for k, pdir in enumerate(dirs):
        res, curves = check_participant(pdir, np.random.default_rng(k))
        res["source"] = "Furmanek et al. 2022, Sci Data 9:23, CC0"
        pout = out / res["participant"]
        pout.mkdir(parents=True, exist_ok=True)
        plot_timing(curves, res["timing"], pout / "timing.png")
        (pout / "check.json").write_text(json.dumps(res, indent=1))
        results.append(res)
        print(res["participant"], " ".join(f"{r['jump_ms']}: raw {_ms(r['raw'])} own {_ms(r['own'])} "
                                          f"dtw {_ms(r['dtw'])} |" for r in res["timing"]), flush=True)
        if k == 0:
            # The standard pipeline on the 200 ms jump, as a worked example.
            # Durations differ by about 2x, so it compares on clock time.
            work = ROOT / "work" / "furmanek2022" / res["participant"] / "trajectories"
            analyse(dict(baseline=work / "N.reps.npz", test=work / "N-to-F-200.reps.npz"),
                    pout / "near_vs_jump200", align_on="onset")
    if len(results) > 1:
        (out / "summary.md").write_text(summarise(results))
        plot_all(results, out / "timing_all.png")
        print(f"wrote {out / 'summary.md'} and timing_all.png")


if __name__ == "__main__":
    main()
