#!/usr/bin/env node
/**
 * make-writer-canon.js — зрізає з AUTHORING.en.md те, чого АГЕНТ-ПИСЬМЕННИК не застосовує,
 * і кладе результат у AUTHORING.write.en.md. Саме цей файл читають агенти фаз «Детальні»,
 * «Базові» та «Вставки» (КРОК1) замість повного канону.
 *
 * НАВІЩО: повний AUTHORING.en.md — 47 КБ ≈ 15.5 тис. вхідних токенів, і його читає КОЖЕН агент
 * (у батчах 2026-08-02 — 374 з 382). Схеми маніфестів і опис конвеєра письменникові не потрібні:
 * маніфест він за каноном НЕ чіпає, статуси розставляє окрема фаза локальним патчером.
 *
 * ⚠️ ЗАЛІЗО: усе, що лишається, переноситься ДОСЛІВНО, байт у байт. Скрипт нічого не переказує
 * і не скорочує — інакше зникла б гарантія «жодне правило письменника не змінилось».
 * Ріжемо ХІРУРГІЧНО, не розділами: у §2 лишається нейминг (письменник ним користується) і йде
 * геть лише схема маніфесту; у §9 лишається абзац «Discipline» і йдуть геть статуси/процес/гігієна.
 *
 * Запускати після КОЖНОЇ правки AUTHORING.en.md. Батч робить це сам першою дією.
 */
const fs = require('fs'), path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'AUTHORING.en.md');
const DST = path.join(ROOT, 'AUTHORING.write.en.md');

/** У межах розділу викидаємо все ВІД рядка, що збігся з `from`, до кінця розділу,
 *  окрім рядків, що збіглися з якимось `keep`. */
const RULES = [
  { section: /^##\s*§2\b/, from: /^\*\*The manifest is the single source\*\*/, keep: [] },
  { section: /^##\s*§9\b/, from: /^\*\*Statuses \(enum/, keep: [/^\*\*Discipline\.\*\*/] },
];

const src = fs.readFileSync(SRC, 'utf8');
const out = [];
let rule = null, dropping = false, cutLines = 0;

for (const line of src.split('\n')) {
  if (/^##\s/.test(line)) {                       // новий розділ — скидаємо стан
    rule = RULES.find((r) => r.section.test(line)) || null;
    dropping = false;
  } else if (rule && !dropping && rule.from.test(line)) {
    dropping = true;
  }
  const keep = dropping && rule && rule.keep.some((re) => re.test(line));
  if (dropping && !keep) { cutLines += line.length ? 1 : 0; continue }
  out.push(line);
}

const NOTE = `> **Це зріз канону для АГЕНТА-ПИСЬМЕННИКА.** Усе нижче — ДОСЛІВНИЙ текст \`AUTHORING.en.md\`.
> Вирізано рівно два шматки, яких письменник не застосовує: у **§2** — схеми маніфестів,
> у **§9** — перелік статусів, опис конвеєра й гігієну репо. Маніфест ти НЕ чіпаєш, статуси
> розставляє окрема фаза. Нейминг файлів (§2) і дисципліну (§9) залишено. Повний канон — \`AUTHORING.en.md\`.
> Файл ГЕНЕРОВАНИЙ: \`node scripts/make-writer-canon.js\`. Руками не правити — правку внось у \`AUTHORING.en.md\`.`;

const i = out.findIndex((l) => /^#\s/.test(l));
out.splice(i < 0 ? 0 : i + 1, 0, '', NOTE);

const res = out.join('\n').replace(/\n{4,}/g, '\n\n\n');
fs.writeFileSync(DST, res, 'utf8');

const kb = (n) => (n / 1024).toFixed(1);
console.log(
  `make-writer-canon: ${kb(src.length)} КБ → ${kb(res.length)} КБ ` +
  `(зрізано ${kb(src.length - res.length)} КБ = ${((100 * (src.length - res.length)) / src.length).toFixed(0)}%, ${cutLines} абзаців)`
);
