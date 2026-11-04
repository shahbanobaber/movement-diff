// Camera, pose tracking and results. The maths lives in analysis.js.
import { analyse, pickSide, segment, toSeries, verdict } from "./analysis.js";

const TARGET = 8;                                   // reaches per set
const MP = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21";
const MODEL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task";
const ARM = { left: [11, 13, 15], right: [12, 14, 16] };

const $ = id => document.getElementById(id);
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const pct = x => `${Math.round(100 * x)}%`;
const video = $("video"), canvas = $("overlay"), ctx = canvas.getContext("2d");

const st = { phase: "off", frames: { A: [], B: [] }, side: null, count: 0, landmarker: null, lastVideoTime: -1, timer: null };

function say(text) { $("status").textContent = text; }
function button(label, onClick, disabled = false) {
  const b = $("main"); b.textContent = label; b.onclick = onClick; b.disabled = disabled;
}
function beep() {
  try {
    const ac = beep.ac || (beep.ac = new AudioContext());
    const o = ac.createOscillator(), g = ac.createGain();
    o.frequency.value = 880; g.gain.value = 0.08; o.connect(g).connect(ac.destination);
    o.start(); o.stop(ac.currentTime + 0.08);
  } catch { /* no sound, no problem */ }
}

// ---------- camera and pose ----------
async function startCamera() {
  button("Starting…", null, true);
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: "user" }, audio: false });
    video.srcObject = stream;
    await video.play();
    $("placeholder").hidden = true;
    say("Loading pose tracking…");
    const { FilesetResolver, PoseLandmarker } = await import(`${MP}/vision_bundle.mjs`);
    const files = await FilesetResolver.forVisionTasks(`${MP}/wasm`);
    const make = delegate => PoseLandmarker.createFromOptions(files, {
      baseOptions: { modelAssetPath: MODEL, delegate }, runningMode: "VIDEO", numPoses: 1 });
    st.landmarker = await make("GPU").catch(() => make("CPU"));
    requestAnimationFrame(loop);
    ready("A");
  } catch (err) {
    say(err.name === "NotAllowedError" ? "Camera blocked. Allow it, or try the sample data." : `Camera didn't start (${err.message}).`);
    button("Start camera", startCamera);
  }
}

function loop() {
  if (video.readyState >= 2 && video.currentTime !== st.lastVideoTime) {
    st.lastVideoTime = video.currentTime;
    const t = performance.now();
    const res = st.landmarker.detectForVideo(video, t);
    const w = video.videoWidth, h = video.videoHeight;
    const lm = res.landmarks?.[0]?.map(p => [p.x * w, p.y * h, p.visibility ?? 1]);
    draw(lm, w, h);
    if (lm && (st.phase === "A" || st.phase === "B")) st.frames[st.phase].push({ t, lm });
  }
  requestAnimationFrame(loop);
}

function draw(lm, w, h) {
  canvas.width = w; canvas.height = h;
  ctx.clearRect(0, 0, w, h);
  if (!lm) return;
  for (const [side, idx] of Object.entries(ARM)) {
    const pts = idx.map(i => lm[i]);
    if (pts.some(p => p[2] < 0.5)) continue;
    const on = !st.side || st.side === side;
    ctx.strokeStyle = on ? css("--b") : "rgba(255,255,255,.35)";
    ctx.lineWidth = on ? 6 : 3; ctx.lineCap = "round";
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); pts.slice(1).forEach(p => ctx.lineTo(p[0], p[1])); ctx.stroke();
    ctx.fillStyle = "#fff";
    pts.forEach(p => { ctx.beginPath(); ctx.arc(p[0], p[1], on ? 7 : 4, 0, 2 * Math.PI); ctx.fill(); });
  }
}

// ---------- recording ----------
function ready(set) {
  st.phase = `ready${set}`;
  say(set === "A" ? `Eyes open: reach to your spot and back, ${TARGET} times.` : `Now eyes closed: reach to the same spot, ${TARGET} times. It beeps each one.`);
  button(set === "A" ? "Record set 1" : "Record set 2", () => record(set));
  $("reset").hidden = false;
}

function countReps(set) {
  const frames = st.frames[set];
  if (frames.length < 20) return 0;
  try {
    const side = st.side || pickSide(frames);
    return segment(toSeries(frames, side)).length;
  } catch { return 0; }
}

function record(set) {
  st.frames[set] = []; st.count = 0; st.phase = set;
  say(`Set ${set === "A" ? 1 : 2}: 0 of ${TARGET}`);
  button("Stop", () => stop(set));
  st.timer = setInterval(() => {
    const n = countReps(set);
    if (n > st.count) { st.count = n; beep(); say(`Set ${set === "A" ? 1 : 2}: ${Math.min(n, TARGET)} of ${TARGET}`); }
    if (n >= TARGET) stop(set);
  }, 400);
}

function stop(set) {
  clearInterval(st.timer);
  const frames = st.frames[set];
  let reps = [];
  try {
    if (set === "A") st.side = pickSide(frames);
    reps = segment(toSeries(frames, st.side));
  } catch { reps = []; }
  if (reps.length < 4) {
    st.phase = `ready${set}`;
    say(`Only ${reps.length} seen. Keep your whole arm in view, pause in your lap between reaches, and try again.`);
    button(set === "A" ? "Record set 1" : "Record set 2", () => record(set));
    return;
  }
  st[`reps${set}`] = reps.slice(0, TARGET + 4).map(r => r.frames);
  if (set === "A") ready("B");
  else { st.phase = "done"; say("Done."); button("Record again", () => { st.side = null; ready("A"); }); show(st.repsA, st.repsB); }
}

