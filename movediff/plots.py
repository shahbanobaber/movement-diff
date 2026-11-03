"""Figures. Colours follow the condition everywhere: baseline blue, test orange, practice aqua."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
GRID, SURFACE, NULL = "#e6e5e1", "#fcfcfb", "#dddcd7"
COLORS = {"baseline": "#2a78d6", "test": "#eb6834", "practice": "#1baf7a"}


def colour(name: str) -> str:
    return COLORS.get(name.split()[0], MUTED)


def _style() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
        "font.size": 9.5, "axes.titlesize": 10.5, "axes.titlelocation": "left", "legend.frameon": False,
        "lines.linewidth": 1.8, "lines.solid_capstyle": "round", "axes.axisbelow": True,
    })


def _phase_guides(ax, bounds, names, label=True) -> None:
    edges = [0.0, *bounds, 1.0]
    for b in bounds:
        ax.axvline(b * 100, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=1)
    if label:
        for k, n in enumerate(names):
            ax.text((edges[k] + edges[k + 1]) * 50, 1.0, n, transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", color=INK2, fontsize=8.5)


def _end_labels(ax, items, x, min_gap=0.07) -> None:
    """Direct labels at the right end of lines, nudged apart so they don't collide."""
    lo, hi = ax.get_ylim()
    ys = sorted(((y - lo) / (hi - lo), text) for y, text in items)
    placed = []
    for y, text in ys:
        if placed and y - placed[-1][0] < min_gap:
            y = placed[-1][0] + min_gap
        placed.append((y, text))
    for y, text in placed:
        ax.text(x, lo + y * (hi - lo), " " + text, color=INK2, fontsize=8.5, va="center", ha="left",
                clip_on=False)


