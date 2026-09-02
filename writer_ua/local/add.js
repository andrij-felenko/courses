#!/usr/bin/env node
/* ============================================================================
   add.js — ЗАВЕСТИ нову тему, нову вставку або крок-вказівник у наявній книзі.

   ⛔ КНИГУ, ТОМ І КУРС ЗАВОДИТЬ ТІЛЬКИ АВТОР (`writer_ua/rules/structure.md`). Ця команда
   на неіснуючу книгу відповідає відмовою й не пропонує її створити — навіть коли
   підстава очевидна. Групу й розділ УСЕРЕДИНІ наявної книги вона створює сама, ні
   в кого не питаючи: асиметрія навмисна.

   ⚠️ «КНИГА Є» ЗНАЧИТЬ «Є manifest.json». Застав тепер два, і обидва потрібні:
   `writer_ua/lib/manifest.js` не заводить книги НІКОЛИ (немає маніфесту — операції не
   застосовуються), а тут перевірка на `MF.loadBook()` спрацьовує ПЕРШОЮ, до будь-яких
   інших дій, щоб команда сказала це людською фразою, а не звітом писаря.

   ⚠️ ПЕРЕД ЗАВЕДЕННЯМ — ПОПЕРЕДЖЕННЯ ПРО ДУБЛІ. Чотири дублі понять уже зайшли в
   корпус мовчки саме тому, що перед створенням ніхто не подивився. Тут підказки
   `lib/dupes.js` друкуються ЗАВЖДИ і НЕ блокують: об'єднувати чи ні —
   рішення людське. Але побачити його треба до запису, а не після.

   Маніфест пишеться ЛИШЕ через `writer_ua/lib/manifest.js`.

   ЩО СТВОРЮЄТЬСЯ НА ДИСКУ. Нічого — ні темі, ні вставці. Тема за каноном заводиться
   `basic:empty` + `detailed:pending`, тобто файл ще належить написати, і порожній
   стаб лише вдавав би роботу. Вставці стаб теж не потрібен: її ім'я файла тримає
   САМ МАНІФЕСТ у записі `{file,status}`, тож нічого не губиться й без файла. Файл
   пише письменник — ця команда лише заводить запис.

   ⚠️ ЩО САМЕ СТАНЕТЬСЯ, СУДИТЬ ПИСАР МАНІФЕСТУ, А НЕ МИ. Тутешній розбір вирішує лише, які
   операції ми маємо на увазі; наслідки показує звіт від `MF.applyOps(dry:true)` —
   ті самі операції, що потім і запишуться. Інакше вивід був би власним переказом
   чужих правил і розходився б з ними мовчки.
   ========================================================================== */
"use strict";
const U = require("./lib/units.js");
const MF = require("../lib/manifest.js");
const DUP = require("../lib/dupes.js");

const HELP = `
add — завести нову тему, вставку або крок-вказівник у наявній книзі

  node writer_ua/local/add.js --book <книга> [що] [--apply]

ТЕМА
  --topic <слуг> --title "Назва" --group <слуг> --chapter <слуг>
  [--group-title "…"] [--chapter-title "…"]   якщо групи чи розділу ще немає
  [--basic empty|pending]      типово empty
  [--detailed pending|empty]   типово pending
  нова тема має рівно два статуси — empty і pending: писати її ще нікому,
  а обидва empty означали б тему, яка не потрапить у жодну чергу

ВСТАВКА (до наявної теми)
  --insert <тема> --type hist|comp|math|proj|api --file <імʼя.md>
  [--status pending|done|…]    типово pending

КРОК-ВКАЗІВНИК (лише курси)
  --ref <книга>/<тема> --title "Назва" --group <слуг> --chapter <слуг>
  [--group-title "…"] [--chapter-title "…"]

РОЗМІЩЕННЯ
  тема й крок стають У КІНЕЦЬ розділу; переставляння — окрема операція,
  якої поки немає

ЗАПИС
  (типово)   сухий прогін: показує, що з'явиться, і підказки про дублі
  --apply    записати

⛔ Книгу, том і курс ця команда не створює ніколи — це робить тільки автор.
`;

