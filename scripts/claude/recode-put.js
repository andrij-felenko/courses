#!/usr/bin/env node
/* Розкладка проєктів із payload-ів: один прохід замість сотень кругів генерації.
   Ужиток: node scripts/claude/recode-put.js --batch scripts/_finish/_recode-<книга>.json [--apply]
           node scripts/claude/recode-put.js --batch … --json        # машинний звіт

   НАВІЩО. Заміряно на двох прогонах поспіль: 872 ходи агентів, у КОЖНОМУ рівно один
   виклик інструмента (розподіл `1→417` і `1→455`, жодного ходу з двома). Інструкція
   «клади файли пачками» не спрацювала ЖОДНОГО разу — модель у цьому режимі так не
   пише. Кожен Write означав повний круг генерації з пересиланням усього контексту,
   а 139 Write + 91 Edit це 55% усіх кругів прогону.

   Тому писати перестав агент. Він віддає всю розкладку ОДНИМ файлом-payload-ом, а
   розкладає її оцей скрипт — локально, за нуль токенів.

   ФОРМАТ PAYLOAD-а (`scripts/_finish/_recode-put/<slug>__<база>.txt`):

       ### FILE: c/main.c
       #include <stdio.h>
       …
       ### FILE: cpp/src/vm.cpp
       …

   Роздільниками, а не JSON-ом, свідомо: код лягає як є, без екранування лапок і
   без `\n` замість переводів рядка. На проєкті в кілька сотень рядків це і зайві
   токени, і реальний шанс обірваного виводу. JSON (`.json`, `{files:[…]}`) теж
   приймається — на випадок, якщо агент віддав саме його.

   Шлях — ВІД теки проєкту (`<тема>/<база>/`), з прямими скісними. Перший сегмент
   мусить бути текою мови (`c`, `cpp`, `py`, `rs`, …): платформа лягає ПІД мову
   (`c/esp-idf/`), і тека мови лишається чесною для перевірки пари c/↔cpp/.

   ⛔ ЧИСТКА. Наявний код — чернетка механічного виносу, і розкладка його ЗАМІНЮЄ, а
   не сусідить із ним. Тому теки мов, названі в payload-і, спершу зносяться. Зноситься
   РІВНО тека проєкту цього .md і нічого поза нею: кожен шлях перевіряється на вихід
   за межі, і юніт без payload-а не чіпається взагалі.                                */
"use strict";
const fs = require("fs");
const path = require("path");
const L = require("../checks/_lib.js");

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const has = (k) => argv.includes(k);

const BATCH = arg("--batch", "");
const PUTDIR = arg("--dir", path.join("scripts", "_finish", "_recode-put"));
const APPLY = has("--apply");
if (!BATCH) { console.error("треба --batch <файл черги>"); process.exit(2); }

let units = [];
try { units = JSON.parse(fs.readFileSync(BATCH, "utf8")); }
catch (e) { console.error("не читається черга: " + e.message); process.exit(2); }

const payloadBase = (u) => `${u.slug}__${path.basename(u.file, ".md")}`;

/* Два формати, обидва законні.
   · РОЗДІЛЬНИКАМИ (`.txt`) — основний, бо код лягає як є: ні екранування лапок,
     ні `\n` замість переводів рядка. На файлі в 300 рядків JSON-екранування це
     і зайві токени, і реальний шанс обірваного чи побитого виводу.
   · JSON (`.json`) — коли агент усе-таки віддав {files:[{path,content}]}.
   Роздільник мусить стояти З ПОЧАТКУ рядка: усередині коду такий рядок не
   трапляється, а зміщений на пробіл — це вже просто текст.                     */
