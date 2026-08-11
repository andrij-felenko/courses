#!/usr/bin/env node
/* Перевірка 17 — C І C++, а не «C або C++».
   Ужиток: node scripts/checks/17-cpp.js <тека теми>

   §5 канону: щойно приклад написано мовою C, до нього додається вкладка C++ —
   якщо тільки C++ там не заборонений фізично. Не «на вибір», а обидві.

   Що робить скрипт САМ (детерміновано):
     (1) знаходить кожен C-блок і дивиться, чи є поруч C++ у тому ж :::tabs;
     (2) ловить зворотний бік — вкладку, підписану cpp, у якій насправді C
         (malloc/free/printf і жодної ознаки C++): така вкладка гірша за відсутню.

   Чого скрипт НЕ вирішує: чи випадок підпадає під один із трьох винятків §5
   (простір ядра · приклад про сам C · чужий заголовок як цитата). Це судить агент —
   тому вихід JUDGE, а не DEFECT: механічно відрізнити модуль ядра від утиліти
   простору користувача за текстом блоку не можна, і вгадувати тут шкідливо. */
"use strict";
const L = require("./_lib.js");

const DIR = L.resolveDir(process.argv[2]);
if (!DIR) { console.error("Вкажи теку теми (шлях від кореня репо або абсолютний)"); process.exit(L.USAGE); }
const T = L.readTopic(DIR);
L.head("17", "де є C — має бути й C++", DIR);

const isC = (l) => /^(c|langc)$/i.test(l);
const isCpp = (l) => /^(c\+\+|cpp|cxx)$/i.test(l);

/* Ознаки того, що у вкладці справді C++, а не C з іншим розширенням. */
const CPP_MARKS = /\bstd::|\bnamespace\b|\btemplate\s*<|\bclass\b|\bconstexpr\b|\bnullptr\b|\bauto\s+\w+\s*=|<vector>|<string>|<memory>|<span>|<expected>|~\w+\s*\(\s*\)/;
const C_MARKS = /\bmalloc\s*\(|\bfree\s*\(|\bprintf\s*\(|\bsprintf\s*\(|\bstrcpy\s*\(/;

const items = [];
let cBlocks = 0, paired = 0;

for (const f of T.files) {
  const src = L.read(f.path);
  /* межі :::tabs — щоб знати, які блоки лежать в одному перемикачі */
  const tabs = [];
  const re = /^:::tabs\s*$/gm;
  let m;
  while ((m = re.exec(src))) {
    const end = src.indexOf("\n:::", m.index + 7);
    tabs.push([m.index, end < 0 ? src.length : end]);
  }
  const inSameTabs = (a, b) => tabs.some(([s, e]) => a >= s && a <= e && b >= s && b <= e);

  /* позиції блоків, щоб перевірити сусідство */
  const pos = [];
  const rb = /```([^\n]*)\n([\s\S]*?)```/g;
  let k;
  while ((k = rb.exec(src))) pos.push({ lang: k[1].trim().split(/\s+/)[0], body: k[2], at: k.index, n: pos.length + 1 });

  for (const b of pos) {
    if (isCpp(b.lang) && C_MARKS.test(b.body) && !CPP_MARKS.test(b.body)) {
      items.push(`${f.file} блок #${b.n}: вкладку підписано «${b.lang}», але всередині C `
        + `(malloc/free/printf і жодної ознаки C++). Це гірше за відсутню вкладку — або переписати ідіоматично, або прибрати`);
      continue;
    }
    if (!isC(b.lang)) continue;
    cBlocks++;
    const twin = pos.find((o) => o !== b && isCpp(o.lang) && inSameTabs(b.at, o.at));
    if (twin) { paired++; continue; }
    const head = b.body.split("\n").filter((x) => x.trim()).slice(0, 3).join(" ").slice(0, 110);
    items.push(`${f.file} блок #${b.n}: C без пари C++ → ${head}`);
  }
}

console.log(`  C-блоків: ${cBlocks} · з парою C++: ${paired}`);
if (!items.length) L.pass("кожен C-блок має пару C++ (або C-блоків немає)");

L.adjudicate(DIR, items.map((it) => ({ file: it.split(" ")[0], text: it })),
  "на КОЖЕН пункт дай вирок: це один із трьох винятків §5 — чи вкладки C++ бракує.\n"
  + "  Винятки, і лише вони: простір ядра (модуль, драйвер — там немає ні бібліотеки, ні винятків) ·\n"
  + "  приклад про сам C як мову (препроцесор, ABI, _Generic) · чужий заголовок, показаний як цитата.\n"
  + "  ok — назви, який саме виняток і чим доведено (шлях/include/збірка як модуль).\n"
  + "  defect — скажи, ЧИМ саме вкладка мусить відрізнятись: malloc/free → контейнер чи unique_ptr ·\n"
  + "  close() у goto → RAII · char*+довжина → span/string_view. Писати її буде repair-topic, не ти.\n"
  + "  Окремий вирок ok: після чесного перекладу різнились би лише заголовки — приклад C-шний\n"
  + "  за природою (сирий syscall, POSIX-структура), друга вкладка дала б читачеві копію першої.");

