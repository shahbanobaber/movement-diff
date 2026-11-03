import numpy as np

from movediff.align import Aligner, dtw, resample, warp


def _reach(n, warp_power=1.0, offset=0.0):
    tau = np.linspace(0, 1, n) ** warp_power
    s = 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5
    x = np.column_stack([s, 0.3 * np.sin(np.pi * s) + offset])
    return x[:, None, :]  # (n, 1 joint, 2)


def test_dtw_identical_is_diagonal():
    a = np.random.default_rng(0).normal(size=(30, 2))
    cost, path = dtw(a, a, band=5)
    assert cost == 0
    assert np.array_equal(path[:, 0], path[:, 1])


def test_warp_undoes_a_time_distortion():
    ref = resample(_reach(80), 101)
    bent = resample(_reach(80, warp_power=1.4), 101)  # same path, different timing
    al = Aligner([ref, ref], mode="velocity", band_frac=0.2)
    aligned, _ = al.align(bent)
    before = np.abs(bent - ref).mean()
    after = np.abs(aligned - ref).mean()
    assert after < 0.25 * before


def test_velocity_alignment_keeps_a_constant_offset():
    ref = resample(_reach(80), 101)
    moved = resample(_reach(80, offset=0.05), 101)
    al = Aligner([ref, ref], mode="velocity")
    aligned, _ = al.align(moved)
    assert np.allclose(aligned[:, 0, 1] - ref[:, 0, 1], 0.05, atol=1e-3)


def test_warp_is_identity_on_diagonal_path():
    traj = np.random.default_rng(1).normal(size=(50, 3, 2))
    path = np.column_stack([np.arange(50), np.arange(50)])
    assert np.allclose(warp(traj, path, 50), traj)
