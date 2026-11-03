# Results summary

Reps: baseline 20, practice 40, test 20. Units: torso lengths. Effector: wrist. Phases: early 0-33%, mid 33-66%, late 66-100%. Baseline reps reach peak wrist speed at 48% of their duration (median), a useful landmark when choosing phase boundaries.

p-values are permutation tests across this person's reps (2000 shuffles), uncorrected for the number of cells.

## practice vs baseline (40 vs 20 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.007 (floor 0.005), p=0.219 | 0.031 (floor 0.007), p<0.001 | 0.010 (floor 0.006), p=0.155 |
| wrist | 0.009 (floor 0.007), p=0.186 | 0.053 (floor 0.012), p<0.001 | 0.016 (floor 0.009), p=0.059 |
| index | 0.008 (floor 0.008), p=0.425 | 0.065 (floor 0.015), p<0.001 | 0.022 (floor 0.010), p=0.028 |

Where the wrist shift sits: early 3%, mid 89%, late 8%. Largest at 51% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | practice | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.018 | 0.022 | 1.20 [0.93, 1.63] | 0.213 |
| elbow | mid | 0.020 | 0.028 | 1.36 [1.08, 1.80] | 0.039 |
| elbow | late | 0.022 | 0.027 | 1.26 [0.97, 1.74] | 0.146 |
| wrist | early | 0.023 | 0.027 | 1.19 [1.01, 1.45] | 0.095 |
| wrist | mid | 0.030 | 0.048 | 1.58 [1.27, 2.02] | 0.003 |
| wrist | late | 0.026 | 0.038 | 1.46 [1.19, 1.89] | 0.006 |
| index | early | 0.026 | 0.032 | 1.21 [1.04, 1.49] | 0.059 |
| index | mid | 0.036 | 0.059 | 1.63 [1.32, 2.11] | 0.002 |
| index | late | 0.031 | 0.045 | 1.47 [1.18, 1.90] | 0.009 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.028 | 0.009 | 0.027 | 10% |
| mid | 0.071 | 0.053 | 0.047 | 56% |
| late | 0.041 | 0.016 | 0.038 | 15% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.014 (dx -0.005, dy +0.013), p=0.048; spread ratio 1.45.

| kinematics | baseline | practice | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.703 ± 0.055 | 0.797 ± 0.071 | +0.093 | +1.39 | <0.001 |
| peak speed (torso lengths/s) | 2.271 ± 0.172 | 2.081 ± 0.206 | -0.190 | -0.96 | 0.001 |
| time to peak speed (% of movement) | 49.2 ± 5.864 | 47.7 ± 9.072 | -1.537 | -0.19 | 0.497 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.000 ± 0.000 | +0.000 | +0.00 | 1.000 |

Mean speed profile differs from baseline by 7.2% of its peak (RMS over the movement).

## test vs baseline (20 vs 20 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.008 (floor 0.009), p=0.447 | 0.028 (floor 0.008), p<0.001 | 0.009 (floor 0.006), p=0.172 |
| wrist | 0.013 (floor 0.011), p=0.295 | 0.040 (floor 0.011), p<0.001 | 0.009 (floor 0.007), p=0.302 |
| index | 0.012 (floor 0.012), p=0.433 | 0.049 (floor 0.014), p<0.001 | 0.009 (floor 0.008), p=0.376 |

Where the wrist shift sits: early 9%, mid 87%, late 4%. Largest at 54% of the movement.

Same wrist shift with linear time instead of DTW: early 0.014 (p=0.258), mid 0.035 (p=0.006), late 0.006 (p=0.689). Where this is much larger than the DTW value, part of the change is timing rather than path.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.018 | 0.044 | 2.43 [1.77, 3.32] | <0.001 |
| elbow | mid | 0.020 | 0.026 | 1.27 [0.95, 1.69] | 0.141 |
| elbow | late | 0.022 | 0.022 | 1.00 [0.67, 1.42] | 0.977 |
| wrist | early | 0.023 | 0.048 | 2.09 [1.59, 2.64] | <0.001 |
| wrist | mid | 0.030 | 0.035 | 1.17 [0.91, 1.47] | 0.209 |
| wrist | late | 0.026 | 0.024 | 0.90 [0.68, 1.17] | 0.421 |
| index | early | 0.026 | 0.052 | 1.99 [1.50, 2.52] | <0.001 |
| index | mid | 0.036 | 0.042 | 1.17 [0.91, 1.48] | 0.214 |
| index | late | 0.031 | 0.027 | 0.87 [0.66, 1.14] | 0.296 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.048 | 0.013 | 0.047 | 7% |
| mid | 0.053 | 0.040 | 0.035 | 58% |
| late | 0.025 | 0.009 | 0.023 | 12% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.005 (dx +0.004, dy -0.002), p=0.515; spread ratio 0.95.

