#!/usr/bin/env node
/* ============================================================================
   newtopic.js — покласти НОВУ ТЕМУ В ЧЕРГУ. Маніфесту НЕ чіпає й письма НЕ починає.

   Ужиток:
     node scripts/antigravity/newtopic.js --book sys-unix \
          --group devices --chapter block-layer \
          --slug nvme-namespaces --title "Простори імен NVMe" \
          --why "<чому це окрема тема>" --meets too-big,key   (треба 2 ознаки з 4)
          [--group-title "<Назва групи>" --group-scope "<про що ця група>"]
          [--chapter-title "<Назва розділу>"]   ← ОБОВ'ЯЗКОВІ, коли групи/розділу ще немає
          [--from <тека статті, що помітила>]   ← --book може бути ІНШОЮ книгою, ніж стаття

   АДРЕСА (канон v7 §1): вид/книга/ГРУПА/РОЗДІЛ/тема. Група й розділ живуть тільки
   в маніфесті — у шляху їх немає, тема лежить пласко: root/<вид>/<книга>/<тема>/.
   Вид не передають: він випливає з книги (root/shelf.json).
     node scripts/antigravity/newtopic.js --book unix-linux --drop <слуг>     (прибрати з черги)
     node scripts/antigravity/newtopic.js --book unix-linux --list

   ЧОМУ ТАК. Тему, яку помітили посеред письма, не можна ні заводити в маніфест
   одразу (маніфест правиться ОДИН раз, наприкінці батчу), ні кидатися писати
   негайно (батч тоді не закінчується ніколи, а черга росте швидше, ніж її
   розбирають). Тому вона лягає в чергу на диск і чекає кінця батчу.

   Дублі: скрипт питає manifest-patch.js у режимі --dry, і той сам каже, чи є
   в книзі близький слуг. Список дублів — не заборона, а привід зупинитись і
   вирішити: нова тема чи розділ у наявній.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const argv = process.argv.slice(2);
const val = (n) => { const i = argv.indexOf("--" + n); return i >= 0 ? argv[i + 1] : null; };
const has = (n) => argv.includes("--" + n);

const BOOK = val("book");
if (!BOOK) { console.error("Ужиток: node scripts/antigravity/newtopic.js --book <книга> --kind <вид> --section <секція> --slug <слуг> --title <назва> --why <навіщо> --meets <ознаки через кому> [--section-title <Назва групи> --section-scope <про що група>]"); process.exit(3); }

const QDIR = path.join("scripts", "_finish");
const QFILE = path.join(QDIR, `_ag-newtopics-${BOOK}.json`);
const load = () => { try { return JSON.parse(fs.readFileSync(QFILE, "utf8")); } catch { return []; } };

/* Відмова мусить лишати слід. 2026-08-15 після підняття планки жодна тема не
   з'явилась у черзі — і з'ясувати, агенти не кликали чи кликали й діставали відмову,
   було нізвідки: скрипт мовчки виходив із кодом. Тепер кожна відмова лягає на диск,
   і наступний батч сам скаже, планка це чи невживаний важіль. */
const RFILE = path.join(QDIR, "_ag-newtopic-refused.json");
const refuse = (why, extra) => {
  let log = []; try { log = JSON.parse(fs.readFileSync(RFILE, "utf8")); } catch { }
  log.push({ when: new Date().toISOString(), book: BOOK, slug: val("slug") || "", from: val("from") || "", why, ...extra });
  try { fs.mkdirSync(QDIR, { recursive: true }); fs.writeFileSync(RFILE, JSON.stringify(log, null, 2), "utf8"); } catch { }
};

if (has("list")) {
  const q = load();
  if (!q.length) { console.log(`черга нових тем для ${BOOK} порожня`); process.exit(0); }
  console.log(`\nчерга нових тем — ${BOOK} (${q.length}):`);
  q.forEach((t, i) => console.log(`  ${i + 1}. [${t.group}/${t.chapter}] ${t.slug} — ${t.title}\n     навіщо: ${t.why}${t.from ? "\n     звідки: " + t.from : ""}`));
  console.log(`\nу маніфест вони підуть наприкінці батчу: node scripts/antigravity/finish-batch.js --book ${BOOK} --kind <вид> --apply`);
  process.exit(0);
}

/* --drop сам по собі: прибрати тему з черги, нічого не заводячи */
if (val("drop") && !val("slug")) {
  const q0 = load();
  const rest = q0.filter((t) => t.slug !== val("drop"));
  if (rest.length === q0.length) { console.error(`теми «${val("drop")}» у черзі немає`); process.exit(3); }
  fs.writeFileSync(QFILE, JSON.stringify(rest, null, 2), "utf8");
  console.log(`з черги прибрано «${val("drop")}» (${q0.length} → ${rest.length})`);
  process.exit(0);
}