const MARK = /^### FILE:[ \t]*(.+?)[ \t]*$/;
function parsePayload(txt) {
  const t = txt.replace(/^﻿/, "");
  if (/^\s*\{/.test(t)) {
    const o = JSON.parse(t);
    return Array.isArray(o && o.files) && o.files.length ? o.files : null;
  }
  const out = [];
  let cur = null;
  for (const ln of t.replace(/\r\n?/g, "\n").split("\n")) {
    const m = ln.match(MARK);
    if (m) { cur = { path: m[1], body: [] }; out.push(cur); continue; }
    if (cur) cur.body.push(ln);
  }
  if (!out.length) return null;
  return out.map((f) => ({ path: f.path, content: f.body.join("\n").replace(/^\n+/, "").replace(/\s+$/, "") + "\n" }));
}

/* Шлях мусить лишитися ВСЕРЕДИНІ теки проєкту. Порожній, абсолютний, з диском,
   із `..` або з першим сегментом-не-мовою — не приймається.                    */
function badPath(rel) {
  if (!rel || typeof rel !== "string") return "порожній шлях";
  const p = rel.replace(/\\/g, "/").trim();
  if (!p) return "порожній шлях";
  if (p.startsWith("/") || /^[A-Za-z]:/.test(p)) return "абсолютний шлях";
  const segs = p.split("/").filter(Boolean);
  if (segs.some((s) => s === "." || s === "..")) return "вихід за межі теки проєкту";
  if (segs.length < 2) return "нема теки мови: шлях мусить починатися з <мова>/";
  if (!L.DIR_TIER[segs[0]]) return `перший сегмент «${segs[0]}» не є текою мови`;
  return null;
}

const rmrf = (p) => { try { fs.rmSync(p, { recursive: true, force: true }); } catch {} };

const rows = [];
for (const u of units) {
  const base = payloadBase(u);
  const pf = [".txt", ".json"].map((e) => path.join(PUTDIR, base + e)).find((p) => fs.existsSync(p));
  const row = { slug: u.slug, file: u.file, payload: pf ? path.relative(process.cwd(), pf).replace(/\\/g, "/") : `${PUTDIR}/${base}.txt`, wrote: 0, langs: [], problems: [] };

  if (!pf) { row.problems.push("payload-а немає — юніт не чіпаємо"); rows.push(row); continue; }

  let files = null;
  try { files = parsePayload(fs.readFileSync(pf, "utf8")); }
  catch (e) { row.problems.push("payload не читається: " + e.message); rows.push(row); continue; }

  if (!files) { row.problems.push("у payload-і не знайдено жодного «### FILE: <шлях>»"); rows.push(row); continue; }

  /* Тека проєкту рахується з ЧЕРГИ, не з payload-а: агент не має права
     перенаправити запис в іншу тему, навіть помилково.                */
  const projDir = L.projectDir(u.dir, u.file);

  const ok = [];
  for (const f of files) {
    const why = badPath(f && f.path);
    if (why) { row.problems.push(`${(f && f.path) || "?"}: ${why}`); continue; }
    if (typeof f.content !== "string" || !f.content.trim()) { row.problems.push(`${f.path}: порожній вміст`); continue; }
    const rel = f.path.replace(/\\/g, "/");
    const abs = path.resolve(projDir, rel);
    if (path.relative(path.resolve(projDir), abs).startsWith("..")) { row.problems.push(`${rel}: вихід за межі теки проєкту`); continue; }
    ok.push({ rel, abs, content: f.content, lang: rel.split("/")[0] });
  }
  if (!ok.length) { row.problems.push("жодного придатного файла — нічого не пишемо"); rows.push(row); continue; }

  row.langs = [...new Set(ok.map((f) => f.lang))].sort();

  if (APPLY) {
    /* Зносимо лише ті теки мов, які payload справді заміщає: мова, якої в payload-і
       немає, лишається як була — це не «неповна розкладка», а свідомий вибір автора. */
    for (const lang of row.langs) rmrf(path.join(projDir, lang));
    for (const f of ok) {
      fs.mkdirSync(path.dirname(f.abs), { recursive: true });
      fs.writeFileSync(f.abs, f.content.replace(/\r\n?/g, "\n"), "utf8");
    }
    row.wrote = ok.length;
  } else row.wrote = ok.length;

  rows.push(row);
}

if (has("--json")) {
  const bad = rows.filter((r) => r.problems.length).length;
  console.log(JSON.stringify({ total: rows.length, applied: APPLY, withProblems: bad, wrote: rows.reduce((a, r) => a + (APPLY ? r.wrote : 0), 0), rows }, null, 1));
  process.exit(0);
}

const done = rows.filter((r) => r.wrote && !r.problems.length).length;
console.log(`\n=== РОЗКЛАДКА === ${APPLY ? "записано" : "СУХИЙ ПРОГІН"}: ${done} з ${rows.length} юнітів чисті\n`);
for (const r of rows) {
  const mark = r.problems.length ? (r.wrote ? "▽" : "✖") : "✓";
  console.log(`  ${mark} ${r.slug}/${r.file}  ${r.wrote} файлів  ${r.langs.join("+") || "—"}`);
  for (const p of r.problems) console.log(`        ← ${p}`);
}
if (!APPLY) console.log("\n(додай --apply, щоб справді записати)");
const nothing = rows.filter((r) => !r.wrote).length;
process.exit(nothing ? 1 : 0);
