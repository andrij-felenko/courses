#!/usr/bin/env node
/* ============================================================================
   lang.js — МОВА ПРОЗИ: маркер @@ і словник до нього. Локально, нуль токенів.

   МАРКЕР. Чуже слово в прозі позначається інлайново:

       Механізм зветься @@en|garbage collection@@ і працює так…

   `@@` вибрано заміром: 0 влучань на 241.5 млн символів прози в 17 867 файлах
   (`{` дав би 2605, `@` — 1280). `en`, а не `eng`: тоді рушій виводить
   `<i lang="en">`, і браузер правильно переносить і читає вголос. Роздільник `|`
   ділить ЛИШЕ перший раз, тож усередині може бути що завгодно. Маркер не
   переходить на новий рядок — інакше незакритий з'їдав би пів статті.

   ЗНАЧЕННЯ ЖИВЕ ТІЛЬКИ У СЛОВНИКУ (root/dictionary.json). Термін трапляється в
   десятках статей; якби тлумачення стояло в самому маркері, воно б розійшлося.

   ⛔ ЩО ЦЕЙ МАРКЕР НЕ РОЗВ'ЯЗУЄ. Задачу «вся мова українська» — ні. Русизми й
   кальки пишуться кирилицею й до нього стосунку не мають: то окрема перевірка,
   з переліком, а не зі словником. І він НЕ для всієї латиниці: її в прозі
   1.74 млн токенів, і 85% — абревіатури й позначення (API, DMA, Linux, C++,
   ESP32), яким маркер не потрібен.

   ПРАВИЛО, БЕЗ ЯКОГО ЦЕ РОЗПОВЗЕТЬСЯ: маркер ставиться там, де термін УВОДЯТЬ, а
   не на кожній згадці. Інакше стаття про кеш матиме його сорок разів, фон
   рябітиме, і читач перестане його помічати.

   ⚠️ ОБІЦЯНКА «0 ВЛУЧАНЬ» СПРАВДЖУЄТЬСЯ ЛИШЕ ПІСЛЯ ЗРІЗАННЯ ІНЛАЙН-КОДУ. У сирому
   рядку `@@` у корпусі таки є — 63 штуки в 36 файлах, і ВСІ до одної всередині
   backtick-ів: версійні теги ELF (`memcpy@@GLIBC_2.14`), манглінг MSVC, `@@version`
   у SQL. Поза інлайн-кодом — рівно нуль. Тому і пошук маркера, і лік парності `@@`
   ідуть по рядку БЕЗ інлайн-коду й адрес посилань. Доти ця перевірка давала 47
   фальшивих «не закритий», а випадкова пара з'їдала справжній маркер далі в рядку:
   термін не реєструвався, і його запис потім оголошувався сиротою.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const U = require("../local/lib/units.js");
const M7 = require("../../scripts/lib/manifest7.js");

const DICT = path.join(U.CONTENT, "dictionary.json");

const HELP = `
lang — маркер @@ і словник чужих термінів

  node writer_ua/checkers/lang.js [кого] [що робити]

КОГО
  --addr a,b,c      адреси через кому
  (труба)           адреси по одній на рядок — вихід find --ids
  фільтри find      --book --kind --group --chapter --type --status …

ЩО РОБИТИ (--terms --orphans --json взаємовиключні: вивід один)
  (типово)          перевірити: закритість, ключ у словнику, повтор у статті
  --latin           додати підозри на чужі слова БЕЗ маркера
                    (з --terms і --orphans не поєднується — їм нічого додавати)
  --orphans         записи словника, яких ніхто не вживає; ЗАВЖДИ весь корпус,
                    тож із фільтрами й --addr не поєднується
  --terms           перелік ужитих термінів із частотою
  --json            звіт машині

СЛОВНИК
  --add "en|garbage collection" --uk "збирання сміття" --gloss "одне речення"
        [--topic <книга>/<тема>] [--apply]
  --topic звіряється з корпусом: книга й тема мусять справді бути
  --apply без --add писати нічого

ЩО ПЕРЕВІРЯЄТЬСЯ
  ✗ маркер не закритий або перенесений на новий рядок
  ✗ ключа немає у словнику — це бите посилання
  ✗ той самий термін позначено двічі в одній статті
  ⚠ (з --latin) два й більше малих латинських слова поспіль поза маркером

  ⚠ — це СИРИЙ СИГНАЛ ДЛЯ ОЧЕЙ, а не гейт: у коді виходу він не рахується.
  Власну назву від терміна воно відрізняє ЛИШЕ регістром, а юніксові власні назви
  пишуться малими (systemd-nspawn, vfio-pci, virtio-rng) — такі імена модулів і
  програм воно ловитиме й далі, і це не поламка, а межа самого прийому.
`;

/* ── словник ───────────────────────────────────────────────────────────────── */