| kinematics | baseline | test | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.703 ± 0.055 | 0.793 ± 0.063 | +0.090 | +1.50 | <0.001 |
| peak speed (torso lengths/s) | 2.271 ± 0.172 | 2.072 ± 0.154 | -0.199 | -1.19 | <0.001 |
| time to peak speed (% of movement) | 49.2 ± 5.864 | 50.7 ± 6.482 | +1.496 | +0.24 | 0.445 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.050 ± 0.224 | +0.050 | +0.31 | 1.000 |

Mean speed profile differs from baseline by 7.9% of its peak (RMS over the movement).

## test first 5 vs baseline (5 vs 20 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.029 (floor 0.012), p=0.032 | 0.044 (floor 0.012), p<0.001 | 0.019 (floor 0.010), p=0.085 |
| wrist | 0.032 (floor 0.015), p=0.025 | 0.071 (floor 0.019), p<0.001 | 0.018 (floor 0.012), p=0.109 |
| index | 0.032 (floor 0.017), p=0.045 | 0.090 (floor 0.023), p<0.001 | 0.022 (floor 0.014), p=0.084 |

Where the wrist shift sits: early 16%, mid 78%, late 5%. Largest at 53% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test first 5 | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.018 | 0.051 | 2.84 [0.54, 4.09] | 0.003 |
| elbow | mid | 0.020 | 0.024 | 1.18 [0.51, 1.52] | 0.438 |
| elbow | late | 0.022 | 0.021 | 0.99 [0.40, 1.34] | 0.946 |
| wrist | early | 0.023 | 0.059 | 2.55 [0.78, 3.40] | <0.001 |
| wrist | mid | 0.030 | 0.033 | 1.10 [0.50, 1.36] | 0.586 |
| wrist | late | 0.026 | 0.019 | 0.72 [0.34, 0.92] | 0.142 |
| index | early | 0.026 | 0.064 | 2.42 [0.78, 3.25] | 0.004 |
| index | mid | 0.036 | 0.041 | 1.14 [0.52, 1.41] | 0.453 |
| index | late | 0.031 | 0.021 | 0.67 [0.34, 0.83] | 0.081 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.062 | 0.032 | 0.052 | 27% |
| mid | 0.077 | 0.071 | 0.030 | 85% |
| late | 0.025 | 0.018 | 0.017 | 53% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.003 (dx -0.002, dy -0.002), p=0.919; spread ratio 1.11.

| kinematics | baseline | test first 5 | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.703 ± 0.055 | 0.793 ± 0.064 | +0.090 | +1.53 | 0.006 |
| peak speed (torso lengths/s) | 2.271 ± 0.172 | 2.127 ± 0.152 | -0.144 | -0.83 | 0.100 |
| time to peak speed (% of movement) | 49.2 ± 5.864 | 48.4 ± 8.433 | -0.870 | -0.13 | 0.780 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.200 ± 0.447 | +0.200 | +1.04 | 0.216 |

Mean speed profile differs from baseline by 7.8% of its peak (RMS over the movement).

## test last 5 vs baseline (5 vs 20 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.014 (floor 0.009), p=0.119 | 0.018 (floor 0.011), p=0.058 | 0.008 (floor 0.010), p=0.600 |
| wrist | 0.013 (floor 0.011), p=0.285 | 0.026 (floor 0.015), p=0.033 | 0.007 (floor 0.012), p=0.865 |
| index | 0.016 (floor 0.013), p=0.217 | 0.035 (floor 0.018), p=0.021 | 0.007 (floor 0.014), p=0.880 |

Where the wrist shift sits: early 19%, mid 76%, late 5%. Largest at 56% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline | test last 5 | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.018 | 0.022 | 1.19 [0.37, 1.55] | 0.473 |
| elbow | mid | 0.020 | 0.029 | 1.44 [0.48, 1.93] | 0.194 |
| elbow | late | 0.022 | 0.031 | 1.41 [0.37, 2.08] | 0.284 |
| wrist | early | 0.023 | 0.022 | 0.94 [0.42, 1.10] | 0.683 |
| wrist | mid | 0.030 | 0.034 | 1.11 [0.38, 1.48] | 0.649 |
| wrist | late | 0.026 | 0.029 | 1.11 [0.38, 1.49] | 0.651 |
| index | early | 0.026 | 0.026 | 1.00 [0.50, 1.19] | 1.000 |
| index | mid | 0.036 | 0.037 | 1.02 [0.43, 1.33] | 0.917 |
| index | late | 0.031 | 0.032 | 1.03 [0.41, 1.36] | 0.881 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.023 | 0.013 | 0.019 | 31% |
| mid | 0.040 | 0.026 | 0.030 | 43% |
| late | 0.027 | 0.007 | 0.026 | 7% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.006 (dx +0.005, dy -0.003), p=0.703; spread ratio 0.91.