def plot_segmentation(diag, reps_name: str, path: Path) -> None:
    _style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 4.6), sharex=True, height_ratios=(1.4, 1))
    t = diag.t
    ax1.plot(t, diag.speed, color=INK2, lw=1)
    ax1.axhline(diag.threshold, color=MUTED, lw=0.8, ls=(0, (3, 3)))
    for c in diag.candidates:
        t0, t1, tp = t[c["onset"]], t[c["offset"]], t[c["peak"]]
        if c["status"] == "kept":
            ax1.axvspan(t0, t1, color=COLORS["baseline"], alpha=0.16, lw=0)
            ax1.text(tp, diag.speed[c["peak"]], str(c["number"]), ha="center", va="bottom", fontsize=7.5, color=INK)
        else:
            ax1.plot(tp, diag.speed[c["peak"]], marker="x", color="#d03b3b", ms=7, mew=1.5)
            ax1.text(tp, diag.speed[c["peak"]], f"{c['number']} {c['reason']}", ha="left", va="bottom",
                     fontsize=7, color="#d03b3b")
    kept = sum(c["status"] == "kept" for c in diag.candidates)
    ax1.set_title(f"{reps_name}: {kept} reps kept of {len(diag.candidates)} candidates "
                  "(shaded = kept, x = rejected, dashed = peak threshold)")
    ax1.set_ylabel("effector speed")
    ax2.plot(t, diag.effector_xy[:, 0], color=INK2, lw=1, label="x (forward)")
    ax2.plot(t, diag.effector_xy[:, 1], color=MUTED, lw=1, ls=(0, (4, 2)), label="y (up)")
    ax2.set_ylabel("effector position")
    ax2.set_xlabel("time (s)")
    ax2.legend(loc="upper right", ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_shift(cmp: dict, joints, bounds, names, units, path: Path) -> None:
    """Where in the movement each condition's mean moved away from the baseline mean."""
    _style()
    keys = [k for k in ("practice vs baseline", "test vs baseline") if k in cmp]
    test = cmp["test vs baseline"]
    L = test["shift_curve"].shape[0]
    x = np.linspace(0, 100, L)
    fig, axes = plt.subplots(1, len(joints), figsize=(3.5 * len(joints) + 0.9, 3.3), sharey=True, squeeze=False)
    axes = axes[0]
    ymax = max(max(cmp[k]["shift_curve"].max() for k in keys), test["null95_curve"].max()) * 1.12
    for j, ax in enumerate(axes):
        ax.fill_between(x, 0, test["null95_curve"][:, j], color=NULL, lw=0, zorder=2,
                        label="noise floor for test (95% of label shuffles)")
        for k in keys:
            ax.plot(x, cmp[k]["shift_curve"][:, j], color=colour(k), zorder=3, label=k.split(" vs ")[0])
        _phase_guides(ax, bounds, names)
        ax.set_title(joints[j], pad=14)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, ymax)
        ax.set_xticks([0, 25, 50, 75, 100])
    _end_labels(axes[-1], [(cmp[k]["shift_curve"][-1, -1], k.split(" vs ")[0]) for k in keys], 100)
    axes[0].set_ylabel(f"distance from baseline mean ({units})")
    fig.supxlabel("% of movement, on the baseline timeline", color=INK2, fontsize=9.5)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper right", ncol=len(lab), fontsize=8.5, bbox_to_anchor=(1.0, 1.0))
    fig.suptitle("Shift: how far the mean movement moved from baseline", x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0, 0.97, 0.95))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_spread(spread: dict, joints, names, units, path: Path) -> None:
    """Within-condition spread per phase: did the movement get less repeatable?"""
    _style()
    conds = [c for c in ("baseline", "practice", "test") if c in spread]
    fig, axes = plt.subplots(1, len(joints), figsize=(3.5 * len(joints), 3.3), sharey=True, squeeze=False)
    axes = axes[0]
    w = 0.8 / len(conds)
    xs = np.arange(len(names))
    for j, ax in enumerate(axes):
        for i, c in enumerate(conds):
            val, ci = spread[c]
            pos = xs - 0.4 + w * (i + 0.5)
            ax.bar(pos, val[:, j], width=w, color=colour(c), edgecolor=SURFACE, linewidth=2,
                   label=c, zorder=2)
            ax.vlines(pos, ci[0, :, j], ci[1, :, j], color=INK2, lw=1, zorder=3)
        ax.set_xticks(xs, names)
        ax.set_title(joints[j])
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel(f"spread around own mean ({units})")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper right", ncol=len(lab), fontsize=8.5, bbox_to_anchor=(1.0, 1.0))
    fig.suptitle("Spread: how repeatable each condition was (lines = 95% bootstrap CI)",
                 x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_trials(rows: list[dict], effector: str, units: str, path: Path, window: int = 5) -> None:
    """Per-rep deviation from the baseline mean in session order (adaptation and washout)."""
    _style()
    fig, ax = plt.subplots(figsize=(9, 3.2))
    order = []
    for r in rows:
        if r["condition"] not in order:
            order.append(r["condition"])
    start = 0
    for name in order:
        dev = np.array([r["deviation"] for r in rows if r["condition"] == name])
        idx = np.arange(start, start + len(dev)) + 1
        ax.scatter(idx, dev, s=18, color=colour(name), edgecolor=SURFACE, linewidth=0.8, zorder=3, label=name)
        if len(dev) >= window:
            run = np.convolve(dev, np.ones(window) / window, mode="valid")
            ax.plot(idx[window // 2 : window // 2 + len(run)], run, color=colour(name), zorder=2, lw=1.8)
        if start:
            ax.axvline(start + 0.5, color=MUTED, lw=0.8, ls=(0, (3, 3)))
        ax.text(start + 1, 1.0, name, transform=ax.get_xaxis_transform(), ha="left", va="bottom",
                color=INK2, fontsize=8.5)
        start += len(dev)
    ax.set_xlim(0, start + 1)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("rep, in recording order")
    ax.set_ylabel(f"{effector} deviation ({units})")
    ax.set_title(f"Every rep against the baseline mean (line = {window}-rep running mean)", pad=14)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_speed(conds: dict, effector: str, units: str, path: Path) -> None:
    """Mean effector speed profile per condition on linear 0-100% time."""
    _style()
    fig, ax = plt.subplots(figsize=(5.6, 3.3))
    names = [c for c in ("baseline", "practice", "test") if c in conds]
    L = conds[names[0]].speed.shape[1]
    x = np.linspace(0, 100, L)
    for n in names:
        s = conds[n].speed
        m, sd = s.mean(0), s.std(0, ddof=1)
        ax.fill_between(x, m - sd, m + sd, color=colour(n), alpha=0.13, lw=0)
        ax.plot(x, m, color=colour(n), label=n)
    ax.set_xlim(0, 100)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("% of movement time")
    ax.set_ylabel(f"{effector} speed ({units}/s)")
    ax.set_title("Velocity profile (band = ±1 SD across reps)")
    ax.legend(loc="upper right", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
