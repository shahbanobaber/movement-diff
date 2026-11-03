"""Imported position data and the onset (clock time) timeline."""

import numpy as np

from movediff.metrics import build_conditions, compare, phase_masks
from movediff.segment import Reps
from movediff.synth import _min_jerk
from movediff.tabular import import_csv

FPS = 100


def _trial(rng, amplitude, extra=0.0, jump_s=None, rest=0.4, dur=0.6, fix=0.7):
    """A forward reach with rest before and after.

    With jump_s, a second movement of `extra` cm starts jump_s after the
    first and lasts `fix` s, added on top: the usual model of a correction.
    """
    end = dur if jump_s is None else jump_s + fix
    t = np.arange(0, end + 1e-9, 1 / FPS)
    x = amplitude * _min_jerk(np.clip(t / dur, 0, 1))
    if jump_s is not None:
        x = x + extra * _min_jerk(np.clip((t - jump_s) / fix, 0, 1))
    pre, post = np.zeros(int(rest * FPS)), np.full(int(rest * FPS), x[-1])
    x = np.concatenate([pre, x, post]) + rng.normal(0, 0.02, len(pre) + len(x) + len(post))
    y = 0.1 * x + rng.normal(0, 0.02, len(x))
    t = np.arange(len(x)) / FPS
    return t, np.stack([np.column_stack([x, y]), np.column_stack([x * 0.8, y])], axis=1)


def _write(path, conds):
    with open(path, "w") as fh:
        fh.write("condition,trial,t,joint,x,y\n")
        for name, trials in conds.items():
            for k, (t, pos) in enumerate(trials, 1):
                for i in range(len(t)):
                    for j, joint in enumerate(("wrist", "elbow")):
                        fh.write(f"{name},{k},{t[i]:.3f},{joint},{pos[i, j, 0]:.4f},{pos[i, j, 1]:.4f}\n")


def test_import_cuts_out_the_movement(tmp_path):
    rng = np.random.default_rng(0)
    _write(tmp_path / "pos.csv", {"base": [_trial(rng, 20) for _ in range(5)]})
    paths = import_csv(tmp_path / "pos.csv", tmp_path / "out", unit="cm", effector="wrist")
    reps = Reps.load(paths["base"])
    assert len(reps) == 5 and reps.joints == ["wrist", "elbow"] and reps.unit == "cm"
    # Movement is 0.6 s inside 1.4 s of data. The cut keeps the moving part only.
    durations = (reps.lengths - 1) / reps.fps
    assert np.all((durations > 0.4) & (durations < 0.7))
    travel = [np.linalg.norm(reps.rep(k)[-1, 0] - reps.rep(k)[0, 0]) for k in range(len(reps))]
    assert np.allclose(travel, 20, atol=2)


def test_onset_timeline_finds_a_change_after_it_happens(tmp_path):
    # Same reach until 0.3 s, then the test trials extend 15 cm further and
    # take longer. On clock time the shift must start after 0.3 s.
    rng = np.random.default_rng(1)
    _write(tmp_path / "pos.csv", {"base": [_trial(rng, 20) for _ in range(20)],
                                  "jump": [_trial(rng, 20, extra=15, jump_s=0.3) for _ in range(15)]})
    paths = import_csv(tmp_path / "pos.csv", tmp_path / "out", unit="cm", effector="wrist")
    reps = {"baseline": Reps.load(paths["base"]), "test": Reps.load(paths["jump"])}
    conds, aligner, _ = build_conditions(reps, "wrist", 101, "onset", 0.1, 1.0)
    c = compare(conds["baseline"], conds["test"], phase_masks([1 / 3, 2 / 3], 101), np.random.default_rng(0), 300, 5)
    above = c["shift_curve"][:, 0] > c["null95_curve"][:, 0]
    first = np.argmax(above) / 100 * aligner.span_s + reps["baseline"].onset_t.mean() - 0.4
    assert above.any() and first > 0.3
