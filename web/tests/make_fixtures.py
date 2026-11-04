"""Write web/sample.json (the synthetic demo sessions) and web/tests/expected.json (Python's numbers on them).

The browser port must reproduce the Python method. Run from the repo root:
  python web/tests/make_fixtures.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from movediff.align import Aligner, resample  # noqa: E402
from movediff.metrics import _phase_rms, _spread_sq, phase_masks  # noqa: E402
from movediff.segment import Reps  # noqa: E402

L = 101


def reps(name):
    r = Reps.load(ROOT / "results/synthetic/trajectories" / f"{name}.reps.npz")
    w, e = r.joints.index("wrist"), r.joints.index("elbow")
    return [r.rep(k)[:, [w, e]] for k in range(len(r))]    # (n, 2 joints, 2), shoulder at the origin


A, B = reps("baseline"), reps("test")
# Arm length (upper arm + forearm), so the sample uses the same units as the camera path.
frames = np.concatenate(A)
arm = float(np.median(np.linalg.norm(frames[:, 1], axis=1) + np.linalg.norm(frames[:, 0] - frames[:, 1], axis=1)))
A, B = [r / arm for r in A], [r / arm for r in B]
sample = {"label": "Simulated arm: the test reaches bend in the middle and wobble at the start",
          "A": [np.round(r, 5).tolist() for r in A], "B": [np.round(r, 5).tolist() for r in B]}
(ROOT / "web/sample.json").write_text(json.dumps(sample, separators=(",", ":")))

# Python's numbers on exactly the rounded data the browser will load.
A = [np.array(r) for r in sample["A"]]
B = [np.array(r) for r in sample["B"]]
masks = phase_masks([1 / 3, 2 / 3], L)
out = {}
for mode in ("none", "velocity"):
    ra, rb = [resample(r, L) for r in A], [resample(r, L) for r in B]
    al = Aligner(ra, mode=mode)
    XA = np.array([al.align(r)[0] for r in ra])
    XB = np.array([al.align(r)[0] for r in rb])
    sq = ((XB.mean(0) - XA.mean(0)) ** 2).sum(-1)        # (L, J)
    out[mode] = {"shift": _phase_rms(sq, masks)[:, 0].tolist(),
                 "spreadA": _phase_rms(_spread_sq(XA), masks)[:, 0].tolist(),
                 "spreadB": _phase_rms(_spread_sq(XB), masks)[:, 0].tolist(),
                 "curve": np.sqrt(sq[:, 0]).tolist()}
(ROOT / "web/tests/expected.json").write_text(json.dumps(out, indent=1))
print(f"arm = {arm:.3f} torso lengths; {len(A)} and {len(B)} reps")
for mode, v in out.items():
    print(mode, "shift", np.round(v["shift"], 4), "spread ratio", np.round(np.array(v["spreadB"]) / v["spreadA"], 3))
