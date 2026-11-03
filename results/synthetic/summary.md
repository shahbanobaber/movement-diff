# Results summary

Reps: baseline 20, practice 40, test 20. Units: torso lengths. Effector: wrist. Phases: early 0-33%, mid 33-66%, late 66-100%. Baseline reps reach peak wrist speed at 48% of their duration (median), a useful landmark when choosing phase boundaries.

p-values are permutation tests across this person's reps (2000 shuffles), uncorrected for the number of cells.

## practice vs baseline (40 vs 20 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.007 (floor 0.005), p=0.209 | 0.032 (floor 0.008), p<0.001 | 0.009 (floor 0.006), p=0.206 |
| wrist | 0.009 (floor 0.007), p=0.184 | 0.053 (floor 0.012), p<0.001 | 0.016 (floor 0.009), p=0.063 |
| index | 0.008 (floor 0.008), p=0.426 | 0.064 (floor 0.015), p<0.001 | 0.022 (floor 0.010), p=0.027 |

Where the wrist shift sits: early 3%, mid 89%, late 8%. Largest at 52% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | practice | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.018 | 0.021 | 1.19 [0.91, 1.61] | 0.253 |
| elbow | mid | 0.020 | 0.029 | 1.41 [1.12, 1.87] | 0.025 |
| elbow | late | 0.022 | 0.028 | 1.29 [0.98, 1.80] | 0.115 |
| wrist | early | 0.023 | 0.028 | 1.22 [1.04, 1.49] | 0.054 |
| wrist | mid | 0.030 | 0.049 | 1.59 [1.29, 2.04] | 0.002 |
| wrist | late | 0.026 | 0.039 | 1.46 [1.18, 1.90] | 0.005 |
| index | early | 0.026 | 0.033 | 1.26 [1.08, 1.55] | 0.025 |
| index | mid | 0.036 | 0.060 | 1.65 [1.33, 2.10] | 0.001 |
| index | late | 0.031 | 0.046 | 1.46 [1.17, 1.91] | 0.010 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.029 | 0.009 | 0.027 | 10% |
| mid | 0.071 | 0.053 | 0.048 | 55% |
| late | 0.041 | 0.016 | 0.038 | 15% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.014 (dx -0.005, dy +0.013), p=0.045; spread ratio 1.50.

| kinematics | baseline | practice | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.705 ± 0.056 | 0.801 ± 0.075 | +0.096 | +1.36 | <0.001 |
| peak speed (torso lengths/s) | 2.271 ± 0.172 | 2.081 ± 0.206 | -0.190 | -0.96 | 0.001 |
| time to peak speed (% of movement) | 49.4 ± 5.698 | 47.9 ± 9.019 | -1.457 | -0.18 | 0.514 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.000 ± 0.000 | +0.000 | +0.00 | 1.000 |

Mean speed profile differs from baseline by 7.3% of its peak (RMS over the movement).

## test vs baseline (20 vs 20 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.008 (floor 0.009), p=0.451 | 0.029 (floor 0.008), p<0.001 | 0.010 (floor 0.006), p=0.137 |
| wrist | 0.013 (floor 0.011), p=0.285 | 0.040 (floor 0.011), p<0.001 | 0.009 (floor 0.007), p=0.263 |
| index | 0.012 (floor 0.012), p=0.418 | 0.049 (floor 0.013), p<0.001 | 0.010 (floor 0.008), p=0.341 |

Where the wrist shift sits: early 9%, mid 86%, late 4%. Largest at 54% of the movement.

Same wrist shift with linear time instead of DTW: early 0.015 (p=0.226), mid 0.035 (p=0.008), late 0.005 (p=0.736). Where this is much larger than the DTW value, part of the change is timing rather than path.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.018 | 0.044 | 2.43 [1.77, 3.34] | <0.001 |
| elbow | mid | 0.020 | 0.024 | 1.16 [0.88, 1.57] | 0.301 |
| elbow | late | 0.022 | 0.021 | 0.98 [0.68, 1.39] | 0.892 |
| wrist | early | 0.023 | 0.048 | 2.12 [1.61, 2.69] | <0.001 |
| wrist | mid | 0.030 | 0.035 | 1.13 [0.89, 1.43] | 0.302 |
| wrist | late | 0.026 | 0.023 | 0.87 [0.67, 1.14] | 0.301 |
| index | early | 0.026 | 0.053 | 2.03 [1.54, 2.60] | <0.001 |
| index | mid | 0.036 | 0.042 | 1.16 [0.90, 1.49] | 0.242 |
| index | late | 0.031 | 0.026 | 0.85 [0.65, 1.12] | 0.218 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.049 | 0.013 | 0.047 | 7% |
| mid | 0.052 | 0.040 | 0.034 | 59% |
| late | 0.024 | 0.009 | 0.022 | 14% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.005 (dx +0.004, dy -0.002), p=0.538; spread ratio 0.95.

