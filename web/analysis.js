// movement-diff in the browser: the same method as the Python package, ported.
// Pure functions only, so Node can test them (web/tests) against the Python results.

export const L = 101;                       // samples per rep after resampling
export const PHASES = [["early", 0, 1 / 3], ["mid", 1 / 3, 2 / 3], ["late", 2 / 3, 1]];
export const POSE = { left: { shoulder: 11, elbow: 13, wrist: 15 }, right: { shoulder: 12, elbow: 14, wrist: 16 } };
const FPS = 30;

// ---------- small numeric helpers ----------
export function rng(seed = 1) {               // mulberry32, so results repeat
  let a = seed >>> 0;
  return () => { a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const median = xs => { const s = xs.filter(Number.isFinite).sort((a, b) => a - b); const n = s.length;
  return n ? (n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2) : NaN; };
const quantile = (xs, q) => { const s = [...xs].sort((a, b) => a - b); const i = q * (s.length - 1);
  const lo = Math.floor(i), hi = Math.ceil(i); return s[lo] + (s[hi] - s[lo]) * (i - lo); };
function interp(x, xp, fp) {                 // like numpy.interp, xp increasing
  if (x <= xp[0]) return fp[0];
  const n = xp.length;
  if (x >= xp[n - 1]) return fp[n - 1];
  let lo = 0, hi = n - 1;
  while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (xp[mid] <= x) lo = mid; else hi = mid; }
  const slope = (fp[hi] - fp[lo]) / (xp[hi] - xp[lo]);   // numpy's formula, to match it bit for bit
  return slope * (x - xp[lo]) + fp[lo];
}
// numpy.linspace(0, 1, n): i * step, with the last point exactly 1.
const linspace = n => { const step = 1 / (n - 1); return Array.from({ length: n }, (_, i) => (i === n - 1 ? 1 : i * step)); };
function shuffle(n, rand) { const p = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [p[i], p[j]] = [p[j], p[i]]; } return p; }


// ---------- from camera frames to one clean, normalised time series ----------
// frames: [{t: ms, lm: [[x, y, visibility] x 33]}], x and y in image pixels (y down).
export function pickSide(frames) {
  let best = "right", most = -1;
  for (const side of ["left", "right"]) {
    const w = POSE[side].wrist;
    let path = 0, prev = null;
    for (const f of frames) {
      const p = f.lm[w];
      if (!p || p[2] < 0.5) { prev = null; continue; }
      if (prev) path += Math.hypot(p[0] - prev[0], p[1] - prev[1]);
      prev = p;
    }
    if (path > most) { most = path; best = side; }
  }
  return best;
}

function gaussianSmooth(xs, sigma) {          // zero-lag smoothing; NaNs stay NaN
  const r = Math.ceil(3 * sigma), k = [];
  for (let i = -r; i <= r; i++) k.push(Math.exp(-0.5 * (i / sigma) ** 2));
  return xs.map((x, i) => {
    if (!Number.isFinite(x)) return NaN;
    let s = 0, w = 0;
    for (let j = -r; j <= r; j++) { const v = xs[i + j]; if (Number.isFinite(v)) { s += v * k[j + r]; w += k[j + r]; } }
    return s / w;
  });
}

