#!/usr/bin/env node
/* Перевірка 05 — ЛІНКИ, ПЕРЕДУМОВИ, ДОСТУПНІСТЬ ВСТАВОК.
   Ужиток: node scripts/checks/05-links.js <тека теми>

   Питання одне: чи дійде читач туди, куди його посилають, — і чи взагалі
   дізнається, що вставка існує.

   За типами файлу:
     detailed — мусить мати <preknowlist> із book:-лінками (§6);
     basic    — <preknowlist> не вимагаємо: базова і є входом;
     вставки  — кожна мусить бути згадана book:-лінком у прозі теми (у базовій
                АБО в детальній — читач заходить із будь-якої).

   Биті лінки судимо ЛИШЕ свої: агент не має права чіпати чужі теки, тож
   вимагати від нього «БИТІ (0)» по всьому корпусу було б нездійсненно. */
"use strict";
const fs = require("fs");
const path = require("path");
const L = require("./_lib.js");

const DIR = L.resolveDir(process.argv[2]);
if (!DIR) { console.error("Вкажи теку теми (шлях від кореня репо або абсолютний)"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("05", "лінки, передумови, доступність вставок", DIR);
if (!T.files.length) L.pass("у теці немає .md");

const bad = [];
const rel = path.relative(L.ROOT, path.resolve(DIR));
const needle = [rel, rel.replace(/\\/g, "/"), rel.replace(/\//g, "\\")];

/* (1) биті лінки — свої */
const r = L.run("node scripts/linkcheck.js");
let inBroken = false;
r.out.split(/\r?\n/).forEach((line) => {
  if (/^===/.test(line)) { inBroken = /БИТІ/.test(line); return; }
  if (!inBroken || !line.trim()) return;
  if (needle.some((n) => line.includes(n))) bad.push(`битий лінк: ${line.trim().slice(0, 140)}`);
});

/* (2) передумови в детальній */
if (T.detailed) {
  const d = T.detailed.text;
  const m = d.match(/<preknowlist>([\s\S]*?)<\/preknowlist>/);
  if (!m) bad.push("детальна стаття без блоку <preknowlist> — §6 вимагає його в кожній новій статті");
  else {
    const block = m[1];
    if (/<details|<summary/i.test(block)) bad.push("усередині <preknowlist> зайва обгортка <details>/<summary> — рушій читає блок порядково, теги стануть фальшивими пунктами");
    if (!/\]\(book:/.test(block)) bad.push("пункти <preknowlist> без book:-лінків — читач не має куди піти по передумову");
    const lines = block.split(/\r?\n/).filter((l) => l.trim());
    if (lines.length < 2) bad.push("<preknowlist> порожній або з одного рядка — назви справжні передумови");
  }
}

/* (3) кожна вставка доступна з прози (будь-якої версії) */
const proseAll = T.prose.map((p) => p.text).join("\n");
T.inserts.forEach((ins) => {
  if (!proseAll.includes(ins.file)) {
    bad.push(`${ins.file} (${ins.label}): вставку не згадано в прозі теми — читач її не відкриє ніколи`);
    return;
  }
  const linked = new RegExp(`\\]\\(book:[^)]*${ins.file.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\)`).test(proseAll);
  if (!linked) bad.push(`${ins.file} (${ins.label}): згадка є, але не book:-лінком — попап не відкриється (§6)`);
});

/* (4) зовнішніх .md-лінків усередині теми бути не має — лише book: */
T.files.forEach((f) => {
  [...f.text.matchAll(/\[[^\]]*\]\(([^)]+\.md)\)/g)].forEach((m) => {
    if (!m[1].startsWith("book:") && !m[1].startsWith("guide:"))
      bad.push(`${f.file} (${f.label}): відносний .md-лінк «${m[1].slice(0, 70)}» — за каноном це book:-попап`);
  });
});

L.defects(bad, "правити лише файли своєї теми");
