#!/usr/bin/env node
/* ============================================================================
   balance.js — ЩО ЦЕЙ ТЕКСТ ЗМУСИТЬ ЗРОБИТИ. Перевірка ДІЇ, а не доставки.

   Сусідній `delivery.js` питає, чи правило доїхало. Цього мало: доїхати може текст, який
   штовхає рівно в один бік, і тоді агент іде в той бік до впору. Ми на цьому обпеклися
   двічі, і щоразу дізнавались із написаного батчу:

     · обсяг — чотири накази «не бери зайвого» і жодного «не спиняйся»: статті на 620 слів
       при медіані книги 2013;
     · вставки — «від нуля до трьох на тип» прочитано як норму: рівно три в кожній темі,
       два батчі поспіль, ті самі типи.

   Обидві вади видно БЕЗ батчу — просто порахувавши, куди штовхає складений запит. Оце
   тут і рахується.

   ЩО ЛОВИТЬ
     1. ОДНОБІЧНІСТЬ — вимір, у якому в запиті є накази лише в один бік. Це не про
        кількість слів, а про напрямок: один бік без другого завжди виносить у крайність.
     2. АНКЕРИ — будь-яке число величини в тексті, що доїжджає до агента. Заміряно двічі:
        показане число стає ціллю (медіана 2970 при орієнтирі 2950). Числа не заборонені —
        але кожне має бути НАВМИСНИМ, тож усі вони тут перелічені поіменно.

   ⛔ ЧОГО НЕ РОБИТЬ: не судить, чи правило добре. Лише напрямок і числа.

   Ужиток:  node writer_ua/checkers/balance.js
   Вихід:   0 — рівно · 1 — є однобічність
   ========================================================================== */
"use strict";
const P = require("../runners/prompt.js");
const L = require("../runners/local.js");
const A = require("../runners/algorithm.js");

const art = L.unitOf("sf-lang", "static-assert", "article", "ДЕТАЛЬНА");
const of = (t) => ({ ...art, type: t, version: "" });

const calls = {
  "ціль": P.goal(art, { mentions: "", linkable: "Л" }),
  "рівень і вставки": P.scope(art, { goal: "ц", preknow: "П", books: "К" }),
  "каркас": P.karkas(art, { goal: "ц", level: 3, preknow: "П", inserts: "В" }),
  "письмо": P.write(art, { goal: "ц", level: 3, sections: "1", theses: "", inserts: "", passed: "", linkable: "Л", opory: "О" }),
  "дописування": P.extend(art, { goal: "ц", level: 3, section: "1", text: "т", neighbours: "", add: "5 | щ", linkable: "Л" }),
  "стиснення": P.compress(art, { goal: "ц", level: 3, section: "1", text: "т", neighbours: "", squeeze: "щ" }),
  "викладка": P.layout(art, { goal: "ц", level: 3, text: "т", passed: "" }),
  "перепис": P.rewrite(art, { goal: "ц", paragraphs: "т", defect: "д", attempt: 1, maxAttempts: A.MAX_LAYOUT, linkable: "Л" }),
  "каркас math": P.karkas(of("math"), { goal: "ц", level: 3, preknow: "", inserts: "В" }),
  "письмо math": P.write(of("math"), { goal: "ц", level: 3, sections: "1", theses: "", inserts: "", passed: "", linkable: "Л", opory: "" }),
};

/**
 * Виміри, у яких ми вже падали. Для кожного — чим у тексті виглядає штовхання в кожен бік.
 * Пари навмисно грубі: питання не в тонкощах, а в тому, чи є другий бік узагалі.
 */
const AXES = {
  "обсяг": {
    down: /МЕЖІ, а не цілі|надто великі стат|лише важливе або корисне|не ріжемо готовий текст|Стеля — це «більше не можна»|переросла стелю|Прибери/,
    up: /не вичерпана|не менше \d+ слів|Не спиняйся на тому|обірваний|коротший за потрібне/,
  },
  "кількість вставок": {
    down: /не додавай вставку заради|Не рівняйся на кількість|не пришити вставкою|порожньо, якщо нічого/,
    up: /Верхньої межі немає|заводь вставку|чи вистачить матеріалу/,
  },
  "фігури": {
    down: /прикраси не треба|порожньо, якщо не треба/,
    up: /там фігура й потрібна|там вона й потрібна|словами передається важко/,
  },
};

/** Числа величин у тексті, який доїжджає. Кожне має бути навмисним. */
const ANCHOR = /(?:^|[^\d])(\d{1,5})\s*(?:[–—-]\s*(\d{1,5})\s*)?(слів|слова|слово|рядк\w*|пункт\w*|вставк\w*|фігур\w*|розділ\w*|кроків)/gi;
const WORDY = /\b(по одн(?:ій|ому)|три-чотири|дві |три |чотири |п'ять )\s*(?:пункт\w*|вставк\w*|фігур\w*|розділ\w*|слов\w*)/gi;

let bad = 0;
console.log("── ОДНОБІЧНІСТЬ ────────────────────────────────────────────────");
for (const [name, prompt] of Object.entries(calls)) {
  const rows = [];
  for (const [axis, re] of Object.entries(AXES)) {
    const d = (prompt.match(new RegExp(re.down, "g")) || []).length;
    const u = (prompt.match(new RegExp(re.up, "g")) || []).length;
    if (!d && !u) continue;                       // вимір тут не зачеплено — і добре
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
