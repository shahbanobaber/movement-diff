"""Step 3: put every rep on one shared timeline with dynamic time warping.

Each rep is first resampled to L points (0-100% of its duration), then warped
onto a reference built from the baseline reps.

By default the warp is computed on joint VELOCITY, not position (derivative
DTW, Keogh & Pazzani 2001). Position-based DTW matches each point to the
nearest point on the reference, so it partly hides the spatial offsets this
tool is trying to measure. Velocity is blind to a constant offset, so the warp
only fixes timing and the offset survives into the deviation metrics.
"""

from __future__ import annotations

import numpy as np


def resample(traj: np.ndarray, n: int) -> np.ndarray:
    """Linear resample of (m, ...) to (n, ...) over normalised time."""
    m = traj.shape[0]
    src, dst = np.linspace(0, 1, m), np.linspace(0, 1, n)
    flat = traj.reshape(m, -1)
    out = np.column_stack([np.interp(dst, src, flat[:, k]) for k in range(flat.shape[1])])
    return out.reshape((n,) + traj.shape[1:])


def features(traj: np.ndarray, mode: str) -> np.ndarray:
    """(n, J, 2) trajectory -> (n, J*2) DTW features.

    Features keep their size. Dividing each rep by its own RMS velocity looks
    tidier but, in validation/, it halved a known undershoot: the warp starts
    trading timing against the shape differences scaling creates.
    """
    if mode == "speed":
        f = np.linalg.norm(np.gradient(traj, axis=0), axis=-1) * (len(traj) - 1)
    elif mode == "velocity":
        f = np.gradient(traj, axis=0) * (len(traj) - 1)
    elif mode == "position":
        f = traj
    else:
        raise ValueError(f"unknown align mode {mode!r}")
    return f.reshape(len(traj), -1)


