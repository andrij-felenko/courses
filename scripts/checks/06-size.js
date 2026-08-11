#!/usr/bin/env node
/* Перевірка 06 — ОБСЯГ за §3, зі смугами Antigravity (канон × SCALE).
   Ужиток: node scripts/checks/06-size.js <тека теми>   [CHECKS_SCALE=1.35]

   Питання одне: чи дописано тему до дна — і чи не роздуто її замість того.

   Antigravity пише дешево, тому смуги підняті на 35% від канонних в ОБИДВА боки:
   нижній край — щоб недописування ловилось (це головна його вада), верхній —
   щоб глибина не билася в стелю. Орієнтир свій на КОЖЕН тип файлу.

   Що дає який код:
     нижче нижнього краю смуги чи вище верхнього → ДЕФЕКТ (машинно);
     у смузі, але нижче орієнтиру                 → ПУНКТ НА ВИРОК (чи тема
       справді вичерпана — буває, що так, і тоді це доводиться, а не заявляється);
     базова > ½ детальної                          → ДЕФЕКТ (залізо §3).

   Скорочувати текст заради проходження гейта заборонено: недобір лікується
   дописуванням, перебір — поділом теми, а не викиданням матеріалу. */
"use strict";
const fs = require("fs");
const L = require("./_lib.js");

const DIR = process.argv[2];
if (!DIR || !fs.existsSync(DIR)) { console.error("Вкажи теку теми"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("06", `обсяг (канон × ${L.SCALE})`, DIR);

const rows = T.files.filter((f) => f.kind !== "other").map((f) => {
  const w = L.proseWords(f.text);
  const b = L.bandOf(f.kind);
  let mark = "✓", note = "";
  if (w < b.lo) { mark = "▽"; note = `нижче смуги (<${b.lo})`; }
  else if (w > b.max) { mark = "▲"; note = `понад виняткову стелю (>${b.max}) — тему треба ділити`; }
  else if (w > b.hi) { mark = "⌇"; note = `виняток §3 (${b.hi}–${b.max}) — чи справді неподільна?`; }
  else if (w < b.aim[0]) { mark = "~"; note = `у смузі, але нижче орієнтиру ${b.aim[0]}–${b.aim[1]}`; }
  return { f, w, b, mark, note };
});
if (!rows.length) L.pass("у теці немає статей і вставок");

console.log("");
rows.forEach((r) => console.log(
  `  ${r.mark} ${String(r.w).padStart(5)}w  ${r.f.file.padEnd(34)} ${r.f.label.padEnd(24)} смуга ${r.b.lo}–${r.b.hi} · орієнтир ${r.b.aim[0]}–${r.b.aim[1]}${r.note ? "  ← " + r.note : ""}`));

const bad = [];
rows.filter((r) => r.mark === "▽").forEach((r) => bad.push(`${r.f.file} (${r.f.label}): ${r.w}w — ${r.note}; дописати до ${r.b.aim[0]}–${r.b.aim[1]}, не «водою», а тим, що бракує: механізм, крайові випадки, простеження, розбір`));
rows.filter((r) => r.mark === "▲").forEach((r) => bad.push(`${r.f.file} (${r.f.label}): ${r.w}w — ${r.note}`));

/* залізо §3: базова ≤ ½ детальної (відношення, від масштабу не залежить) */
if (T.basic && T.detailed) {
  const wb = L.proseWords(T.basic.text), wd = L.proseWords(T.detailed.text);
  const ratio = wd ? wb / wd : 0;
  console.log(`\n  пара база↔деталь: ${wb}w / ${wd}w = ${Math.round(ratio * 100)}%  (стеля бази ${Math.round(wd / 2)}w)`);
  if (ratio > 0.55) bad.push(`базова ${wb}w — це ${Math.round(ratio * 100)}% детальної (${wd}w); §3 дозволяє ½. Базову НЕ стискати: або ріжемо матеріал (виведення, варіації, крайові випадки), або базової тут не треба взагалі — тоді basic:empty`);
}
if (bad.length) L.defects(bad, "обсяг лікується дописуванням або поділом, ніколи — скороченням");

const soft = rows.filter((r) => r.mark === "~" || r.mark === "⌇");
if (!soft.length) L.pass("усі файли у смугах і в орієнтирах");

L.adjudicate(DIR, soft.map((r) => ({
  file: r.f.file, kind: r.f.kind,
  text: `${r.w}w при орієнтирі ${r.b.aim[0]}–${r.b.aim[1]} — ${r.note}`,
})),
  "по кожному файлу: тему справді вичерпано на цьому обсязі — чи бракує матеріалу? " +
  "Доказ «ok»: перелічи, що саме вже розібрано (механізм, крайові випадки, простеження, приклад) і чому решта до теми не належить. " +
  "Доказ «defect»: назви, чого бракує. Скорочення ніколи не є відповіддю.");