/* Білий перелік ключів. Невідомий довгий прапорець мовчки ковтався: `--detaild empty`
   проходив, і тема заводилася не з тим статусом, ніж просили. Так само, як у find і як
   вимагає units.js: команда мусить упізнати прапорець або впасти. */
const KEYS = new Set([
  "book", "topic", "insert", "ref",
  "title", "group", "chapter", "group-title", "chapter-title",
  "basic", "detailed", "type", "file", "status",
]);

/* Нова тема — це `basic:empty` + `detailed:pending` (`rules/structure.md`) і нічого інше.
   `done` без файла зробив би її в рідері готовою статтею, якої ніхто не писав. */
const NEW_STATUSES = ["empty", "pending"];

/* Прапорці, які має ЦЕЙ режим. Чужий у режимі — така сама мовчазна одруківка, як
   невідомий: `--insert … --title "…"` колись приймався й нічого не означав. */
const OF_MODE = {
  "--topic": ["topic", "title", "group", "chapter", "group-title", "chapter-title", "basic", "detailed"],
  "--insert": ["insert", "type", "file", "status"],
  "--ref": ["ref", "title", "group", "chapter", "group-title", "chapter-title"],
};

/* ── перевірки імен ────────────────────────────────────────────────────────── */

const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/;
const need = (v, what) => { if (!v) throw new Error(`нема ${what}`); return v; };

function checkSlug(s, what) {
  if (!SLUG_RE.test(String(s || ""))) throw new Error(`${what} «${s}» не є слугом: ASCII, малі, дефіси, без номерів у голові`);
  if (/^\d|-\d+$/.test(s)) throw new Error(`${what} «${s}» має номер — номерів у слугах немає ніде`);
  return s;
}

/** Книга є ⟺ у неї є manifest.json. Див. шапку: інакше цю книгу заведе `--apply`. */
function openBook(slug) {
  const shelf = MF.books().get(slug);
  const book = shelf && MF.loadBook(shelf.bookDir);
  if (!book)
    throw new Error(`книги «${slug}» немає (manifest.json не знайдено). Книгу, том і курс заводить ТІЛЬКИ автор — ця команда цього не робить`);
  return { dir: shelf.bookDir, kind: shelf.kind, book };
}

/* ── дублі ─────────────────────────────────────────────────────────────────── */

/**
 * Друкуємо ЗАВЖДИ й не блокуємо. Раніше ці підказки віддавав одноразовий агент,
 * чий stdout нікуди не потрапляв, — а як він іще й помирав, вивід гинув разом із
 * ним. Саме так у корпус мовчки зайшли чотири дублі. Тому й ЗБІЙ підказок тут
 * гучний: мовчазний `catch` відтворював би ту саму поразку.
 */
function warnDupes(slug, book) {
  let hints = [];
  try { hints = DUP.hints(slug, book) || []; }
  catch (e) { console.error(`add: підказки про дублі не спрацювали: ${e.message}`); return; }
  if (!hints.length) return;
  console.error(`\n⚠ МОЖЛИВІ ДУБЛІ ПОНЯТТЯ для «${slug}» (${hints.length}):`);
  for (const h of hints.slice(0, 20)) console.error("   " + h);
  console.error("   Не блокує: об'єднувати чи ні — рішення людське.\n");
}

/* ── розміщення: група й розділ ────────────────────────────────────────────── */

/**
 * Куди кладемо тему чи крок. Групу й розділ команда створює сама, але НАЗВУ їм
 * вигадати не може: без `--group-title` маніфест підставив би слуг замість назви,
 * і це лишилося б у книзі назавжди.
 */