const M7 = require("../lib/manifest7.js");
const GROUP = val("group") || val("section");          // --section приймаємо як синонім: звичка з v6
const CHAPTER = val("chapter");
const SLUG = val("slug");
const TITLE = val("title");
const WHY = val("why");
const GROUP_TITLE = val("group-title") || val("section-title");
const GROUP_SCOPE = val("group-scope") || val("section-scope");
const CHAPTER_TITLE = val("chapter-title");
const FROM = val("from") || "";
for (const [n, v] of [["group", GROUP], ["chapter", CHAPTER], ["slug", SLUG], ["title", TITLE], ["why", WHY]])
  if (!v) { console.error(`бракує --${n}`); process.exit(3); }
if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(SLUG)) { console.error(`слуг має бути kebab-case без номерів: ${SLUG}`); process.exit(3); }

/* Слуг має бути такий, щоб на нього надалі НІЧОГО не налізло (AUTHORING §2). Родове
   однослівне ім'я — найдешевший спосіб зробити майбутній дубль. Не блокуємо: `mutex`,
   `vdso`, `dma` — точні терміни, а `cache` чи `memory` — ні, і машина їх не розрізнить. */
if (!SLUG.includes("-")) {
  console.log(`\n⚠ слуг «${SLUG}» однослівний. Це годиться лише для ТОЧНОГО терміна (mutex, vdso).`);
  console.log(`  Родове слово (cache, timers, memory, geometry) — уточни складеним:`);
  console.log(`  cache → cache-eviction-policies · timers → hardware-timer-capture-compare.`);
}

const BOOKDIR = M7.bookDirOf(BOOK);
const MF = BOOKDIR ? path.relative(process.cwd(), path.join(BOOKDIR, "manifest.json")) : `root/<вид>/${BOOK}/manifest.json`;
if (!BOOKDIR) {
  console.error(`
✖ книги «${BOOK}» (${KIND}) не існує: нема ${MF}`);
  console.error(`   ⛔ КНИГУ, ТОМ І КУРС ЗАВОДИТЬ ТІЛЬКИ АВТОР — ні ти, ні цей скрипт.`);
  console.error(`   Спіраль (AUTHORING §2): спершу власна відповідь, тоді звірка з BOOKS.md,`);
  console.error(`   і аж потім — з наявними книгами. Жодна не підходить → клади тему в`);
  console.error(`   НАЙБЛИЖЧУ наявну книгу, а в --why скажи «книги під це немає».`);
  console.error(`   Реєстр пропонованих книг: BOOKS.md у корені репо.
`);
  process.exit(3);
}

/* уже є в маніфесті? */
const BOOKMF = M7.loadBook(BOOKDIR);
if (BOOKMF && M7.findTopic(BOOKMF, SLUG)) {
  console.log(`тема «${SLUG}» уже є в маніфесті ${MF} — у чергу не кладемо`);
  process.exit(0);
}

/* ── ОБҐРУНТУВАННЯ: дві ознаки з чотирьох ────────────────────────────────────
   Планка пройшла три редакції, і кожна ламалась по-своєму.

   Спершу — кон'юнкція з обов'язковим --also («назви іншу тему, якій це теж
   потрібне»). Різала й потрібне: ДРУГИЙ споживач поняття зазвичай зʼявляється
   пізніше за першого, тож вимога «назви сусіда зараз» відмовляла темам лише
   тому, що черга ще не дійшла до сусідів. За цілий батч фізики — нуль тем і
   ПОРОЖНІЙ журнал відмов: до важеля навіть не дотягнулись.

   Потім — три ознаки з пʼяти, і серед них `subject` («поняття в предметі ЦІЄЇ
   книги»). Ця ознака хибна по суті: фізика законно спирається на математику,
   програмування — на алгоритми, і правильна відповідь тут не «відмовити», а
   ЗАВЕСТИ ТЕМУ В ТУ КНИГУ, ЯКІЙ ВОНА НАЛЕЖИТЬ (--book math). Скрипт це вміє:
   черга й маніфест беруться з --book, а не з книги статті.

   Лишилось чотири ознаки, і вистачає ДВОХ. Судить їх сам агент — машина цього
   не вміє. Сенс не в тому, щоб зловити брехню, а в тому, щоб рішення було
   свідомим: назвати дві ознаки важче, ніж не думаючи набрати команду. */
