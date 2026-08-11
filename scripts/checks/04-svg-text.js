#!/usr/bin/env node
/* Перевірка 04 — ТЕКСТ УСЕРЕДИНІ ФІГУР.
   Ужиток: node scripts/checks/04-svg-text.js <тека теми>

   Питання одне: чи не лежить у написах на фігурах те, що в прозі вже заборонено
   (гомогліфи, русизми). Написи не гейтить більше НІЩО: wordcount читає лише .md,
   svgcheck судить геометрію, а не мову.

   Особливість проти інших перевірок: правити треба figs.py і перегенерувати —
   редагувати .svg руками заборонено, бо наступний прогін figs.py усе змиє. */
"use strict";
const fs = require("fs");
const L = require("./_lib.js");

const DIR = L.resolveDir(process.argv[2]);
if (!DIR) { console.error("Вкажи теку теми (шлях від кореня репо або абсолютний)"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("04", "текст усередині фігур", DIR);
if (!fs.existsSync(T.imgDir)) L.pass("у темі немає фігур");

const r = L.run(`node scripts/textcheck.js "${DIR}" --only 7 --json`);
let svgText = [];
try { svgText = JSON.parse(r.out).svgText || []; } catch {
  console.log(r.out.trimEnd());
  L.defects(["textcheck не дав JSON — перевірити руками: node scripts/textcheck.js <тека> --only 7"]);
}
if (!svgText.length) L.pass("написи у фігурах чисті");

L.defects(svgText.map((s) =>
  `${s.file} напис #${s.n}: ${s.kind} «${s.word}»${s.to ? " → «" + s.to + "»" : ""}${s.ctx ? "   [" + String(s.ctx).slice(0, 60) + "]" : ""}`),
  "правити у figs.py і перегенерувати (python figs.py), .svg руками не чіпати");
