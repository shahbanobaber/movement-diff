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
