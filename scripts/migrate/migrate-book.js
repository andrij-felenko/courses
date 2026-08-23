/* migrate-book.js — перенос ОДНІЄЇ книги в нове дерево за файлом розкладки.
   node scripts/migrate/migrate-book.js <placement.json> [--apply]

   placement.json:
   { "target": { "kind":"sci", "book":"physics", "title":"Фізика" },
     "groups": [ { "slug":"mechanics", "title":"Механіка",
        "chapters": [ { "slug":"kinematics", "title":"Кінематика",
           "topics": [ { "slug":"friction", "from":"book/physics/mechanics/friction" } ] } ] } ] }
   chapter.slug === "." — тема лежить прямо в групі, розділу немає.
   Джерело теми може бути з БУДЬ-ЯКОЇ старої книги — цільове дерево приймає звідусіль. */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const R = path.resolve(__dirname, "../..");
const NL = String.fromCharCode(10), INS = ["hist", "comp", "math", "proj", "api"];
const SKIP = new Set([".git", "node_modules", ".claude", ".github"]);
const args = process.argv.slice(2);
const PF = args.find(a => !a.startsWith("--")), APPLY = args.includes("--apply");
if (!PF) { console.error("ужиток: node scripts/migrate/migrate-book.js <placement.json> [--apply]"); process.exit(2); }
const P = JSON.parse(fs.readFileSync(PF, "utf8"));
const KIND = P.target.kind, BOOK = P.target.book;
const DEST = "root/" + KIND + "/" + BOOK;

function git(a) { const r = cp.spawnSync("git", a, { cwd: R, encoding: "utf8" });
  if (r.status !== 0) { console.error("STOP git " + a.join(" ") + ": " + (r.stderr || "").trim()); process.exit(1); } }
function walk(d, o) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name);
  if (e.isDirectory()) { if (!SKIP.has(e.name)) walk(p, o) } else if (e.name.endsWith(".md")) o.push(p); } return o; }
function parseJs(f) { const w = { __BOOKS__: [] }; new Function("window", fs.readFileSync(f, "utf8"))(w); return w.__BOOKS__[0]; }
const mfOf = rel => rel.split("/").slice(0, 2).join("/") + "/manifest.js";
/* усі теми розкладки пласким списком */
const flat = [];
for (const g of P.groups || []) for (const c of g.chapters || []) for (const t of c.topics || [])
  flat.push({ slug: t.slug, from: t.from, group: g.slug, chapter: c.slug });

/* передумови */
/* Передумови роблять прогін ІДЕМПОТЕНТНИМ: обрив посеред роботи лікується повторним запуском.
   джерело є  + ціль вільна   -> переносимо
   джерела нема + ціль є      -> уже перенесено попереднім (обірваним) прогоном, пропускаємо
   джерела нема + цілі нема   -> справжня втрата
   джерело є   + ціль є       -> справжній конфлікт (дубль) */
const bad = [];
const seen = {}, DONE = {};        // DONE ключується слугом: у злитті інші обʼєкти, ніж у flat
let already = 0;
for (const t of flat) {
  const srcOk = fs.existsSync(path.join(R, t.from));
  const dstOk = fs.existsSync(path.join(R, DEST + "/" + t.slug));
  if (seen[t.slug]) bad.push("слуг двічі в розкладці: " + t.slug);
  seen[t.slug] = 1;
  if (srcOk && dstOk) bad.push("і джерело, і ціль існують (ДУБЛЬ): " + t.from);
  else if (!srcOk && !dstOk) bad.push("нема ні джерела, ні цілі: " + t.from);
  else if (!srcOk && dstOk) { t.done = true; DONE[t.slug] = 1; already++; }
}
if (already) console.log("уже перенесено попереднім прогоном: " + already + " — пропускаю їх");
/* вид мусить бути в реєстрі — інакше книга поїде в неіснуючу теку й не зареєструється */
const shelfPre = JSON.parse(fs.readFileSync(path.join(R, "root/shelf.json"), "utf8"));
if (!shelfPre.kinds.some(k => k.kind === KIND))
  bad.push("невідомий вид \"" + KIND + "\" — у root/shelf.json його немає");
/* слуг книги мусить бути глобально унікальним: коротка адреса root:<книга>/<тема> не має сегмента виду */
for (const K2 of shelfPre.kinds) if (K2.kind !== KIND && K2.books.indexOf(BOOK) >= 0)
  bad.push("слуг книги \"" + BOOK + "\" уже зайнятий видом \"" + K2.kind + "\" — коротка адреса їх не розрізнить");
