#!/usr/bin/env node
/* ============================================================================
   newtopic.js — покласти НОВУ ТЕМУ В ЧЕРГУ. Маніфесту НЕ чіпає й письма НЕ починає.

   Ужиток:
     node scripts/antigravity/newtopic.js --book unix-linux --kind reference \
          --section devices --slug nvme-namespaces --title "Простори імен NVMe" \
          --why "<чому це окрема тема>" --meets too-big,key   (треба 2 ознаки з 4)
          [--from <тека статті, що помітила>]   ← --book може бути ІНШОЮ книгою, ніж стаття
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
if (!BOOK) { console.error("Ужиток: node scripts/antigravity/newtopic.js --book <книга> --kind <вид> --section <секція> --slug <слуг> --title <назва> --why <навіщо> --meets <ознаки через кому>"); process.exit(3); }

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
  q.forEach((t, i) => console.log(`  ${i + 1}. [${t.section}] ${t.slug} — ${t.title}\n     навіщо: ${t.why}${t.from ? "\n     звідки: " + t.from : ""}`));
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

const KIND = val("kind") || "book";
const SECTION = val("section");
const SLUG = val("slug");
const TITLE = val("title");
const WHY = val("why");
const FROM = val("from") || "";
for (const [n, v] of [["kind", KIND], ["section", SECTION], ["slug", SLUG], ["title", TITLE], ["why", WHY]])
  if (!v) { console.error(`бракує --${n}`); process.exit(3); }
if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(SLUG)) { console.error(`слуг має бути kebab-case без номерів: ${SLUG}`); process.exit(3); }

const MF = path.join(KIND, BOOK, "manifest.js");
if (!fs.existsSync(MF)) {
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
const mfSrc = fs.readFileSync(MF, "utf8");
if (new RegExp(`slug\\s*:\\s*["']${SLUG}["']`).test(mfSrc)) {
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

/* що скаже manifest-patch про схожі слуги (нічого не пишемо: --dry) */
const op = JSON.stringify([{ op: "topic", section: SECTION, slug: SLUG, title: TITLE, basic: "empty", detailed: "pending" }]);
const tmp = path.join(QDIR, `_ag-dupecheck-${BOOK}.json`);
fs.mkdirSync(QDIR, { recursive: true });
fs.writeFileSync(tmp, op, "utf8");
let dryOut = "";
try { dryOut = execSync(`node scripts/manifest-patch.js "${MF}" --ops "${tmp}" --dry`).toString(); }
catch (e) { dryOut = ((e.stdout || "") + (e.stderr || "")).toString(); }
try { try { fs.unlinkSync(tmp); } catch {} } catch {}
const dupes = dryOut.split(/\r?\n/).filter((l) => /•/.test(l)).map((l) => l.trim());
if (/МОЖЛИВІ ДУБЛІ/.test(dryOut)) {
  console.log(`\n⚠ МОЖЛИВІ ДУБЛІ ПОНЯТТЯ — глянь, перш ніж заводити нову тему:`);
  dupes.forEach((d) => console.log(`   ${d}`));
  console.log(`   Якщо це те саме поняття — не заводь тему, а допиши наявну.`);
}

/* Тема може належати ІНШІЙ книзі, ніж стаття, що її помітила: фізика спирається на
   математику, програмування — на алгоритми. Тоді вона лягає в чергу тієї книги й
   чекає її батчу. Скажемо про це вголос, щоб не виглядало помилкою в звіті. */
const fromBook = (FROM.split(/[\\/]/).filter(Boolean)[1] || "");
if (fromBook && fromBook !== BOOK) {
  console.log(`\n↪ тема йде в ЧУЖУ книгу: стаття з «${fromBook}», тема в «${BOOK}».`);
  console.log(`  Це нормальний шлях. Зареєструє її finish-batch книги «${BOOK}» — не твоєї.`);
  console.log(`  Лінк став одразу: topic:${BOOK}/${SLUG}.`);
}
if (!new RegExp(`slug\\s*:\\s*["']${SECTION}["']`).test(mfSrc))
  console.log(`⚠ секції «${SECTION}» у ${MF} немає — finish-batch не зможе покласти туди тему.\n  Назви наявну секцію цієї книги або скажи людині, що потрібна нова.`);

q.push({ section: SECTION, slug: SLUG, title: TITLE, why: WHY, from: FROM, meets: [...claimed], kind: KIND, dupes, queuedAt: new Date().toISOString() });
fs.writeFileSync(QFILE, JSON.stringify(q, null, 2), "utf8");
console.log(`\n✓ у черзі: [${SECTION}] ${SLUG} — ${TITLE}`);
console.log(`  файл: ${QFILE}  (тем у черзі: ${q.length})`);
console.log(`  маніфест НЕ змінено, письмо НЕ запущено — так і має бути.`);
