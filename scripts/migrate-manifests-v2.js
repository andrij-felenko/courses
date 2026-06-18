/* scripts/migrate-manifests-v2.js — міграція book-маніфестів під схему AUTHORING.md §2.
   - status готових файлів (done/deeper/update) → recheck; empty лишається empty.
   - histories[] → hist:[{file,status}]; extras[] → comp/math/proj за префіксом, {file,status}.
   - origin зберігається; guide-маніфести не чіпаються.
   Запуск: node scripts/migrate-manifests-v2.js            (запис)
           node scripts/migrate-manifests-v2.js --dry      (лише звіт) */
const fs = require("fs");
const path = require("path");

const DRY = process.argv.includes("--dry");
const ROOT = path.resolve(__dirname, "..");
const J = (v) => JSON.stringify(v);

function loadBooks(src) {
  const fn = new Function("window", src + "\nreturn window.__BOOKS__ || [];");
  return fn({});
}

function insertStatus() { return "recheck"; }

function splitExtras(extras, bucket) {
  for (const f of extras || []) {
    const pfx = String(f).split("-")[0];
    const kind = (pfx === "comp" || pfx === "math" || pfx === "proj") ? pfx : null;
    if (kind) bucket[kind].push({ file: f, status: insertStatus() });
    else { bucket._leftover.push(f); }
  }
}

function migrateTopic(t, stats) {
  // статус
  if (t.status && t.status !== "empty") { if (t.status !== "recheck") stats.toRecheck++; t.status = "recheck"; }

  const bucket = { comp: [], math: [], proj: [], _leftover: [] };
  // hist
  let hist = [];
  if (Array.isArray(t.hist)) hist = t.hist.map((o) => (typeof o === "string" ? { file: o, status: insertStatus() } : o));
  if (Array.isArray(t.histories)) hist = hist.concat(t.histories.map((f) => ({ file: f, status: insertStatus() })));
  // comp/math/proj уже в новій схемі — зберегти
  for (const k of ["comp", "math", "proj"]) if (Array.isArray(t[k])) for (const o of t[k]) bucket[k].push(typeof o === "string" ? { file: o, status: insertStatus() } : o);
  // extras → розкласти
  splitExtras(t.extras, bucket);

  // зібрати тему в канонічному порядку
  const out = { slug: t.slug, title: t.title };
  if (t.status !== undefined) out.status = t.status;
  if (t.levels !== undefined) out.levels = t.levels;
  if (t.origin !== undefined) out.origin = t.origin;
  if (hist.length) { out.hist = hist; stats.inserts += hist.length; }
  for (const k of ["comp", "math", "proj"]) if (bucket[k].length) { out[k] = bucket[k]; stats.inserts += bucket[k].length; }
  if (bucket._leftover.length) { out.extras = bucket._leftover; stats.leftover += bucket._leftover.length; }
  // невідомі ключі — зберегти
  const known = ["slug", "title", "status", "levels", "origin", "hist", "comp", "math", "proj", "histories", "extras"];
  for (const k of Object.keys(t)) if (!known.includes(k)) out[k] = t[k];
  return out;
}

function inlineInserts(arr) {
  return "[" + arr.map((o) => `{ file: ${J(o.file)}, status: ${J(o.status)} }`).join(", ") + "]";
}
function printTopic(t) {
  const p = [`slug: ${J(t.slug)}`, `title: ${J(t.title)}`];
  if (t.status !== undefined) p.push(`status: ${J(t.status)}`);
  if (t.levels !== undefined) p.push(`levels: [${t.levels.map(J).join(", ")}]`);
  if (t.origin !== undefined) p.push(`origin: ${J(t.origin)}`);
  for (const k of ["hist", "comp", "math", "proj"]) if (t[k]) p.push(`${k}: ${inlineInserts(t[k])}`);
  if (t.extras) p.push(`extras: [${t.extras.map(J).join(", ")}]`);
  const known = ["slug", "title", "status", "levels", "origin", "hist", "comp", "math", "proj", "extras"];
  for (const k of Object.keys(t)) if (!known.includes(k)) p.push(`${k}: ${J(t[k])}`);
  return `{ ${p.join(", ")} }`;
}
function printBook(b) {
  let s = "";
  s += `/* book/${b.slug}/manifest.js — книга-предмет «${b.title}» (тип "${b.type}").\n`;
  s += `   Схема — AUTHORING.md §2: { type, slug, title, sections:[ {slug,title,scope, topics:[ {slug,title,status,levels,origin, hist/comp/math/proj:[{file,status}]} ]} ] }\n`;
  s += `   Статуси: done | empty | update | deeper | recheck. */\n`;
  s += `(window.__BOOKS__ = window.__BOOKS__ || []).push({\n`;
  s += `  type: ${J(b.type)}, slug: ${J(b.slug)}, title: ${J(b.title)},\n`;
  s += `  sections: [\n`;
  for (const sec of b.sections || []) {
    s += `    { slug: ${J(sec.slug)}, title: ${J(sec.title)}, scope: ${J(sec.scope)},\n`;
    s += `      topics: [\n`;
    for (const t of sec.topics || []) s += `        ${printTopic(t)},\n`;
    s += `      ] },\n`;
  }
  s += `  ]\n});\n`;
  return s;
}

const files = fs.readdirSync(path.join(ROOT, "book")).map((d) => path.join(ROOT, "book", d, "manifest.js")).filter((f) => fs.existsSync(f));
let total = { toRecheck: 0, inserts: 0, leftover: 0, topics: 0 };
for (const f of files) {
  const src = fs.readFileSync(f, "utf8");
  const books = loadBooks(src);
  const stats = { toRecheck: 0, inserts: 0, leftover: 0 };
  for (const b of books) for (const sec of b.sections || []) { sec.topics = (sec.topics || []).map((t) => migrateTopic(t, stats)); total.topics += sec.topics.length; }
  const out = books.map(printBook).join("\n");
  total.toRecheck += stats.toRecheck; total.inserts += stats.inserts; total.leftover += stats.leftover;
  console.log(`${path.relative(ROOT, f)}: →recheck ${stats.toRecheck}, вставок ${stats.inserts}${stats.leftover ? `, LEFTOVER ${stats.leftover}` : ""}`);
  if (!DRY) fs.writeFileSync(f, out, "utf8");
}
console.log(`\nРАЗОМ: тем ${total.topics}, →recheck ${total.toRecheck}, вставок ${total.inserts}, нерозкладених extras ${total.leftover}${DRY ? "  (DRY — без запису)" : "  (записано)"}`);
