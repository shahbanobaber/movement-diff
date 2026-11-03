"""Step 5: run the metrics for every comparison and write metrics.json, summary.md and figures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import plots
from .metrics import KINEMATICS, build_conditions, compare, phase_masks, spread_with_ci, trial_series
from .segment import Reps


def analyse(
    paths: dict[str, Path | None],
    out_dir: Path,
    *,
    effector: str | None = None,
    bounds: tuple[float, ...] = (1 / 3, 2 / 3),
    names: tuple[str, ...] = ("early", "mid", "late"),
    align_on: str = "velocity",
    band: float = 0.1,
    unit_cm: float | None = None,
    L: int = 101,
    n_perm: int = 2000,
    n_boot: int = 2000,
    seed: int = 0,
    first_n: int = 5,
) -> dict:
    if len(names) != len(bounds) + 1:
        raise SystemExit(f"{len(bounds)} phase boundaries need {len(bounds) + 1} names, got {len(names)}")
    order = [k for k in ("baseline", "practice", "test") if paths.get(k)]
    reps = {k: Reps.load(paths[k]) for k in order}
    unit = {r.unit for r in reps.values()}
    if len(unit) > 1:
        raise SystemExit(f"sessions were scaled differently ({unit}); re-run segment with the same --scale")
    unit = unit.pop()
    units = "cm" if unit_cm else f"{unit} lengths"
    factor = unit_cm or 1.0
    effector = effector or reps["baseline"].effector

    conds, aligner, joints = build_conditions(reps, effector, L, align_on, band, factor)
    e = joints.index(effector)
    masks = phase_masks(list(bounds), L)
    rng = np.random.default_rng(seed)

    pairs = []
    if "practice" in conds:
        pairs.append(("practice vs baseline", conds["baseline"], conds["practice"]))
    test = conds["test"]
    pairs.append(("test vs baseline", conds["baseline"], test))
    if len(test) >= 2 * first_n:
        pairs.append((f"test first {first_n} vs baseline", conds["baseline"],
                      test.subset(range(first_n), f"test first {first_n}")))
        pairs.append((f"test last {first_n} vs baseline", conds["baseline"],
                      test.subset(range(len(test) - first_n, len(test)), f"test last {first_n}")))
    b = conds["baseline"]
    h = len(b) // 2
    pairs.append(("baseline 2nd half vs 1st half", b.subset(range(h), "baseline 1st half"),
                  b.subset(range(h, len(b)), "baseline 2nd half")))

    cmp = {label: compare(ref, other, masks, rng, n_perm, n_boot) for label, ref, other in pairs}

    # Cross-check: the same comparison with linear 0-100% time and no DTW. If
    # the two agree, the shift is in the path. If the linear shift is much
    # bigger, part of it is the movement's timing, which the warp removed.
    if align_on != "none":
        lin, _, _ = build_conditions(reps, effector, L, "none", band, factor)
        cmp["test vs baseline"]["linear"] = compare(lin["baseline"], lin["test"], masks, rng, n_perm, 10)
    spread = {k: spread_with_ci(conds[k], masks, rng, n_boot) for k in order}
    trials = trial_series(conds, order, e)

    settings = dict(
        sessions={k: str(paths[k]) for k in order}, n_reps={k: len(conds[k]) for k in order},
        joints=joints, effector=effector, units=units, phases=dict(zip(names, _edges(bounds), strict=True)),
        align_on=align_on, band=band, samples=L, n_perm=n_perm, n_boot=n_boot, seed=seed,
        baseline_peak_speed_at=float(np.median(conds["baseline"].t_peak)),
    )

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = dict(settings=settings, comparisons={k: _to_json(v, joints, names) for k, v in cmp.items()},
                  spread={k: _spread_json(v, joints, names) for k, v in spread.items()}, trials=trials)
    (out_dir / "metrics.json").write_text(json.dumps(result, indent=1))
    (out_dir / "summary.md").write_text(_summary(result, cmp, joints, names, effector, units))

    plots.plot_shift(cmp, joints, list(bounds), list(names), units, out_dir / "shift_by_phase.png")
    plots.plot_spread(spread, joints, list(names), units, out_dir / "spread_by_condition.png")
    plots.plot_trials(trials, effector, units, out_dir / "trials.png")
    plots.plot_speed(conds, effector, units, out_dir / "speed_profile.png")
    print(f"wrote {out_dir}/metrics.json, summary.md and 4 figures")
    return result


def _edges(bounds):
    e = [0.0, *bounds, 1.0]
    return [[round(e[k], 3), round(e[k + 1], 3)] for k in range(len(e) - 1)]


def _pj(arr, joints, names):
    return {j: {n: _num(arr[p, k]) for p, n in enumerate(names)} for k, j in enumerate(joints)}


def _num(x):
    x = np.asarray(x)
    return [round(float(v), 5) for v in x] if x.ndim else round(float(x), 5)


def _to_json(c: dict, joints, names) -> dict:
    out = {k: c[k] for k in ("ref", "other", "n_ref", "n_other", "endpoint", "kinematics", "speed_profile_rmsd")}
    for key in ("shift", "noise_floor", "p_shift", "share", "spread_ref", "spread_other", "spread_ratio",
                "p_spread", "rmsd", "within"):
        out[key] = _pj(c[key], joints, names)
    out["signed_shift_xy"] = _pj(c["signed"], joints, names)
    out["spread_ratio_ci"] = {j: {n: [_num(c["spread_ratio_ci"][0, p, k]), _num(c["spread_ratio_ci"][1, p, k])]
                                  for p, n in enumerate(names)} for k, j in enumerate(joints)}
    out["shift_peak_at"] = {j: _num(c["peak_at"][k]) for k, j in enumerate(joints)}
    if "linear" in c:
        out["shift_linear_time"] = _pj(c["linear"]["shift"], joints, names)
        out["p_shift_linear_time"] = _pj(c["linear"]["p_shift"], joints, names)
    return out


def _spread_json(v, joints, names):
    val, ci = v
    return {j: {n: dict(value=_num(val[p, k]), ci=[_num(ci[0, p, k]), _num(ci[1, p, k])])
                for p, n in enumerate(names)} for k, j in enumerate(joints)}


def _p(p: float) -> str:
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def _pe(p: float) -> str:
    return "p<0.001" if p < 0.001 else f"p={p:.3f}"


def _f(x: float) -> str:
    return f"{x:.3f}" if abs(x) < 10 else f"{x:.1f}"


def _summary(result, cmp, joints, names, effector, units) -> str:
    s = result["settings"]
    e = joints.index(effector)
    lines = [
        "# Results summary",
        "",
        f"Reps: {', '.join(f'{k} {v}' for k, v in s['n_reps'].items())}. Units: {units}. "
        f"Effector: {effector}. Phases: "
        + ", ".join(f"{n} {int(a * 100)}-{int(b * 100)}%" for n, (a, b) in s["phases"].items())
        + f". Baseline reps reach peak {effector} speed at {s['baseline_peak_speed_at']:.0%} of their duration "
        "(median), a useful landmark when choosing phase boundaries.",
        "",
        "p-values are permutation tests across this person's reps "
        f"({s['n_perm']} shuffles), uncorrected for the number of cells.",
        "",
    ]
    for label, c in cmp.items():
        lines += [f"## {label} ({c['n_other']} vs {c['n_ref']} reps)", ""]
        lines += ["Shift of the mean movement, per phase. Noise floor = the same statistic "
                  "averaged over label shuffles.", ""]
        lines += ["| joint | " + " | ".join(names) + " |", "|---" * (len(names) + 1) + "|"]
        for k, j in enumerate(joints):
            cells = [f"{_f(c['shift'][p, k])} (floor {_f(c['noise_floor'][p, k])}), {_pe(c['p_shift'][p, k])}"
                     for p in range(len(names))]
            lines.append(f"| {j} | " + " | ".join(cells) + " |")
        share = ", ".join(f"{n} {c['share'][p, e]:.0%}" for p, n in enumerate(names))
        lines += ["", f"Where the {effector} shift sits: {share}. "
                      f"Largest at {c['peak_at'][e]:.0%} of the movement.", ""]
        if "linear" in c:
            lin = c["linear"]
            cells = ", ".join(f"{n} {_f(lin['shift'][p, e])} ({_pe(lin['p_shift'][p, e])})"
                              for p, n in enumerate(names))
            lines += [f"Same {effector} shift with linear time instead of DTW: {cells}. Where this is much "
                      "larger than the DTW value, part of the change is timing rather than path.", ""]

        lines += ["Spread around the condition's own mean, per phase.", "",
                  f"| joint | phase | {c['ref']} | {c['other']} | ratio [95% CI] | p |", "|---" * 6 + "|"]
        for k, j in enumerate(joints):
            for p, n in enumerate(names):
                lo, hi = c["spread_ratio_ci"][:, p, k]
                lines.append(f"| {j} | {n} | {_f(c['spread_ref'][p, k])} | {_f(c['spread_other'][p, k])} | "
                             f"{c['spread_ratio'][p, k]:.2f} [{lo:.2f}, {hi:.2f}] | {_p(c['p_spread'][p, k])} |")

        lines += ["", f"Accuracy-style score for the {effector} (RMS distance from the baseline mean) "
                      "split into its two parts. shift^2 + spread^2 = score^2.", "",
                  "| phase | score | shift part | spread part | share from shift |", "|---" * 5 + "|"]
        for p, n in enumerate(names):
            r, sh, w = c["rmsd"][p, e], c["shift"][p, e], c["within"][p, e]
            lines.append(f"| {n} | {_f(r)} | {_f(sh)} | {_f(w)} | {sh ** 2 / r ** 2:.0%} |")

        ep = c["endpoint"]
        lines += ["", f"Endpoint of the {effector}, the closest thing here to an outcome score: "
                      f"mean moved {_f(ep['shift'])} (dx {ep['dx']:+.3f}, dy {ep['dy']:+.3f}), {_pe(ep['p'])}; "
                      f"spread ratio {ep['spread_ratio']:.2f}.", ""]

        lines += ["| kinematics | " + c["ref"] + " | " + c["other"] + " | diff | Hedges g | p |", "|---" * 6 + "|"]
        for key, (label_k, unit_k) in KINEMATICS.items():
            k = c["kinematics"][key]
            u = unit_k.replace("units", units)
            lines.append(f"| {label_k} ({u}) | {_f(k['ref_mean'])} ± {_f(k['ref_sd'])} | "
                         f"{_f(k['other_mean'])} ± {_f(k['other_sd'])} | {k['diff']:+.3f} | {k['g']:+.2f} | "
                         f"{_p(k['p'])} |")
        lines += ["", f"Mean speed profile differs from {c['ref']} by {c['speed_profile_rmsd']:.1%} "
                      "of its peak (RMS over the movement).", ""]
    return "\n".join(lines)
