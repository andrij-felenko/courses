/* ⚠️ ЛЕГАСІ КАМПАНІЇ RECHECK (завершена 2026-07-25). Читає ПРИБРАНЕ дерево v6
   (book/ + guide/ + catalog/ + manifest.js із window.__BOOKS__), тож на дереві v7
   не працює — не запускай, доки не переписано. Живий конвеєр ревізії сьогодні:
   review-batch.js → review-queue.js → review-apply.js. */
/* scripts/claude/recheck-build.js — генерує самодостатній воркфлоу scripts/claude/recheck-run.js
   із ВБУДОВАНИМ батчем (обхід ліміту розміру args воркфлоу-тулзи).
   Запуск:
     node scripts/claude/recheck-build.js <book> [start=0] [count=5]          // черга recheck однієї книги, у порядку маніфесту
     node scripts/claude/recheck-build.js guide:<slug> [start=0] [count=10]   // у порядку КРОКІВ курсу (ref→book-тема), лише recheck, без дублів
   Потім:   Workflow scriptPath="scripts/claude/recheck-run.js"  (БЕЗ args). */
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const target = process.argv[2] || "algorithms";        // "<book>"  або  "guide:<slug>"
const start = parseInt(process.argv[3] || "0", 10);
const count = parseInt(process.argv[4] || (target.startsWith("guide:") ? "10" : "5"), 10);

const raw = execFileSync("node", [path.join(__dirname, "recheck-index.js")], { encoding: "utf8", maxBuffer: 1 << 26 });
const d = JSON.parse(raw);   // { index, titles, sections, lookup, queue(усі книги) }

let label, fullQueue, unresolved = [], skipped = {};

