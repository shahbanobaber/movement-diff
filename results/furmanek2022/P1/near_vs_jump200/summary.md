# Results summary

Reps: baseline 89, test 14. Units: cm. Effector: wrist. Phases: early 0-33%, mid 33-66%, late 66-100%. Baseline reps reach peak wrist speed at 41% of their duration (median), a useful landmark when choosing phase boundaries.

Timeline: milliseconds from movement onset, 0 to 970 ms; phases are fractions of that.

p-values are permutation tests across this person's reps (2000 shuffles), uncorrected for the number of cells.

## test vs baseline (14 vs 89 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| wrist | 0.137 (floor 0.200), p=0.734 | 4.779 (floor 0.468), p<0.001 | 16.1 (floor 1.273), p<0.001 |
| thumb | 0.216 (floor 0.225), p=0.492 | 5.064 (floor 0.475), p<0.001 | 16.0 (floor 1.257), p<0.001 |
| index | 0.338 (floor 0.273), p=0.250 | 5.447 (floor 0.521), p<0.001 | 16.6 (floor 1.308), p<0.001 |

Where the wrist shift sits: early 0%, mid 8%, late 92%. Largest at 100% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test | ratio [95% CI] | p |
|---|---|---|---|---|---|
| wrist | early | 0.741 | 0.844 | 1.14 [0.80, 1.43] | 0.318 |
| wrist | mid | 0.786 | 1.581 | 2.01 [1.47, 2.41] | <0.001 |
| wrist | late | 0.643 | 1.432 | 2.23 [1.51, 2.68] | <0.001 |
| thumb | early | 0.808 | 1.001 | 1.24 [0.88, 1.54] | 0.230 |
| thumb | mid | 0.682 | 1.518 | 2.22 [1.61, 2.67] | <0.001 |
| thumb | late | 0.583 | 1.295 | 2.22 [1.48, 2.68] | <0.001 |
| index | early | 0.994 | 1.110 | 1.12 [0.80, 1.38] | 0.468 |
| index | mid | 0.838 | 1.608 | 1.92 [1.42, 2.31] | <0.001 |
| index | late | 0.696 | 1.359 | 1.95 [1.30, 2.39] | <0.001 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.825 | 0.137 | 0.814 | 3% |
| mid | 5.016 | 4.779 | 1.524 | 91% |
| late | 16.2 | 16.1 | 1.380 | 99% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 19.2 (dx +19.185, dy +0.240), p<0.001; spread ratio 1.12.

| kinematics | baseline | test | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.515 ± 0.028 | 0.976 ± 0.042 | +0.461 | +15.19 | <0.001 |
| peak speed (cm/s) | 59.5 ± 4.112 | 59.2 ± 4.360 | -0.267 | -0.06 | 0.819 |
| time to peak speed (% of movement) | 40.2 ± 3.189 | 28.5 ± 16.4 | -11.686 | -1.76 | <0.001 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.929 ± 0.267 | +0.929 | +9.61 | <0.001 |

Mean speed profile differs from baseline by 18.4% of its peak (RMS over the movement).

## test first 5 vs baseline (5 vs 89 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| wrist | 0.356 (floor 0.309), p=0.331 | 4.906 (floor 0.546), p<0.001 | 16.3 (floor 1.380), p<0.001 |
| thumb | 0.121 (floor 0.341), p=0.977 | 5.172 (floor 0.540), p<0.001 | 16.1 (floor 1.363), p<0.001 |
| index | 0.497 (floor 0.417), p=0.291 | 5.673 (floor 0.614), p<0.001 | 16.9 (floor 1.438), p<0.001 |

Where the wrist shift sits: early 0%, mid 8%, late 92%. Largest at 100% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test first 5 | ratio [95% CI] | p |
|---|---|---|---|---|---|
| wrist | early | 0.741 | 0.549 | 0.74 [0.43, 0.79] | 0.146 |
| wrist | mid | 0.786 | 1.328 | 1.69 [0.72, 1.96] | 0.024 |
| wrist | late | 0.643 | 1.284 | 2.00 [0.51, 2.30] | 0.011 |
| thumb | early | 0.808 | 0.791 | 0.98 [0.37, 1.15] | 0.953 |
| thumb | mid | 0.682 | 1.338 | 1.96 [1.07, 2.28] | 0.008 |
| thumb | late | 0.583 | 1.121 | 1.92 [0.49, 2.18] | 0.013 |
| index | early | 0.994 | 0.794 | 0.80 [0.44, 0.90] | 0.379 |
| index | mid | 0.838 | 1.417 | 1.69 [0.78, 1.91] | 0.020 |
| index | late | 0.696 | 1.265 | 1.82 [0.52, 2.08] | 0.018 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.606 | 0.356 | 0.491 | 34% |
| mid | 5.047 | 4.906 | 1.187 | 94% |
| late | 16.3 | 16.3 | 1.149 | 100% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 19.0 (dx +19.003, dy -0.276), p<0.001; spread ratio 1.16.

| kinematics | baseline | test first 5 | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.515 ± 0.028 | 0.958 ± 0.037 | +0.443 | +15.47 | <0.001 |
| peak speed (cm/s) | 59.5 ± 4.112 | 59.9 ± 2.784 | +0.418 | +0.10 | 0.822 |
| time to peak speed (% of movement) | 40.2 ± 3.189 | 29.1 ± 19.4 | -11.168 | -2.16 | 0.001 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 2.000 ± 0.000 | +1.000 | +0.00 | <0.001 |

