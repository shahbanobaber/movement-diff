# Results summary

Reps: baseline 89, test 14. Units: cm. Effector: wrist. Phases: early 0-33%, mid 33-66%, late 66-100%. Baseline reps reach peak wrist speed at 40% of their duration (median), a useful landmark when choosing phase boundaries.

Timeline: milliseconds from movement onset, 0 to 540 ms; phases are fractions of that.

p-values are permutation tests across this person's reps (2000 shuffles), uncorrected for the number of cells.

## test vs baseline (14 vs 89 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| wrist | 0.119 (floor 0.155), p=0.658 | 0.270 (floor 0.264), p=0.411 | 2.014 (floor 0.307), p<0.001 |
| thumb | 0.236 (floor 0.211), p=0.344 | 0.173 (floor 0.254), p=0.710 | 2.357 (floor 0.305), p<0.001 |
| index | 0.367 (floor 0.256), p=0.178 | 0.266 (floor 0.313), p=0.551 | 2.621 (floor 0.349), p<0.001 |

Where the wrist shift sits: early 0%, mid 2%, late 98%. Largest at 100% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test | ratio [95% CI] | p |
|---|---|---|---|---|---|
| wrist | early | 0.581 | 0.647 | 1.11 [0.78, 1.38] | 0.449 |
| wrist | mid | 1.004 | 1.272 | 1.27 [0.79, 1.68] | 0.161 |
| wrist | late | 0.867 | 1.488 | 1.72 [1.17, 2.17] | 0.002 |
| thumb | early | 0.789 | 0.978 | 1.24 [0.75, 1.65] | 0.404 |
| thumb | mid | 0.931 | 1.253 | 1.35 [0.88, 1.74] | 0.080 |
| thumb | late | 0.731 | 1.469 | 2.01 [1.37, 2.51] | <0.001 |
| index | early | 0.960 | 1.058 | 1.10 [0.77, 1.39] | 0.640 |
| index | mid | 1.182 | 1.394 | 1.18 [0.76, 1.52] | 0.288 |
| index | late | 0.905 | 1.517 | 1.68 [1.18, 2.09] | 0.002 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.635 | 0.119 | 0.623 | 4% |
| mid | 1.255 | 0.270 | 1.226 | 5% |
| late | 2.473 | 2.014 | 1.434 | 66% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 19.3 (dx +19.293, dy +0.221), p<0.001; spread ratio 1.02.

| kinematics | baseline | test | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.538 ± 0.037 | 1.018 ± 0.057 | +0.480 | +11.97 | <0.001 |
| peak speed (cm/s) | 59.5 ± 4.112 | 59.2 ± 4.360 | -0.267 | -0.06 | 0.819 |
| time to peak speed (% of movement) | 39.9 ± 3.258 | 28.4 ± 16.0 | -11.527 | -1.76 | <0.001 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.929 ± 0.267 | +0.929 | +9.61 | <0.001 |

Mean speed profile differs from baseline by 18.2% of its peak (RMS over the movement).

## test first 5 vs baseline (5 vs 89 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| wrist | 0.314 (floor 0.238), p=0.234 | 0.431 (floor 0.403), p=0.397 | 2.075 (floor 0.406), p<0.001 |
| thumb | 0.113 (floor 0.315), p=0.950 | 0.181 (floor 0.386), p=0.874 | 2.390 (floor 0.383), p<0.001 |
| index | 0.411 (floor 0.388), p=0.385 | 0.350 (floor 0.480), p=0.644 | 2.776 (floor 0.458), p<0.001 |

Where the wrist shift sits: early 2%, mid 4%, late 94%. Largest at 100% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test first 5 | ratio [95% CI] | p |
|---|---|---|---|---|---|
| wrist | early | 0.581 | 0.370 | 0.64 [0.36, 0.68] | 0.052 |
| wrist | mid | 1.004 | 0.719 | 0.72 [0.41, 0.80] | 0.165 |
| wrist | late | 0.867 | 1.094 | 1.26 [0.67, 1.41] | 0.329 |
| thumb | early | 0.789 | 0.531 | 0.67 [0.33, 0.86] | 0.321 |
| thumb | mid | 0.931 | 1.003 | 1.08 [0.38, 1.30] | 0.776 |
| thumb | late | 0.731 | 1.219 | 1.67 [0.89, 1.92] | 0.050 |
| index | early | 0.960 | 0.601 | 0.63 [0.33, 0.76] | 0.159 |
| index | mid | 1.182 | 0.971 | 0.82 [0.46, 0.97] | 0.394 |
| index | late | 0.905 | 1.212 | 1.34 [0.77, 1.46] | 0.176 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.456 | 0.314 | 0.331 | 47% |
| mid | 0.774 | 0.431 | 0.643 | 31% |
| late | 2.294 | 2.075 | 0.978 | 82% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 19.1 (dx +19.145, dy -0.297), p<0.001; spread ratio 0.89.

| kinematics | baseline | test first 5 | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.538 ± 0.037 | 1.006 ± 0.058 | +0.468 | +12.31 | <0.001 |
| peak speed (cm/s) | 59.5 ± 4.112 | 59.9 ± 2.784 | +0.418 | +0.10 | 0.822 |
| time to peak speed (% of movement) | 39.9 ± 3.258 | 28.8 ± 19.0 | -11.064 | -2.16 | <0.001 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 2.000 ± 0.000 | +1.000 | +0.00 | <0.001 |

