#!/usr/bin/env node
/* Перевірка 07 — ЧИСЛА: чи підтверджує проза те, що стверджують підписи, вставки
   й друга версія статті.
   Ужиток: node scripts/checks/07-numbers.js <тека теми>

   Беремо ЛИШЕ числа з одиницею (байти, мс, %, Гц, рази…). Голі цілі не беремо:
   на них гейт тоне в шумі й перестає щось означати.

   Три джерела розбіжности, кожне зі своїм змістом:
     (1) підпис під фігурою ↔ проза того самого файлу — фігура не має стверджувати
         числа, якого текст не називає;
     (2) базова ↔ детальна — версії однієї теми не мають розходитись у числах;
     (3) вставка ↔ проза статті — за однаковим сусіднім словом і однією одиницею
         числа мусять збігатися, інакше читач упіймає суперечність. */
"use strict";
const fs = require("fs");
const L = require("./_lib.js");

const DIR = L.resolveDir(process.argv[2]);
if (!DIR) { console.error("Вкажи теку теми (шлях від кореня репо або абсолютний)"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("07", "числа: підписи, версії, вставки ↔ проза", DIR);
if (!T.prose.length) L.pass("у темі немає прози — нема з чим звіряти");

const UNIT = "%|байт(?:и|ів|а)?|біт(?:и|ів|а)?|[кКМГТ]Б|[кМГ]?Гц|мс|мкс|нс|с(?!\\p{L})|хв|год|раз(?:и|ів|у)?|ядер|ядра|потоків|рядків|циклів|тактів|секунд|мілісекунд";
const RE = new RegExp(`(\\d+(?:[.,]\\d+)?)\\s*(${UNIT})`, "gu");

function nums(text) {
  const out = [];
  const src = L.strip(text);
  for (const m of src.matchAll(RE)) {
    const before = src.slice(Math.max(0, m.index - 40), m.index);
    const words = (before.match(/[\p{L}]{3,}/gu) || []).slice(-2).map((w) => w.toLowerCase());
    out.push({ raw: `${m[1]} ${m[2]}`, val: m[1].replace(",", "."), unit: m[2], ctx: words.join(" ") });
  }
  return out;
}
const capsOf = (text) => (text.match(/^\*[^*].*\*$/gm) || []).join("\n");

const items = [];

/* (1) підпис ↔ проза свого файлу */
T.files.forEach((f) => {
  const caps = capsOf(f.text);
  if (!caps.trim()) return;
  const proseOnly = f.text.replace(/^\*[^*].*\*$/gm, "");
  const inProse = new Set(nums(proseOnly).map((x) => x.raw));
  nums(caps).forEach((c) => {
    if (!inProse.has(c.raw))
      items.push({ file: f.file, kind: f.kind, text: `підпис до фігури стверджує «${c.raw}», а проза цього файлу такого числа не називає` });
  });
});

/* (2) базова ↔ детальна */
if (T.basic && T.detailed) {
  const inD = new Set(nums(T.detailed.text).map((x) => x.raw));
  nums(T.basic.text).forEach((b) => {
    if (!inD.has(b.raw))
      items.push({ file: T.basic.file, kind: "basic", text: `базова називає «${b.raw}» (${b.ctx}), а детальна цього числа не має — версії розійшлися` });
  });
}

/* (3) вставка ↔ проза статті: однакове сусіднє слово + одна одиниця, різні значення */
const proseNums = T.prose.flatMap((p) => nums(p.text));
T.inserts.forEach((ins) => {
  nums(ins.text).forEach((i) => {
    if (!i.ctx) return;
    const clash = proseNums.find((p) => p.unit === i.unit && p.ctx && p.ctx === i.ctx && p.val !== i.val);
    if (clash)
      items.push({ file: ins.file, kind: ins.kind, text: `«${i.ctx} ${i.raw}» у вставці проти «${clash.ctx} ${clash.raw}» у статті — те саме поняття, різні числа` });
  });
});

if (!items.length) L.pass("числа з одиницями збігаються між прозою, підписами, версіями і вставками");

L.adjudicate(DIR, items,
  "по кожному пункту: це справді розбіжність — чи два різні виміри, які просто стоять поруч? " +
  "Доказ «ok»: покажи, що числа стосуються різних речей (цитати обох місць). " +
  "Доказ «defect»: скажи, яке з двох правильне і чим доведено (перерахунок, джерело, документація).");