function loadDict() {
  if (!fs.existsSync(DICT)) return { schema: 1, terms: {} };
  try {
    const d = JSON.parse(fs.readFileSync(DICT, "utf8"));
    d.terms = d.terms || {};
    return d;
  } catch (e) { throw new Error(`словник не читається: ${e.message}`); }
}

function saveDict(d) {
  const tmp = DICT + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(d, null, 2) + "\n", "utf8");
  fs.renameSync(tmp, DICT);
}

/* ── розбір прози ──────────────────────────────────────────────────────────── */

const MARK = /@@([^@\n]*)@@/g;
const OPEN = /@@/g;

/**
 * Рядки файла з ознакою «це проза». Сита ДВА, і вони різні навмисно.
 *
 * Тіла огорож немає в жодному: там і маркер, і латиниця — це код.
 *
 * `prose:false` (таблиця, директива `:::`, рядок-зображення) вимикає лише `--latin`:
 * у комірці таблиці й у шляху `:::code` латиниця законна. А МАРКЕР шукається в таких
 * рядках нарівні з рештою: термін цілком законно вводять у комірці означень, і доти
 * той маркер був невидимий — зі словником не звірявся й ужитим не рахувався.
 */
function scanLines(md) {
  const out = [];
  let inCode = false;
  md.split(/\r?\n/).forEach((line, i) => {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; return; }
    if (inCode) return;
    out.push({ n: i + 1, line, prose: !(/^:::/.test(t) || /^!\[/.test(t) || /^\|.*\|/.test(t)) });
  });
  return out;
}