Mean speed profile differs from baseline by 19.7% of its peak (RMS over the movement).

## test last 5 vs baseline (5 vs 89 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| wrist | 0.172 (floor 0.314), p=0.856 | 5.165 (floor 0.564), p<0.001 | 16.5 (floor 1.408), p<0.001 |
| thumb | 0.494 (floor 0.352), p=0.158 | 5.436 (floor 0.558), p<0.001 | 16.3 (floor 1.394), p<0.001 |
| index | 0.408 (floor 0.427), p=0.479 | 5.760 (floor 0.616), p<0.001 | 16.7 (floor 1.432), p<0.001 |

Where the wrist shift sits: early 0%, mid 9%, late 91%. Largest at 100% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test last 5 | ratio [95% CI] | p |
|---|---|---|---|---|---|
| wrist | early | 0.741 | 1.107 | 1.49 [0.60, 1.93] | 0.083 |
| wrist | mid | 0.786 | 1.825 | 2.32 [1.13, 2.84] | 0.004 |
| wrist | late | 0.643 | 1.448 | 2.25 [0.54, 3.03] | 0.005 |
| thumb | early | 0.808 | 1.383 | 1.71 [0.70, 2.10] | 0.070 |
| thumb | mid | 0.682 | 1.737 | 2.55 [1.05, 3.18] | 0.001 |
| thumb | late | 0.583 | 1.438 | 2.47 [0.78, 3.22] | 0.003 |
| index | early | 0.994 | 1.565 | 1.58 [0.76, 1.92] | 0.079 |
| index | mid | 0.838 | 1.796 | 2.14 [1.06, 2.61] | 0.005 |
| index | late | 0.696 | 1.375 | 1.97 [0.54, 2.59] | 0.020 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 1.005 | 0.172 | 0.990 | 3% |
| mid | 5.417 | 5.165 | 1.632 | 91% |
| late | 16.5 | 16.5 | 1.295 | 99% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 19.4 (dx +19.416, dy +0.609), p<0.001; spread ratio 0.83.

| kinematics | baseline | test last 5 | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.515 ± 0.028 | 0.976 ± 0.039 | +0.461 | +16.03 | <0.001 |
| peak speed (cm/s) | 59.5 ± 4.112 | 60.2 ± 6.230 | +0.731 | +0.17 | 0.699 |
| time to peak speed (% of movement) | 40.2 ± 3.189 | 34.8 ± 19.2 | -5.470 | -1.07 | 0.030 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.800 ± 0.447 | +0.800 | +8.51 | <0.001 |

Mean speed profile differs from baseline by 16.6% of its peak (RMS over the movement).

## baseline 2nd half vs 1st half (45 vs 44 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| wrist | 0.163 (floor 0.144), p=0.338 | 0.143 (floor 0.152), p=0.491 | 0.075 (floor 0.123), p=0.743 |
| thumb | 0.156 (floor 0.158), p=0.464 | 0.107 (floor 0.133), p=0.616 | 0.137 (floor 0.110), p=0.301 |
| index | 0.395 (floor 0.196), p=0.025 | 0.391 (floor 0.163), p=0.007 | 0.282 (floor 0.133), p=0.026 |

Where the wrist shift sits: early 51%, mid 38%, late 11%. Largest at 32% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline 1st half | baseline 2nd half | ratio [95% CI] | p |
|---|---|---|---|---|---|
| wrist | early | 0.689 | 0.787 | 1.14 [0.96, 1.41] | 0.154 |
| wrist | mid | 0.751 | 0.821 | 1.09 [0.91, 1.32] | 0.373 |
| wrist | late | 0.650 | 0.641 | 0.99 [0.81, 1.20] | 0.896 |
| thumb | early | 0.802 | 0.814 | 1.01 [0.79, 1.36] | 0.918 |
| thumb | mid | 0.691 | 0.677 | 0.98 [0.81, 1.20] | 0.859 |
| thumb | late | 0.601 | 0.563 | 0.94 [0.77, 1.15] | 0.533 |
| index | early | 0.980 | 0.978 | 1.00 [0.80, 1.27] | 0.984 |
| index | mid | 0.821 | 0.818 | 1.00 [0.83, 1.20] | 0.975 |
| index | late | 0.709 | 0.662 | 0.93 [0.77, 1.15] | 0.486 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.795 | 0.163 | 0.778 | 4% |
| mid | 0.825 | 0.143 | 0.812 | 3% |
| late | 0.638 | 0.075 | 0.634 | 1% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.075 (dx +0.021, dy +0.072), p=0.737; spread ratio 0.99.

| kinematics | baseline 1st half | baseline 2nd half | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.509 ± 0.025 | 0.520 ± 0.030 | +0.011 | +0.39 | 0.065 |
| peak speed (cm/s) | 60.3 ± 4.155 | 58.7 ± 3.961 | -1.574 | -0.38 | 0.066 |
| time to peak speed (% of movement) | 40.5 ± 3.005 | 39.9 ± 3.371 | -0.549 | -0.17 | 0.428 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.000 ± 0.000 | +0.000 | +0.00 | 1.000 |

Mean speed profile differs from baseline 1st half by 1.7% of its peak (RMS over the movement).