export function toSeries(frames, side, { fps = FPS, maxGap = 0.25, sigma = 1.5, minVis = 0.5 } = {}) {
  const idx = POSE[side];
  const names = ["shoulder", "elbow", "wrist"];
  const t0 = frames[0].t / 1000, t1 = frames[frames.length - 1].t / 1000;
  const n = Math.max(2, Math.floor((t1 - t0) * fps) + 1);
  const t = Array.from({ length: n }, (_, i) => t0 + i / fps);
  const out = {};
  for (const name of names) {
    const ts = [], xs = [], ys = [];
    for (const f of frames) {
      const p = f.lm[idx[name]];
      if (p && p[2] >= minVis) { ts.push(f.t / 1000); xs.push(p[0]); ys.push(-p[1]); }   // y up
    }
    if (ts.length < 2) throw new Error(`could not see the ${side} ${name}`);
    const xi = t.map(tt => interp(tt, ts, xs)), yi = t.map(tt => interp(tt, ts, ys));
    // Mark samples inside long tracking gaps as missing.
    let k = 0;
    for (let i = 0; i < n; i++) {
      while (k < ts.length - 1 && ts[k + 1] < t[i]) k++;
      const near = Math.min(Math.abs(t[i] - ts[k]), k + 1 < ts.length ? Math.abs(ts[k + 1] - t[i]) : Infinity);
      const inside = t[i] >= ts[0] && t[i] <= ts[ts.length - 1];
      const gap = k + 1 < ts.length ? ts[k + 1] - ts[k] : 0;
      if (!inside || (gap > maxGap && near > 1 / fps)) { xi[i] = NaN; yi[i] = NaN; }
    }
    out[name] = [gaussianSmooth(xi, sigma), gaussianSmooth(yi, sigma)];
  }
  // Relative to the shoulder, in units of this person's arm length (upper arm + forearm).
  const rel = name => out[name][0].map((x, i) => [x - out.shoulder[0][i], out[name][1][i] - out.shoulder[1][i]]);
  const elbow = rel("elbow"), wrist = rel("wrist");
  const arm = median(elbow.map((e, i) => Math.hypot(e[0], e[1]) + Math.hypot(wrist[i][0] - e[0], wrist[i][1] - e[1])));
  const scale = p => [p[0] / arm, p[1] / arm];
  return { t, fps, side, arm, wrist: wrist.map(scale), elbow: elbow.map(scale) };
}

// ---------- cut the series into reaches (as movediff/segment.py) ----------
// Speed peaks of the wrist, kept only when the wrist is moving away from where
// it rests (the camera-agnostic version of "forward"). Each reach is cut where
// speed crosses one threshold for the whole set (10% of the median peak), then
// cut again on speed along the reach's own direction, so sideways wobble can't
// move the cut.
function bounds(sig, thr, prev, p, nxt) {
  let a = p, b = p;
  while (a > prev && Number.isFinite(sig[a]) && sig[a] >= thr) a--;
  while (b < nxt && Number.isFinite(sig[b]) && sig[b] >= thr) b++;
  const ok = Number.isFinite(sig[a]) && Number.isFinite(sig[b]) && sig[a] < thr && sig[b] < thr;
  return { a, b, ok };
}

export function segment(series, { onsetFrac = 0.1, minPeak = 0.25, minSep = 0.3, minDur = 0.15, maxDur = 4,
                                   minPathFrac = 0.5 } = {}) {
  const { wrist, elbow, fps } = series;
  const n = wrist.length;
  const v = wrist.map((_, i) => (i === 0 || i === n - 1) ? [NaN, NaN]
    : [0, 1].map(c => (wrist[i + 1][c] - wrist[i - 1][c]) * fps / 2));
  const speed = v.map(x => Math.hypot(x[0], x[1]));
  const finite = speed.filter(Number.isFinite);
  if (finite.length < 10) return [];
  const slow = quantile(finite, 0.2);
  const still = wrist.filter((p, i) => Number.isFinite(speed[i]) && speed[i] <= slow);
  const rest = [median(still.map(p => p[0])), median(still.map(p => p[1]))];
  const sep = Math.round(minSep * fps), floor = minPeak * quantile(finite, 0.99);
  let peaks = [];
  for (let i = 1; i < n - 1; i++) {
    const s = speed[i];
    if (Number.isFinite(s) && s >= floor && s >= (speed[i - 1] || 0) && s > (speed[i + 1] || 0)) peaks.push(i);
  }
  peaks = peaks.filter(p => !peaks.some(q => q !== p && Math.abs(q - p) <= sep && speed[q] > speed[p]));
  const outward = peaks.filter(p => v[p][0] * (wrist[p][0] - rest[0]) + v[p][1] * (wrist[p][1] - rest[1]) > 0);
  if (!outward.length) return [];
  const thr = onsetFrac * median(outward.map(p => speed[p]));
  const reps = [];
  for (const p of outward) {
    const k = peaks.indexOf(p);
    const prev = k > 0 ? peaks[k - 1] : 0, nxt = k + 1 < peaks.length ? peaks[k + 1] : n - 1;
    let { a, b, ok } = bounds(speed, thr, prev, p, nxt);
    if (ok && b > a) {
      const ax = [wrist[b][0] - wrist[a][0], wrist[b][1] - wrist[a][1]], len = Math.hypot(ax[0], ax[1]);
      if (len > 0) {
        const along = v.map(x => Math.abs((x[0] * ax[0] + x[1] * ax[1]) / len));
        ({ a, b, ok } = bounds(along, thr, prev, p, nxt));
      }
    }
    if (!ok || a <= 0 || b >= n - 1) continue;           // runs off the recording or into a tracking gap
    const dur = (b - a) / fps;
    if (dur < minDur || dur > maxDur) continue;
    if (reps.some(r => r.start === a && r.end === b)) continue;
    let path = 0;
    for (let i = a + 1; i <= b; i++) path += Math.hypot(wrist[i][0] - wrist[i - 1][0], wrist[i][1] - wrist[i - 1][1]);
    reps.push({ start: a, end: b, path, frames: Array.from({ length: b - a + 1 }, (_, j) => [wrist[a + j], elbow[a + j]]) });
  }
  const med = median(reps.map(r => r.path));
  return reps.filter(r => r.path >= minPathFrac * med);   // fidgets travel much less than a real reach
}