def dtw(a: np.ndarray, b: np.ndarray, band: int | None = None) -> tuple[float, np.ndarray]:
    """DTW between (n, d) and (m, d) with a Sakoe-Chiba band of `band` samples.

    Returns (cost per step, path) where path is a (K, 2) array of (i, j) pairs.
    """
    n, m = len(a), len(b)
    cost = np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1))
    if band is not None:
        w = max(band, abs(n - m))
        i, j = np.indices((n, m))
        cost = np.where(np.abs(i * (m - 1) / max(n - 1, 1) - j) <= w, cost, np.inf)
    inf = float("inf")
    D = [[inf] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0.0
    rows = cost.tolist()
    for i in range(1, n + 1):
        ci, prev, row = rows[i - 1], D[i - 1], D[i]
        for j in range(1, m + 1):
            c = ci[j - 1]
            if c == inf:
                continue
            best = prev[j - 1]
            if prev[j] < best:
                best = prev[j]
            if row[j - 1] < best:
                best = row[j - 1]
            row[j] = c + best
    # Backtrack, preferring the diagonal on ties.
    i, j, path = n, m, [(n - 1, m - 1)]
    while i > 1 or j > 1:
        options = ((D[i - 1][j - 1], i - 1, j - 1), (D[i - 1][j], i - 1, j), (D[i][j - 1], i, j - 1))
        _, i, j = min(options, key=lambda o: o[0])
        path.append((i - 1, j - 1))
    path.reverse()
    return D[n][m] / (n + m), np.array(path)


def time_map(path: np.ndarray, n_ref: int, n_rep: int, smooth: int = 7) -> np.ndarray:
    """Turn a DTW path into a smooth, increasing map: reference sample -> fractional rep sample.

    A raw DTW path is a staircase, and reading a rep off it puts small steps
    into every curve. Averaging the matched rep index per reference sample,
    smoothing it and forcing it to increase removes the steps.
    """
    s = np.zeros(n_ref)
    c = np.zeros(n_ref)
    np.add.at(s, path[:, 0], path[:, 1])
    np.add.at(c, path[:, 0], 1)
    j = s / c
    if smooth > 1:
        pad = smooth // 2
        padded = np.concatenate([2 * j[0] - j[pad:0:-1], j, 2 * j[-1] - j[-2 : -pad - 2 : -1]])
        j = np.convolve(padded, np.ones(smooth) / smooth, mode="valid")
    j = np.maximum.accumulate(np.clip(j, 0, n_rep - 1))
    j[0], j[-1] = 0, n_rep - 1
    return j


def warp(traj: np.ndarray, path: np.ndarray, n_ref: int) -> np.ndarray:
    """Read a rep at the reference timeline's sample points."""
    j = time_map(path, n_ref, len(traj))
    flat = traj.reshape(len(traj), -1)
    idx = np.arange(len(traj))
    out = np.column_stack([np.interp(j, idx, flat[:, k]) for k in range(flat.shape[1])])
    return out.reshape((n_ref,) + traj.shape[1:])


class Aligner:
    """Warps reps onto the timeline of one real baseline rep, the medoid.

    The medoid is the baseline rep with the smallest total DTW distance to the
    others. Using a real rep as the target, rather than an average of warped
    reps, matters: warping stretches and squeezes time, so an average of
    warped reps has a lumpy velocity profile no real movement has, and every
    rep aligned to it inherits the lumps.

    mode "none" skips DTW and keeps the linear 0-100% time normalisation, as a
    check on what the warping changes.
    """

    def __init__(self, baseline: list[np.ndarray], mode: str = "velocity", band_frac: float = 0.1,
                 refine: bool = False):
        self.mode = mode
        self.L = len(baseline[0])
        self.band = max(1, int(round(band_frac * self.L)))
        if mode == "none":
            self.medoid = None
            self.reference = np.mean(baseline, axis=0)
            return
        feats = [features(r, mode) for r in baseline]
        n = len(feats)
        dist = np.zeros((n, n))
        for a in range(n):
            for b in range(a + 1, n):
                dist[a, b] = dist[b, a] = dtw(feats[a], feats[b], self.band)[0]
        self.medoid = int(np.argmin(dist.sum(axis=1)))
        medoid = baseline[self.medoid]
        if refine:  # kept for the benchmark: target = mean of baseline warped onto the medoid
            self.reference = np.mean([warp(r, dtw(feats[self.medoid], f, self.band)[1], self.L)
                                      for r, f in zip(baseline, feats, strict=True)], axis=0)
        else:
            # DTW picks the medoid by shape, not timing, so its own clock can be
            # early or late. Retime it so the average baseline rep maps onto it
            # with no warp: then "33% of the movement" means 33% of a typical
            # baseline rep, and phase boundaries are cut where people expect.
            maps = [time_map(dtw(feats[self.medoid], f, self.band)[1], self.L, self.L) for f in feats]
            # Fit a gentle curve to the average map: a lumpy retiming would put
            # lumps back into the target's velocity profile.
            u = np.linspace(0, 1, self.L)
            mean_map = np.mean(maps, axis=0) / (self.L - 1)
            coef = np.polyfit(u, mean_map - u, 4)
            mean_map = np.maximum.accumulate(np.clip(u + np.polyval(coef, u) - np.polyval(coef, 0) * (1 - u)
                                                     - np.polyval(coef, 1) * u, 0, 1))
            idx = np.interp(np.linspace(0, 1, self.L), mean_map, np.arange(self.L))
            flat = medoid.reshape(self.L, -1)
            self.reference = np.column_stack([np.interp(idx, np.arange(self.L), flat[:, k])
                                              for k in range(flat.shape[1])]).reshape(medoid.shape)
        self._ref_feat = features(self.reference, mode)

    def align(self, traj: np.ndarray) -> tuple[np.ndarray, float]:
        if self.mode == "none":
            return traj, 0.0
        cost, path = dtw(self._ref_feat, features(traj, self.mode), self.band)
        return warp(traj, path, self.L), cost