if (target.startsWith("guide:")) {
  const gslug = target.slice("guide:".length);
  const mf = path.join(ROOT, "guide", gslug, "manifest.js");
  if (!fs.existsSync(mf)) { console.error(`Курс не знайдено: ${mf}`); process.exit(2); }
  const sb = { window: {} }; vm.createContext(sb); vm.runInContext(fs.readFileSync(mf, "utf8"), sb, { filename: mf });
  const g = (sb.window.__GUIDES__ || []).find(x => x.slug === gslug) || (sb.window.__GUIDES__ || [])[0];
  if (!g) { console.error(`У ${mf} немає __GUIDES__`); process.exit(2); }
  label = "guide-" + gslug;
  const seen = new Set();
  fullQueue = [];
  for (const m of g.modules || []) for (const c of m.chapters || []) for (const s of c.steps || []) {
    if (!s.ref) continue;                                  // bridge-кроки тут відсутні; ref = "<book>/<section>/<slug>"
    const rec = d.lookup[s.ref];
    if (!rec) { unresolved.push(s.ref); continue; }        // битий ref (не резолвиться у book-тему)
    if (rec.status !== "recheck") { skipped[rec.status] = (skipped[rec.status] || 0) + 1; continue; }
    if (seen.has(s.ref)) continue;                         // курс може посилатися на тему двічі — аудит один раз
    seen.add(s.ref);
    fullQueue.push(rec);
  }
} else if (target.startsWith("tree:")) {
  // ОБХІД ГРАФА book:-лінків від сіда (BFS): збираємо найближчі recheck-теми по лінк-відстані.
  // Проходимо КРІЗЬ done (читаємо їхні лінки), пропускаємо empty (нема файлу/лінків). Дублі — раз.
  const seed = target.slice("tree:".length);
  const bySlug = {};                                          // book -> slug -> rec
  for (const k in d.lookup) { const r = d.lookup[k]; (bySlug[r.book] = bySlug[r.book] || {})[r.slug] = r; }
  const segs = seed.split("/").filter(Boolean);
  let seedRec = segs.length >= 3 ? d.lookup[seed] : (bySlug[segs[0]] || {})[segs[1]];
  if (!seedRec) { console.error(`Сід не знайдено: ${seed} (формат tree:<book>/<slug> або tree:<book>/<section>/<slug>)`); process.exit(2); }
  const reLink = /book:([a-z][a-z0-9-]*)\/([a-z0-9][a-z0-9-]*)/gi;
  const outLinks = (rec) => {
    const dir = path.join(ROOT, "book", rec.book, rec.section, rec.slug);
    const files = [rec.slug + ".md", ...["hist", "comp", "math", "proj"].flatMap(t => (rec.inserts && rec.inserts[t] || []).map(x => x.file))];
    const edges = [];
    for (const f of files) {
      const p = path.join(dir, f);
      if (!fs.existsSync(p)) continue;
      const txt = fs.readFileSync(p, "utf8"); let m;
      while ((m = reLink.exec(txt))) edges.push([m[1].toLowerCase(), m[2].toLowerCase()]);
    }
    return edges;
  };
  label = "tree-" + seedRec.slug;
  const seen = new Set([seedRec.book + "/" + seedRec.slug]); const q = [seedRec]; fullQueue = [];
  while (q.length && fullQueue.length < count) {
    const cur = q.shift();
    if (cur.status === "recheck") fullQueue.push(cur);        // збираємо лише recheck
    else skipped[cur.status] = (skipped[cur.status] || 0) + 1;
    if (cur.status === "empty") continue;                     // empty — нема файлу, лінків не читаємо
    for (const [bk, sl] of outLinks(cur)) {
      const key = bk + "/" + sl;
      if (seen.has(key)) continue; seen.add(key);
      const rec = (bySlug[bk] || {})[sl];
      if (!rec) { unresolved.push(key); continue; }
      q.push(rec);
    }
  }
} else if (target.startsWith("course:")) {
  // BFS по графу book:-лінків, ПРИВ'ЯЗАНИЙ до порядку курсу (зовнішній цикл — кроки guide).
  // Від кожного крока курсу — черга (FIFO) рівень-за-рівнем: тема → її лінк-цілі → їхні → … (кільцями).
  // Кожну тему ВІДВІДУЄМО раз (done/empty — роутери; recheck ЩЕ Й збираємо в порядку BFS).
  // Піддерево вичерпали → наступний крок курсу. empty — лист. Відсутні цілі — в unresolved.
  const _ct = target.slice("course:".length).split("@");      // course:<guide>[@status1,status2]
  const gslug = _ct[0];
  const COLLECT = _ct[1] ? _ct[1].split(",") : null;           // фільтр збору (null=усі non-done); обхід проходить усе одно
  const gmf = path.join(ROOT, "guide", gslug, "manifest.js");
  if (!fs.existsSync(gmf)) { console.error(`Курс не знайдено: ${gmf}`); process.exit(2); }
  const gsb = { window: {} }; vm.createContext(gsb); vm.runInContext(fs.readFileSync(gmf, "utf8"), gsb, { filename: gmf });
  const g = (gsb.window.__GUIDES__ || []).find(x => x.slug === gslug) || (gsb.window.__GUIDES__ || [])[0];
  if (!g) { console.error(`У ${gmf} немає __GUIDES__`); process.exit(2); }
  label = "course-" + gslug;
  const bySlug = {};
  for (const k in d.lookup) { const r = d.lookup[k]; (bySlug[r.book] = bySlug[r.book] || {})[r.slug] = r; }
  const reLink = /book:([a-z][a-z0-9-]*)\/([a-z0-9][a-z0-9-]*)/gi;
  const outRefs = (rec) => {
    const dir = path.join(ROOT, "book", rec.book, rec.section, rec.slug);
    const files = [rec.slug + ".md", ...["hist", "comp", "math", "proj"].flatMap(t => (rec.inserts && rec.inserts[t] || []).map(x => x.file))];
    const out = [];
    for (const f of files) {
      const p = path.join(dir, f); if (!fs.existsSync(p)) continue;
      const txt = fs.readFileSync(p, "utf8"); let m;
      while ((m = reLink.exec(txt))) out.push([m[1].toLowerCase(), m[2].toLowerCase()]);
    }
    return out;
  };
  const visited = new Set(); fullQueue = [];
  const bfsFrom = (startKey) => {
    const q = [startKey];
    while (q.length) {
      const key = q.shift();                                  // FIFO → BFS рівнями
      if (visited.has(key)) continue; visited.add(key);
      const rec = d.lookup[key]; if (!rec) continue;
      if (rec.status !== "done" && (!COLLECT || COLLECT.includes(rec.status))) fullQueue.push(rec);
      else skipped[rec.status] = (skipped[rec.status] || 0) + 1;
      if (rec.status === "empty") continue;                   // empty — ще нема файлу, лінків не читаємо (підхопимо після написання)
      for (const [bk, sl] of outRefs(rec)) {
        const r2 = (bySlug[bk] || {})[sl];
        if (!r2) { unresolved.push(bk + "/" + sl); continue; } // ціль-лінк не існує як тема
        const k2 = r2.book + "/" + r2.section + "/" + r2.slug;
        if (!visited.has(k2)) q.push(k2);                     // у ХВІСТ → кільце нижче
      }
    }
  };
  for (const m of g.modules || []) for (const c of m.chapters || []) for (const st of c.steps || []) if (st.ref && !visited.has(st.ref)) bfsFrom(st.ref);
} else {
  label = target;
  fullQueue = d.queue[target] || [];
}

const topics = fullQueue.slice(start, start + count);
if (!topics.length) { console.error(`Немає recheck-тем для "${target}" з offset ${start} (черга ${fullQueue.length}).`); process.exit(2); }

const CANON_TXT = fs.readFileSync(path.join(ROOT, "AUTHORING.md"), "utf8");   // читаю канон САМ, передаю агентам зібраним
const EMBED = { book: label, topics, index: d.index, canon: CANON_TXT };
const tmpl = fs.readFileSync(path.join(__dirname, "recheck-audit.js"), "utf8");
if (!tmpl.includes("/*__EMBED__*/")) { console.error("У шаблоні recheck-audit.js немає маркера /*__EMBED__*/"); process.exit(3); }
fs.writeFileSync(path.join(__dirname, "recheck-run.js"), tmpl.replace("/*__EMBED__*/", "const EMBED = " + JSON.stringify(EMBED) + ";"));

console.log(`wrote scripts/claude/recheck-run.js — target=${target} start=${start} count=${topics.length} (recheck-черга всього ${fullQueue.length})`);
if (Object.keys(skipped).length) console.log("пропущено non-recheck ref-цілей:", JSON.stringify(skipped));
if (unresolved.length) console.log(`UNRESOLVED ref-ів: ${unresolved.length}; напр.: ${unresolved.slice(0, 6).join(", ")}`);
console.log("батч:\n  " + topics.map((t, i) => `${start + i}. ${t.book}/${t.section}/${t.slug} — «${t.title}»`).join("\n  "));