| kinematics | baseline | test | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.705 ± 0.056 | 0.797 ± 0.071 | +0.092 | +1.40 | <0.001 |
| peak speed (torso lengths/s) | 2.271 ± 0.172 | 2.072 ± 0.154 | -0.199 | -1.19 | <0.001 |
| time to peak speed (% of movement) | 49.4 ± 5.698 | 50.7 ± 6.627 | +1.348 | +0.21 | 0.486 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.050 ± 0.224 | +0.050 | +0.31 | 1.000 |

Mean speed profile differs from baseline by 7.9% of its peak (RMS over the movement).

## test first 5 vs baseline (5 vs 20 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.029 (floor 0.012), p=0.035 | 0.044 (floor 0.012), p<0.001 | 0.019 (floor 0.010), p=0.075 |
| wrist | 0.032 (floor 0.015), p=0.025 | 0.071 (floor 0.019), p<0.001 | 0.019 (floor 0.012), p=0.103 |
| index | 0.032 (floor 0.017), p=0.041 | 0.090 (floor 0.023), p<0.001 | 0.023 (floor 0.014), p=0.079 |

Where the wrist shift sits: early 16%, mid 78%, late 5%. Largest at 53% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test first 5 | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.018 | 0.051 | 2.86 [0.53, 4.13] | 0.002 |
| elbow | mid | 0.020 | 0.024 | 1.17 [0.51, 1.51] | 0.491 |
| elbow | late | 0.022 | 0.021 | 0.96 [0.36, 1.31] | 0.858 |
| wrist | early | 0.023 | 0.059 | 2.58 [0.78, 3.45] | <0.001 |
| wrist | mid | 0.030 | 0.033 | 1.09 [0.50, 1.36] | 0.619 |
| wrist | late | 0.026 | 0.018 | 0.69 [0.31, 0.88] | 0.123 |
| index | early | 0.026 | 0.064 | 2.45 [0.79, 3.30] | 0.003 |
| index | mid | 0.036 | 0.041 | 1.13 [0.52, 1.41] | 0.475 |
| index | late | 0.031 | 0.020 | 0.65 [0.32, 0.82] | 0.079 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.061 | 0.032 | 0.052 | 27% |
| mid | 0.077 | 0.071 | 0.030 | 85% |
| late | 0.025 | 0.019 | 0.016 | 56% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.003 (dx -0.002, dy -0.002), p=0.919; spread ratio 1.11.

| kinematics | baseline | test first 5 | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.705 ± 0.056 | 0.793 ± 0.064 | +0.088 | +1.48 | 0.008 |
| peak speed (torso lengths/s) | 2.271 ± 0.172 | 2.127 ± 0.152 | -0.144 | -0.83 | 0.100 |
| time to peak speed (% of movement) | 49.4 ± 5.698 | 48.4 ± 8.433 | -0.998 | -0.15 | 0.750 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.200 ± 0.447 | +0.200 | +1.04 | 0.216 |

Mean speed profile differs from baseline by 7.8% of its peak (RMS over the movement).

## test last 5 vs baseline (5 vs 20 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.014 (floor 0.008), p=0.108 | 0.020 (floor 0.010), p=0.014 | 0.008 (floor 0.010), p=0.583 |
| wrist | 0.013 (floor 0.011), p=0.263 | 0.026 (floor 0.015), p=0.027 | 0.007 (floor 0.012), p=0.872 |
| index | 0.016 (floor 0.012), p=0.226 | 0.033 (floor 0.017), p=0.030 | 0.007 (floor 0.014), p=0.888 |