const CRITERIA = {
  "too-big": "пояснити поняття парою речень не вийде — треба механізм, виведення чи приклад\n                 (вміщається — то коротка вставка у своїй теці, а не тема)",
  key: "стаття посилається на нього багато разів, отже воно ключове — йому місце\n                 в preknowlist і в черзі pending",
  eases: "воно важливе для розуміння саме цієї теми: окрема стаття про нього значно\n                 спрощує читання цієї",
  searchable: "читач сам піде шукати його окремо, не читавши цієї статті",
};
const MIN = Number(process.env.AG_NEWTOPIC_MIN || 2);
const claimed = new Set((val("meets") || "").split(",").map((s) => s.trim()).filter(Boolean));
const bad = [...claimed].filter((c) => !CRITERIA[c]);
if (bad.length) { console.error(`✖ невідомі ознаки в --meets: ${bad.join(", ")}`); bad.forEach((b) => claimed.delete(b)); }

if (claimed.size < MIN) {
  console.error(`\n✖ ознак ${claimed.size}, а треба ${MIN} з чотирьох. Перелічи ті, що справді справджуються:`);
  console.error(`   --meets ${Object.keys(CRITERIA).join(",")}`);
  Object.entries(CRITERIA).forEach(([k, v]) => console.error(`     ${claimed.has(k) ? "✓" : " "} ${k.padEnd(11)} — ${v}`));
  console.error(`\n   Менше двох — це не тема: поясни поняття двома реченнями в тексті`);
  console.error(`   або віднеси у вставку своєї теки. Нуль нових тем — нормальний результат.`);
  console.error(`   Поняття з іншої галузі — НЕ привід відмовлятись: заведи його в ту книгу,`);
  console.error(`   якій воно належить (--book math, --book algorithms), і постав лінк.`);
  refuse("few-criteria", { claimed: [...claimed] });
  process.exit(5);
}

/* уже в черзі? */
const q = load();
if (q.some((t) => t.slug === SLUG)) {
  console.log(`тема «${SLUG}» уже в черзі ${QFILE} — нічого не змінено`);
  process.exit(0);
}

/* --drop: прибрати з черги свою ж раніше заведену тему (щоб замінити її важливішою) */
const DROP = val("drop");
if (DROP) {
  const before = q.length;
  const rest = q.filter((t) => t.slug !== DROP);
  if (rest.length === before) { console.error(`теми «${DROP}» у черзі немає`); process.exit(3); }
  fs.writeFileSync(QFILE, JSON.stringify(rest, null, 2), "utf8");
  console.log(`з черги прибрано «${DROP}» (${before} → ${rest.length})`);
  q.length = 0; q.push(...rest);
}

/* СТЕЛЯ: щонайбільше дві нові теми з однієї статті.
   Виміряно 2026-08-15: письменники заводили 2.7 теми на статтю (83 теми з 31 статті);
   черга росла швидше, ніж її розбирають. Стеля 2 знімає приблизно третину — і знімає
   саме хвіст, бо третя й четверта тема з однієї статті майже завжди або грань наявної,
   або те, що чесніше сказати двома реченнями просто в тексті. Судити «чи справді треба»
   агент не може безсторонньо — тому судить лічильник.

   Рахуємо ЛИШЕ те, що ще чекає в черзі. Записи з applied:true — це історія: вони вже
   в маніфесті, і якби вони теж лічилися, стаття, яка колись завела дві теми, була б
   забанена назавжди (саме так 2026-08-15 стеля мовчки замкнула 11 статей фізики). */
const CAP = Number(process.env.AG_NEWTOPIC_CAP || 2);
if (FROM) {
  const mine = q.filter((t) => !t.applied && t.from && path.basename(t.from) === path.basename(FROM));
  if (mine.length >= CAP) {
    console.error(`\n✖ СТЕЛЯ: ця стаття вже завела ${mine.length} нові теми, більше не можна.`);
    mine.forEach((t) => console.error(`   • ${t.slug} — ${t.title}`));
    console.error(`\n   Що робити:`);
    console.error(`   • поняття можна пояснити двома реченнями — поясни просто в тексті;`);
    console.error(`   • це грань наявної теми — допиши ту тему, а не заводь нову;`);
    console.error(`   • нова важливіша за котрусь із заведених — заміни:`);
    console.error(`       node scripts/antigravity/newtopic.js … --drop <слуг тієї, що поступається>`);
    refuse("cap", { queued: mine.map((t) => t.slug) });
    process.exit(4);
  }
}

/* Схожі слуги — по всьому корпусу v7. Чотири сигнали, ті самі, що були в
   manifest-patch: вкладеність по сегментах, збіг без дефісів, спільне РІДКІСНЕ
   слово, той самий слуг в іншій книзі. Не блокує — рішення людське (§6). */
const dupes = M7.dupeHints(SLUG, BOOK);
if (dupes.length) {
  console.log(`\n⚠ МОЖЛИВІ ДУБЛІ ПОНЯТТЯ — глянь, перш ніж заводити нову тему:`);
  dupes.forEach((d) => console.log(`   • ${d}`));
  console.log(`   Те саме поняття — не заводь тему, а допиши наявну.`);
  console.log(`   Схоже, але РІЗНЕ — заводь, і дай ОБОМ точніші назви (§6): оманлива`);
  console.log(`   назва гірша за зайву тему.`);
}

