"""Synthetic sessions with KNOWN changes, to check the instrument recovers them.

A planar two-link arm reaches forward from a rest position near the hip to a
target in front of the shoulder, then returns. Wrist paths follow a
minimum-jerk profile (Flash & Hogan 1985). Output files use the same format as
extract.py, so everything after pose extraction runs unchanged.

Every rep in every session also gets its own timing (see `timing_sd`), so
alignment has real work to do.

Injected into the TEST session relative to baseline:
  1. a mean path bulge in the MIDDLE of the reach (peak at 50% of movement
     time, gone by the endpoint), decaying over test reps like an aftereffect
     washing out
  2. extra rep-to-rep variability in the EARLY part of the reach only
  3. slower reaches (0.92 s vs 0.80 s)
  4. NO change in where the reach ends
and the person sits in a different spot (camera offset and 4% scale change),
which normalisation should remove.

A good instrument reports: shift concentrated mid, spread up early only,
duration up, endpoint unchanged. tests/test_synthetic.py checks exactly that.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .landmarks import lm

FPS = 30.0
TL = 200.0  # torso length in pixels
UPPER, FORE, HAND = 0.55, 0.50, 0.18  # segment lengths in torso lengths
REST = np.array([0.25, -0.80])
TARGET = np.array([0.95, -0.15])
UNDERSHOOT = 0.06  # scenario "undershoot": test reaches stop this far short of baseline

TRUTH = dict(
    bulge_mean_test=0.025, bulge_extra_first=0.07, bulge_decay_reps=6.0, bulge_centre=0.5, bulge_width=0.08,
    early_sd_test=0.045, early_window=0.4, duration_baseline=0.80, duration_test=0.92,
    endpoint_change=0.0, timing_sd=0.12, units="torso lengths",
)


def _min_jerk(tau):
    return 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5


def _elbow(w):
    """Elbow position for wrist positions w (n, 2) relative to the shoulder, elbow below the line."""
    d = np.clip(np.linalg.norm(w, axis=1), 1e-6, UPPER + FORE - 1e-6)
    a = np.arccos(np.clip((UPPER ** 2 + d ** 2 - FORE ** 2) / (2 * UPPER * d), -1, 1))
    ang = np.arctan2(w[:, 1], w[:, 0]) - a
    return UPPER * np.column_stack([np.cos(ang), np.sin(ang)])


def _reach(kind: str, k: int, rng, scenario: str = "bulge") -> tuple[np.ndarray, float]:
    """Wrist path (n, 2) for rep k of a session, relative to the shoulder, plus its duration."""
    direction = TARGET - REST
    unit = direction / np.linalg.norm(direction)
    normal = np.array([-unit[1], unit[0]])

    base_sd, early_sd, endpoint_shift = 0.012, 0.0, np.zeros(2)
    if kind == "baseline":
        dur, bulge = rng.normal(TRUTH["duration_baseline"], 0.05), 0.0
    elif kind == "practice":
        dur = rng.normal(0.90, 0.06)
        bulge = 0.03 + 0.12 * np.exp(-k / 10)
        endpoint_shift = np.array([0.0, 0.08 * np.exp(-k / 8)])
        base_sd = 0.03
    elif kind == "test":
        dur = rng.normal(TRUTH["duration_test"], 0.05)
        early_sd = TRUTH["early_sd_test"]
        if scenario == "bulge":
            bulge = TRUTH["bulge_mean_test"] + TRUTH["bulge_extra_first"] * np.exp(-k / TRUTH["bulge_decay_reps"])
        elif scenario == "undershoot":
            bulge, endpoint_shift = 0.0, -UNDERSHOOT * unit
        else:
            raise ValueError(f"unknown scenario {scenario!r}")
    else:
        raise ValueError(kind)

    n = int(round(dur * FPS)) + 1
    # Real reps differ in timing within the movement (a longer or shorter
    # deceleration), not just in total duration. Each rep's clock runs as
    # t**p with p drawn around 1. Spatial changes are injected against tau,
    # the movement's own phase, so they stay where they belong.
    tau = np.linspace(0, 1, n) ** np.exp(rng.normal(0, TRUTH["timing_sd"]))
    s = _min_jerk(tau)
    start = REST + rng.normal(0, 0.008, 2)
    end = TARGET + rng.normal(0, 0.012, 2) + endpoint_shift
    path = start + s[:, None] * (end - start)
    g = np.exp(-0.5 * ((tau - TRUTH["bulge_centre"]) / TRUTH["bulge_width"]) ** 2)
    early = np.where(tau < TRUTH["early_window"], np.sin(np.pi * tau / TRUTH["early_window"]), 0.0)
    off = bulge * g + rng.normal(0, base_sd) * np.sin(np.pi * tau) + rng.normal(0, early_sd) * early
    return path + off[:, None] * normal, dur


def session(kind: str, n_reps: int, seed: int, shift_px=(0.0, 0.0), scale=1.0, scenario="bulge") -> dict:
    rng = np.random.default_rng(seed)
    shoulder0 = np.array([300.0, 520.0]) + np.array(shift_px)
    wrist, lean = [], []

    def hold(pos, secs):
        m = int(round(secs * FPS))
        wrist.append(np.repeat(pos[None], m, 0) + rng.normal(0, 0.002, (m, 2)).cumsum(0) * 0.2)
        lean.append(np.zeros(m))

    hold(REST, 1.0)
    for k in range(n_reps):
        out, _ = _reach(kind, k, rng, scenario)
        wrist.append(out)
        lean.append(_min_jerk(np.linspace(0, 1, len(out))) * 0.03)
        hold(out[-1], rng.uniform(0.35, 0.6))
        n_back = int(round(rng.normal(0.8, 0.05) * FPS)) + 1
        s = _min_jerk(np.linspace(0, 1, n_back))[:, None]
        back_to = REST + rng.normal(0, 0.008, 2)
        wrist.append(out[-1] + s * (back_to - out[-1]))
        lean.append(0.03 * (1 - s[:, 0]))
        hold(back_to, rng.uniform(0.5, 0.9))
    w = np.concatenate(wrist)
    lean_x = np.concatenate(lean)
    T = len(w)

    px = TL * scale
    shoulder = shoulder0 + np.column_stack([lean_x * px, np.zeros(T)])
    elbow = _elbow(w)
    fore = (w - elbow) / np.linalg.norm(w - elbow, axis=1, keepdims=True)
    index = w + HAND * fore

    xy = np.zeros((T, 33, 2))
    vis = np.full((T, 33), 0.95)
    xy[:] = shoulder0  # parked landmarks
    side = "right"
    xy[:, lm(side, "shoulder")] = shoulder
    xy[:, lm(side, "elbow")] = shoulder + elbow * px
    xy[:, lm(side, "wrist")] = shoulder + w * px
    xy[:, lm(side, "index")] = shoulder + index * px
    xy[:, lm(side, "pinky")] = shoulder + index * px
    xy[:, lm(side, "thumb")] = shoulder + index * px
    xy[:, lm(side, "hip")] = shoulder0 + np.array([0.0, -px])
    xy[:, lm("left", "hip")] = shoulder0 + np.array([0.0, -px])
    xy[:, lm(side, "nose")] = shoulder + np.array([0.15, 0.55]) * px
    for leg in ("knee", "ankle", "heel", "foot_index"):
        vis[:, lm("left", leg)] = vis[:, lm("right", leg)] = 0.2  # under the table
    xy += rng.normal(0, 1.2, xy.shape)  # landmark jitter, ~0.006 torso lengths
    return dict(xy=xy, z=np.zeros((T, 33)), vis=vis, world=np.zeros((T, 33, 3)), t=np.arange(T) / FPS,
                fps=FPS, width=800, height=800, video="synthetic")


def write_sessions(out_dir: Path, n_base=20, n_practice=40, n_test=20, seed=1, scenario="bulge") -> dict[str, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = dict(baseline=(n_base, (0, 0), 1.0), practice=(n_practice, (10, 0), 1.0), test=(n_test, (25, -8), 1.04))
    paths = {}
    for i, (kind, (n, shift, scale)) in enumerate(specs.items()):
        path = out_dir / f"{kind}.pose.npz"
        np.savez_compressed(path, **session(kind, n, seed + i, shift, scale, scenario))
        paths[kind] = path
    truth = dict(TRUTH, scenario=scenario, undershoot=UNDERSHOOT)
    (out_dir / "ground_truth.json").write_text(json.dumps(truth, indent=1))
    return paths
