#!/usr/bin/env node
/* ============================================================================
   formulas.js — ПЕРЕВІРКА ФОРМУЛ. Локально, нуль токенів, без жодного судження
   про математику.

   Судить не зміст, а РОЗМІТКУ: чи доїхала формула до читача цілою. Це два різні
   питання, і друге лагодиться механічно.

   ЩО ЛОВИТЬ

   1. З'ЇДЕНИЙ БЕКСЛЕШ. `\text{…}` перетворюється на `<таб>ext{…}`, коли рядок із
      формулою проходить крізь щось, де `\t` читається як табуляція. Заміряно на
      корпусі: 231 рядок у 24 темах, усі — той самий `\text`. Читач бачить
      літеральне «ext{Base}» замість формули. Так само гинуть `\times`, `\to`,
      `\tau`, `\theta`, `\top`, `\frac` (через `\f`), `\nabla` (через `\n`),
      `\rho`/`\rangle` (через `\r`), `\beta` (через `\b`), `\v…` — усе, де за
      бекслешем стоїть буква, яку мова програмування знає як керівну послідовність.

   2. НЕПАРНИЙ РОЗДІЛЬНИК. Непарна кількість `$$` або непарна кількість одинарних
      `$` у рядку: половина формули лишається текстом, і рідер малює її як прозу.

   3. ПОРОЖНЯ ФОРМУЛА — `$$ $$` чи `$ $`: слід від правки, з якої винесли вміст.

   ⛔ ЧОГО НЕ РОБИТЬ: не судить, чи формула правильна, чи доречна, чи потрібна тут
   узагалі. Це робота письменника й викладки, не сита.

   Ужиток:
     node writer_ua/checkers/formulas.js --book sf-security
     node writer_ua/checkers/formulas.js --addr sf-security/aslr:detailed
     node writer_ua/checkers/formulas.js --book sf-security --fix
   ========================================================================== */
"use strict";
const fs = require("fs");
const U = require("../local/lib/units.js");

const HELP = `
formulas — розмітка формул: з'їдені бекслеші, непарні роздільники, порожні формули

  node writer_ua/checkers/formulas.js [кого] [--fix]

КОГО — ті самі фільтри, що в find:
  --book --kind --group --chapter --type --status --slug --title
  --addr a,b,c            адреси через кому
  (труба)                 адреси по одній на рядок

  --fix                   полагодити те, що лагодиться однозначно (лише бекслеші)
  --limit N               показати перші N файлів із вадами
`;

/* ── з'їдені бекслеші ───────────────────────────────────────────────────────
   Ключ — та сама керівна послідовність, значення — команда TeX, яку з неї з'їли.
   Беремо ЛИШЕ ті, де підміна однозначна: `\t`+«ext{» це завжди `\text{`, бо
   табуляція перед «ext{» у прозі не трапляється. Там, де однозначності немає
   (просто табуляція серед тексту), нічого не чіпаємо й нічого не кажемо. */
const EATEN = [
  ["\t", ["ext{", "imes", "o ", "au", "heta", "op ", "ext ", "ilde"]],
  ["\f", ["rac{", "orall"]],
  ["\n", ["abla", "eq ", "u "]],
  ["\r", ["ho", "angle", "ightarrow"]],
  ["\b", ["eta", "ullet", "igcup", "igcap"]],
  ["\v", ["arepsilon", "arphi", "ec{"]],
  ["\0", ["mega"]],
];

/** Усі місця, де за керівним символом стоїть хвіст відомої команди TeX. */
function eaten(text) {
  const out = [];
  const L = String(text).split(/\r?\n/);
  for (let i = 0; i < L.length; i++)
    for (const [ch, tails] of EATEN)
      for (const tail of tails) {
        let at = -1;
        while ((at = L[i].indexOf(ch + tail, at + 1)) >= 0)
          out.push({ line: i + 1, was: ch + tail, want: "\\" + (ch === "\t" ? "t" : ch === "\f" ? "f" : ch === "\n" ? "n" : ch === "\r" ? "r" : ch === "\b" ? "b" : ch === "\v" ? "v" : "0") + tail });
      }
  return out;
}

/**
 * Непарні роздільники й порожні формули — по рядках.
 *
 * ⚠️ ІНЛАЙНОВИЙ КОД ЗНІМАЄМО ПЕРШИМ. Долар у `` `$v=<version>` `` — це формат хеша
 * PHC, а не роздільник формули; так само `$PATH`, `$2y$10$…`, `$(cmd)`. Без цього
 * сито кричало на статті про хешування паролів, де жодної формули немає.
 */
