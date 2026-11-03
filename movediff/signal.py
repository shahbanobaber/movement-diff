"""Small signal helpers: uniform resampling, gap filling, zero-lag low-pass filter."""

from __future__ import annotations

import numpy as np


def to_uniform(t: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Resample x (T, ...) onto a uniform time grid if the frame times are irregular.

    Phone cameras often record variable frame rate. Returns (t, x, fps).
    """
    dt = np.diff(t)
    step = float(np.median(dt))
    if np.all(np.abs(dt - step) < 0.25 * step):
        return t, x, 1.0 / step
    tu = np.arange(t[0], t[-1] + 1e-9, step)
    flat = x.reshape(len(t), -1)
    out = np.column_stack([np.interp(tu, t, flat[:, k]) for k in range(flat.shape[1])])
    return tu, out.reshape((len(tu),) + x.shape[1:]), 1.0 / step


def _runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """[start, end) of each run of True."""
    padded = np.concatenate([[False], mask, [False]])
    edges = np.flatnonzero(np.diff(padded.astype(int)))
    return list(zip(edges[::2], edges[1::2], strict=True))


def fill_gaps(x: np.ndarray, max_gap: int) -> tuple[np.ndarray, np.ndarray]:
    """Linearly interpolate missing frames along axis 0.

    Every gap is filled so the filter can run, but gaps longer than `max_gap`
    frames, or touching either end, are reported in the returned (T,) mask so
    reps that overlap them can be dropped.
    """
    x = np.array(x, dtype=float, copy=True)
    T = x.shape[0]
    flat = x.reshape(T, -1)
    missing = np.isnan(flat).any(axis=1)
    still = np.zeros(T, dtype=bool)
    for s, e in _runs(missing):
        if e - s > max_gap or s == 0 or e == T:
            still[s:e] = True
    idx = np.arange(T)
    for k in range(flat.shape[1]):
        col = flat[:, k]
        ok = ~np.isnan(col)
        if ok.sum() >= 2:
            flat[:, k] = np.interp(idx, idx[ok], col[ok])
    return flat.reshape(x.shape), still


def lowpass(x: np.ndarray, fps: float, cutoff: float | None, order: int = 2) -> np.ndarray:
    """Zero-lag Butterworth low-pass along axis 0 (filtfilt doubles the order)."""
    from scipy.signal import butter, filtfilt

    nyq = fps / 2.0
    if not cutoff or cutoff >= 0.95 * nyq or x.shape[0] < 10:
        return x
    b, a = butter(order, cutoff / nyq)
    return filtfilt(b, a, x, axis=0, padlen=min(3 * max(len(a), len(b)), x.shape[0] - 1))