// ---------- results ----------
function show(A, B, label) {
  let res;
  try { res = analyse(A, B, { nPerm: 500 }); } catch (err) { say(err.message); return; }
  const v = verdict(res);
  const phaseWord = { early: "at the start", mid: "in the middle", late: "at the end" };
  const parts = [];
  if (v.shift) parts.push(`Your reach shifted ${phaseWord[v.shift.phase]}`);
  if (v.spread) parts.push(`${v.shift ? "and" : "Your reach"} got ${v.spread.ratio > 1 ? "less" : "more"} steady ${phaseWord[v.spread.phase]}`);
  $("headline").textContent = (label ? `${label}: ` : "") + (parts.length ? `${parts.join(" ")}.` : "No clear change. Both sets look the same.");
  const biggest = res.phases.reduce((a, b) => (b.shift > a.shift ? b : a));
  const steadiest = res.phases.reduce((a, b) => (Math.abs(Math.log(b.ratio)) > Math.abs(Math.log(a.ratio)) ? b : a));
  const where = { early: "start", mid: "middle", late: "end" };
  const chance = p => (p < 0.05 ? "" : " · could be chance");
  $("tiles").innerHTML = [
    [pct(biggest.shift), `of arm length: biggest shift, at the ${where[biggest.name]}${chance(biggest.pShift)}`],
    [`${steadiest.ratio.toFixed(1)}×`, `as variable at the ${where[steadiest.name]}${chance(steadiest.pSpread)}`],
    [`${res.nA} + ${res.nB}`, "reaches compared"],
  ].map(([v, k]) => `<div class="tile"><div class="v">${v}</div><div class="k">${k}</div></div>`).join("");
  $("results").hidden = false;
  draw2(res);
  $("results").scrollIntoView({ behavior: "smooth", block: "start" });
  window.__lastResult = res;   // for the browser test
}

function draw2(res) {
  const style = { background: "transparent", color: css("--ink2"), fontSize: "12px" };
  const sets = [["set 1", res.alignedA, res.meanA, css("--a")], ["set 2", res.alignedB, res.meanB, css("--b")]];
  const faint = sets.flatMap(([name, reps]) => reps.flatMap((r, k) => r.map(([x, y], i) => ({ name, k, i, x, y }))));
  const means = sets.flatMap(([name, , mean]) => mean.map(([x, y], i) => ({ name, i, x, y })));
  const pel = $("paths");
  pel.replaceChildren(Plot.plot({
    width: pel.clientWidth, height: pel.clientWidth, style, aspectRatio: 1, inset: 10,
    x: { label: null, ticks: [] }, y: { label: null, ticks: [] },
    color: { domain: ["set 1", "set 2"], range: [css("--a"), css("--b")], legend: true },
    marks: [
      Plot.line(faint, { x: "x", y: "y", z: d => `${d.name}${d.k}`, stroke: "name", strokeOpacity: 0.18, strokeWidth: 1 }),
      Plot.line(means, { x: "x", y: "y", z: "name", stroke: "name", strokeWidth: 3 }),
      Plot.dot(means.filter(d => d.i === 0), { x: "x", y: "y", fill: "name", r: 4 }),
    ],
  }));
  // In percent of arm length, so the axis reads in whole numbers.
  const curve = res.curve.shift.map((s, i) => ({ u: i / (res.curve.shift.length - 1), s: 100 * s, n: 100 * res.curve.null95[i] }));
  const sel = $("shift");
  sel.replaceChildren(Plot.plot({
    width: sel.clientWidth, height: Math.max(220, sel.clientWidth * 0.75), style, marginLeft: 40,
    x: { label: "Through the reach →", tickFormat: "%", domain: [0, 1] },
    y: { label: "↑ % of arm length", grid: true },
    marks: [
      Plot.areaY(curve, { x: "u", y: "n", fill: css("--band") }),
      Plot.text([{ u: 0.02, n: Math.max(...curve.map(d => d.n)) }], { x: "u", y: "n", text: () => "chance", fill: css("--muted"), textAnchor: "start", dy: -8 }),
      Plot.ruleX([1 / 3, 2 / 3], { stroke: css("--line") }),
      Plot.line(curve, { x: "u", y: "s", stroke: css("--b"), strokeWidth: 2.5 }),
      Plot.tip(curve, Plot.pointerX({ x: "u", y: "s", title: d => `${pct(d.u)} through\nApart by ${d.s.toFixed(1)}% of arm length\nChance: up to ${d.n.toFixed(1)}%` })),
    ],
  }));
}

// ---------- wiring ----------
$("main").onclick = startCamera;
$("sample").onclick = async () => {
  const s = await (await fetch("sample.json")).json();
  show(s.A, s.B, "Sample");
};
$("reset").onclick = () => { clearInterval(st.timer); st.side = null; st.frames = { A: [], B: [] }; $("results").hidden = true; ready("A"); };

const theme = new URLSearchParams(location.search).get("theme");
if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme;

// Test hook: feed landmark frames as if they came from the camera.
window.__movediff = {
  feed(set, frames) { st.frames[set] = frames; },
  stop,
};
