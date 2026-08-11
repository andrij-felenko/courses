#!/usr/bin/env node
/* Перевірка 03 — ФІГУРИ: геометрія, місце, підключення (§5).
   Ужиток: node scripts/checks/03-figures.js <тека теми>

   Питання одне: чи побачить читач фігуру — і чи вона там, де про неї сказано.
   Усе тут машинне, тому вирок дає скрипт.

   За типами файлу: фігура належить темі, а не файлу, тому підключення шукаємо
   в БУДЬ-ЯКОМУ .md теми — і в базовій, і в детальній, і у вставках. Але шлях
   у посиланні мусить бути від кореня репо (інакше на GitHub Pages ламається). */
"use strict";
const fs = require("fs");
const path = require("path");
const L = require("./_lib.js");

const DIR = process.argv[2];
if (!DIR || !fs.existsSync(DIR)) { console.error("Вкажи теку теми"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("03", "фігури: геометрія, місце, підключення", DIR);

const hasImg = fs.existsSync(T.imgDir);
const loose = fs.readdirSync(DIR).filter((f) => f.toLowerCase().endsWith(".svg"));
const svgs = hasImg ? fs.readdirSync(T.imgDir).filter((f) => f.toLowerCase().endsWith(".svg")) : [];
const allMd = T.files.map((f) => f.text).join("\n");
const refs = [...allMd.matchAll(/!\[[^\]]*\]\(([^)]+\.svg)\)/g)].map((m) => m[1]);

if (!hasImg && !loose.length && !refs.length) L.pass("у темі немає фігур");

const bad = [];

/* (1) геометрія й підключення — оракул svgcheck */
if (hasImg) {
  const r = L.run(`python scripts/svgcheck.py "${DIR}" --links`);
  console.log(r.out.trimEnd());
  if (!/із зауваженнями: 0/.test(r.out)) bad.push("svgcheck дав зауваження — правити у figs.py і перегенерувати (руками .svg не чіпати)");
  if (/нема файлу|відсутн/i.test(r.out)) bad.push("є підключення в .md без файлу фігури");
}

/* (2) місце й імена */
loose.forEach((f) => bad.push(`SVG лежить у корені теми, має бути в img/: ${f}`));
svgs.forEach((f) => {
  if (/_/.test(f)) bad.push(`ім'я не kebab-case (підкреслення): img/${f}`);
  if (!allMd.includes(f)) bad.push(`фігуру згенеровано, але вона не підключена в жодному .md теми: img/${f}`);
});
if (svgs.length && !fs.existsSync(path.join(DIR, "figs.py")))
  bad.push("є фігури, але немає figs.py — фігури мусять бути відтворюваними");

/* (3) шлях у посиланні — від кореня репо */
refs.forEach((r) => {
  if (!r.startsWith("/")) bad.push(`посилання на фігуру не від кореня репо (зламається на GitHub Pages): ${r.slice(0, 80)}`);
  else if (!fs.existsSync(path.join(L.ROOT, r.replace(/^\//, "")))) bad.push(`посилання веде в нікуди: ${r}`);
});

/* (4) підпис під фігурою — читач має знати, на що дивиться */
T.files.forEach((f) => {
  const lines = f.text.split(/\r?\n/);
  lines.forEach((line, i) => {
    if (!/^!\[[^\]]*\]\([^)]*\.svg\)/.test(line.trim())) return;
    const after = (lines[i + 1] || "").trim() || (lines[i + 2] || "").trim();
    if (!/^\*.+\*$/.test(after))
      bad.push(`${f.file} (${f.label}) рядок ${i + 1}: фігура без курсивного підпису під нею — читач не знає, що саме показано`);
  });
});

L.defects(bad, "фігури правити у figs.py й перегенерувати: python figs.py");
