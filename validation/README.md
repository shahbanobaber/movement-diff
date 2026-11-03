# Validation

Checks that the method measures what it claims. Everything here runs on simulated data where the right answer is known.

## Choosing the alignment

Reps have to be put on a shared timeline before they can be compared point by point, and the method used changes the answer. Four options were tested on three simulated changes, with six seeds each. The script is [benchmark_alignment.py](benchmark_alignment.py), and [alignment_benchmark.md](alignment_benchmark.md) has the full output.

| Alignment | Error on mid-reach bend | Error on undershoot | Undershoot, mid phase (true 0.031) | Timing change left over |
|---|---|---|---|---|
| Linear time only | 0.009 | 0.008 | 0.030 | 100% |
| DTW on position | 0.007 | 0.026 | 0.005 | 1-3% |
| DTW on velocity (default) | 0.010 | 0.012 | 0.030 | 20-23% |
| DTW on speed | 0.011 | 0.018 | 0.048 | 32-35% |

Errors are in torso lengths, about 50 cm.

- **Position DTW** erases most of an undershoot, because it slides the short reach along the long one until they match. Undershoot is what depth compression in a headset would cause, so this rules it out.
- **Linear time** reports a pure timing change as a change in path. A slower, more careful reach would show up as a fake shift.
- **Velocity DTW** is the only option that holds up in all three cases. It over-reads the end of an undershoot by about 18%.

Because no option wins everywhere, every summary also prints the shift computed with linear time. If the two agree, the change is in the path. If the linear one is much larger, part of it is timing.

## Bugs the simulation caught

1. **Fidgets counted as reps.** Candidates that travel less than half the median rep distance are now rejected and marked on the segmentation plot.
2. **Extra wobble looked like a shift.** Wobble at the start of a reach triggered the rep cut early, and the misaligned reps showed a significant fake shift later in the movement. Reps are now cut on speed along the main direction of the movement.
3. **An averaged template was distorted.** Averaging time-warped reps gave a speed profile no real reach has, and every rep was then aligned to it. The template is now one real baseline rep, retimed to average baseline timing.

## Real VR data

Script: [furmanek2022.py](furmanek2022.py). Output: [results/furmanek2022/P1/](../results/furmanek2022/P1/).

The data come from Furmanek et al. (2022), released under CC0. People reached to grasp a virtual object in an Oculus Rift DK2 while motion capture tracked the wrist, thumb and index finger at 75 Hz, resampled to 100 Hz. In the distance experiment, the object sometimes jumped to a new distance 100, 200 or 300 ms after movement onset. The check uses participant P1 from the public subset: reaches to the near object (20 cm, 89 trials) against reaches where it jumped from 20 cm to 40 cm (14 to 16 trials per jump time). Positions are projected onto the reach direction across the table and height, the plane a side camera would see.

The data go in through `movediff import` like any other CSV, so this also tests the import path.

The reference is a plain comparison of the raw wrist positions, aligned only on the paper's own onset (switch release). For each 10 ms step it runs a permutation test, and it records the first moment the difference stays above the 95% noise band for 50 ms. The tool uses the same rule on its shift curve.

| Object jumped at | Raw data | Tool, onset mode | Tool, DTW |
|---|---|---|---|
| 100 ms | 410 ms | 376 ms | 63 ms |
| 200 ms | 490 ms | 474 ms | 68 ms |
| 300 ms | 570 ms | 555 ms | 144 ms |

Onset mode agrees with the raw data to within 35 ms. It reads slightly early because it lines reps up on each rep's own movement onset, which removes some timing jitter. In the raw data each separation comes 270 to 310 ms after its jump, a plausible reaction time.

DTW fails here, at every band width tried (0.1, 0.3 and 0.5). Normal reaches took 540 ms and jumped reaches 910 to 1,190 ms. On a 0-100% timeline, 40% of a jumped reach is about 400 ms but 40% of a normal reach is about 220 ms. The tool compared different moments and found a difference before the object moved. DTW matches on the shape of the velocity profile, and a two-part corrective reach has a different shape from a one-part reach, so warping can't fix it.

What changed as a result:

- `--align-on onset` compares reps at the same milliseconds after onset, up to the baseline's median duration. A rep that has already ended holds its final position.
- The summary warns when test reps take more than 1.25x or less than 0.8x as long as baseline reps.
- `tests/test_tabular.py` reproduces the failure. A simulated two-part reach fails under DTW and passes under onset mode.

For the aftereffect experiment in PROTOCOL.md, baseline and test are the same reach, so durations should be close and DTW stays the default. The warning will say if they aren't.