// ---------- alignment (as movediff/align.py) ----------
export function resample(rep, n = L) {
  const src = linspace(rep.length), dst = linspace(n);
  return dst.map(u => rep[0].map((_, j) => [0, 1].map(c => interp(u, src, rep.map(f => f[j][c])))));
}

function velocityFeatures(rep) {             // (n, J*2), np.gradient * (n - 1)
  const n = rep.length, out = [];
  for (let i = 0; i < n; i++) {
    const a = rep[Math.max(0, i - 1)], b = rep[Math.min(n - 1, i + 1)], h = (i === 0 || i === n - 1) ? 1 : 2;
    const row = [];
    for (let j = 0; j < a.length; j++) for (let c = 0; c < 2; c++) row.push((b[j][c] - a[j][c]) / h * (n - 1));
    out.push(row);
  }
  return out;
}

export function dtw(a, b, band) {
  const n = a.length, m = b.length, w = Math.max(band, Math.abs(n - m));
  const D = Array.from({ length: n + 1 }, () => new Float64Array(m + 1).fill(Infinity));
  D[0][0] = 0;
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (Math.abs((i - 1) * (m - 1) / Math.max(n - 1, 1) - (j - 1)) > w) continue;
      let c = 0;
      for (let k = 0; k < a[0].length; k++) c += (a[i - 1][k] - b[j - 1][k]) ** 2;
      D[i][j] = Math.sqrt(c) + Math.min(D[i - 1][j - 1], D[i - 1][j], D[i][j - 1]);
    }
  }
  let i = n, j = m;
  const path = [[n - 1, m - 1]];
  while (i > 1 || j > 1) {
    const opts = [[D[i - 1][j - 1], i - 1, j - 1], [D[i - 1][j], i - 1, j], [D[i][j - 1], i, j - 1]];
    let best = opts[0];
    for (const o of opts) if (o[0] < best[0]) best = o;    // ties go to the diagonal, as in Python
    [, i, j] = best;
    path.push([i - 1, j - 1]);
  }
  path.reverse();
  return { cost: D[n][m] / (n + m), path };
}

export function timeMap(path, nRef, nRep, smooth = 7) {
  const s = new Float64Array(nRef), c = new Float64Array(nRef);
  for (const [i, j] of path) { s[i] += j; c[i] += 1; }
  let jm = Array.from(s, (v, i) => v / c[i]);
  if (smooth > 1) {
    const pad = Math.floor(smooth / 2);
    const head = [], tail = [];
    for (let k = pad; k >= 1; k--) head.push(2 * jm[0] - jm[k]);
    for (let k = 1; k <= pad; k++) tail.push(2 * jm[nRef - 1] - jm[nRef - 1 - k]);
    const padded = [...head, ...jm, ...tail];
    jm = jm.map((_, i) => { let t = 0; for (let k = 0; k < smooth; k++) t += padded[i + k]; return t / smooth; });
  }
  let run = -Infinity;
  jm = jm.map(v => (run = Math.max(run, Math.min(Math.max(v, 0), nRep - 1))));
  jm[0] = 0; jm[nRef - 1] = nRep - 1;
  return jm;
}