/** Рядок без інлайн-коду й адрес посилань — там і латиниця, і `@@` законні. */
const noCode = (s) => s.replace(/`[^`]*`/g, " ").replace(/\]\([^)]*\)/g, "] ");

/** …і без самих маркерів: позначене всередині них уже позначене. */
const noMark = (s) => s.replace(/@@[^@\n]*@@/g, " ");

/* ── підозра на чуже слово без маркера ─────────────────────────────────────────
   СЛОВО МОЖЕ МІСТИТИ ДЕФІС, а між словами мусить бути СПРАВЖНІЙ ПРОБІЛ. Доти дефіс
   був прирівняний до пробілу, і один дефісний токен зараховувався як «два слова
   поспіль»: 984 з 3160 підозр `sys-unix` (31%) були `dma-buf`, `blk-mq`, `zero-copy`,
   `read-only`.

   ФРАЗА судиться ЦІЛОЮ, разом із сусідніми латинськими токенами БУДЬ-ЯКОГО регістру.
   Є серед них токен з великої літери чи ВЕРСАЛОМ — це власна назва, цитата або
   повідомлення ОС, і підозра знімається. Доти фраза різалася по великій літері, і
   на очі лягав понівечений уламок: «such file or directory» з `No such file or
   directory`, «many open files» з `Too many open files`, шматки виводу valgrind.

   ⚠️ Чим це НЕ є: гейтом. Регістр — єдина ознака, якою воно відрізняє власну назву
   від терміна, а юніксові власні назви пишуться малими. Тож `systemd-nspawn` і
   `vfio-pci` тут світитимуться завжди — сире сито для очей, і нічого більше. */
const PHRASE = /[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*(?: [A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*)*/g;
const SMALL = /^[a-z]{2,}(?:-[a-z]+)*$/;                 // слово з малих, дефіс усередині дозволено

function latinSuspects(s) {
  const out = [];
  for (const m of s.matchAll(PHRASE)) {
    const tokens = m[0].split(" ");
    if (tokens.some((t) => /[A-Z]/.test(t))) continue;    // власна назва, цитата, повідомлення
    let run = 0;
    for (const t of tokens) {
      if (!SMALL.test(t)) { run = 0; continue; }
      if (++run >= 2) { out.push(m[0]); break; }          // показуємо фразу цілою — уламок нечитний
    }
  }
  return out;
}

/* ── перевірка одного файла ────────────────────────────────────────────────── */

function checkFile(file, dict, opt) {
  const md = fs.readFileSync(file, "utf8");
  const bad = [], used = new Map();

  for (const { n, line, prose } of scanLines(md)) {
    /* І лік парності, і пошук маркера — по рядку БЕЗ інлайн-коду: `@@` у backtick-ах
       (`memcpy@@GLIBC_2.14`, `@@version`) інакше і сам вважався б дефектом, і ковтав
       би справжній маркер далі в рядку. Показуємо при цьому СИРИЙ рядок — людині
       треба бачити те, що лежить у файлі. */
    const text = noCode(line);
    const opens = (text.match(OPEN) || []).length;
    if (opens % 2) bad.push({ line: n, kind: "не закритий", text: line.trim().slice(0, 90) });

    for (const m of text.matchAll(MARK)) {
      const body = m[1];
      const bar = body.indexOf("|");
      if (bar <= 0) { bad.push({ line: n, kind: "нема мови до |", text: m[0] }); continue; }
      const lang = body.slice(0, bar), term = body.slice(bar + 1);
      if (!/^[a-z]{2,3}$/.test(lang)) bad.push({ line: n, kind: `мова «${lang}» не за BCP 47`, text: m[0] });
      if (!term.trim()) { bad.push({ line: n, kind: "порожній термін", text: m[0] }); continue; }
      const key = `${lang}|${term}`;
      if (!dict.terms[key]) bad.push({ line: n, kind: "нема у словнику", text: key });
      used.set(key, (used.get(key) || 0) + 1);
    }

    /* Підозри — лише по прозі: у комірці таблиці й у директиві латиниця законна. */
    if (opt.latin && prose)
      for (const s of latinSuspects(noMark(text)))
        bad.push({ line: n, kind: "латиниця без маркера", text: s, warn: true });
  }

  for (const [key, n] of used)
    if (n > 1) bad.push({ line: 0, kind: `позначено ${n} разів — маркер ставлять там, де термін уводять`, text: key });

  return { bad, used };
}

/* ── головне ───────────────────────────────────────────────────────────────── */

function main(argv) {
  if (argv.includes("--help") || argv.includes("-h")) { console.log(HELP.trim()); return 0; }

  const { flags, rest } = U.parseArgs(argv);
  const opt = { latin: false, orphans: false, terms: false, json: false, apply: false };
  let addrs = null, add = null;
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    const val = () => {
      const v = rest[i + 1];
      if (v === undefined || v.startsWith("--")) throw new Error(`${a} без значення`);
      i++; return v;
    };
    if (a === "--latin") opt.latin = true;
    else if (a === "--orphans") opt.orphans = true;
    else if (a === "--terms") opt.terms = true;
    else if (a === "--json") opt.json = true;
    else if (a === "--apply") opt.apply = true;
    else if (a === "--addr") {
      if (addrs) throw new Error("--addr двічі");
      addrs = val().split(",").map((s) => s.trim()).filter(Boolean);
      if (!addrs.length) throw new Error("--addr порожній");
    } else if (a === "--add") { add = { key: val() }; }
    else if (a === "--uk") { (add || (add = {})).uk = val(); }
    else if (a === "--gloss") { (add || (add = {})).gloss = val(); }
    else if (a === "--topic") { (add || (add = {})).topic = val(); }
    else throw new Error(`невідомий прапорець: ${a}`);
  }

  /* Суперечка режимів розв'язувалася за спиною: `--json --terms` друкував `--terms`,
     `--latin --terms` мовчки викидав `--latin`, `--apply` без `--add` тихо не робив
     нічого. Той самий запобіжник, що у find і count: краще впасти, ніж викинути
     прапорець, який людина набрала свідомо. */
  const modes = [["--terms", opt.terms], ["--orphans", opt.orphans], ["--json", opt.json]]
    .filter(([, on]) => on).map(([name]) => name);
  if (modes.length > 1) throw new Error(`разом не можна: ${modes.join(" ")} — вивід один`);
  if (opt.latin && (opt.terms || opt.orphans))
    throw new Error(`--latin із ${opt.terms ? "--terms" : "--orphans"} не працює: підозри там нікуди додати`);
  if (opt.apply && !add) throw new Error("--apply без --add: записувати нічого — ця команда більше нічого не пише");

  const dict = loadDict();

  /* ── поповнення словника ── */
  if (add) {
    if (!add.key) throw new Error("--add без ключа: потрібне \"<мова>|<термін>\"");
    if (!/^[a-z]{2,3}\|.+/.test(add.key)) throw new Error(`ключ «${add.key}» не за формою <мова>|<термін>`);
    if (!add.uk) throw new Error("--uk: усталений український відповідник обов'язковий");
    if (!add.gloss) throw new Error("--gloss: тлумачення одним реченням обов'язкове");
    if (dict.terms[add.key]) throw new Error(`ключ «${add.key}» у словнику вже є`);
    /* Тему звіряємо з корпусом. Найцінніше в записі — посилання на тему (словник стає
       навігацією), і саме воно писалося наосліп: одруківка давала запис, який мовчки
       нікуди не веде. Адреса — та сама мова, що й усюди: рівно `книга/тема`. */
    if (add.topic) {
      const p = U.parseAddr(add.topic);
      if (!p || p.part) throw new Error(`--topic «${add.topic}»: адреса теми це рівно два сегменти — <книга>/<тема>`);
      const b = M7.books().get(p.book);
      const book = b && M7.loadBook(b.bookDir);
      if (!book) throw new Error(`--topic «${add.topic}»: книги «${p.book}» у корпусі немає`);
      if (!M7.findTopic(book, p.slug)) throw new Error(`--topic «${add.topic}»: теми «${p.slug}» у книзі «${p.book}» немає`);
    }
    const [lang, term] = [add.key.slice(0, add.key.indexOf("|")), add.key.slice(add.key.indexOf("|") + 1)];
    const rec = { lang, term, uk: add.uk, gloss: add.gloss };
    if (add.topic) rec.topic = add.topic;
    console.log(`словник + ${add.key}\n  ${JSON.stringify(rec)}`);
    if (!opt.apply) { console.log("\nсухий прогін — щоб записати, додай --apply"); return 0; }
    dict.terms[add.key] = rec;
    saveDict(dict);
    console.log(`записано у ${path.relative(U.ROOT, DICT)}   термінів: ${Object.keys(dict.terms).length}`);
    return 0;
  }

  /* ── кого перевіряємо ── */
  const pipe = U.stdinAddrs();
  if (addrs && pipe.given && pipe.addrs.length) throw new Error("адреси й труба разом — вибери щось одне");
  const addrMode = !!addrs || pipe.given;
  const hasFilters = Object.keys(flags).length > 0;

  /* Сирота — це «запис, якого НІХТО В КОРПУСІ не вживає», тож звужений відбір відповідає
     не на те питання: `--orphans --book unix` (0.099 с проти 3.98 с) оголошував сиротою
     чинний термін, ужитий в іншій книзі. Обхід усього корпусу тут не розкіш, а означення. */
  if (opt.orphans && (addrMode || hasFilters))
    throw new Error("--orphans дивиться ВЕСЬ корпус — сирота це «ніхто ніде не вживає»; "
      + `звужений відбір (${addrMode ? "--addr чи труба" : "фільтри"}) оголосив би сиротою чинний термін`);

  let units;
  if (addrMode) {
    if (hasFilters) throw new Error("адреси й фільтри разом — вибери щось одне");
    const src = addrs || pipe.addrs;
    if (!src.length) { console.log("адрес не надійшло — перевіряти нічого"); return 0; }
    const got = U.byAddrs(src);
    if (got.ambiguous.length)
      console.error(`lang: неоднозначних адрес пропущено (${got.ambiguous.length}): ${got.ambiguous.map((x) => x.addr).join(", ")}`);
    if (got.missing.length) { console.error(`lang: не знайшлося (${got.missing.length}): ${got.missing.slice(0, 5).join(", ")}`); return 2; }
    units = got.units;
  } else if (hasFilters) {
    U.validate(flags);
    units = U.filter(U.enumerate({ kinds: flags.kinds, books: flags.books }), flags);
  } else if (opt.orphans) units = U.enumerate({});
  else throw new Error("кого перевіряти — дай --addr, трубу з find --ids або фільтри");

  /* Один файл вставки, зареєстрований у маніфесті під двома типами, приходить із
     фільтра двома одиницями на ОДИН файл. Прочитати його двічі означало б подвоїти
     і дефекти, і лік ужитих термінів, тож зводимо — але вголос, як `count` і `find`:
     це вада ДАНИХ корпусу, і мовчазне зведення її ховає. */
  const seen = new Set(), dupes = new Set();
  const files = [];
  for (const u of units) {
    if (u.slug == null) continue;
    const f = U.fileOf(u);
    if (!f || !fs.existsSync(f)) continue;
    if (seen.has(f)) { dupes.add(U.addrOf(u)); continue; }
    seen.add(f); files.push({ addr: U.addrOf(u), file: f });
  }
  if (dupes.size)
    console.error(`lang: увага — повторені адреси зведено до однієї (${dupes.size}): ${[...dupes].join(", ")}`);
  if (!files.length) { console.log("перевіряти нічого — жодного файла на диску"); return 0; }

  const report = [], usedAll = new Map();
  for (const f of files) {
    const { bad, used } = checkFile(f.file, dict, opt);
    for (const [k, n] of used) usedAll.set(k, (usedAll.get(k) || 0) + n);
    if (bad.length) report.push({ ...f, bad });
  }

  if (opt.terms) {
    const rows = [...usedAll].sort((a, b) => b[1] - a[1]);
    if (!rows.length) console.log("маркерів не знайшлося");
    rows.forEach(([k, n]) => console.log(`${String(n).padStart(5)}  ${k}${dict.terms[k] ? "" : "   ← нема у словнику"}`));
    return 0;
  }

  if (opt.orphans) {
    const orphans = Object.keys(dict.terms).filter((k) => !usedAll.has(k));
    console.log(orphans.length ? `сироти словника (${orphans.length}):\n  ` + orphans.join("\n  ") : "сиріт у словнику немає");
    return 0;
  }

  if (opt.json) { console.log(JSON.stringify(report, null, 1)); return report.some((r) => r.bad.some((b) => !b.warn)) ? 1 : 0; }

  const errs = report.reduce((s, r) => s + r.bad.filter((b) => !b.warn).length, 0);
  const warns = report.reduce((s, r) => s + r.bad.filter((b) => b.warn).length, 0);
  for (const r of report) {
    console.log(`\n${r.addr}`);
    for (const b of r.bad)
      console.log(`  ${b.warn ? "⚠" : "✗"} ${b.line ? String(b.line).padStart(4) : "   —"}  ${b.kind}: ${b.text}`);
  }
  console.log(`\nфайлів: ${files.length}   дефектів: ${errs}${opt.latin ? `   підозр: ${warns}` : ""}   термінів ужито: ${usedAll.size}`);
  return errs ? 1 : 0;
}

if (require.main === module) {
  try { process.exit(main(process.argv.slice(2))); }
  catch (e) { console.error("lang: " + e.message); process.exit(2); }
}
module.exports = { main };