function delimiters(text) {
  const out = [];
  const L = String(text).split(/\r?\n/);
  let inFence = false, blockOpen = 0;
  for (let i = 0; i < L.length; i++) {
    const raw = L[i];
    if (/^\s*```/.test(raw)) { inFence = !inFence; continue; }
    if (inFence) continue;
    if (/^\s*:::/.test(raw)) continue;
    /* Долар не завжди роздільник. Знімаємо все, де він означає інше, — інакше сито
       кричить там, де формул немає взагалі:
         `$v=<version>`   формат хеша PHC в інлайновому коді
         $(pgrep node)    підстановка оболонки, ${HOME} — теж вона
         $20–50           ціна; долар перед цифрою це гроші, а не математика     */
    const l = raw.replace(/`[^`]*`/g, " ");
    if (/\$\$\s*\$\$/.test(l)) out.push({ line: i + 1, why: "порожня блокова формула $$ $$" });
    blockOpen += (l.match(/\$\$/g) || []).length;
    /* ⚠️ ПОДВІЙНІ ЗНІМАЄМО ПЕРШИМИ, і аж тоді судимо одинарні. Інакше `$$…$$` читається
       як два одинарні поспіль, тобто як порожня формула «$ $», і кожна блокова формула
       корпусу стає вадою. */
    const single = l.replace(/\$\$/g, " ");
    /* ⚠️ ПОРОЖНЮ ФОРМУЛУ ЗНАХОДЯТЬ ПАРУВАННЯМ, А НЕ ВЗІРЦЕМ. Символьно «$ $» усередині
       `$a$ $b$` виглядає так само, як справді порожня формула: у першому випадку це
       закривний долар, пробіл і відкривний, у другому — відкривний і закривний. Тому
       ділимо рядок по доларах: вміст формули лежить на НЕПАРНИХ місцях, проміжки між
       формулами — на парних, і питання лишається тільки до непарних. */
    const parts = single.split("$");
    for (let k = 1; k < parts.length - 1; k += 2)
      if (!parts[k].trim()) { out.push({ line: i + 1, why: "порожня формула $ $" }); break; }
    /* ⚠️ НЕМАТЕМАТИЧНІ ДОЛАРИ СПИСУЄМО ЛИШЕ ЯК ПОРЯТУНОК, а не наперед. Обидві спроби
       зняти їх заздалегідь ламали законні формули: `$0 = \emptyset$` починається з
       долара перед цифрою, а `$(2k+1)^2 = …$` — з долара перед дужкою, і саме їх ми
       й з'їдали, самі роблячи лік непарним. Тож: спершу рахуємо як є; парно — питання
       немає; непарно — пробуємо списати на ціну чи оболонку, і лише якщо й тоді
       непарно, роздільник справді загублено. */
    const odd = (s) => ((s.match(/\$/g) || []).length) % 2;
    if (odd(single)) {
      const rescued = single
        .replace(/\$[({][^)}]*[)}]/g, " ")   // $(cmd), ${HOME} — оболонка
        .replace(/\$(?=\d)/g, " ");          // $20 — ціна
      if (odd(rescued)) out.push({ line: i + 1, why: "непарна кількість одинарних $" });
    }
  }
  if (blockOpen % 2) out.push({ line: 0, why: "непарна кількість $$ у файлі — блок не закрито" });
  return out;
}

/* ── прогін ────────────────────────────────────────────────────────────────── */

function main(argv) {
  if (argv.includes("--help") || argv.includes("-h")) { process.stdout.write(HELP); return 0; }
  const fix = argv.includes("--fix");
  const li = argv.indexOf("--limit");
  const limit = li >= 0 ? Number(argv[li + 1]) : Infinity;
  const rest = argv.filter((a, i) => a !== "--fix" && a !== "--limit" && !(li >= 0 && i === li + 1));

  /* Відбір — спільною мовою `find`: ті самі прапорці, той самий сенс, і адреси з
     труби теж. Свого розбору тут немає й не буде. */
  const { flags } = U.parseArgs(rest);
  const piped = U.stdinAddrs() || [];
  const chosen = piped.length
    ? U.byAddrs(piped).units
    : U.filter(U.enumerate({ kinds: flags.kinds, books: flags.books }), flags);
  const units = chosen.filter((u) => !u.ref);
  if (!units.length) { process.stdout.write("нічого не відібрано\n"); return 0; }

  const seen = new Set();
  let files = 0, badFiles = 0, nEaten = 0, nDelim = 0, fixed = 0, shown = 0;

  for (const u of units) {
    const p = U.fileOf(u);
    if (!p || seen.has(p) || !fs.existsSync(p)) continue;
    seen.add(p); files++;
    let s = fs.readFileSync(p, "utf8");
    const e = eaten(s), d = delimiters(s);
    if (!e.length && !d.length) continue;
    badFiles++; nEaten += e.length; nDelim += d.length;

    if (fix && e.length) {
      for (const x of new Set(e.map((y) => y.was)))
        s = s.split(x).join(e.find((y) => y.was === x).want);
      fs.writeFileSync(p, s, "utf8");
      fixed += e.length;
    }

    if (shown++ < limit) {
      process.stdout.write(`\n${U.addrOf(u) || p}\n`);
      const byWas = new Map();
      for (const x of e) byWas.set(x.want, (byWas.get(x.want) || 0) + 1);
      for (const [want, n] of byWas)
        process.stdout.write(`  з'їдений бекслеш ×${n}: має бути «${want}»${fix ? " — полагоджено" : ""}\n`);
      for (const x of d.slice(0, 5))
        process.stdout.write(`  ${x.line ? "рядок " + x.line + ": " : ""}${x.why}\n`);
      if (d.length > 5) process.stdout.write(`  …ще ${d.length - 5} про роздільники\n`);
    }
  }

  process.stdout.write(`\nфайлів: ${files}   з вадами: ${badFiles}   з'їдених бекслешів: ${nEaten}` +
    `   роздільники: ${nDelim}${fix ? `   полагоджено: ${fixed}` : ""}\n`);
  if (!fix && nEaten) process.stdout.write("бекслеші лагодяться однозначно — додай --fix\n");
  /* Роздільники самі не лагодимо НІКОЛИ: непарний `$` означає або загублений
     роздільник, або долар як валюту, і вгадувати тут дорожче, ніж показати. */
  return badFiles ? 1 : 0;
}

if (require.main === module) {
  try { process.exit(main(process.argv.slice(2))); }
  catch (e) { console.error("formulas: " + e.message); process.exit(3); }
}
module.exports = { eaten, delimiters };