function readAt(rep, positions) {             // rep sampled at fractional indices
  const idx = rep.map((_, i) => i);
  return positions.map(p => rep[0].map((_, j) => [0, 1].map(c => interp(p, idx, rep.map(f => f[j][c])))));
}

function polyfit(x, y, deg) {                 // least squares, normal equations (small degree)
  const m = deg + 1, A = Array.from({ length: m }, () => new Float64Array(m)), r = new Float64Array(m);
  for (let k = 0; k < x.length; k++) {
    const pw = Array.from({ length: m }, (_, i) => x[k] ** i);
    for (let i = 0; i < m; i++) { r[i] += pw[i] * y[k]; for (let j = 0; j < m; j++) A[i][j] += pw[i] * pw[j]; }
  }
  for (let i = 0; i < m; i++) {               // Gaussian elimination with partial pivoting
    let piv = i;
    for (let k = i + 1; k < m; k++) if (Math.abs(A[k][i]) > Math.abs(A[piv][i])) piv = k;
    [A[i], A[piv]] = [A[piv], A[i]]; [r[i], r[piv]] = [r[piv], r[i]];
    for (let k = i + 1; k < m; k++) { const f = A[k][i] / A[i][i]; for (let j = i; j < m; j++) A[k][j] -= f * A[i][j]; r[k] -= f * r[i]; }
  }
  const coef = new Float64Array(m);
  for (let i = m - 1; i >= 0; i--) { let s = r[i]; for (let j = i + 1; j < m; j++) s -= A[i][j] * coef[j]; coef[i] = s / A[i][i]; }
  return u => coef.reduce((acc, c, i) => acc + c * u ** i, 0);
}

// Target = the medoid baseline rep, retimed to average baseline timing (see align.py for why).
export function makeAligner(baseline, { mode = "velocity", bandFrac = 0.1 } = {}) {
  if (mode === "none") return rep => rep;
  const band = Math.max(1, Math.round(bandFrac * L));
  const feats = baseline.map(velocityFeatures);
  const n = feats.length, dist = Array.from({ length: n }, () => new Float64Array(n));
  for (let a = 0; a < n; a++) for (let b = a + 1; b < n; b++) dist[a][b] = dist[b][a] = dtw(feats[a], feats[b], band).cost;
  let med = 0;
  for (let a = 1; a < n; a++) if (dist[a].reduce((s, v) => s + v, 0) < dist[med].reduce((s, v) => s + v, 0)) med = a;
  const maps = feats.map(f => timeMap(dtw(feats[med], f, band).path, L, L));
  const u = linspace(L);
  let mean = u.map((_, i) => maps.reduce((s, m) => s + m[i], 0) / maps.length / (L - 1));
  const fit = polyfit(u, mean.map((v, i) => v - u[i]), 4);
  let run = -Infinity;
  mean = u.map(x => (run = Math.max(run, Math.min(Math.max(x + fit(x) - fit(0) * (1 - x) - fit(1) * x, 0), 1))));
  const idx = u.map(x => interp(x, mean, u.map((_, i) => i)));
  const reference = readAt(baseline[med], idx);
  const refFeat = velocityFeatures(reference);
  return rep => readAt(rep, timeMap(dtw(refFeat, velocityFeatures(rep), band).path, L, rep.length));
}

// ---------- the comparison (as movediff/metrics.py) ----------
function meanRep(reps) {
  const n = reps.length;
  return reps[0].map((frame, t) => frame.map((_, j) => [0, 1].map(c => reps.reduce((s, r) => s + r[t][j][c], 0) / n)));
}
const masks = () => PHASES.map(([, lo, hi], k) => Array.from({ length: L }, (_, i) => {
  const f = i / (L - 1); return f >= lo && (k === PHASES.length - 1 ? f <= hi : f < hi);
}));
const phaseRms = (sq, ms) => ms.map(m => Math.sqrt(sq.reduce((s, v, i) => s + (m[i] ? v : 0), 0) / m.filter(Boolean).length));

function spreadSq(reps, j) {                  // unbiased mean squared distance to the group mean, per sample
  const mu = meanRep(reps), R = reps.length;
  return mu.map((frame, t) => reps.reduce((s, r) => s + (r[t][j][0] - frame[j][0]) ** 2 + (r[t][j][1] - frame[j][1]) ** 2, 0) / (R - 1));
}

