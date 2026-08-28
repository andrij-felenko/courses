#!/usr/bin/env node
/* ЧЕРГА ДОПИСУВАННЯ — локальна, агентів і токенів НЕ їсть.

   Ужиток:
     node scripts/antigravity/update-queue.js --book <слуг> [--status deeper,update]
                                              [--limit N] [--short-only] [--write]

   ДЕФОЛТ — `deeper,update`, і саме в такому порядку. `deeper` («поглибити») точніший
   за `update` («переписати»): він каже, що текст правильний, але мілкий, — а це рівно
   те, з чим працює цей конвеєр. `update` лишається в дефолті, бо ним теж позначали
   недопис до появи `deeper`.

   Навіщо окремо від write-batch. Той батч працює ТЕМАМИ: тема або написана, або ні.
   Дописування — робота іншої зернистості: у маніфесті статус має КОЖНА версія
   (`basic`, `detailed`) і КОЖНА вставка окремо, тож на дописування може стояти сама
   лише `proj-`-вставка при цілком готовій статті. Черга тому й ФАЙЛОВА: одиниця — це
   один `.md`, а не тека.

   Звідки береться `deeper`. Статус проставляє звірка оцінки з розміром
   (`scripts/levels-actual.js`): агенти дали темі рівень розкриття 1–5, скрипт зміряв
   прозу детальної й переклав обсяг у рівень за тією ж зонною шкалою. Δ ≥ 2 (тема на
   дві зони мілкіша за свою оцінку) → `deeper`. Δ у межах ±1 не чіпають: це допуск.

   Що робить: бере з маніфесту всі одиниці в потрібному статусі, звіряє їх із ДИСКОМ,
   міряє прозу тим самим `proseWords`, що й перевірка 06, дістає рівень розкриття з
   батч-файла прогону й рахує підлогу обсягу. Далі ділить на три купи:

     ДОПИСАТИ  — файл є, але коротший за підлогу свого рівня (головна робота);
     БЕЗ РІВНЯ — темі не проставлено рівень: підлога невідома, спершу фаза оцінки;
     НАПИСАТИ  — статус стоїть, а файлу на диску немає: це письмо, не дописування,
                 і йде воно у write-batch, а не сюди.

   Дефолт кладе в чергу і короткі, і ті, що вже над підлогою: статус `update` міг стояти
   з інших причин (мова, факти, нитка), і їх лікує звичайне коло гейта. `--short-only`
   лишає в черзі САМІ короткі — коли треба тільки дописування й нічого більше.

   Пише `scripts/_finish/_update-<книга>.json` у форматі, який уже читають
   `gate.js --batch` і `finish-batch.js --batch` (обидва беруть `.dir` з елементів
   `topics`), тож окремого перекладача не треба.                                     */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("../lib/manifest7.js");
const L = require("../checks/_lib.js");

const argv = process.argv.slice(2);
const val = (k) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : null; };
const has = (k) => argv.includes(`--${k}`);

const BOOK = val("book");
if (!BOOK) { console.error("Ужиток: node scripts/antigravity/update-queue.js --book <слуг> [--status update] [--limit N] [--short-only] [--write]"); process.exit(L.USAGE); }
const WANT = new Set((val("status") || "deeper,update").split(",").map((s) => s.trim()).filter(Boolean));
const LIMIT = Number(val("limit") || 0) || 0;
const SHORT_ONLY = has("short-only");

const rec = M7.books().get(BOOK);
if (!rec) { console.error(`книги «${BOOK}» немає у root/shelf.json`); process.exit(3); }
const book = M7.loadBook(rec.bookDir);
if (!book) { console.error(`не прочитати маніфест книги ${rec.bookDir}`); process.exit(3); }

/* ── збір одиниць ─────────────────────────────────────────────────────────── */
const units = [];                       // {dir, slug, file, kind, status, group, chapter}
for (const t of M7.allTopics(book)) {
  if (!t.own) continue;                 // ref у курсі власного файлу не має
  const dir = path.join(rec.bookDir, t.slug);
  const add = (file, kind, status) => { if (status && WANT.has(status)) units.push({ dir, slug: t.slug, file, kind, status, group: t.group, chapter: t.chapter, title: t.title }); };
  add(`${t.slug}.md`, "basic", t.node.basic && t.node.basic.status);
  add(`${t.slug}-d.md`, "detailed", t.node.detailed && t.node.detailed.status);
  for (const type of M7.INSERT_TYPES)
    for (const ins of t.node[type] || []) add(ins.file, type, ins.status);
}

