#!/usr/bin/env node
/* Перевірка 08 — АРИФМЕТИКА робочих прикладів.
   Ужиток: node scripts/checks/08-arithmetic.js <тека теми>

   Беремо ЛИШЕ обчислювальні рядки: ліворуч вираз, праворуч ЧИСЛО. Лістинги коду
   (оголошення, присвоєння зі «;», порівняння, команди збірки) не беремо — інакше
   агент перераховує «cc -O2» і перевірка перетворюється на шум.

   Ask свій на кожен тип:
     math-      — перерахувати КОЖЕН крок виведення й перевірити, чи підпис кроку
                  справді описує перехід;
     proj-      — перерахувати очікуваний вивід програми й звірити одиниці;
     detailed/basic — перерахувати приклад і звірити з висновком у прозі;
     api-       — звірити числа таблиць (розміри полів, стелі) з документацією;
     hist-/comp- — обчислень майже не буває; що знайшлося, те й рахуємо. */
"use strict";
const fs = require("fs");
const L = require("./_lib.js");

const DIR = L.resolveDir(process.argv[2]);
if (!DIR) { console.error("Вкажи теку теми (шлях від кореня репо або абсолютний)"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("08", "арифметика робочих прикладів", DIR);

const DECL = /\b(int|long|short|char|float|double|const|static|struct|void|let|var|def|class|return|if|while|for|printf|scanf|#define|#include)\b/;
function isComputation(line) {
  const t = line.trim();
  if (!t || t.length > 160) return false;
  if (/^[#/]|^\/\/|\/\*|\*\//.test(t)) return false;         // коментар
  if (/[;{}]/.test(t)) return false;                          // код
  if (/[=!<>]=|=>|\+=|-=|\*=|\/=/.test(t)) return false;      // порівняння й складені присвоєння
  if (DECL.test(t)) return false;
  const m = t.match(/^(.+?)=\s*([-+]?\d[\d\s.,·×]*)\s*([\p{L}%/]{0,12})$/u);
  if (!m) return false;
  return /\d/.test(m[1]) || /[+\-×·÷*/^]/.test(m[1]);         // ліворуч має бути що рахувати
}

const items = [];
T.files.forEach((f) => {
  L.codeBlocks(f.text).forEach((b) => {
    const lines = b.body.split(/\r?\n/).filter(isComputation);
    if (!lines.length) return;
    items.push({
      file: f.file, kind: f.kind,
      text: `код-блок #${b.n}${b.lang ? " (" + b.lang + ")" : ""}, обчислювальних рядків ${lines.length}: ${lines.slice(0, 3).map((s) => s.trim()).join(" · ").slice(0, 200)}`,
    });
  });
});

/* обчислення, що втекли в прозу: «разом 4096 + 512 = 4608» поза код-блоком */
T.files.forEach((f) => {
  L.strip(f.text).split(/\r?\n/).forEach((line, i) => {
    const t = line.trim();
    if (!/\d\s*[+\-×·÷]\s*\d/.test(t) || !/=/.test(t)) return;
    items.push({ file: f.file, kind: f.kind, text: `рядок ${i + 1}: обчислення в прозі — «${t.slice(0, 120)}» (перерахувати, а за §5 воно ще й має жити в код-блоці)` });
  });
});

if (!items.length) L.pass("обчислювальних прикладів не знайдено");

L.adjudicate(DIR, items,
  "ПЕРЕРАХУЙ кожен блок сам, не дивлячись у наведену відповідь, тоді звір. Перевір одиниці (байти/біти, мс/мкс, степені двійки) " +
  "і те, що результат збігається з висновком, який робить проза. " +
  "У math- додатково: чи підпис кроку [у дужках] справді описує цей перехід. " +
  "У proj- додатково: чи такий вивід справді дасть наведена програма. " +
  "Доказ — власний перерахунок числами, а не «збігається».");
