#!/usr/bin/env node
/* Перевірка 01 — ФОРМУЛИ: жодного LaTeX, обчислення — у код-блоках (§5).
   Ужиток: node scripts/checks/01-latex.js <тека теми>
   Питання перевірки одне: чи побачить читач формулу такою, як її задумано,
   у рушії БЕЗ математичного рендерера.

   За типами файлу:
     basic/detailed — LaTeX заборонено; формула в прозі → код-блок;
     math-          — те саме + кожен крок виведення окремим рядком, вирівняним по «=»;
     proj-/api-     — LaTeX заборонено; вирази живуть у коді, а не в прозі;
     hist-/comp-    — LaTeX заборонено (там формул майже не буває — і добре). */
"use strict";
const path = require("path");
const fs = require("fs");
const L = require("./_lib.js");

const DIR = L.resolveDir(process.argv[2]);
if (!DIR) { console.error("Вкажи теку теми (шлях від кореня репо або абсолютний)"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("01", "формули: LaTeX і оформлення обчислень", DIR);
if (!T.files.length) L.pass("у теці немає .md");

const bad = [];

/* (1) LaTeX — оракул той самий, що в спільного гейта (він уміє не плутати валюту) */
const r = L.run(`node scripts/textcheck.js "${DIR}" --only 2 --json`);
let tex = [];
try { tex = (JSON.parse(r.out).tex || []); } catch { /* нижче скажемо, що оракул мовчав */ }
if (!r.out.trim()) bad.push("textcheck не дав виводу — перевірити руками: node scripts/textcheck.js <тека> --only 2");
tex.forEach((t) => {
  const kind = L.classify(path.basename(t.file), T.slug);
  bad.push(`${path.basename(t.file)} (${L.KIND_LABEL[kind]}) рядок ${t.line}: LaTeX ${JSON.stringify(t.hits)} — на Unicode, інлайн-код або код-блок`);
});

/* (2) формула, залишена в прозі: рядок з «=» без жодної кириличної літери, поза кодом.
       Судимо лише там, де формули справді бувають, — щоб не чіпати проекти й історію. */
const FORMULA_KINDS = new Set(["basic", "detailed", "math"]);
T.files.filter((f) => FORMULA_KINDS.has(f.kind)).forEach((f) => {
  let inCode = false;
  f.text.split(/\r?\n/).forEach((line, i) => {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; return; }
    if (inCode || !t) return;
    if (/^[|>#!]/.test(t) || /^[-*]\s/.test(t)) return;          // таблиця, цитата, заголовок, список
    const naked = t.replace(/`[^`]*`/g, "").replace(/\[[^\]]*\]\([^)]*\)/g, "");
    if (!/[=≈≤≥≠]/.test(naked)) return;
    if (/[а-яіїєґА-ЯІЇЄҐ]/.test(naked)) return;                   // є проза — це речення, не формула
    if (naked.replace(/[^\wА-Яа-я]/g, "").length < 4) return;
    bad.push(`${f.file} (${f.label}) рядок ${i + 1}: формула лишилась у прозі — «${naked.slice(0, 60)}»; за §5 це код-блок, вирівняний по «=», з підписом кроку у [дужках]`);
  });
});

if (bad.length) L.defects(bad, "правити самі файли; фігур і маніфесту не чіпати");

/* (3) виведення без пояснень кроків — НЕ машинний дефект, а питання до судді.
       Ланцюг виведення пізнається по рядках-продовженнях, що ПОЧИНАЮТЬСЯ з «=»:
       чотири незалежні тотожності в стовпчик — це таблиця, і підписів вона не потребує.
       Підписом вважаємо і [дужки], і звичайний хвіст-пояснення після виразу. */
const items = [];
T.files.filter((f) => f.kind === "math" || f.kind === "detailed").forEach((f) => {
  L.codeBlocks(f.text).forEach((b) => {
    const lines = b.body.split(/\r?\n/).filter((l) => l.trim());
    const chain = lines.filter((l) => /^\s*=/.test(l));
    if (chain.length < 2) return;                                   // не ланцюг, а перелік
    const annotated = lines.filter((l) => /\[[^\]]+\]/.test(l) || /\s{3,}\S.*[а-яіїєґ]{3,}/.test(l) || /[а-яіїєґ]{3,}\s+[а-яіїєґ]{3,}/.test(l));
    if (annotated.length) return;                                   // пояснення є — у якій формі, судить суддя нижче
    items.push({ file: f.file, kind: f.kind, text: `код-блок #${b.n}: ланцюг із ${chain.length + 1} кроків без жодного пояснення переходу — «${lines.slice(0, 2).join(" ⏎ ").slice(0, 140)}»` });
  });
});
if (!items.length) L.pass("LaTeX 0, формул у прозі немає, виведення пояснені");

L.adjudicate(DIR, items,
  "по кожному блоку: чи зрозуміє читач, ЧОМУ кожен перехід дозволено? " +
  "Доказ «ok» — назви правило, що виправдовує кожен крок, і покажи, що воно сказане поруч у прозі. " +
  "Доказ «defect» — назви крок, для якого правила ніде немає. За §5 підпис кроку йде у квадратних дужках у тому ж рядку.");