Mean speed profile differs from baseline by 19.1% of its peak (RMS over the movement).

## test last 5 vs baseline (5 vs 89 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| wrist | 0.185 (floor 0.246), p=0.673 | 0.167 (floor 0.409), p=0.880 | 2.375 (floor 0.423), p<0.001 |
| thumb | 0.606 (floor 0.334), p=0.080 | 0.321 (floor 0.392), p=0.572 | 2.727 (floor 0.401), p<0.001 |
| index | 0.517 (floor 0.402), p=0.250 | 0.222 (floor 0.489), p=0.872 | 2.919 (floor 0.464), p<0.001 |

Where the wrist shift sits: early 1%, mid 0%, late 99%. Largest at 100% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test last 5 | ratio [95% CI] | p |
|---|---|---|---|---|---|
| wrist | early | 0.581 | 0.779 | 1.34 [0.69, 1.60] | 0.184 |
| wrist | mid | 1.004 | 1.715 | 1.71 [0.45, 2.29] | 0.072 |
| wrist | late | 0.867 | 1.828 | 2.11 [0.76, 2.60] | 0.007 |
| thumb | early | 0.789 | 1.434 | 1.82 [0.72, 2.26] | 0.115 |
| thumb | mid | 0.931 | 1.614 | 1.73 [0.50, 2.30] | 0.076 |
| thumb | late | 0.731 | 1.719 | 2.35 [0.97, 2.99] | 0.004 |
| index | early | 0.960 | 1.546 | 1.61 [0.76, 1.94] | 0.150 |
| index | mid | 1.182 | 1.875 | 1.59 [0.49, 2.12] | 0.096 |
| index | late | 0.905 | 1.797 | 1.99 [0.73, 2.40] | 0.012 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.721 | 0.185 | 0.697 | 7% |
| mid | 1.543 | 0.167 | 1.534 | 1% |
| late | 2.883 | 2.375 | 1.635 | 68% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 19.5 (dx +19.470, dy +0.574), p<0.001; spread ratio 0.77.

| kinematics | baseline | test last 5 | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.538 ± 0.037 | 1.008 ± 0.048 | +0.470 | +12.56 | <0.001 |
| peak speed (cm/s) | 59.5 ± 4.112 | 60.2 ± 6.230 | +0.731 | +0.17 | 0.699 |
| time to peak speed (% of movement) | 39.9 ± 3.258 | 34.5 ± 18.9 | -5.419 | -1.06 | 0.031 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.800 ± 0.447 | +0.800 | +8.51 | <0.001 |

Mean speed profile differs from baseline by 16.9% of its peak (RMS over the movement).

## baseline 2nd half vs 1st half (45 vs 44 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| wrist | 0.116 (floor 0.114), p=0.440 | 0.296 (floor 0.189), p=0.162 | 0.187 (floor 0.165), p=0.348 |
| thumb | 0.117 (floor 0.150), p=0.597 | 0.185 (floor 0.178), p=0.423 | 0.078 (floor 0.140), p=0.805 |
| index | 0.403 (floor 0.185), p=0.028 | 0.550 (floor 0.225), p=0.011 | 0.442 (floor 0.174), p=0.006 |

Where the wrist shift sits: early 10%, mid 64%, late 26%. Largest at 57% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline 1st half | baseline 2nd half | ratio [95% CI] | p |
|---|---|---|---|---|---|
| wrist | early | 0.510 | 0.643 | 1.26 [1.04, 1.53] | 0.018 |
| wrist | mid | 0.952 | 1.043 | 1.10 [0.90, 1.37] | 0.406 |
| wrist | late | 0.804 | 0.924 | 1.15 [0.94, 1.42] | 0.204 |
| thumb | early | 0.754 | 0.826 | 1.10 [0.73, 1.56] | 0.683 |
| thumb | mid | 0.945 | 0.919 | 0.97 [0.79, 1.25] | 0.800 |
| thumb | late | 0.723 | 0.746 | 1.03 [0.84, 1.28] | 0.788 |
| index | early | 0.950 | 0.938 | 0.99 [0.70, 1.35] | 0.949 |
| index | mid | 1.170 | 1.141 | 0.97 [0.80, 1.22] | 0.821 |
| index | late | 0.866 | 0.897 | 1.04 [0.86, 1.26] | 0.711 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.646 | 0.116 | 0.636 | 3% |
| mid | 1.073 | 0.296 | 1.032 | 8% |
| late | 0.933 | 0.187 | 0.914 | 4% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.091 (dx +0.042, dy +0.081), p=0.618; spread ratio 0.97.

| kinematics | baseline 1st half | baseline 2nd half | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.530 ± 0.031 | 0.546 ± 0.040 | +0.016 | +0.45 | 0.035 |
| peak speed (cm/s) | 60.3 ± 4.155 | 58.7 ± 3.961 | -1.574 | -0.38 | 0.066 |
| time to peak speed (% of movement) | 40.2 ± 3.121 | 39.6 ± 3.396 | -0.579 | -0.18 | 0.415 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.000 ± 0.000 | +0.000 | +0.00 | 1.000 |

Mean speed profile differs from baseline 1st half by 1.9% of its peak (RMS over the movement).
