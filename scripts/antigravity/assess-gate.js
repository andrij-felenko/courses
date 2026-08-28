#!/usr/bin/env node
/* ГЕЙТ ФАЗИ ОЦІНКИ — приймає або відхиляє розкладку рівнів по батчу.

   Ужиток:  node scripts/antigravity/assess-gate.js --batch scripts/_finish/_batch-<книга>.json

   Коди:  0 — розкладку прийнято, можна писати
          1 — ВІДХИЛЕНО: пусти фазу оцінки наново
          3 — ужиток

   ⛔ ПОРІГ НЕ ПОКАЗУЮТЬ ОЦІНЮВАЧЕВІ. НІКОЛИ. Ні числом, ні натяком, ні
   «попереднього разу вийшло замало». Він живе тут, у коді, і тільки тут.

   Причина не в секретності, а в тому, що вже двічі сталося з обсягом: показане
   моделі число стає ціллю. Скажеш оцінювачеві «середня має бути вище 2.2» — він
   видасть розкладку із середньою 2.2 і нічим більше; рівні перестануть означати
   важливість тем і почнуть означати арифметику. Тоді ми матимемо той самий недопис,
   тільки заведений на поверх вище й захований краще.

   Тому переоцінка ТИХА: той самий промпт, той самий список тем, чистий контекст.
   Оцінювач не знає, що це друга спроба, і не має знати. Ми не підказуємо йому
   відповідь — ми просто не беремо розкладку, у якій майже все виявилось дотичним.

   Що саме перевіряємо. Не окремий рівень — його правильність звідси не видно, і
   судити її має суддя читанням. Перевіряємо РОЗКЛАДКУ як ціле: якщо середня по
   батчу лягла низько, це означає не «нам трапився пакет дрібних тем», а що оцінювач
   поставив усім по одиниці, не розкладаючи. Шістнадцять тем, з яких половина нічого
   не тримає, — це не книга, це збій оцінки.                                        */
"use strict";
const fs = require("fs");
const path = require("path");

/* ── поріг ────────────────────────────────────────────────────────────────────
   Середня по батчу не нижча за 2.2. Взято з розкладу, який мала б давати жива
   книга: більшість тем звичайні (Р2), помітна частка робочих (Р3), кілька несучих
   і одна-дві дотичні. Така суміш дає середню близько 2.4–2.8, тож 2.2 — це не
   мета, а ПІДЛОГА здорового глузду: нижче за неї опиняється лише розкладка, де
   майже все назвали дотичним.                                                    */
const MIN_MEAN = 2.2;
const MAX_TRIES = 3;

const argv = process.argv.slice(2);
const val = (k) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : null; };
const BATCH = val("batch");
const TRY = Number(val("try") || 1) || 1;
if (!BATCH) { console.error("Ужиток: node scripts/antigravity/assess-gate.js --batch <файл> [--try N]"); process.exit(3); }

let j;
try { j = JSON.parse(fs.readFileSync(BATCH, "utf8")); }
catch (e) { console.error(`не прочитати ${BATCH}: ${e.message}`); process.exit(3); }
const list = (Array.isArray(j) ? j : (j.topics || j.units || [])).filter((x) => x && typeof x === "object" && x.dir);
if (!list.length) { console.error(`у ${BATCH} немає записів із "dir" — фаза оцінки не відпрацювала взагалі`); process.exit(1); }

const lv = (x) => { const n = Math.round(Number(x.level)); return Number.isFinite(n) && n >= 1 && n <= 5 ? n : null; };
const levels = list.map(lv);
const missing = list.filter((x, i) => levels[i] === null);
const good = levels.filter((n) => n !== null);

console.log(`\n=== ГЕЙТ ОЦІНКИ: ${path.basename(BATCH)} · спроба ${TRY}/${MAX_TRIES} ===\n`);
const hist = [1, 2, 3, 4, 5].map((n) => good.filter((x) => x === n).length);
hist.forEach((c, i) => console.log(`  Р${i + 1}  ${String(c).padStart(3)}  ${"█".repeat(c)}`));
const mean = good.length ? good.reduce((a, b) => a + b, 0) / good.length : 0;
console.log(`\n  тем ${list.length} · оцінено ${good.length} · середня ${mean.toFixed(2)}`);

if (missing.length) {
  console.log(`\n✖ ВІДХИЛЕНО: ${missing.length} тем без рівня`);
  missing.slice(0, 10).forEach((x) => console.log(`    ${x.dir}`));
  console.log(`\nПусти фазу оцінки наново — ТИМ САМИМ промптом, на весь список.`);
  process.exit(1);
}
if (mean < MIN_MEAN) {
  console.log(`\n✖ ВІДХИЛЕНО: розкладка лягла надто низько — майже все названо дотичним.`);
  console.log(`\nПусти фазу оцінки НАНОВО, тим самим промптом, свіжим агентом із чистим контекстом.`);
  console.log(`⛔ Оцінювачеві НЕ кажи ні цієї причини, ні того, що це повторна спроба, ні жодного`);
  console.log(`   числа звідси. Інакше він видасть розкладку під поріг, а не під теми.`);
  if (TRY >= MAX_TRIES) {
    console.log(`\n⚠ Спроба ${TRY} з ${MAX_TRIES} — далі не крути. Спинись і поклич людину:`);
    console.log(`   або в цьому пакеті справді самі дрібні теми, або оцінювач не розкладає.`);
  } else {
    console.log(`\nНаступний виклик: node scripts/antigravity/assess-gate.js --batch ${BATCH} --try ${TRY + 1}`);
  }
  process.exit(1);
}
console.log(`\n✓ ПРИЙНЯТО — можна писати.`);
process.exit(0);