export function compare(A, B, { nPerm = 500, seed = 1, joint = 0 } = {}) {
  const rand = rng(seed), ms = masks(), na = A.length, nb = B.length;
  const sqDiff = (ma, mb) => ma.map((f, t) => (mb[t][joint][0] - f[joint][0]) ** 2 + (mb[t][joint][1] - f[joint][1]) ** 2);
  const sq = sqDiff(meanRep(A), meanRep(B));
  const shift = phaseRms(sq, ms);
  const pooled = [...A, ...B];
  const nullCurve = [], hits = shift.map(() => 0);
  for (let k = 0; k < nPerm; k++) {
    const p = shuffle(na + nb, rand);
    const s = sqDiff(meanRep(p.slice(nb).map(i => pooled[i])), meanRep(p.slice(0, nb).map(i => pooled[i])));
    nullCurve.push(s.map(Math.sqrt));
    phaseRms(s, ms).forEach((v, i) => { if (v >= shift[i] - 1e-12) hits[i]++; });
  }
  const null95 = sq.map((_, t) => quantile(nullCurve.map(c => c[t]), 0.95));
  const sa = phaseRms(spreadSq(A, joint), ms), sb = phaseRms(spreadSq(B, joint), ms);
  const ratio = sb.map((v, i) => v / sa[i]);
  // Spread test on residuals, each set centred on its own mean, so a shift can't leak in.
  const res = (reps) => { const mu = meanRep(reps), f = Math.sqrt(reps.length / (reps.length - 1));
    return reps.map(r => r.map((fr, t) => ((fr[joint][0] - mu[t][joint][0]) * f) ** 2 + ((fr[joint][1] - mu[t][joint][1]) * f) ** 2)); };
  const ss = [...res(A), ...res(B)];
  const meanSs = idx => ss[0].map((_, t) => idx.reduce((s, i) => s + ss[i][t], 0) / idx.length);
  const obs = ratio.map(r => Math.abs(Math.log(r))), sHits = ratio.map(() => 0);
  for (let k = 0; k < nPerm; k++) {
    const p = shuffle(na + nb, rand);
    const ra = phaseRms(meanSs(p.slice(0, na)), ms), rb = phaseRms(meanSs(p.slice(na)), ms);
    rb.forEach((v, i) => { if (Math.abs(Math.log(v / ra[i])) >= obs[i] - 1e-12) sHits[i]++; });
  }
  return {
    phases: PHASES.map(([name], i) => ({ name, shift: shift[i], pShift: (1 + hits[i]) / (1 + nPerm),
      spreadA: sa[i], spreadB: sb[i], ratio: ratio[i], pSpread: (1 + sHits[i]) / (1 + nPerm) })),
    curve: { shift: sq.map(Math.sqrt), null95 },
    meanA: meanRep(A).map(f => f[joint]), meanB: meanRep(B).map(f => f[joint]),
    nA: na, nB: nb,
  };
}

// Everything from two sets of raw reps (arrays of frames) to the result.
export function analyse(repsA, repsB, { align = "velocity", nPerm = 500, seed = 1 } = {}) {
  if (repsA.length < 3 || repsB.length < 3) throw new Error("need at least 3 reaches in each set");
  const ra = repsA.map(r => resample(r)), rb = repsB.map(r => resample(r));
  const aligner = makeAligner(ra, { mode: align });
  const A = ra.map(aligner), B = rb.map(aligner);
  return { ...compare(A, B, { nPerm, seed }), alignedA: A.map(r => r.map(f => f[0])), alignedB: B.map(r => r.map(f => f[0])) };
}

// Short sentences for the result.
export function verdict(res) {
  const sig = res.phases.filter(p => p.pShift < 0.05).sort((a, b) => b.shift - a.shift);
  const spread = res.phases.filter(p => p.pSpread < 0.05).sort((a, b) => Math.abs(Math.log(b.ratio)) - Math.abs(Math.log(a.ratio)));
  return {
    shift: sig.length ? { phase: sig[0].name, size: sig[0].shift, p: sig[0].pShift } : null,
    spread: spread.length ? { phase: spread[0].name, ratio: spread[0].ratio, p: spread[0].pSpread } : null,
  };
}
