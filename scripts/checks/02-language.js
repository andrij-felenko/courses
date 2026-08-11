#!/usr/bin/env node
/* Перевірка 02 — МОВА: гомогліфи (машинно), русизми й склейки (вирок агента).
   Ужиток: node scripts/checks/02-language.js <тека теми>

   Гомогліфи — тверде: латинська літера всередині кириличного слова ламає пошук.
   Скрипт лагодить їх сам (--apply) і ПЕРЕВІРЯЄ, що після лагодження їх нуль;
   що не полагодилось — дефект (раніше ця діра тихо проходила як «чисто»).

   Русизми й склейки — контекстні, тому йдуть на вирок. За типами:
     proj-/api- — латиниця в іменах прапорців і функцій НЕ склейка (це поверхня);
     hist-      — прізвища й назви установ латиницею — норма;
     решта      — судити суворо. */
"use strict";
const path = require("path");
const fs = require("fs");
const L = require("./_lib.js");

const DIR = L.resolveDir(process.argv[2]);
if (!DIR) { console.error("Вкажи теку теми (шлях від кореня репо або абсолютний)"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("02", "мова: гомогліфи, русизми, склейки", DIR);
if (!T.files.length) L.pass("у теці немає .md");

/* (1) гомогліфи — полагодити й ПЕРЕВІРИТИ залишок окремим прогоном */
L.run(`node scripts/textcheck.js "${DIR}" --only 1 --apply`);
const after = L.run(`node scripts/textcheck.js "${DIR}" --only 1 --json`);
let homo = [];
try { homo = JSON.parse(after.out).homo || []; } catch { /* нижче */ }
if (homo.length) {
  L.defects(homo.map((h) => {
    const kind = L.classify(path.basename(h.file), T.slug);
    return `${path.basename(h.file)} (${L.KIND_LABEL[kind]}) рядок ${h.line}: «${h.from}» → «${h.to}» — автозаміна не взяла, правити руками`;
  }), "гомогліфи ламають пошук по сайту");
}

/* (2) русизми й склейки — на вирок */
const r = L.run(`node scripts/textcheck.js "${DIR}" --only 3 --json`);
let lang = [];
try { lang = JSON.parse(r.out).lang || []; } catch { /* оракул мовчав */ }
if (!lang.length) L.pass("гомогліфів 0, русизмів і склейок 0");

const items = lang.map((x) => {
  const base = path.basename(x.file);
  const kind = L.classify(base, T.slug);
  return { file: base, kind, text: `рядок ${x.line}: ${x.kind} «${x.word}»${x.hint ? " → " + x.hint : ""}` };
});

L.adjudicate(DIR, items,
  "по кожному слову: це справді русизм/склейка чи термін, ім'я або назва прапорця? " +
  "У proj-/api- латинські імена функцій і прапорців — норма; у hist- норма прізвища й установи латиницею; " +
  "у прозі статті — заміняй живим українським відповідником. Доказ: рядок із файлу і чим саме заміна виправдана.");
