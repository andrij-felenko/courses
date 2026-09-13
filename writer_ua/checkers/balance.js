#!/usr/bin/env node
/* ============================================================================
   balance.js — ЩО ЦЕЙ ТЕКСТ ЗМУСИТЬ ЗРОБИТИ. Перевірка ДІЇ, а не доставки.

   Доїхати може текст, який штовхає рівно в один бік, і тоді агент іде в той бік до
   впору: чотири «не бери зайвого» без жодного «не спиняйся» дали статті на 620 слів;
   «від нуля до трьох на тип» стало нормою — рівно три в кожній темі. Обидві вади видно
   БЕЗ батчу — порахувавши, куди штовхає складений запит.

   ЩО ЛОВИТЬ
     1. ОДНОБІЧНІСТЬ — вимір, у якому в запиті є накази лише в один бік.
     2. АНКЕРИ — кожне число величини, що доїжджає до агента: показане число стає
        ціллю, тож кожне має бути НАВМИСНИМ, і всі вони тут перелічені поіменно.

   Ужиток:  node writer_ua/checkers/balance.js
   Вихід:   0 — рівно · 1 — є однобічність
   ========================================================================== */
"use strict";
const P = require("../runners/prompt.js");
const L = require("../runners/local.js");
const MF = require("../lib/manifest.js");

const pick = (kind) => {
  for (const [slug, b] of MF.books()) {
    if (b.kind !== kind) continue;
    const bk = MF.loadBook(MF.bookDirOf(slug));
    const t = bk && MF.allTopics(bk).find((x) => x.own);
    if (t) return L.unitOf(slug, t.slug);
  }
  throw new Error(`немає книги виду ${kind}`);
};
const art = pick("sci");
const ins = (t) => L.unitOf(art.book, art.slug, t, "", `${t}-probe`);
const W = { goal: "ц", level: 3, depth: "г", sections: "1 | важливість: висока | п", theses: "", integrate: "", preknow: "", passed: "", linkable: "Л", code: "" };

const calls = {
  "ціль": P.goal(art, { mentions: "", passed: "" }),
  "структура": P.structure(art, { goal: "ц", books: "к" }),
  "каркас": P.karkas(art, { goal: "ц", passed: "П", known: "К", inserts: "В", detailed: "" }),
  "письмо": P.write(art, W),
  "дописування": P.extend(art, { ...W, section: "1", text: "т", add: "1 | 5 | щ", floor: 300, ceiling: 1200 }),
  "стиснення": P.compress(art, { goal: "ц", level: 3, section: "1", text: "т", theses: "", squeeze: "щ", by: 100 }),
  "аналіз": P.analysis(art, { goal: "ц", level: 3, text: "т", theses: "", groups: "1", force: false }),
  "каркас math": P.karkas(ins("math"), { goal: "ц", passed: "", known: "К", inserts: "", detailed: "" }),
  "письмо math": P.write(ins("math"), W),
};

/** Виміри, у яких ми вже падали: чим у тексті виглядає штовхання в кожен бік. */
const AXES = {
  "обсяг": {
    down: /стаття серед інших статей|більше не можна|компактніш|лише те, без чого читач не зрозуміє/,
    up: /не вичерпана|не менше \d+ слів|не орієнтуйся на пару речень|коротший за потрібне/,
  },
  "кількість вставок": {
    down: /Немає такого тіла — немає вставки|Єдина межа — ТЕМАТИКА/,
    up: /Верхньої межі немає|на користь написаного|Три «так» — заводь/,
  },
  "фігури": {
    down: /Фігура несе вагу|чи стане зрозуміліше/,
    up: /словами передається важко|там її бракує|Лімітів немає/,
  },
};

/** Числа величин у тексті, який доїжджає. Кожне має бути навмисним. */
const ANCHOR = /(?:^|[^\d])(\d{1,5})\s*(?:[–—-]\s*(\d{1,5})\s*)?(слів|слова|слово|речень|рядк\w*|пункт\w*|вставк\w*|фігур\w*|розділ\w*|кроків)/gi;
/* ⛔ БЕЗ `\b`: межа слова знає лише латиницю, тож перед «по одній» вона не спрацьовує
   ніколи — сито мовчало на всьому корпусі. Заперечний погляд назад на літеру. */
const WORDY = /(?<!\p{L})(по одн(?:ій|ому)|три-чотири|дві |три |чотири |п'ять )\s*(?:пункт\w*|вставк\w*|фігур\w*|розділ\w*|слов\w*)/giu;

let bad = 0;
console.log("── ОДНОБІЧНІСТЬ ────────────────────────────────────────────────");
for (const [name, prompt] of Object.entries(calls)) {
  const rows = [];
  for (const [axis, re] of Object.entries(AXES)) {
    const d = (prompt.match(new RegExp(re.down, "g")) || []).length;
    const u = (prompt.match(new RegExp(re.up, "g")) || []).length;
    if (!d && !u) continue;
    const one = (d && !u) || (u && !d);
    if (one) bad++;
    rows.push(`   ${axis.padEnd(18)} вниз ${String(d).padStart(2)} · вгору ${String(u).padStart(2)}${one ? "   ⛔ ОДИН БІК" : ""}`);
  }
  if (rows.length) { console.log(` ${name}`); rows.forEach((r) => console.log(r)); }
}

console.log("\n── ЧИСЛА, ЩО ДОЇЖДЖАЮТЬ ДО АГЕНТА ──────────────────────────────");
const seen = new Map();
for (const [name, prompt] of Object.entries(calls)) {
  for (const re of [ANCHOR, WORDY]) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(prompt))) {
      const key = m[0].trim().replace(/\s+/g, " ");
      if (!seen.has(key)) seen.set(key, new Set());
      seen.get(key).add(name);
    }
  }
}
if (!seen.size) console.log("   немає жодного");
for (const [k, where] of [...seen].sort()) console.log(`   «${k}»`.padEnd(34) + [...where].join(", "));

console.log(`\nоднобічних вимірів: ${bad} · різних чисел у завданнях: ${seen.size}`);
process.exit(bad ? 1 : 0);
