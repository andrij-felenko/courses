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
const DIR = argv[1];
const flag = (name) => { const i = argv.indexOf("--" + name); return i >= 0 ? argv[i + 1] : null; };
const has = (name) => argv.includes("--" + name);

if (!/^\d\d$/.test(CHECK) || !DIR || !fs.existsSync(DIR)) {
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

const n = Number(flag("item"));
const status = flag("status");
const proof = flag("proof");
const it = items.find((e) => e.n === n);
if (!it) { console.error(`нема пункту ${n} (є 1..${items.length})`); process.exit(L.USAGE); }
if (status !== "ok" && status !== "defect") { console.error("--status має бути ok або defect"); process.exit(L.USAGE); }

/* гейт доказу — механічний, щоб «перевірено» не проходило */
const EMPTY = /^(перевірено|усе гаразд|все гаразд|ок|ok|добре|виглядає правильно|100%.*|perfect.*|чисто)\.?$/i;
if (!proof || proof.trim().length < 25 || EMPTY.test(proof.trim())) {
  console.error("ВИРОК ВІДКИНУТО: --proof має бути конкретним доказом (від 25 символів).");
  console.error("Доказ — це цитата з номером рядка, перерахунок, джерело з тим, що в ньому сказано,");
  console.error("або дослівний рядок виводу команди. Заява без доказу вироком не є.");
  process.exit(L.USAGE);
}

V[it.key] = { status, proof: proof.trim(), file: it.file, item: it.text.slice(0, 300), at: new Date().toISOString() };
L.saveVerdicts(DIR, CHECK, V);
console.log(`вирок записано: перевірка ${CHECK}, пункт ${n} → ${status}`);
console.log(`доказ: ${proof.trim().slice(0, 200)}`);
const left = items.filter((e) => !V[e.key]).length;
console.log(left ? `лишилось без вироку: ${left}` : `усі пункти мають вирок — прожени перевірку знову`);