| kinematics | baseline | test last 5 | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.703 ± 0.055 | 0.813 ± 0.069 | +0.110 | +1.84 | 0.004 |
| peak speed (torso lengths/s) | 2.271 ± 0.172 | 2.042 ± 0.206 | -0.228 | -1.24 | 0.017 |
| time to peak speed (% of movement) | 49.2 ± 5.864 | 53.0 ± 4.555 | +3.775 | +0.65 | 0.193 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.000 ± 0.000 | +0.000 | +0.00 | 1.000 |

Mean speed profile differs from baseline by 9.8% of its peak (RMS over the movement).

## baseline 2nd half vs 1st half (10 vs 10 reps)

Shift of the mean movement, per phase. Noise floor = the same statistic averaged over label shuffles.

| joint | early | mid | late |
|---|---|---|---|
| elbow | 0.004 (floor 0.007), p=0.780 | 0.009 (floor 0.008), p=0.393 | 0.005 (floor 0.008), p=0.730 |
| wrist | 0.005 (floor 0.010), p=0.923 | 0.011 (floor 0.013), p=0.586 | 0.005 (floor 0.011), p=0.921 |
| index | 0.006 (floor 0.011), p=0.881 | 0.013 (floor 0.015), p=0.610 | 0.007 (floor 0.012), p=0.801 |

Where the wrist shift sits: early 14%, mid 72%, late 14%. Largest at 40% of the movement.

Spread around the condition's own mean, per phase.

| joint | phase | baseline 1st half | baseline 2nd half | ratio [95% CI] | p |
|---|---|---|---|---|---|
| elbow | early | 0.016 | 0.021 | 1.34 [0.84, 1.97] | 0.226 |
| elbow | mid | 0.018 | 0.022 | 1.20 [0.80, 1.88] | 0.396 |
| elbow | late | 0.018 | 0.025 | 1.41 [0.92, 2.39] | 0.145 |
| wrist | early | 0.023 | 0.024 | 1.04 [0.77, 1.46] | 0.780 |
| wrist | mid | 0.029 | 0.032 | 1.11 [0.78, 1.76] | 0.586 |
| wrist | late | 0.024 | 0.029 | 1.22 [0.80, 1.86] | 0.321 |
| index | early | 0.027 | 0.026 | 0.96 [0.69, 1.39] | 0.824 |
| index | mid | 0.034 | 0.039 | 1.12 [0.78, 1.78] | 0.530 |
| index | late | 0.029 | 0.034 | 1.17 [0.77, 1.84] | 0.426 |

Accuracy-style score for the wrist (RMS distance from the baseline mean) split into its two parts. shift^2 + spread^2 = score^2.

| phase | score | shift part | spread part | share from shift |
|---|---|---|---|---|
| early | 0.023 | 0.005 | 0.023 | 4% |
| mid | 0.032 | 0.011 | 0.030 | 12% |
| late | 0.028 | 0.005 | 0.028 | 3% |

Endpoint of the wrist, the closest thing here to an outcome score: mean moved 0.004 (dx +0.004, dy +0.000), p=0.803; spread ratio 0.96.

| kinematics | baseline 1st half | baseline 2nd half | diff | Hedges g | p |
|---|---|---|---|---|---|
| movement time (s) | 0.707 ± 0.056 | 0.700 ± 0.057 | -0.007 | -0.11 | 0.890 |
| peak speed (torso lengths/s) | 2.265 ± 0.145 | 2.277 ± 0.203 | +0.012 | +0.06 | 0.881 |
| time to peak speed (% of movement) | 48.5 ± 7.014 | 49.9 ± 4.725 | +1.394 | +0.22 | 0.628 |
| speed peaks per rep (count) | 1.000 ± 0.000 | 1.000 ± 0.000 | +0.000 | +0.00 | 1.000 |

Mean speed profile differs from baseline 1st half by 2.2% of its peak (RMS over the movement).
