#!/usr/bin/env node
/* ============================================================================
   verdict.js — агент записує ВИРОК на пункт перевірки. Без доказу не приймає.

   Ужиток:
     node scripts/checks/verdict.js <NN> <тека> --item <N> --status ok|defect --proof "<доказ>"
     node scripts/checks/verdict.js <NN> <тека> --list        (показати пункти й наявні вироки)
     node scripts/checks/verdict.js <NN> <тека> --clear <N>   (зняти свій вирок, якщо помилився)

   ЩО ТАКЕ ДОКАЗ: цитата з файлу з номером рядка · перерахунок · назва джерела й що
   в ньому сказано · дослівний рядок виводу команди. Не доказ: «перевірено»,
   «усе гаразд», «виглядає правильно», «100% PERFECT» — такі вироки відкидаються.

   Вирок прив'язаний до ТЕКСТУ пункту. Змінили текст — вирок протух і питається
   наново. Саме це не дає конвеєрові зациклитись і водночас не дає «замести».
   ========================================================================== */
"use strict";
const fs = require("fs");
const L = require("./_lib.js");

const argv = process.argv.slice(2);
const CHECK = (argv[0] || "").padStart(2, "0");
const DIR = L.resolveDir(argv[1]);
const flag = (name) => { const i = argv.indexOf("--" + name); return i >= 0 ? argv[i + 1] : null; };
const has = (name) => argv.includes("--" + name);

if (!/^\d\d$/.test(CHECK) || !DIR) {
  console.error('Ужиток: node scripts/checks/verdict.js <NN> <тека> --item <N> --status ok|defect --proof "<доказ>"');
  process.exit(L.USAGE);
}

const items = L.loadItems(DIR, CHECK);
if (!items.length) {
  console.error(`Спершу прожени саму перевірку: node scripts/checks/${CHECK}-*.js "${DIR}"`);
  process.exit(L.USAGE);
}
const V = L.loadVerdicts(DIR, CHECK);

if (has("list")) {
  console.log(`\nпункти перевірки ${CHECK} у ${DIR}:`);
  items.forEach((e) => {
    const v = V[e.key];
    console.log(`  [${e.n}] ${v ? (v.status === "ok" ? "✓ ok    " : "✖ defect") : "· без вироку"}  ${e.file}: ${e.text.slice(0, 120)}`);
    if (v) console.log(`        доказ: ${v.proof}`);
  });
  process.exit(0);
}

if (has("clear")) {
  const n = Number(flag("clear"));
  const it = items.find((e) => e.n === n);
  if (!it) { console.error(`нема пункту ${n}`); process.exit(L.USAGE); }
  delete V[it.key];
  L.saveVerdicts(DIR, CHECK, V);
  console.log(`вирок на пункт ${n} знято`);
  process.exit(0);
}

/* ── кілька вироків за ОДИН виклик ──────────────────────────────────────────
   Судді кладуть по 10–20 вироків на тему, і кожен окремий запуск — це окремий
   виклик інструмента з окремою відповіддю. Тепер приймаємо серію трійок:
     --item 1 --status ok --proof "…"  --item 2 --status defect --proof "…"
   Порядок прапорців зберігається, групи ріжемо по кожному --item. Один --item
   працює так само, як працював, — старі промпти нічого не помічають.          */
const groups = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] !== "--item") continue;
  const g = { n: Number(argv[i + 1]) };
  for (let j = i + 2; j < argv.length && argv[j] !== "--item"; j++) {
    if (argv[j] === "--status") g.status = argv[j + 1];
    if (argv[j] === "--proof") g.proof = argv[j + 1];
  }
  groups.push(g);
}
if (!groups.length) { console.error("треба --item <N> --status ok|defect --proof \"<доказ>\""); process.exit(L.USAGE); }

/* гейт доказу — механічний, щоб «перевірено» не проходило */
const EMPTY = /^(перевірено|усе гаразд|все гаразд|ок|ok|добре|виглядає правильно|100%.*|perfect.*|чисто)\.?$/i;
const bad = [];
for (const g of groups) {
  const it = items.find((e) => e.n === g.n);
  if (!it) bad.push(`пункт ${g.n}: такого немає (є 1..${items.length})`);
  else if (g.status !== "ok" && g.status !== "defect") bad.push(`пункт ${g.n}: --status має бути ok або defect`);
  else if (!g.proof || g.proof.trim().length < 25 || EMPTY.test(g.proof.trim())) bad.push(`пункт ${g.n}: доказ порожній або надто короткий`);
  else g.it = it;
}
if (bad.length) {
  console.error("ВИРОК ВІДКИНУТО (жоден не записано, щоб серія не лягла наполовину):");
  bad.forEach((b) => console.error("  • " + b));
  console.error("Доказ — цитата з номером рядка, перерахунок, джерело з тим, що в ньому сказано,");
  console.error("або дослівний рядок виводу команди. Заява без доказу вироком не є.");
  process.exit(L.USAGE);
}

const at = new Date().toISOString();
for (const g of groups) V[g.it.key] = { status: g.status, proof: g.proof.trim(), file: g.it.file, item: g.it.text.slice(0, 300), at };
L.saveVerdicts(DIR, CHECK, V);
console.log(`вироків записано: ${groups.length} (перевірка ${CHECK}) — ${groups.map((g) => g.n + "→" + g.status).join(", ")}`);
const left = items.filter((e) => !V[e.key]).length;
console.log(left ? `лишилось без вироку: ${left}` : `усі пункти мають вирок — прожени перевірку знову`);