if (bad.length) { console.error("СТОП — передумови не виконані:" + NL + "  " + bad.join(NL + "  ")); process.exit(1); }
console.log("передумови OK: тем " + flat.length + ", джерел на місці, жодної зайнятої цілі");

/* статуси й вставки беремо зі СТАРОГО маніфесту кожної теми */
const srcCache = {};
function oldTopic(from) {
  /* ВАЖЛИВО: шукаємо за ПОВНИМ шляхом (секція + слуг), а не за слугом.
     Один слуг може лежати у двох секціях однієї книги — пошук за слугом брав би не ту тему. */
  const parts = from.split("/");
  const mf = mfOf(from), secSlug = parts[2], slug = parts[3];
  if (!srcCache[mf]) srcCache[mf] = parseJs(path.join(R, mf));
  const m = srcCache[mf];
  if (!m) return null;
  for (const s of m.sections || []) {
    if (s.slug !== secSlug) continue;
    for (const t of s.topics || []) if (t.slug === slug) return { m, sec: s, t };
  }
  return null;
}
const missing = flat.filter(t => !t.done && !oldTopic(t.from));
if (missing.length) { console.error("СТОП — нема в старому маніфесті: " + missing.map(x => x.from).join(", ")); process.exit(1); }

if (!APPLY) {
  const groups = (P.groups || []).length;
  let chapters = 0; (P.groups || []).forEach(g => chapters += (g.chapters || []).length);
  console.log("ціль: " + DEST + "   груп " + groups + ", розділів " + chapters + ", тем " + flat.length);
  const from = {}; flat.forEach(t => { const b = t.from.split("/").slice(0, 2).join("/"); from[b] = (from[b] || 0) + 1; });
  Object.keys(from).forEach(b => console.log("   із " + b.padEnd(28) + from[b]));
  console.log("(суха прогонка; --apply щоб виконати)");
  process.exit(0);
}
/* 1. перенос тек + правка власних img-шляхів (атомарно на тему) */
fs.mkdirSync(path.join(R, DEST), { recursive: true });
let nImg = 0;
for (const t of flat) {
  if (t.done) continue;                       // уже на місці після обірваного прогону
  const to = DEST + "/" + t.slug;
  git(["mv", t.from, to]);
  const OLD = "/" + t.from + "/", NEW = "/" + to + "/";
  for (const f of walk(path.join(R, to), [])) {
    const s = fs.readFileSync(f, "utf8");
    if (s.indexOf(OLD) < 0) continue;
    nImg += s.split(OLD).length - 1;
    fs.writeFileSync(f, s.split(OLD).join(NEW), "utf8");
  }
}
console.log("перенесено тем: " + (flat.length - already) + " (пропущено вже готових " + already + "), img-шляхів переписано: " + nImg);

/* 2. новий manifest.json із розкладки + статуси й вставки зі старих маніфестів */
/* ЗЛИТТЯ, не затирання: книга-ціль може вже мати теми з попереднього прогону
   (інша книга-джерело, інший шматок). Затирання знищило б їх мовчки. */
const mfDest = path.join(R, DEST, "manifest.json");
const had = fs.existsSync(mfDest) ? JSON.parse(fs.readFileSync(mfDest, "utf8")) : null;
const out = had || { schema: 7, kind: KIND, slug: BOOK, title: P.target.title, groups: [] };
if (had && had.kind !== KIND) { console.error("СТОП: наявний manifest.json має kind=" + had.kind + ", а розкладка каже " + KIND); process.exit(1); }
const hadN = (function () { let n = 0; (out.groups || []).forEach(g => (g.chapters || []).forEach(c => n += (c.topics || []).length)); return n; })();
let skippedReg = 0;
const seenSlug = {};
(out.groups || []).forEach(g => (g.chapters || []).forEach(c => (c.topics || []).forEach(t => seenSlug[t.slug] = g.slug + "/" + c.slug)));

