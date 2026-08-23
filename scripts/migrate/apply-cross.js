/* Крос-книжні дублі: злиття + перейменування за cross-config.json.
   Файли, маніфести (можуть бути різні книги) і лінки за один прохід.
   Маніфест після правки перепарсюється й глибоко звіряється; інакше стоп без запису. */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const R = path.resolve(__dirname, "../.."), APPLY = process.argv.includes("--apply");
const NL = String.fromCharCode(10), INS = ["hist", "comp", "math", "proj", "api"];
const SKIP = new Set([".git", "node_modules", ".claude", ".github"]);
const CFGPATH = process.argv.slice(2).find(a => !a.startsWith("--")) || path.join(__dirname, "cross-config.json");
const CFG = JSON.parse(fs.readFileSync(CFGPATH, "utf8"));
CFG.merges = CFG.merges || []; CFG.renames = CFG.renames || []; CFG.drops = CFG.drops || [];
const mfOf = p => p.split("/").slice(0, 2).join("/") + "/manifest.js";
const bookOf = p => p.split("/")[1];
const slugOf = p => p.split("/").pop();
function git(a) { const r = cp.spawnSync("git", a, { cwd: R, encoding: "utf8" });
  if (r.status !== 0) { console.error("STOP git " + a.join(" ") + ": " + (r.stderr || "").trim()); process.exit(1); } }
function walk(d, o) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name);
  if (e.isDirectory()) { if (!SKIP.has(e.name)) walk(p, o) } else if (e.name.endsWith(".md")) o.push(p); } return o; }
function figsOf(f) { const t = fs.readFileSync(f, "utf8"), o = new Set(); let i = 0;
  while ((i = t.indexOf("img/", i)) >= 0) { const j = t.indexOf(".svg", i);
    if (j > 0 && j - i < 90) o.add(t.slice(i + 4, j + 4)); i += 4; } return Array.from(o); }
function parse(src) { const w = { __BOOKS__: [] }; new Function("window", src)(w); return w.__BOOKS__[0]; }
const q = s => JSON.stringify(String(s));
function serTopic(t) { const p = ["slug: " + q(t.slug), "title: " + q(t.title)];
  for (const v of ["basic", "detailed"]) if (t[v]) p.push(v + ": { status: " + q(t[v].status) + " }");
  const keys = INS.concat(Object.keys(t).filter(k => ["slug","title","basic","detailed"].indexOf(k) < 0 && INS.indexOf(k) < 0));
  for (const k of keys) { if (!t[k]) continue;
    if (!Array.isArray(t[k])) { p.push(k + ": " + JSON.stringify(t[k])); continue; }
    if (!t[k].length) { p.push(k + ": []"); continue; }
    const ok = t[k].every(i => i && typeof i === "object" && typeof i.file === "string");
    p.push(k + ": " + (ok ? "[" + t[k].map(i => "{ file: " + q(i.file) + ", status: " + q(i.status) + " }").join(", ") + "]" : JSON.stringify(t[k]))); }
  return "        { " + p.join(", ") + " },"; }
function serialize(head, m) { const L = [head.replace(/\s*$/, ""), "(window.__BOOKS__ = window.__BOOKS__ || []).push({",
    "  type: " + q(m.type) + ", slug: " + q(m.slug) + ", title: " + q(m.title) + ",", "  sections: ["];
  for (const s of m.sections || []) { L.push("    { slug: " + q(s.slug) + ", title: " + q(s.title) + ", scope: " + q(s.scope || "") + ",");
    L.push("      topics: ["); for (const t of s.topics || []) L.push(serTopic(t)); L.push("      ] },"); }
  L.push("  ]"); L.push("});"); return L.join(NL) + NL; }
const canon = x => Array.isArray(x) ? x.map(canon) : (x && typeof x === "object"
  ? Object.keys(x).sort().reduce((o, k) => (o[k] = canon(x[k]), o), {}) : x);
const eq = (a, b) => JSON.stringify(canon(a)) === JSON.stringify(canon(b));
const MF = {};
function load(mf) { if (MF[mf]) return MF[mf];
  const file = path.join(R, mf), src = fs.readFileSync(file, "utf8");
  return (MF[mf] = { file: file, head: src.slice(0, src.indexOf("(window.__BOOKS__")), m: parse(src) }); }
function findTopic(mf, slug) { const o = load(mf);
  for (const s of o.m.sections || []) for (const t of s.topics || []) if (t.slug === slug) return { sec: s, t: t };
  return null; }
