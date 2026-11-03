# Recording protocol

One person, one sitting, about 45 minutes with setup. Everything below is decided before the first rep and kept the same across blocks.

## Before recording

Write down the primary measure and commit it to this repo. The commit date is the timestamp. A reasonable choice:

> Primary: wrist shift and wrist spread ratio in each phase, test against baseline. Everything else is descriptive.

## The movement

Seated pointing at a target. Sit at a table with your hand resting on the table edge near your hip. Tape a small target at shoulder height on a box or wall, a little under arm's length in front of you. Each rep is one reach: touch the target with your index finger, hold for a second, go back to rest, pause one to two seconds.

This task has a clear start and end, its endpoint gives an outcome score to compare against, and it's the standard task in adaptation studies. A dart-throw motion works too. Add `--pad-before 0.4` to segment so the backswing is included, and `--cutoff 10` because throws are fast.

## Equipment

- **Camera A** records every block. A phone on a tripod or a stack of books, at 60 fps if it allows, 30 otherwise. Lock exposure and focus.
- **Device B** gives the displaced view, during practice only. A second phone or a laptop webcam showing a live view of your hand and the target.
- **Cardboard** to block your direct view of your arm during practice.
- **Tape** for the target and to mark where the chair and camera stand.
- **Tape measure** for your torso length.

## Camera A

- Side-on to the moving arm, lens at about shoulder height, at right angles to the reach. Everything the tool measures lies in the plane this camera sees.
- Shoulder, elbow, wrist, hand and hip in frame through the whole reach, with a margin.
- Plain background, even light, bare arm or a fitted sleeve.
- Tape the chair and camera positions. The camera must not move between blocks. Normalisation handles a small shift. It can't handle a new viewing angle.

Measure from the top of your shoulder to the bony point on the side of your hip, on the moving side. That number in cm is `--unit-cm`.

## Pilot

Record 5 reps. Run extract with `--overlay`, then segment. Check two things:

1. The overlay skeleton sits on your arm in every frame of the reach.
2. The segmentation plot shows 5 shaded reps and nothing else.

Adjust the setup until both hold, then delete the pilot video.

## Visual condition for baseline and test

Baseline and test must be done the same way. The recommended way is to look at the target, close your eyes, then reach, opening your eyes again at rest. With eyes closed, vision can't correct the reach partway through. Any trace of the practice block then shows in full, instead of being corrected away within a few reps.

If you keep your eyes open instead, expect the effect to fade fast. The "test first 5" comparison and the trials plot are there for that case.

## Block 1: baseline

20 reps with camera A recording.

## Block 2: perturbed practice

40 reps, camera A still recording.

- Hold the cardboard at chin height so it hides your arm and the target from direct view.
- Watch only device B's screen. Aim its camera at your hand and the target from an angle, so the screen shows them displaced from where they really are.
- The displacement has to act forward-back or up-down, in the plane camera A sees. A purely sideways displacement causes errors camera A can't see.
- Check it works. Your first few practice reps should miss the target clearly and then improve. If they don't miss, the displacement is too small.
- Eyes open throughout. You're learning from the screen.

## Block 3: test

Start straight after practice, with no break. Put the cardboard and device B away. 20 reps, done the same way as baseline.

## Control, if there's time

On another day, repeat all three blocks with an undisplaced view in block 2. If test still differs from baseline, the change came from practice or fatigue, not from the displacement.

## Processing

```bash
python -m movediff extract data/baseline.mp4 data/practice.mp4 data/test.mp4 --overlay
python -m movediff segment work/baseline.pose.npz --side right --expect 20
python -m movediff segment work/practice.pose.npz --side right --expect 40
python -m movediff segment work/test.pose.npz --side right --expect 20
python -m movediff analyse --baseline trajectories/baseline.reps.npz \
    --practice trajectories/practice.reps.npz --test trajectories/test.reps.npz \
    --unit-cm <your torso length> --out-dir results/real
```

Use `--side left` if you point with your left arm. Open every segmentation plot before running analyse.

## Video and privacy

Raw video goes in `data/`, which `.gitignore` keeps out of the repo, and so are the overlay videos in `work/`. Both show your face. What goes public is the per-rep trajectories in `trajectories/` and the results.
