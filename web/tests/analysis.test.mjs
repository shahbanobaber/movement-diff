// node --test web/tests
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import { analyse, POSE, segment, toSeries, verdict } from "../analysis.js";

const here = new URL(".", import.meta.url);
const sample = JSON.parse(readFileSync(new URL("../sample.json", here)));
const expected = JSON.parse(readFileSync(new URL("expected.json", here)));
const close = (a, b, tol, what) => a.forEach((v, i) => assert.ok(Math.abs(v - b[i]) <= tol, `${what}[${i}]: ${v} vs ${b[i]}`));

// Linear time must match to rounding. With DTW the two can pick a different
// warping path on near-ties (the medoid retiming uses numpy's least squares,
// not an identical solver), so phase numbers match to 0.5%.
for (const [mode, rel] of [["none", 1e-9], ["velocity", 5e-3]]) {
  test(`matches the Python package (${mode} alignment)`, () => {
    const res = analyse(sample.A, sample.B, { align: mode, nPerm: 20 });
    const e = expected[mode];
    const within = (a, b, what) => a.forEach((v, i) => assert.ok(Math.abs(v - b[i]) <= rel * Math.abs(b[i]) + 1e-9,
                                                                 `${what}[${i}]: ${v} vs ${b[i]}`));
    within(res.phases.map(p => p.shift), e.shift, "shift");
    within(res.phases.map(p => p.spreadA), e.spreadA, "spreadA");
    within(res.phases.map(p => p.spreadB), e.spreadB, "spreadB");
    if (mode === "none") close(res.curve.shift, e.curve, 1e-9, "curve");
  });
}

test("finds the planted change in the sample", () => {
  const v = verdict(analyse(sample.A, sample.B, { nPerm: 300 }));
  assert.equal(v.shift.phase, "mid");          // the path bends in the middle
  assert.equal(v.spread.phase, "early");       // and wobbles at the start
  assert.ok(v.spread.ratio > 1.5);
});

// A camera recording of n reaches: shoulder fixed, wrist reaching out and back along a
// min-jerk path, in image pixels with y down, landmarks at an uneven ~30 fps.
function recording(n, { seed = 1, side = "right", reach = 160 } = {}) {
  let s = seed;
  const rand = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  const mj = u => 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5;
  const frames = [];
  let t = 0;
  const sh = [320, 200], upper = 120, fore = 110;
  for (let r = 0; r < n; r++) {
    for (const [dur, from, to] of [[0.5, 0, 0], [0.6, 0, 1], [0.6, 1, 0]]) {     // pause, reach, return
      for (let k = 0; k < dur * 30; k++) {
        const u = mj(k / (dur * 30));
        const ext = from + (to - from) * u;                 // 0 = arm folded, 1 = reached out
        const wrist = [sh[0] + 60 + reach * ext, sh[1] + 150 - 140 * ext];
        const elbow = [sh[0] + 30 + 80 * ext, sh[1] + upper * (1 - 0.6 * ext)];
        const lm = Array.from({ length: 33 }, () => [0, 0, 0.1]);
        const id = POSE[side];
        lm[id.shoulder] = [sh[0] + rand() - 0.5, sh[1] + rand() - 0.5, 0.99];
        lm[id.elbow] = [elbow[0] + rand() - 0.5, elbow[1] + rand() - 0.5, 0.99];
        lm[id.wrist] = [wrist[0] + rand() - 0.5, wrist[1] + rand() - 0.5, 0.99];
        frames.push({ t, lm });
        t += 1000 / 30 + (rand() - 0.5) * 8;
      }
    }
  }
  return { frames, fore };
}

test("cuts a camera recording into its reaches", () => {
  const { frames } = recording(8);
  const series = toSeries(frames, "right");
  assert.ok(series.arm > 150 && series.arm < 300, `arm ${series.arm}`);
  const reps = segment(series);
  assert.equal(reps.length, 8);                         // the returns are not counted
  for (const r of reps) {
    const dur = (r.end - r.start) / series.fps;
    assert.ok(dur > 0.4 && dur < 0.75, `rep lasted ${dur}`);
    const [first, last] = [r.frames[0][0], r.frames.at(-1)[0]];
    assert.ok(Math.hypot(...last) > Math.hypot(...first), "a reach moves away from the shoulder");
  }
});

test("a recording compared with itself shows no change", () => {
  const a = segment(toSeries(recording(8, { seed: 3 }).frames, "right")).map(r => r.frames);
  const b = segment(toSeries(recording(8, { seed: 7 }).frames, "right")).map(r => r.frames);
  const v = verdict(analyse(a, b, { nPerm: 300 }));
  assert.equal(v.shift, null);
});

test("a shorter reach shows up as a late shift", () => {
  const a = segment(toSeries(recording(8, { seed: 3 }).frames, "right")).map(r => r.frames);
  const b = segment(toSeries(recording(8, { seed: 7, reach: 120 }).frames, "right")).map(r => r.frames);
  const v = verdict(analyse(a, b, { nPerm: 300 }));
  assert.equal(v.shift?.phase, "late");
});