const linkMap = [], fileOps = [];
for (const M of CFG.merges) {
  for (const pair of M.take) { const f = pair[1];
    fileOps.push([M.die + "/" + f, M.win + "/" + f]);
    for (const g of figsOf(path.join(R, M.die, f))) {
      const from = M.die + "/img/" + g; if (!fs.existsSync(path.join(R, from))) continue;
      let to = M.win + "/img/" + g;
      if (fs.existsSync(path.join(R, to))) to = M.win + "/img/" + g.replace(".svg", "-alt.svg");
      fileOps.push([from, to]); } }
  fileOps.push({ rm: M.die, pathFix: [M.die, M.win] });
  linkMap.push([bookOf(M.die), slugOf(M.die), bookOf(M.win), slugOf(M.win)]);
}
for (const RN of CFG.renames) {
  const dir = RN.path.split("/").slice(0, -1).join("/"), old = slugOf(RN.path);
  fileOps.push({ mvdir: [RN.path, dir + "/" + RN.slug], old: old, neu: RN.slug });
  linkMap.push([bookOf(RN.path), old, bookOf(RN.path), RN.slug]);
}
if (!APPLY) {
  console.log("ZLYTTYA: " + CFG.merges.length + "   PEREIMENUVAN: " + CFG.renames.length + "   fileOps: " + fileOps.length);
  CFG.merges.forEach(M => console.log("  " + slugOf(M.win).padEnd(26) + "<- " + bookOf(M.die).padEnd(14) +
    (M.take.length ? "bere " + M.take.map(x => x[1]).join(", ") : "nichoho")));
  CFG.renames.forEach(RN => console.log("  " + slugOf(RN.path).padEnd(26) + "-> " + RN.slug));
  process.exit(0);
}
for (const op of fileOps) {
  if (Array.isArray(op)) { git(["mv", op[0], op[1]]); continue; }
  if (op.mvdir) { const a = op.mvdir[0], b = op.mvdir[1]; git(["mv", a, b]);
    for (const e of fs.readdirSync(path.join(R, b))) {
      if (e === op.old + ".md") git(["mv", b + "/" + e, b + "/" + op.neu + ".md"]);
      else if (e === op.old + "-d.md") git(["mv", b + "/" + e, b + "/" + op.neu + "-d.md"]); }
    const OLD = "/" + a + "/", NEW = "/" + b + "/";
    for (const e of fs.readdirSync(path.join(R, b))) {
      if (!e.endsWith(".md") && !e.endsWith(".py")) continue;
      const p = path.join(R, b, e), s = fs.readFileSync(p, "utf8");
      if (s.indexOf(OLD) < 0) continue; fs.writeFileSync(p, s.split(OLD).join(NEW), "utf8"); }
    continue; }
  if (op.rm) { const die = op.pathFix[0], win = op.pathFix[1], OLD = "/" + die + "/", NEW = "/" + win + "/";
    for (const e of fs.readdirSync(path.join(R, win))) {
      if (!e.endsWith(".md")) continue;
      const p = path.join(R, win, e), s = fs.readFileSync(p, "utf8");
      if (s.indexOf(OLD) < 0) continue; fs.writeFileSync(p, s.split(OLD).join(NEW), "utf8"); }
    git(["rm", "-r", "-q", op.rm]); }
}
console.log("faylovi operatsii: " + fileOps.length);
for (const M of CFG.merges) {
  const W = findTopic(mfOf(M.win), slugOf(M.win)), D = findTopic(mfOf(M.die), slugOf(M.die));
  if (!W || !D) { console.error("STOP: tema ne znaydena " + M.win + " / " + M.die); process.exit(1); }
  for (const pair of M.take) { const type = pair[0], f = pair[1];
    const src = (D.t[type] || []).find(i => i.file === f);
    W.t[type] = W.t[type] || [];
    if (!W.t[type].some(i => i.file === f)) W.t[type].push({ file: f, status: (src && src.status) || "recheck" }); }
  if (M.take.length && W.t.detailed) W.t.detailed.status = "recheck";
  D.sec.topics.splice(D.sec.topics.indexOf(D.t), 1);
}
for (const D of CFG.drops) {
  const mf = D.book + "/manifest.js", o = load(mf);
  let found = null;
  for (const sec of o.m.sections || []) { const i = (sec.topics || []).findIndex(t => t.slug === D.slug);
    if (i >= 0) { found = { sec: sec, i: i }; break; } }
  if (!found) { console.error("STOP: nema temy " + mf + " / " + D.slug); process.exit(1); }
  found.sec.topics.splice(found.i, 1);
  console.log("  drop " + D.book + "/" + D.slug);
}
for (const RN of CFG.renames) {
  const T = findTopic(mfOf(RN.path), slugOf(RN.path));
  if (!T) { console.error("STOP: tema ne znaydena " + RN.path); process.exit(1); }
  T.t.slug = RN.slug; T.t.title = RN.title;
}
for (const mf of Object.keys(MF)) { const o = MF[mf];
  const out = serialize(o.head, o.m), back = parse(out);
  if (!back || !eq(back, o.m)) { console.error("STOP " + mf + ": zvirka ne ziyshlasya"); process.exit(1); }
  fs.writeFileSync(o.file, out, "utf8");
  let n = 0; for (const s of o.m.sections || []) n += (s.topics || []).length;
  console.log("  manifest " + mf.padEnd(30) + "tem " + n); }
const pairs = []; let nl = 0, nf = 0;
for (const f of walk(R, [])) {
  const s = fs.readFileSync(f, "utf8"); let out = s, hit = 0;
  for (const lm of linkMap) {
    const from = "](book:" + lm[0] + "/" + lm[1] + ")", to = "](book:" + lm[2] + "/" + lm[3] + ")";
    while (out.indexOf(from) >= 0) { out = out.replace(from, to); hit++;
      pairs.push({ from: lm[0] + "/" + lm[1], to: lm[2] + "/" + lm[3], file: path.relative(R, f) }); } }
  if (!hit) continue; fs.writeFileSync(f, out, "utf8"); nl += hit; nf++;
}
console.log("linkiv peretsileno: " + nl + " u " + nf + " faylakh");
const dst = path.join(__dirname, "link-changes.json");
const prev = fs.existsSync(dst) ? JSON.parse(fs.readFileSync(dst, "utf8")) : [];
fs.writeFileSync(dst, JSON.stringify(prev.concat(pairs), null, 2) + NL, "utf8");
console.log("par u link-changes.json: " + (prev.length + pairs.length));