/* ── міряння ──────────────────────────────────────────────────────────────── */
const levelCache = new Map();
const levelOf = (dir) => { if (!levelCache.has(dir)) levelCache.set(dir, L.readLevel(dir)); return levelCache.get(dir); };

const grow = [], noLevel = [], missing = [], enough = [];
for (const u of units) {
  const p = path.join(u.dir, u.file);
  if (!fs.existsSync(p)) { missing.push(u); continue; }
  const lv = levelOf(u.dir);
  const level = lv ? (u.kind === "detailed" ? lv.topic : u.kind === "basic" ? null : lv.inserts[u.file]) : undefined;
  const b = L.bandOf(u.kind, level);
  const words = L.proseWords(L.read(p));
  const row = { ...u, words, level: level == null ? null : level, floor: b.floor, hi: b.hi, need: Math.max(0, b.floor - words) };
  /* базова рівня не має — її тримає залізо §3, тож «без рівня» до неї не стосується */
  if (!lv || (u.kind !== "basic" && level == null)) { noLevel.push(row); continue; }
  (row.need > 0 ? grow : enough).push(row);
}

/* ── звіт ─────────────────────────────────────────────────────────────────── */
const nm = (s) => String(s).padStart(5);
console.log(`\n=== ЧЕРГА ДОПИСУВАННЯ: ${BOOK} (${rec.kind}) · статуси: ${[...WANT].join(", ")} ===\n`);
console.log(`одиниць у маніфесті в цих статусах: ${units.length}`);
console.log(`  дописати (коротші за підлогу):  ${grow.length}`);
console.log(`  над підлогою (лише коло гейта): ${enough.length}`);
console.log(`  без рівня (спершу оцінка):      ${noLevel.length}`);
console.log(`  статус є, файлу немає (письмо): ${missing.length}`);

const show = (title, rows, withNeed) => {
  if (!rows.length) return;
  console.log(`\n── ${title} ──`);
  for (const r of rows.slice(0, 200)) {
    const lv = r.level ? `Р${r.level}` : " —";
    console.log(`  ${lv} ${nm(r.words)}w ${withNeed ? `→ ${nm(r.floor)}w (+${nm(r.need)})` : "".padEnd(20)}  ${path.relative(L.ROOT, path.join(r.dir, r.file)).split(path.sep).join("/")}  [${r.kind}/${r.status}]`);
  }
  if (rows.length > 200) console.log(`  … і ще ${rows.length - 200}`);
};
grow.sort((a, b) => b.need - a.need);
show("ДОПИСАТИ — від найбільшого недобору", grow, true);
show("БЕЗ РІВНЯ — підлога невідома, спершу фаза оцінки", noLevel, false);
show("СТАТУС Є, ФАЙЛУ НЕМАЄ — це письмо, не дописування", missing, false);

/* ── черга на диск ────────────────────────────────────────────────────────── */
const pick = SHORT_ONLY ? grow : grow.concat(enough);
const byDir = new Map();
for (const r of pick) {
  if (!byDir.has(r.dir)) byDir.set(r.dir, { dir: path.relative(L.ROOT, r.dir).split(path.sep).join("/"), level: r.level, files: [] });
  byDir.get(r.dir).files.push({ file: r.file, kind: r.kind, status: r.status, words: r.words, level: r.level, floor: r.floor, hi: r.hi, need: r.need });
}
let topics = [...byDir.values()];
/* межа — по ТЕМАХ, бо гейт і суддя працюють текою: половину теми в батч не візьмеш */
topics.sort((a, b) => b.files.reduce((s, f) => s + f.need, 0) - a.files.reduce((s, f) => s + f.need, 0));
if (LIMIT) topics = topics.slice(0, LIMIT);

const out = path.join(L.ROOT, "scripts", "_finish", `_update-${BOOK}.json`);
const payload = { book: BOOK, kind: rec.kind, status: [...WANT], topics };
console.log(`\nу чергу: тем ${topics.length}, файлів ${topics.reduce((s, t) => s + t.files.length, 0)}, недобору ${topics.reduce((s, t) => s + t.files.reduce((x, f) => x + f.need, 0), 0)} слів`);
if (has("write")) {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(payload, null, 2), "utf8");
  console.log(`записано: ${path.relative(L.ROOT, out).split(path.sep).join("/")}`);
  console.log(`той самий файл читають:  node scripts/checks/gate.js --batch ${path.relative(L.ROOT, out).split(path.sep).join("/")}`);
} else {
  console.log(`(чернетка — щоб записати чергу, додай --write)`);
}
if (noLevel.length) console.log(`\n⚠ ${noLevel.length} одиниць без рівня: доки фаза оцінки не проставить рівні, 06-та дасть їм дефект.`);
