"""End to end on synthetic sessions where the right answer is known (see movediff/synth.py)."""

import numpy as np
import pytest

from movediff.metrics import build_conditions, compare, phase_masks
from movediff.segment import segment
from movediff.synth import write_sessions

L = 101
MASKS = phase_masks([1 / 3, 2 / 3], L)
EARLY, MID, LATE = 0, 1, 2


def _run(tmp_path, scenario):
    poses = write_sessions(tmp_path, seed=1, scenario=scenario)
    reps = {k: segment(p)[0] for k, p in poses.items()}
    conds, _, joints = build_conditions(reps, "wrist", L, "velocity", 0.1, 1.0)
    rng = np.random.default_rng(0)
    test = compare(conds["baseline"], conds["test"], MASKS, rng, 500, 500)
    b = conds["baseline"]
    half = compare(b.subset(range(10), "b1"), b.subset(range(10, 20), "b2"), MASKS, rng, 500, 200)
    return reps, test, half, joints.index("wrist")


@pytest.fixture(scope="module")
def bulge(tmp_path_factory):
    return _run(tmp_path_factory.mktemp("bulge"), "bulge")


@pytest.fixture(scope="module")
def undershoot(tmp_path_factory):
    return _run(tmp_path_factory.mktemp("undershoot"), "undershoot")


def test_segmentation_finds_every_rep(bulge):
    reps = bulge[0]
    assert {k: len(r) for k, r in reps.items()} == {"baseline": 20, "practice": 40, "test": 20}


def test_normalisation_removes_where_the_person_sat(bulge):
    # The test session is filmed 25 px to the side and 4% larger. After
    # normalisation the resting wrist should be in the same place.
    reps = bulge[0]
    start = {k: np.mean([r.rep(i)[0, r.joints.index("wrist")] for i in range(len(r))], axis=0)
             for k, r in reps.items()}
    assert np.linalg.norm(start["test"] - start["baseline"]) < 0.02


def test_bulge_shift_is_found_in_the_middle(bulge):
    _, c, _, e = bulge
    assert c["p_shift"][MID, e] < 0.01
    assert c["share"][MID, e] > 0.5
    assert 0.4 <= c["peak_at"][e] <= 0.6


def test_bulge_endpoint_looks_unchanged(bulge):
    # The case outcome scores miss: the path changed, the end point did not.
    _, c, _, _ = bulge
    assert c["endpoint"]["p"] > 0.05
    assert c["endpoint"]["shift"] < 0.02


def test_extra_variability_is_found_early_only(bulge):
    _, c, _, e = bulge
    assert c["spread_ratio"][EARLY, e] > 1.5 and c["p_spread"][EARLY, e] < 0.05
    lo, hi = c["spread_ratio_ci"][:, LATE, e]
    assert lo < 1 < hi


def test_slower_reaches_are_found(bulge):
    _, c, _, _ = bulge
    k = c["kinematics"]["duration"]
    assert k["diff"] > 0.08 and k["p"] < 0.01


def test_baseline_halves_do_not_differ(bulge):
    _, _, half, e = bulge
    assert (half["p_shift"][:, e] > 0.05).all()


def test_undershoot_is_found_at_the_end(undershoot):
    _, c, _, e = undershoot
    assert c["share"][LATE, e] > 0.5
    assert c["shift"][LATE, e] > c["shift"][MID, e] > c["shift"][EARLY, e]
    assert c["endpoint"]["p"] < 0.01
    assert c["endpoint"]["dx"] < 0  # stops short of the baseline reach
