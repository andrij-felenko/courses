#!/usr/bin/env node
/* ============================================================================
   newtopic.js — покласти НОВУ ТЕМУ В ЧЕРГУ. Маніфесту НЕ чіпає й письма НЕ починає.

   Ужиток:
     node scripts/antigravity/newtopic.js --book unix-linux --kind reference \
          --section devices --slug nvme-namespaces --title "Простори імен NVMe" \
          --why "<чому це окрема тема>" --also <слуг наявної теми, якій це теж потрібне> [--from <тека>]
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
if (!BOOK) { console.error("Ужиток: node scripts/antigravity/newtopic.js --book <книга> --kind <вид> --section <секція> --slug <слуг> --title <назва> --why <навіщо>"); process.exit(3); }

const QDIR = path.join("scripts", "_finish");
const QFILE = path.join(QDIR, `_ag-newtopics-${BOOK}.json`);
const load = () => { try { return JSON.parse(fs.readFileSync(QFILE, "utf8")); } catch { return []; } };

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
const ALSO = (val("also") || "").split(",").map((s) => s.trim()).filter(Boolean);
for (const [n, v] of [["kind", KIND], ["section", SECTION], ["slug", SLUG], ["title", TITLE], ["why", WHY]])
  if (!v) { console.error(`бракує --${n}`); process.exit(3); }
if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(SLUG)) { console.error(`слуг має бути kebab-case без номерів: ${SLUG}`); process.exit(3); }

const MF = path.join(KIND, BOOK, "manifest.js");
if (!fs.existsSync(MF)) { console.error(`нема маніфесту: ${MF}`); process.exit(3); }

/* уже є в маніфесті? */
const mfSrc = fs.readFileSync(MF, "utf8");
if (new RegExp(`slug\\s*:\\s*["']${SLUG}["']`).test(mfSrc)) {
  console.log(`тема «${SLUG}» уже є в маніфесті ${MF} — у чергу не кладемо`);
  process.exit(0);
}

/* ── ОБҐРУНТУВАННЯ: хто ЩЕ по неї прийде ────────────────────────────────────
   Найдорожча помилка черги — не дубль, а розповзання предмета. Стаття про
   відображення Ено чесно спирається на множину Кантора, теорему Такенса й
   підкову Смейла — але заведи їх усі, і книга про хаос затягує половину
   топології. Тому потрібне поняття, по яке прийде не лише ця стаття: назви
   щонайменше одну ВЖЕ НАПИСАНУ тему цієї книги, якій воно теж потрібне, — і
   скрипт перевірить, що така тема справді є в маніфесті. Одна стаття, якій
   щось знадобилось, — це привід сказати два речення в тексті, а не завести тему. */
if (!ALSO.length) {
  console.error(`\n✖ бракує --also: назви ВЖЕ НАПИСАНУ тему цієї книги (крім своєї), якій це поняття теж потрібне.`);
  console.error(`   Не можеш назвати жодної — поняття потрібне лише твоїй статті. Тоді це не тема:`);
  console.error(`   поясни його двома реченнями просто в тексті або віднеси у вставку своєї теки.`);
  console.error(`\n   node scripts/antigravity/newtopic.js … --also <слуг наявної теми>[,<ще один>]`);
  process.exit(5);
}
const unknown = ALSO.filter((s) => !new RegExp(`slug\\s*:\\s*["']${s}["']`).test(mfSrc));
if (unknown.length) {
  console.error(`\n✖ у --also названо теми, яких у ${MF} немає: ${unknown.join(", ")}`);
  console.error(`   Треба слуг НАПИСАНОЇ теми цієї книги, а не тієї, яку ще хтось колись напише.`);
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
   агент не може безсторонньо — тому судить лічильник. */
const CAP = Number(process.env.AG_NEWTOPIC_CAP || 2);
if (FROM) {
  const mine = q.filter((t) => t.from && path.basename(t.from) === path.basename(FROM));
  if (mine.length >= CAP) {
    console.error(`\n✖ СТЕЛЯ: ця стаття вже завела ${mine.length} нові теми, більше не можна.`);
    mine.forEach((t) => console.error(`   • ${t.slug} — ${t.title}`));
    console.error(`\n   Що робити:`);
    console.error(`   • поняття можна пояснити двома реченнями — поясни просто в тексті;`);
    console.error(`   • це грань наявної теми — допиши ту тему, а не заводь нову;`);
    console.error(`   • нова важливіша за котрусь із заведених — заміни:`);
    console.error(`       node scripts/antigravity/newtopic.js … --drop <слуг тієї, що поступається>`);
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

q.push({ section: SECTION, slug: SLUG, title: TITLE, why: WHY, from: FROM, also: ALSO, kind: KIND, dupes, queuedAt: new Date().toISOString() });
fs.writeFileSync(QFILE, JSON.stringify(q, null, 2), "utf8");
console.log(`\n✓ у черзі: [${SECTION}] ${SLUG} — ${TITLE}`);
console.log(`  файл: ${QFILE}  (тем у черзі: ${q.length})`);
console.log(`  маніфест НЕ змінено, письмо НЕ запущено — так і має бути.`);
