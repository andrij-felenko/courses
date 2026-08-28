#!/usr/bin/env node
/* ============================================================================
   manifest-patch.js — детермінований редактор маніфесту. **Схема 7 (JSON).**

   ЩО ЗМІНИЛОСЯ. До переносу маніфест був `.js`-файлом, і цей скрипт правив його
   ТЕКСТ рядок за рядком: шукав межі масивів, стежив за комами, відкочувався, якщо
   результат не перепарсився. Уся та хірургія існувала рівно тому, що редагувати
   код як текст небезпечно. У v7 маніфест — JSON, тож правка стала звичайною:
   розібрати → змінити → серіалізувати. Тому скрипт тепер тонкий і лише перекладає
   аргументи в `scripts/lib/manifest7.js`, де живе єдиний на весь тулінг розбір.

   Ужиток:
     node scripts/manifest-patch.js <книга|шлях-до-manifest.json> --ops <файл.json> [--dry]

   `<книга>` — слуг книги (`sf-apps`, `sys-unix`); теку знайде `shelf.json`.
   Шлях до `manifest.json` теж приймається — для сумісності зі старими викликами.

   ОПЕРАЦІЇ (див. manifest7.applyOps):
     { op:"group",     slug, title, scope? }
     { op:"chapter",   group, slug, title }
     { op:"topic",     group, chapter, slug, title, basic?, detailed?,
                       groupTitle?, groupScope?, chapterTitle? }
     { op:"ref",       group, chapter, ref, title }
     { op:"status",    slug, ver:"basic"|"detailed", status }
     { op:"status-if", slug, ver, from, to }
     { op:"insert",    slug, type:"hist|comp|math|proj|api", file, status }

   ЛЕГАСІ. `op:"section"` приймається як синонім `op:"group"`, а поле `section`
   у `topic`/`insert` — як `group`: старі виклики не падають. Розділ у такому разі
   береться з `chapter`, а нема його — дорівнює групі (тема лягає в однойменний
   розділ, що для книг без внутрішнього поділу правильно).

   ДУБЛІ. Перед заведенням теми друкуємо «⚠ МОЖЛИВІ ДУБЛІ ПОНЯТТЯ» — чотири сигнали
   з `manifest7.dupeHints`. Не блокує: об'єднувати чи ні — рішення людське (§6).
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const M = require("./lib/manifest7.js");

const argv = process.argv.slice(2);
const DRY = argv.includes("--dry");
const val = (n) => { const i = argv.indexOf("--" + n); return i >= 0 ? argv[i + 1] : null; };
const target = argv.find((a) => !a.startsWith("--") && argv[argv.indexOf(a) - 1] !== "--ops");

if (!target || !val("ops")) {
  console.error("Ужиток: node scripts/manifest-patch.js <книга|manifest.json> --ops <файл.json> [--dry]");
  process.exit(3);
}

/* Ціль: слуг книги або шлях до manifest.json (легасі). */
let bookDir = M.bookDirOf(target);
if (!bookDir) {
  const p = path.resolve(target);
  if (/manifest\.json$/i.test(p) && fs.existsSync(p)) bookDir = path.dirname(p);
  else if (fs.existsSync(p) && fs.statSync(p).isDirectory()) bookDir = p;
}
if (!bookDir) { console.error(`нема книги «${target}» у root/ — перевір слуг (root/shelf.json)`); process.exit(3); }

let ops;
try { ops = JSON.parse(fs.readFileSync(val("ops"), "utf8")); }
catch (e) { console.error(`не читається файл операцій: ${e.message}`); process.exit(3); }
if (!Array.isArray(ops)) { console.error("файл операцій має бути МАСИВОМ"); process.exit(3); }

/* Легасі-переклад: section → group; chapter за замовчуванням дорівнює групі. */
const BOOK = path.basename(bookDir);
ops = ops.map((o) => {
  const x = { ...o };
  if (x.op === "section") x.op = "group";
  if (x.section && !x.group) { x.group = x.section; delete x.section; }
  if (x.sectionTitle && !x.groupTitle) x.groupTitle = x.sectionTitle;
  if (x.sectionScope && !x.groupScope) x.groupScope = x.sectionScope;
  if (x.op === "topic" || x.op === "ref") { if (!x.chapter) x.chapter = x.group; if (!x.chapterTitle) x.chapterTitle = x.groupTitle; }
  return x;
});

/* Дублі — до запису, щоб людина побачила їх раніше, ніж тема ляже в маніфест. */
const newTopics = ops.filter((o) => o.op === "topic" && o.slug);
const hints = [];
for (const t of newTopics) for (const h of M.dupeHints(t.slug, BOOK)) hints.push(h);
if (hints.length) {
  console.log(`\n⚠ МОЖЛИВІ ДУБЛІ ПОНЯТТЯ (${hints.length}) — не блокує, але подивись:`);
  hints.slice(0, 30).forEach((h) => console.log(`   • ${h}`));
  console.log(`   Те саме поняття — не заводь тему, допиши наявну.`);
  console.log(`   Схоже, але РІЗНЕ — заводь, і дай ОБОМ точніші назви (§6).`);
}

const rep = M.applyOps(bookDir, ops, { dry: DRY });

console.log(`\n${DRY ? "DRY — нічого не записано" : "ЗАПИСАНО"}: ${path.relative(process.cwd(), path.join(bookDir, "manifest.json"))}`);
console.log(`  груп +${rep.group || 0} · розділів +${rep.chapter || 0} · тем +${rep.topic || 0} · ref +${rep.ref || 0} · статусів ${rep.status || 0} · вставок ${rep.insert || 0} · знято ${rep.removed || 0} · перекладено ${rep.moved || 0} · перейменовано ${rep.retitled || 0}`)
if ((rep.skipped || []).length) {
  console.log(`  пропущено (уже так): ${rep.skipped.length}`);
  rep.skipped.slice(0, 12).forEach((s) => console.log(`     · ${s}`));
}
if ((rep.errors || []).length) {
  console.error(`\n✖ помилок ${rep.errors.length} — нічого не змінено`);
  rep.errors.forEach((e) => console.error(`     ✖ ${e}`));
  process.exit(4);
}
