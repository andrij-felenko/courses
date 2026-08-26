/* ⚠️ ЛЕГАСІ КАМПАНІЇ RECHECK (завершена 2026-07-25). Читає ПРИБРАНЕ дерево v6
   (book/ + guide/ + catalog/ + manifest.js із window.__BOOKS__), тож на дереві v7
   не працює — не запускай, доки не переписано. Живий конвеєр ревізії сьогодні:
   review-batch.js → review-queue.js → review-apply.js. */
/* scripts/claude/recheck-apply.js — застосовує рішення воркфлоу до book-маніфестів (статуси topic+вставок, levels).
   Запуск:  node scripts/claude/recheck-apply.js <runFile.js> <output.json>
     runFile  — scripts/claude/recheck-run.js (EMBED.topics: [{book,section,slug,inserts}], у ТОМУ Ж порядку, що й reports)
     output   — JSON воркфлоу (result.reports[], той самий порядок)
   Працює ЛІНІЙНО по рядках маніфесту, ключ — унікальний origin теми (тож дублікати slug не плутаються).
   Нічого не пише, доки всі рішення не зматчено; наприкінці — node-check-сумісний результат. */
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const ROOT = path.resolve(__dirname, "..");

const runFile = process.argv[2], outFile = process.argv[3];
if (!runFile || !outFile) { console.error("usage: node scripts/claude/recheck-apply.js <runFile.js> <output.json>"); process.exit(1); }

// EMBED.topics із run-файлу
const runSrc = fs.readFileSync(runFile, "utf8");
const m = runSrc.match(/const EMBED = (\{[\s\S]*?\});\s*\n/);
if (!m) { console.error("не знайшов EMBED у " + runFile); process.exit(2); }
const EMBED = JSON.parse(m[1]);
const topics = EMBED.topics || [];

// reports
const out = JSON.parse(fs.readFileSync(outFile, "utf8"));
const reports = (out.result && out.result.reports) || out.reports || [];

// МАТЧ ЗА SLUG (не за позицією) — стійко до впалих агентів, яких .filter(Boolean) прибрав зі звіту
const repBySlug = {};
for (const r of reports) { const s = String(r.slug).split("/").pop(); (repBySlug[s] = repBySlug[s] || []).push(r); }

// origin кожної теми — з ЖИВОГО маніфесту (section+slug унікальні)
function parseBook(book) {
  const mf = path.join(ROOT, "book", book, "manifest.js");
  const sb = { window: {} }; vm.createContext(sb); vm.runInContext(fs.readFileSync(mf, "utf8"), sb, { filename: mf });
  const b = (sb.window.__BOOKS__ || [])[0];
  const map = {};
  for (const sec of b.sections || []) for (const t of sec.topics || []) map[sec.slug + "/" + t.slug] = t;
  return map;
}
const bookMaps = {};

const decisions = [], skipped = [];
for (const t of topics) {
  const cand = repBySlug[t.slug] || [];
  if (cand.length === 0) { skipped.push(`${t.book}/${t.slug}`); continue; }       // агент впав → лишаємо recheck
  if (cand.length > 1) console.warn(`⚠ ${t.slug}: ${cand.length} звітів — беру перший`);
  const r = cand[0];
  bookMaps[t.book] = bookMaps[t.book] || parseBook(t.book);
  const to = bookMaps[t.book][t.section + "/" + t.slug];
  if (!to) { console.error(`✗ не знайшов у маніфесті: ${t.book}/${t.section}/${t.slug}`); process.exit(3); }
  // мапа вставка-файл → статус (зі звіту); незгадані лишаємо як є й попереджаємо
  const insMap = {};
  for (const ia of r.insertsAudited || []) insMap[ia.file] = ia.proposedStatus;
  const registered = ["hist", "comp", "math", "proj"].flatMap(k => (to[k] || []).map(x => x.file));
  for (const f of registered) if (!(f in insMap)) { insMap[f] = "done"; console.warn(`⚠ ${t.slug}: вставку ${f} не згадано у звіті → ставлю done`); }
  decisions.push({ book: t.book, slug: t.slug, origin: to.origin, status: r.proposedStatus, hasLevels: !!to.levels, inserts: insMap });
}

// застосувати по книгах, лінійно по рядках
const byBook = {};
for (const d of decisions) (byBook[d.book] = byBook[d.book] || []).push(d);

let totalTopics = 0, totalInserts = 0;
for (const [book, ds] of Object.entries(byBook)) {
  const mf = path.join(ROOT, "book", book, "manifest.js");
  let lines = fs.readFileSync(mf, "utf8").split("\n");
  for (const d of ds) {
    const idx = lines.findIndex(L => L.includes(`origin: "${d.origin}"`) && L.includes(`slug: "${d.slug}"`));
    if (idx < 0) { console.error(`✗ рядок не знайдено: ${book} ${d.slug} (origin ${d.origin})`); process.exit(4); }
    let L = lines[idx];
    // topic status (+ levels, якщо ще нема) — лише ПЕРШЕ "recheck" (це статус теми, перед origin)
    if (d.hasLevels) L = L.replace('status: "recheck"', `status: "${d.status}"`);
    else L = L.replace('status: "recheck", origin:', `status: "${d.status}", levels: ["basic"], origin:`);
    totalTopics++;
    // вставки — кожна за іменем файлу
    for (const [file, st] of Object.entries(d.inserts)) {
      const before = L;
      L = L.replace(`file: "${file}", status: "recheck"`, `file: "${file}", status: "${st}"`);
      if (L !== before) totalInserts++;
    }
    lines[idx] = L;
  }
  fs.writeFileSync(mf, lines.join("\n"));
  console.log(`✓ ${book}: ${ds.length} тем оновлено`);
}
console.log(`Разом: ${totalTopics} тем, ${totalInserts} вставок.`);
if (skipped.length) console.log(`⚠ ПРОПУЩЕНО (немає звіту, лишаються recheck): ${skipped.join(", ")}`);