function placement(o, book) {
  const group = checkSlug(need(o.group, "--group"), "слуг групи");
  const chapter = checkSlug(need(o.chapter, "--chapter"), "слуг розділу");
  const gsNew = !MF.groupSlugs(book).has(group);
  const chNew = gsNew || !MF.chapterSlugs(book, group).has(chapter);
  if (gsNew && !o["group-title"]) throw new Error(`групи «${group}» ще немає — дай --group-title`);
  if (chNew && !o["chapter-title"]) throw new Error(`розділу «${chapter}» ще немає — дай --chapter-title`);
  return { group, chapter, gsNew, chNew, where: `${group}/${chapter}${gsNew ? "  (група НОВА)" : chNew ? "  (розділ НОВИЙ)" : ""}` };
}

/* ── головне ───────────────────────────────────────────────────────────────── */

function main(argv) {
  if (argv.includes("--help") || argv.includes("-h") || !argv.length) { console.log(HELP.trim()); return 0; }

  const o = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--apply") { o.apply = true; continue; }
    if (!a.startsWith("--")) throw new Error(`не розумію: ${a}`);
    const key = a.slice(2);
    if (!KEYS.has(key)) throw new Error(`невідомий прапорець: ${a}`);
    const v = argv[i + 1];
    if (v === undefined || v.startsWith("--")) throw new Error(`${a} без значення`);
    /* Порожнє значення мовчки ставало типовим (`--basic ""` → empty) — а це одруківка,
       рівно як `--level ""` в units.js, і мовчки прийняти її означає завести не те. */
    if (!v.trim()) throw new Error(`${a} порожній — це одруківка, а не «як типово»`);
    if (key in o) throw new Error(`${a} двічі`);
    o[key] = v; i++;
  }

  /* Застава про книгу — ПЕРША: далі йдуть дії, що вже читають і пишуть її маніфест. */
  const bookSlug = need(o.book, "--book");
  const { dir: bookDir, kind, book } = openBook(bookSlug);

  const modes = [["--topic", !!o.topic], ["--insert", !!o.insert], ["--ref", !!o.ref]]
    .filter(([, on]) => on).map(([name]) => name);
  if (modes.length > 1) throw new Error(`разом не можна: ${modes.join(" ")} — заводимо щось одне`);
  if (!modes.length) throw new Error("що заводимо — --topic, --insert або --ref");
  const mine = new Set(OF_MODE[modes[0]]);
  const alien = Object.keys(o).filter((k) => k !== "book" && k !== "apply" && !mine.has(k));
  if (alien.length) throw new Error(`${modes[0]} не знає ${alien.map((k) => "--" + k).join(" ")}`);

  const ops = [];
  const plan = [];
  const TAIL = "стає в кінець розділу; переставляння — окрема операція, якої поки немає";

  /* ── нова тема ── */
  if (o.topic) {
    const slug = checkSlug(o.topic, "слуг теми");
    const title = need(o.title, "--title");
    if (MF.findTopic(book, slug)) throw new Error(`тема «${slug}» у книзі вже є`);

    const basic = o.basic || "empty";
    const detailed = o.detailed || "pending";
    for (const [k, v] of [["--basic", basic], ["--detailed", detailed]])
      if (!NEW_STATUSES.includes(v))
        throw new Error(`${k}: новій темі можна лише ${NEW_STATUSES.join(" або ")}, а не «${v}» — файла ще немає, писати її щойно ставимо в чергу`);
    /* Обидва `empty` — тема, яку не візьме жодна черга: заведена й ненаписана назавжди. */
    if (basic === "empty" && detailed === "empty")
      throw new Error("--basic empty і --detailed empty разом: така тема не потрапить у жодну чергу й не буде написана ніколи");

    const at = placement(o, book);
    warnDupes(slug, bookSlug);

    ops.push({
      op: "topic", slug, title, group: at.group, chapter: at.chapter,
      groupTitle: o["group-title"], chapterTitle: o["chapter-title"],
      basic, detailed,
    });
    plan.push(`тема    ${bookSlug}/${slug}   «${title}»`);
    plan.push(`        у ${at.where}`);
    plan.push(`        basic:${basic}  detailed:${detailed}`);
    plan.push(`        ${TAIL}`);
  }

  /* ── нова вставка ── */
  else if (o.insert) {
    const slug = o.insert;
    const t = MF.findTopic(book, slug);
    if (!t) throw new Error(`теми «${slug}» у книзі «${bookSlug}» немає`);
    const type = need(o.type, "--type");
    if (!U.INSERTS.includes(type)) throw new Error(`--type: тип вставки це ${U.INSERTS.join(" ")}`);

    const file = need(o.file, "--file");
    if (!/^[a-z0-9][a-z0-9-]*\.md$/.test(file)) throw new Error(`ім'я «${file}» не за неймингом: <type>-<name>.md`);
    if (!file.startsWith(type + "-")) throw new Error(`ім'я «${file}» має починатися з «${type}-» — так каже нейминг`);
    if ((t.node[type] || []).some((x) => x.file === file)) throw new Error(`вставка «${file}» у темі вже є`);

    const status = o.status || "pending";
    if (!U.STATUSES.includes(status)) throw new Error(`--status: невідомий статус «${status}»`);

    ops.push({ op: "insert", slug, type, file, status });
    plan.push(`вставка ${bookSlug}/${slug}:${file.replace(/\.md$/, "")}   тип ${type}, статус ${status}`);
  }

  /* ── крок-вказівник ── */
  else {
    /* Вказівник буває ЛИШЕ в курсі (CLAUDE.md): у книгоподібному виді стаття — атом,
       і рушій там на `ref` не розрахований. */
    if (kind !== "course") throw new Error(`книга «${bookSlug}» має вид «${kind}» — крок-вказівник буває лише в курсі`);
    const ref = o.ref;
    const seg = ref.split("/");
    if (seg.length !== 2 || !seg[0] || !seg[1])
      throw new Error(`--ref «${ref}»: адреса це рівно два сегменти — <книга>/<тема>, бо групи й розділу в ній немає`);
    const [tBook, tSlug] = seg;
    const target = MF.books().get(tBook);
    const targetBook = target && MF.loadBook(target.bookDir);
    if (!targetBook) throw new Error(`--ref «${ref}»: книги «${tBook}» немає`);
    if (!MF.findTopic(targetBook, tSlug)) throw new Error(`--ref «${ref}»: теми «${tSlug}» у книзі «${tBook}» немає`);

    const title = need(o.title, "--title");
    const at = placement(o, book);

    ops.push({
      op: "ref", ref, title, group: at.group, chapter: at.chapter,
      groupTitle: o["group-title"], chapterTitle: o["chapter-title"],
    });
    plan.push(`крок    ${bookSlug} → ${ref}   «${title}»`);
    plan.push(`        у ${at.where}`);
    plan.push(`        ${TAIL}`);
  }

  console.log(plan.join("\n"));

  /* Ті самі операції спершу насухо — щоб показане число було звітом писаря маніфесту, а не
     нашим передбаченням. Запис іде другим прогоном і звітує вже за себе. */
  const dry = MF.applyOps(bookDir, ops, { dry: true });
  const rep = o.apply ? MF.applyOps(bookDir, ops) : dry;

  /* Непорожній `skipped` — це РОЗХОДЖЕННЯ наміру зі звітом писаря маніфесту, найцінніше у виводі. */
  if (rep.skipped.length) {
    console.log(`\nпропущено (нічого не змінює): ${rep.skipped.length}`);
    rep.skipped.forEach((s) => console.log(`   · ${s}`));
  }
  console.log(o.apply
    ? `\nзаписано: ${rep.changed}`
    : `\nсухий прогін: ${rep.changed} — щоб записати, додай --apply`);

  if (rep.errors.length) { rep.errors.forEach((e) => console.error("add: " + e)); return 1; }
  return 0;
}

if (require.main === module) {
  try { process.exit(main(process.argv.slice(2))); }
  catch (e) { console.error("add: " + e.message); process.exit(2); }
}
module.exports = { main };