/* Тема може належати ІНШІЙ книзі, ніж стаття, що її помітила: фізика спирається на
   математику, програмування — на алгоритми. Тоді вона лягає в чергу тієї книги й
   чекає її батчу. Скажемо про це вголос, щоб не виглядало помилкою в звіті. */
const fromBook = (FROM.split(/[\\/]/).filter(Boolean)[1] || "");
if (fromBook && fromBook !== BOOK) {
  console.log(`\n↪ тема йде в ЧУЖУ книгу: стаття з «${fromBook}», тема в «${BOOK}».`);
  console.log(`  Це нормальний шлях. Зареєструє її finish-batch книги «${BOOK}» — не твоєї.`);
  console.log(`  Лінк став одразу: root:${BOOK}/${SLUG}.`);
}
/* Нова ГРУПА — твоє рішення, не людське (канон §2, спіраль): книгу заводить автор, групу
   й розділ ти сам. Але заводити її треба ЯВНО: без назви й `scope` finish-batch не має
   чого записати, opTopic лається «нема секції», і тема мовчки не лягає. */
const GROUP_NEW = !BOOKMF || !M7.groupSlugs(BOOKMF).has(GROUP);
const CHAPTER_NEW = GROUP_NEW || !M7.chapterSlugs(BOOKMF, GROUP).has(CHAPTER);
if (GROUP_NEW && (!GROUP_TITLE || !GROUP_SCOPE)) {
  console.error(`\n✖ групи «${GROUP}» у ${MF} ще немає — отже ти її СТВОРЮЄШ.`);
  console.error(`   Це твоє право (книгу заводить автор, групу — ти), але назви її явно:`);
  console.error(`     --group-title "<Назва групи>"   одне-чотири слова, іменникова група.`);
  console.error(`                                       НЕ перелік, НЕ гасло, НЕ «Основи чогось»,`);
  console.error(`                                       НЕ двокрапка з поясненням, НЕ «Інше».`);
  console.error(`     --group-scope "<про що ця група>"  одне речення ПРО ГРУПУ, не про тему.`);
  console.error(`                                       Погано: «Це тема про кеш, тому Кеш».`);
  console.error(`                                       Добре:  «Сюди все, де відповідь беруть із`);
  console.error(`                                                копії замість першоджерела».`);
  console.error(`   Якщо ж група насправді ПОТРІБНА наявна — назви наявну в --group.\n`);
  refuse("group-unnamed", { group: GROUP });
  process.exit(6);
}
if (CHAPTER_NEW && !CHAPTER_TITLE) {
  console.error(`\n✖ розділу «${CHAPTER}» ще немає — назви його: --chapter-title "<Назва розділу>"`);
  console.error(`   Розділ — ЕТАП РОБОТИ, а не дисципліна (§1), і мусить мати вагу:`);
  console.error(`   тонку тему кладуть туди, де вона важить, а не роблять із неї розділ.\n`);
  refuse("chapter-unnamed", { group: GROUP, chapter: CHAPTER });
  process.exit(6);
}
if (GROUP_NEW) {
  console.log(`\n＋ НОВА ГРУПА «${GROUP}» — ${GROUP_TITLE}`);
  if (GROUP_SCOPE.toLowerCase().includes(TITLE.toLowerCase()))
    console.log(`  ⚠ scope переказує назву теми. Він має казати про ГРУПУ — що сюди лягає взагалі.`);
}
if (CHAPTER_NEW) console.log(`＋ НОВИЙ РОЗДІЛ «${CHAPTER}» — ${CHAPTER_TITLE}`);
if (GROUP_NEW || CHAPTER_NEW) console.log(`  Заведе їх finish-batch у тому ж проході, що й тему.`);

q.push({ group: GROUP, chapter: CHAPTER, slug: SLUG, title: TITLE, why: WHY, from: FROM, meets: [...claimed], dupes,
         ...(GROUP_NEW ? { groupTitle: GROUP_TITLE, groupScope: GROUP_SCOPE } : {}),
         ...(CHAPTER_NEW ? { chapterTitle: CHAPTER_TITLE } : {}),
         queuedAt: new Date().toISOString() });
fs.writeFileSync(QFILE, JSON.stringify(q, null, 2), "utf8");
console.log(`\n✓ у черзі: [${GROUP}/${CHAPTER}] ${SLUG} — ${TITLE}`);
console.log(`  файл: ${QFILE}  (тем у черзі: ${q.length})`);
console.log(`  маніфест НЕ змінено, письмо НЕ запущено — так і має бути.`);
