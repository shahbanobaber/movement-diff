"""Step 4: the metrics.

For each condition every rep sits on the baseline timeline (from align.py),
so at each point t of the movement there is a cloud of rep positions per joint.

shift(t)   distance between the condition's mean position and the baseline mean.
           Systematic change: the movement moved.
spread(t)  RMS distance of reps from their OWN condition mean.
           Repeatability: the movement got noisier or tighter.

They add up. For a condition's reps measured against the baseline mean,
    mean squared deviation = shift^2 + spread^2
so an accuracy-style score (deviation from the template) cannot tell a
shifted-but-consistent learner from an on-average-correct-but-noisy one.
This module reports the two parts separately, per joint and per phase.

Every number comes with a reference for "how big is this by chance":
  shift: permutation test. Shuffle rep labels between the two conditions and
         recompute; the mean of the shuffled values is the noise floor.
  spread: bootstrap CI for the ratio, and a permutation test on residuals
          (each condition centred on its own mean first, so a mean shift does
          not leak into the variance test).
Tests are across reps of one person: they say whether THIS person's movement
changed, not whether people in general would show it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import find_peaks

from .align import Aligner, resample


@dataclass
class Condition:
    name: str
    aligned: np.ndarray     # (R, L, J, 2) on the baseline timeline
    speed: np.ndarray       # (R, L) effector speed on linear 0-100% time (not warped)
    duration: np.ndarray    # (R,) s
    peak_speed: np.ndarray  # (R,) units/s
    t_peak: np.ndarray      # (R,) fraction of movement time
    n_sub: np.ndarray       # (R,) speed peaks (submovements)
    endpoint: np.ndarray    # (R, 2) effector position at the last frame
    rep_ids: np.ndarray

    def __len__(self) -> int:
        return len(self.aligned)

    def subset(self, idx, name: str) -> "Condition":
        idx = np.asarray(idx)
        return Condition(name, self.aligned[idx], self.speed[idx], self.duration[idx], self.peak_speed[idx],
                         self.t_peak[idx], self.n_sub[idx], self.endpoint[idx], self.rep_ids[idx])


KINEMATICS = {
    "duration": ("movement time", "s"),
    "peak_speed": ("peak speed", "units/s"),
    "t_peak": ("time to peak speed", "% of movement"),
    "n_sub": ("speed peaks per rep", "count"),
}


def phase_masks(bounds: list[float], L: int) -> list[np.ndarray]:
    frac = np.arange(L) / (L - 1)
    edges = [0.0, *bounds, 1.0]
    masks = []
    for k in range(len(edges) - 1):
        hi = frac <= edges[k + 1] if k == len(edges) - 2 else frac < edges[k + 1]
        masks.append((frac >= edges[k]) & hi)
    return masks


def _phase_rms(sq: np.ndarray, masks) -> np.ndarray:
    """sq (..., L, J) squared values -> (..., P, J) RMS within each phase."""
    return np.stack([np.sqrt(sq[..., m, :].mean(axis=-2)) for m in masks], axis=-2)


def _phase_sum(sq: np.ndarray, masks) -> np.ndarray:
    return np.stack([sq[..., m, :].sum(axis=-2) for m in masks], axis=-2)


def _spread_sq(X: np.ndarray) -> np.ndarray:
    """Unbiased mean squared distance to the group mean: (R, L, J, 2) -> (L, J)."""
    R = len(X)
    return ((X - X.mean(0)) ** 2).sum(-1).sum(0) / (R - 1)


def _hedges_g(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    if sp == 0:
        return 0.0
    return float((b.mean() - a.mean()) / sp * (1 - 3 / (4 * (na + nb) - 9)))


def _perm_p_diff(a: np.ndarray, b: np.ndarray, rng, n_perm: int) -> float:
    """Two-sided permutation p for a difference in means (works on (R,) or (R, d))."""
    pooled = np.concatenate([a, b])
    na = len(a)
    obs = np.linalg.norm(np.atleast_1d(b.mean(0) - a.mean(0)))
    hits = 0
    for _ in range(n_perm):
        p = rng.permutation(len(pooled))
        d = pooled[p[na:]].mean(0) - pooled[p[:na]].mean(0)
        hits += np.linalg.norm(np.atleast_1d(d)) >= obs - 1e-12
    return (1 + hits) / (1 + n_perm)


def build_conditions(reps_by_name: dict, effector: str, L: int, align_on: str, band: float,
                     factor: float, refine: bool = False) -> tuple[dict[str, Condition], Aligner, list[str]]:
    joints = reps_by_name["baseline"].joints
    for r in reps_by_name.values():
        if r.joints != joints:
            raise SystemExit(f"{r.name}: joints {r.joints} differ from baseline {joints}")
    e = joints.index(effector)

    resampled = {k: [resample(r.rep(i) * factor, L) for i in range(len(r))] for k, r in reps_by_name.items()}
    aligner = Aligner(resampled["baseline"], mode=align_on, band_frac=band, refine=refine)

    conds = {}
    for k, r in reps_by_name.items():
        aligned, speed, dur, peak, tpk, nsub, endp = [], [], [], [], [], [], []
        for i in range(len(r)):
            raw = r.rep(i) * factor
            m = len(raw)
            sp = np.linalg.norm(np.gradient(raw[:, e], axis=0), axis=-1) * r.fps
            aligned.append(aligner.align(resampled[k][i])[0])
            speed.append(resample(sp[:, None], L)[:, 0])
            dur.append((m - 1) / r.fps)
            peak.append(sp.max())
            tpk.append(sp.argmax() / (m - 1))
            nsub.append(max(1, len(find_peaks(sp, prominence=0.1 * sp.max())[0])))
            endp.append(raw[-1, e])
        conds[k] = Condition(k, np.array(aligned), np.array(speed), np.array(dur), np.array(peak),
                             np.array(tpk), np.array(nsub, dtype=float), np.array(endp), r.rep_ids)
    return conds, aligner, joints


def spread_with_ci(c: Condition, masks, rng, n_boot: int) -> tuple[np.ndarray, np.ndarray]:
    """(P, J) spread and (2, P, J) bootstrap 95% CI."""
    value = _phase_rms(_spread_sq(c.aligned), masks)
    R = len(c)
    boots = np.array([_phase_rms(_spread_sq(c.aligned[rng.integers(0, R, R)]), masks) for _ in range(n_boot)])
    return value, np.percentile(boots, [2.5, 97.5], axis=0)


def compare(ref: Condition, other: Condition, masks, rng, n_perm: int, n_boot: int) -> dict:
    """Everything that changed from `ref` to `other`. Arrays are (P, J) unless noted."""
    A, B = ref.aligned, other.aligned
    na, nb = len(A), len(B)
    delta = B.mean(0) - A.mean(0)                    # (L, J, 2)
    sq = (delta ** 2).sum(-1)                        # (L, J)
    shift = _phase_rms(sq, masks)
    share = _phase_sum(sq, masks) / sq.sum(0)
    signed = np.stack([delta[m].mean(0) for m in masks])   # (P, J, 2)

    pooled = np.concatenate([A, B])
    total = pooled.sum(0)
    null_phase = np.empty((n_perm,) + shift.shape)
    null_curve = np.empty((n_perm,) + sq.shape)
    for k in range(n_perm):
        idx_b = rng.permutation(na + nb)[:nb]
        sum_b = pooled[idx_b].sum(0)
        d = sum_b / nb - (total - sum_b) / na
        s = (d ** 2).sum(-1)
        null_curve[k] = np.sqrt(s)
        null_phase[k] = _phase_rms(s, masks)
    p_shift = (1 + (null_phase >= shift - 1e-12).sum(0)) / (1 + n_perm)

    # Spread: ratio, bootstrap CI, permutation on residuals.
    sa, sb = _phase_rms(_spread_sq(A), masks), _phase_rms(_spread_sq(B), masks)
    ratio = sb / sa
    boots = np.empty((n_boot,) + ratio.shape)
    for k in range(n_boot):
        ia, ib = rng.integers(0, na, na), rng.integers(0, nb, nb)
        boots[k] = _phase_rms(_spread_sq(B[ib]), masks) / _phase_rms(_spread_sq(A[ia]), masks)
    ratio_ci = np.percentile(boots, [2.5, 97.5], axis=0)
    res = np.concatenate([(A - A.mean(0)) * np.sqrt(na / (na - 1)), (B - B.mean(0)) * np.sqrt(nb / (nb - 1))])
    ss = (res ** 2).sum(-1)                          # (N, L, J)
    obs = np.abs(np.log(ratio))
    hits = np.zeros_like(ratio)
    for _ in range(n_perm):
        p = rng.permutation(na + nb)
        r = _phase_rms(ss[p[na:]].mean(0), masks) / _phase_rms(ss[p[:na]].mean(0), masks)
        hits += np.abs(np.log(r)) >= obs - 1e-12
    p_spread = (1 + hits) / (1 + n_perm)

    # Accuracy-style score and its exact decomposition (population variance here so the sum is exact).
    msd = ((B - A.mean(0)) ** 2).sum(-1).mean(0)
    within = ((B - B.mean(0)) ** 2).sum(-1).mean(0)

    # Endpoint: what an outcome measure would see.
    ea, eb = ref.endpoint, other.endpoint
    e_res_a = np.linalg.norm(ea - ea.mean(0), axis=1)
    e_res_b = np.linalg.norm(eb - eb.mean(0), axis=1)
    endpoint = dict(
        shift=float(np.linalg.norm(eb.mean(0) - ea.mean(0))),
        dx=float(eb.mean(0)[0] - ea.mean(0)[0]),
        dy=float(eb.mean(0)[1] - ea.mean(0)[1]),
        p=_perm_p_diff(ea, eb, rng, n_perm),
        spread_ref=float(np.sqrt((e_res_a ** 2).sum() / (na - 1))),
        spread_other=float(np.sqrt((e_res_b ** 2).sum() / (nb - 1))),
    )
    endpoint["spread_ratio"] = endpoint["spread_other"] / endpoint["spread_ref"]

    kin = {}
    for key in KINEMATICS:
        a, b = getattr(ref, key), getattr(other, key)
        scale = 100.0 if key == "t_peak" else 1.0
        kin[key] = dict(ref_mean=float(a.mean() * scale), ref_sd=float(a.std(ddof=1) * scale),
                        other_mean=float(b.mean() * scale), other_sd=float(b.std(ddof=1) * scale),
                        diff=float((b.mean() - a.mean()) * scale), g=_hedges_g(a, b),
                        p=_perm_p_diff(a, b, rng, n_perm))

    prof_a, prof_b = ref.speed.mean(0), other.speed.mean(0)
    return dict(
        ref=ref.name, other=other.name, n_ref=na, n_other=nb,
        shift=shift, noise_floor=null_phase.mean(0), p_shift=p_shift, share=share, signed=signed,
        shift_curve=np.sqrt(sq), null95_curve=np.percentile(null_curve, 95, axis=0),
        peak_at=np.argmax(sq, axis=0) / (len(sq) - 1),
        spread_ref=sa, spread_other=sb, spread_ratio=ratio, spread_ratio_ci=ratio_ci, p_spread=p_spread,
        rmsd=_phase_rms(msd, masks), within=_phase_rms(within, masks),
        endpoint=endpoint, kinematics=kin,
        speed_profile_rmsd=float(np.sqrt(((prof_b - prof_a) ** 2).mean()) / prof_a.max()),
    )


def trial_series(conds: dict[str, Condition], order: list[str], e: int) -> list[dict]:
    """Per-rep RMS deviation of the effector from the baseline mean, in session order.

    Baseline reps are measured against the mean of the OTHER baseline reps, so
    they are not flattered by being part of their own reference.
    """
    base = conds["baseline"].aligned[:, :, e]       # (R, L, 2)
    total = base.sum(0)
    R = len(base)
    rows = []
    for name in order:
        c = conds[name]
        for i in range(len(c)):
            x = c.aligned[i, :, e]
            ref = (total - x) / (R - 1) if name == "baseline" else total / R
            dev = float(np.sqrt(((x - ref) ** 2).sum(-1).mean()))
            rows.append(dict(condition=name, rep=int(c.rep_ids[i]), deviation=dev))
    return rows