for (const g of P.groups || []) {
  let G = out.groups.find(x => x.slug === g.slug);
  if (!G) { G = { slug: g.slug, title: g.title, scope: g.scope || "", chapters: [] }; out.groups.push(G); }
  else if (!G.scope && g.scope) G.scope = g.scope;
  for (const c of g.chapters || []) {
    let C = G.chapters.find(x => x.slug === c.slug);
    if (!C) { C = { slug: c.slug, title: c.title, topics: [] }; G.chapters.push(C); }
    for (const t of c.topics || []) {
      if (seenSlug[t.slug]) {
        if (DONE[t.slug]) { skippedReg++; continue; }              // уже і перенесено, і зареєстровано — нічого робити
        console.error("СТОП: тема \"" + t.slug + "\" уже є в цій книзі (" + seenSlug[t.slug] + ")"); process.exit(1);
      }
      const src0 = oldTopic(t.from);
      if (!src0) {
        console.error("СТОП: нема запису в старому маніфесті для " + t.from +
          (DONE[t.slug] ? NL + "  (тему вже перенесено, але в новому маніфесті її немає — стан не відновлюваний автоматично)" : ""));
        process.exit(1);
      }
      const o = src0.t, e = { slug: o.slug, title: t.title || o.title };
      e.basic = { status: (o.basic && o.basic.status) || "empty" };
      e.detailed = { status: (o.detailed && o.detailed.status) || "empty" };
      for (const k of INS) if (o[k] && o[k].length) e[k] = o[k];
      C.topics.push(e); seenSlug[t.slug] = g.slug + "/" + c.slug;
    }
  }
}
let nT = 0; out.groups.forEach(g => g.chapters.forEach(c => nT += c.topics.length));

/* ЗВІРКА ВХІД == ВИХІД: скільки тем було в розкладці, стільки й мало додатися */
const expect = hadN + flat.length - skippedReg;
if (nT !== expect) {
  console.error("СТОП: у маніфесті мало стати " + expect + " тем (" + hadN + " було + " + (flat.length - skippedReg) + " нових), а вийшло " + nT);
  process.exit(1);
}
/* і стільки ж тек на диску */
const dirsN = fs.readdirSync(path.join(R, DEST), { withFileTypes: true }).filter(e => e.isDirectory()).length;
if (dirsN !== nT) { console.error("СТОП: тек на диску " + dirsN + ", тем у маніфесті " + nT); process.exit(1); }

fs.writeFileSync(mfDest, JSON.stringify(out, null, 2) + NL, "utf8");
console.log("написано " + DEST + "/manifest.json   тем " + nT + (had ? "  (було " + hadN + ", додано " + (flat.length - skippedReg) + ")" : "") + "   тек на диску " + dirsN + " ✓");
/* 3. прибрати перенесені теми зі СТАРИХ маніфестів (їх може бути кілька) */
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
const touched = {};
for (const t of flat) { const o = oldTopic(t.from); if (!o) continue;   // уже викинуто попереднім прогоном
  touched[mfOf(t.from)] = 1; o.sec.topics.splice(o.sec.topics.indexOf(o.t), 1); }
for (const mf of Object.keys(touched)) {
  const file = path.join(R, mf), src = fs.readFileSync(file, "utf8");
  const head = src.slice(0, src.indexOf("(window.__BOOKS__"));
  const res = serialize(head, srcCache[mf]);
  const w = { __BOOKS__: [] }; new Function("window", res)(w);
  if (!w.__BOOKS__[0]) { console.error("СТОП " + mf + ": не парситься після правки"); process.exit(1); }
  fs.writeFileSync(file, res, "utf8");
  let n = 0; for (const s of srcCache[mf].sections || []) n += (s.topics || []).length;
  console.log("  старий маніфест " + mf.padEnd(30) + "лишилось тем " + n);
}

/* 4. реєстр + таблиця пар */
const shelfPath = path.join(R, "root/shelf.json");
const shelf = JSON.parse(fs.readFileSync(shelfPath, "utf8"));
const K = shelf.kinds.find(k => k.kind === KIND);
if (K && K.books.indexOf(BOOK) < 0) { K.books.push(BOOK); K.books.sort();
  fs.writeFileSync(shelfPath, JSON.stringify(shelf, null, 2) + NL, "utf8");
  console.log("  реєстр: " + KIND + " <- " + BOOK); }
const lc = path.join(__dirname, "link-changes.json");
const prev = fs.existsSync(lc) ? JSON.parse(fs.readFileSync(lc, "utf8")) : [];
const add = flat.filter(t => t.from.split("/")[1] !== BOOK)
  .map(t => ({ from: t.from.split("/")[1] + "/" + t.slug, to: BOOK + "/" + t.slug, file: "(міграція книги)" }));
if (add.length) { fs.writeFileSync(lc, JSON.stringify(prev.concat(add), null, 2) + NL, "utf8");
  console.log("  пар дописано: " + add.length + " (теми, що змінили книгу)"); }
console.log(NL + "далі: node scripts/linkcheck.js  ·  python scripts/svgcheck.py " + DEST + " --links");
