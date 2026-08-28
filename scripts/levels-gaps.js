#!/usr/bin/env node
/* ПЕРЕВІРКА ПОВНОТИ ОЦІНОК — що з поточного recheck іще не має рівня.

   Корпус рухається під час оцінювання: Antigravity пише паралельно, і тема, яка
   перейшла в recheck ПІСЛЯ генерації вхідного списку, в оцінку не потрапляє.
   Саме так `hw-arch/esp32-s3-ai` лишилася без рівня (42 теми у вході, 43 зараз).

   Цей скрипт звіряє scripts/_levels/<книга>.json із ЖИВИМ маніфестом і показує:
     ✖ у recheck, але без оцінки — треба доміряти;
     ○ оцінена, але вже не в recheck — статус змінили після оцінки (не помилка).   */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("./lib/manifest7.js");

const DIR = path.join(__dirname, "_levels");
const files = fs.existsSync(DIR) ? fs.readdirSync(DIR).filter((f) => f.endsWith(".json")) : [];
let rated = 0, miss = 0, stale = 0, pending = 0;
const gaps = [];

for (const [slug, rec] of M7.books()) {
  const b = M7.loadBook(rec.bookDir); if (!b) continue;
  const now = new Set();
  for (const t of M7.allTopics(b)) {
    if (!t.own) continue;
    const d = t.node.detailed && t.node.detailed.status, ba = t.node.basic && t.node.basic.status;
    /* `deeper` — це теж оцінена тема: статус їй поставила саме звірка оцінки з розміром
       (levels-actual.js). Без цього рядка звіт показував би 1581 «оцінену, що вийшла з
       recheck» — тобто нашу ж власну роботу як розбіжність. */
    if (d === "recheck" || d === "deeper" || ba === "recheck") now.add(t.slug);
  }
  const f = path.join(DIR, `${slug}.json`);
  if (!fs.existsSync(f)) { if (now.size) { pending += now.size; gaps.push([slug, now.size, "книга ще не оцінена"]); } continue; }
  const j = JSON.parse(fs.readFileSync(f, "utf8"));
  const have = new Set(j.topics.filter((t) => t.mean !== null).map((t) => t.slug));
  rated += have.size;
  const m = [...now].filter((s) => !have.has(s));
  const s = [...have].filter((x) => !now.has(x));
  miss += m.length; stale += s.length;
  if (m.length) gaps.push([slug, m.length, "✖ БЕЗ ОЦІНКИ: " + m.slice(0, 6).join(", ")]);
  if (s.length) gaps.push([slug, s.length, "○ оцінені, вже не в recheck: " + s.slice(0, 4).join(", ")]);
}

console.log(`\n=== ПОВНОТА ОЦІНОК ===`);
console.log(`оцінено ${rated} · без оцінки в поточному recheck ${miss} · оцінені, що вийшли з recheck ${stale}`);
console.log(`у ще не оцінених книгах ${pending}\n`);
for (const [b, n, why] of gaps) console.log(`  ${b.padEnd(22)} ${String(n).padStart(4)}  ${why}`);
process.exit(miss ? 1 : 0);