Where the wrist shift sits: early 20%, mid 75%, late 5%. Largest at 55% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test last 5 | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.018 | 0.020 | 1.13 [0.35, 1.46] | 0.654 |
| elbow | mid | 0.020 | 0.022 | 1.10 [0.49, 1.49] | 0.675 |
| elbow | late | 0.022 | 0.030 | 1.36 [0.51, 1.93] | 0.309 |
| wrist | early | 0.023 | 0.022 | 0.98 [0.41, 1.20] | 0.891 |
| wrist | mid | 0.030 | 0.027 | 0.87 [0.39, 1.13] | 0.492 |
| wrist | late | 0.026 | 0.028 | 1.05 [0.46, 1.37] | 0.842 |
| index | early | 0.026 | 0.028 | 1.09 [0.48, 1.37] | 0.607 |
| index | mid | 0.036 | 0.031 | 0.85 [0.41, 1.07] | 0.397 |
| index | late | 0.031 | 0.031 | 0.98 [0.45, 1.29] | 0.921 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.024 | 0.013 | 0.020 | 30% |
| mid | 0.035 | 0.026 | 0.024 | 54% |
| late | 0.026 | 0.007 | 0.025 | 7% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.006 (dx +0.005, dy -0.003), p=0.703; spread ratio 0.91.

| kinematics | baseline | test last 5 | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.705 ± 0.056 | 0.820 ± 0.084 | +0.115 | +1.79 | 0.005 |
| peak speed (torso lengths/s) | 2.271 ± 0.172 | 2.042 ± 0.206 | -0.228 | -1.24 | 0.017 |
| time to peak speed (% of movement) | 49.4 ± 5.698 | 53.3 ± 5.175 | +3.912 | +0.67 | 0.178 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.000 ± 0.000 | +0.000 | +0.00 | 1.000 |

Mean speed profile differs from baseline by 10.0% of its peak (RMS over the movement).

## baseline 2nd half vs 1st half (10 vs 10 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.004 (floor 0.007), p=0.798 | 0.009 (floor 0.008), p=0.382 | 0.006 (floor 0.008), p=0.677 |
| wrist | 0.004 (floor 0.009), p=0.961 | 0.011 (floor 0.013), p=0.607 | 0.005 (floor 0.011), p=0.934 |
| index | 0.004 (floor 0.011), p=0.960 | 0.012 (floor 0.015), p=0.621 | 0.007 (floor 0.013), p=0.791 |

Where the wrist shift sits: early 10%, mid 76%, late 14%. Largest at 40% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline 1st half | baseline 2nd half | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.016 | 0.021 | 1.34 [0.84, 1.99] | 0.241 |
| elbow | mid | 0.018 | 0.022 | 1.23 [0.80, 1.89] | 0.338 |
| elbow | late | 0.019 | 0.025 | 1.33 [0.85, 2.46] | 0.234 |
| wrist | early | 0.023 | 0.024 | 1.03 [0.75, 1.45] | 0.868 |
| wrist | mid | 0.029 | 0.032 | 1.11 [0.78, 1.75] | 0.588 |
| wrist | late | 0.025 | 0.029 | 1.17 [0.76, 1.89] | 0.441 |
| index | early | 0.027 | 0.026 | 0.93 [0.66, 1.34] | 0.665 |
| index | mid | 0.035 | 0.039 | 1.13 [0.79, 1.83] | 0.525 |
| index | late | 0.030 | 0.034 | 1.13 [0.73, 1.84] | 0.549 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.023 | 0.004 | 0.022 | 3% |
| mid | 0.033 | 0.011 | 0.031 | 12% |
| late | 0.028 | 0.005 | 0.028 | 3% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.004 (dx +0.004, dy +0.000), p=0.803; spread ratio 0.96.

| kinematics | baseline 1st half | baseline 2nd half | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.707 ± 0.056 | 0.703 ± 0.060 | -0.003 | -0.06 | 1.000 |
| peak speed (torso lengths/s) | 2.265 ± 0.145 | 2.277 ± 0.203 | +0.012 | +0.06 | 0.881 |
| time to peak speed (% of movement) | 48.5 ± 7.014 | 50.2 ± 4.224 | +1.651 | +0.27 | 0.542 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.000 ± 0.000 | +0.000 | +0.00 | 1.000 |

Mean speed profile differs from baseline 1st half by 2.0% of its peak (RMS over the movement).
