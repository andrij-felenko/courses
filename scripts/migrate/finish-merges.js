/* Маніфести після злиття семи пар: переможець забирає вставки донора, донор зникає.
   Переможцям, що ввібрали чужі вставки, ставимо detailed:recheck — прозі треба їх вплести.
   Серіалізація канонічна; після запису перепарс і глибока звірка, інакше відкат. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../.."), APPLY = process.argv.includes("--apply");
const NL = String.fromCharCode(10), INS = ["hist", "comp", "math", "proj", "api"];

const EDITS = [
  { mf: "book/physics/manifest.js", win: "permittivity", die: "dielectric-constant",
    take: [["math", "math-debye-relaxation.md"], ["proj", "proj-dielectric-sim.md"]] },
  { mf: "book/physics/manifest.js", win: "ferroelectricity", die: "ferroelectrics",
    take: [["proj", "proj-hysteresis-sim.md"]] },
  { mf: "book/physics/manifest.js", win: "magnetic-monopole", die: "magnetic-monopole-theory", take: [] },
  { mf: "book/physics/manifest.js", win: "superconductivity", die: "superconductor",
    take: [["api", "api-superconductor-parameters.md"], ["comp", "comp-josephson-junction.md"]] },
  { mf: "book/electronics/manifest.js", win: "integrator-differentiator", die: "opamp-integrator-differentiator",
    take: [["hist", "hist-miller-integrator.md"], ["math", "math-opamp-integrator-transfer.md"]] },
  { mf: "book/electronics/manifest.js", win: "shockley-queisser-limit", die: "shockley-queisser",
    take: [["math", "math-detailed-balance-derivation.md"]] },
];
const SWAP = { mf: "book/math/manifest.js", win: "quadratic-residues", die: "quadratic-residue" };

function parse(src) { const w = { __BOOKS__: [] }; new Function("window", src)(w); return w.__BOOKS__[0]; }
const q = s => JSON.stringify(String(s));
function serTopic(t) {
  const p = ["slug: " + q(t.slug), "title: " + q(t.title)];
  for (const v of ["basic", "detailed"]) if (t[v]) p.push(v + ": { status: " + q(t[v].status) + " }");
  const keys = INS.concat(Object.keys(t).filter(k => ["slug","title","basic","detailed"].indexOf(k) < 0 && INS.indexOf(k) < 0));
  for (const k of keys) {
    if (!t[k]) continue;
    if (!Array.isArray(t[k])) { p.push(k + ": " + JSON.stringify(t[k])); continue; }
    if (!t[k].length) { p.push(k + ": []"); continue; }
    const isIns = t[k].every(i => i && typeof i === "object" && typeof i.file === "string");
    p.push(k + ": " + (isIns ? "[" + t[k].map(i => "{ file: " + q(i.file) + ", status: " + q(i.status) + " }").join(", ") + "]" : JSON.stringify(t[k])));
  }
  return "        { " + p.join(", ") + " },";
}
function serialize(head, m) {
  const L = [head.replace(/\s*$/, ""), "(window.__BOOKS__ = window.__BOOKS__ || []).push({",
    "  type: " + q(m.type) + ", slug: " + q(m.slug) + ", title: " + q(m.title) + ",", "  sections: ["];
  for (const sec of m.sections || []) {
    L.push("    { slug: " + q(sec.slug) + ", title: " + q(sec.title) + ", scope: " + q(sec.scope || "") + ",");
    L.push("      topics: [");
    for (const t of sec.topics || []) L.push(serTopic(t));
    L.push("      ] },");
  }
  L.push("  ]"); L.push("});");
  return L.join(NL) + NL;
}
const canon = x => Array.isArray(x) ? x.map(canon) : (x && typeof x === "object"
  ? Object.keys(x).sort().reduce((o, k) => (o[k] = canon(x[k]), o), {}) : x);
const eq = (a, b) => JSON.stringify(canon(a)) === JSON.stringify(canon(b));

const byMf = {};
for (const e of EDITS) (byMf[e.mf] = byMf[e.mf] || []).push(e);
(byMf[SWAP.mf] = byMf[SWAP.mf] || []).push(SWAP);

for (const [mf, list] of Object.entries(byMf)) {
  const file = path.join(R, mf), src = fs.readFileSync(file, "utf8");
  const m = parse(src), head = src.slice(0, src.indexOf("(window.__BOOKS__"));
  const all = (m.sections || []).flatMap(s => (s.topics || []).map(t => ({ sec: s, t: t })));
  const log = [];
  for (const e of list) {
    const W = all.find(x => x.t.slug === e.win), D = all.find(x => x.t.slug === e.die);
    if (!W || !D) { console.error("СТОП: не знайдено " + e.win + " або " + e.die); process.exit(1); }
    if (e === SWAP) {
      for (const k of INS) delete W.t[k];
      for (const k of INS) if (D.t[k]) W.t[k] = D.t[k];
      W.t.basic = D.t.basic; W.t.detailed = D.t.detailed;
      log.push(e.win + "  <= вставки й статуси від " + e.die);
    } else {
      for (const [type, fname] of e.take) {
        const from = (D.t[type] || []).find(i => i.file === fname);
        W.t[type] = W.t[type] || [];
        if (!W.t[type].some(i => i.file === fname)) W.t[type].push({ file: fname, status: (from && from.status) || "recheck" });
      }
      if (e.take.length && W.t.detailed) W.t.detailed.status = "recheck";
      log.push(e.win + "  <- " + (e.take.length ? e.take.map(x => x[1]).join(", ") : "(нічого)") + "   мінус " + e.die);
    }
    D.sec.topics.splice(D.sec.topics.indexOf(D.t), 1);
  }
  const out = serialize(head, m), back = parse(out);
  if (!back || !eq(back, m)) { console.error("СТОП " + mf + ": звірка не зійшлася — не пишу"); process.exit(1); }
  let n = 0; for (const s of m.sections || []) n += (s.topics || []).length;
  console.log((APPLY ? "OK " : "-- ") + mf + "   тем: " + n);
  log.forEach(l => console.log("     " + l));
  if (APPLY) fs.writeFileSync(file, out, "utf8");
}
console.log(APPLY ? NL + "записано" : NL + "(суха прогонка; --apply щоб записати)");
