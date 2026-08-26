#!/usr/bin/env node
/* Черга ревізії: теми зі статусом recheck, ЧИЇ ТЕКИ СПРАВДІ Є НА ДИСКУ.
 *
 * Навіщо окремий скрипт. Раніше чергу будував дешевий агент: «прочитай manifest.js,
 * поверни перші N тем зі статусом recheck, перевір Bash-ом, що тека існує». На прогоні
 * 2026-08-15 з 120 виданих слугів 32 виявилися вигаданими — page-cache, oom-killer,
 * fork-and-exec: правдоподібні назви тем unix-linux, яких немає ні в маніфесті, ні на
 * диску. Тридцять два редактори-Opus стартували, прочитали канон, пошукали теку й
 * повернули «теки не існує». Читання маніфесту — детермінована робота, і коштувати
 * вона має нуль токенів.
 *
 *   node scripts/claude/review-queue.js --book sys-unix [--limit 120]
 *                                       [--status recheck] [--json <файл>] [--all]
 *
 * Друкує таблицю для людини; з --json кладе на диск масив тек для args.dirs.
 *
 * Другий режим — операції для manifest-patch, теж детерміновано (той самий урок:
 * агент, що складає JSON зі статусами руками, помиляється саме там, де помилку не видно):
 *
 *   node scripts/claude/review-queue.js --book sys-unix \
 *        --ops-done --slugs "a,b,c" --json scripts/_finish/_review-ops-sys-unix.json
 *
 * Пише status-if recheck→done лише для тих версій (basic/detailed), які зараз recheck.
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const _M7 = require(`${ROOT}\\scripts\\lib\\manifest7.js`)
/* BOOKDIR оголошено НИЖЧЕ, після BOOK: доти воно стояло тут і читало BOOK до його
   оголошення — ReferenceError на першому ж рядку, тобто скрипт не стартував узагалі,
   а з ним і вся фаза «Черга» воркфлоу review-batch. */
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 && argv[i + 1] ? argv[i + 1] : d; };
const has = (k) => argv.includes(k);

const BOOK = arg("--book", "");
/* --kind більше не потрібен: вид книги дає shelf.json через manifest7. Аргумент
   ще приймають review-batch/review-apply заради сумісності виклику — тут він не вживався. */
const LIMIT = has("--all") ? Infinity : Number(arg("--limit", 120));
const WANT = arg("--status", "recheck");
const OUT = arg("--json", "");
if (!BOOK) { console.error("треба --book <slug>"); process.exit(2); }

const BOOKDIR = _M7.bookDirOf(BOOK);                                 // v7: вид випливає з книги
if (!BOOKDIR) { console.error("нема книги «" + BOOK + "» у root/ — перевір слуг (root/shelf.json)"); process.exit(2); }
const mf = path.join(BOOKDIR, "manifest.json");

/* v7: маніфест — JSON, розбирає його manifest7. Доти тут стояло `new Function(window, …)`
   над файлом як над .js із `window.__BOOKS__`, а далі розбір форм v6 (modules→chapters→steps
   для курсу, sections→topics для решти). На JSON перше кидає SyntaxError, тож до другого
   не доходило ніколи. Групи й розділи тепер однакові для ВСІХ видів — розгалуження зникло. */
const _book = _M7.loadBook(BOOKDIR);
if (!_book) { console.error("нема маніфесту книги: " + mf); process.exit(2); }
const rows = _M7.allTopics(_book).filter((t) => t.own).map((t) => ({ section: t.group, t: t.node }));

/* ── режим операцій: recheck → done для названих слугів ───────────────────── */
if (has("--ops-done")) {
  const want = new Set(arg("--slugs", "").split(",").map((s) => s.trim()).filter(Boolean));
  if (!want.size) { console.error("треба --slugs \"a,b,c\""); process.exit(2); }
  const TO = arg("--to", "done");
  const ops = []; const missing = [], skipped = [];
  const seen = new Set();
  for (const { t } of rows) {
    if (!want.has(t.slug)) continue;
    seen.add(t.slug);
    for (const ver of ["detailed", "basic"]) {
      const st = (t[ver] || {}).status;
      if (st === WANT) ops.push({ op: "status-if", slug: t.slug, ver, from: WANT, to: TO });
      else if (st && st !== TO) skipped.push(`${t.slug}/${ver}=${st}`);
    }
  }
  for (const s of want) if (!seen.has(s)) missing.push(s);
  console.log(`слугів на вході: ${want.size}   операцій ${WANT}→${TO}: ${ops.length}`);
  if (skipped.length) console.log(`  не в статусі «${WANT}», не чіпаємо: ${skipped.length}  ${skipped.slice(0, 8).join(" ")}`);
  if (missing.length) console.log(`  ✖ нема в маніфесті: ${missing.length}  ${missing.slice(0, 8).join(" ")}`);
  if (!OUT) { console.error("треба --json <файл> для операцій"); process.exit(2); }
  fs.mkdirSync(path.dirname(path.resolve(ROOT, OUT)), { recursive: true });
  fs.writeFileSync(path.resolve(ROOT, OUT), JSON.stringify(ops, null, 2), "utf8");
  console.log(`операції → ${OUT}`);
  process.exit(0);
}

const queue = [], ghosts = [], other = [];
for (const { section, t } of rows) {
  const d = (t.detailed || {}).status, b = (t.basic || {}).status;
  if (d !== WANT && b !== WANT) { other.push(t.slug); continue; }
  /* BOOKDIR тепер АБСОЛЮТНИЙ (його дає manifest7), тож ROOT удруге не приклеюємо —
     доти виходило «<ROOT>\<ROOT>\root\…», тека не знаходилась, і КОЖНА тема падала
     в ghosts як «запис є, тексту нема». */
  const abs = path.join(BOOKDIR, t.slug);
  const rel = path.relative(ROOT, abs).replace(/\\/g, "/");
  /* тека без жодного .md — це запис у маніфесті без тексту, ревізувати нічого */
  const written = fs.existsSync(abs) && fs.readdirSync(abs).some((f) => f.endsWith(".md"));
  (written ? queue : ghosts).push({ rel, slug: t.slug, section, detailed: d, basic: b });
}

const take = queue.slice(0, LIMIT === Infinity ? queue.length : LIMIT);
console.log(`книга ${BOOK}   статус «${WANT}»`);
console.log(`  у маніфесті зі статусом:  ${queue.length + ghosts.length}`);
console.log(`  з них написані на диску:  ${queue.length}`);
console.log(`  запис є, тексту нема:     ${ghosts.length}${ghosts.length ? "  ← у чергу НЕ йдуть" : ""}`);
console.log(`  видано в чергу:           ${take.length}`);
if (ghosts.length) {
  console.log("\nбез тексту на диску:");
  ghosts.slice(0, 40).forEach((g) => console.log(`  ${g.section}/${g.slug}   detailed:${g.detailed} basic:${g.basic}`));
  if (ghosts.length > 40) console.log(`  … ще ${ghosts.length - 40}`);
}
if (OUT) {
  fs.mkdirSync(path.dirname(path.resolve(ROOT, OUT)), { recursive: true });
  /* --with-files: віддаємо ще й перелік файлів теки. Це знімає з кожного редактора
     крок на ls — найдорожчий крок, бо він перший, а роботи в ньому нуль. */
  const payload = has("--with-files")
    ? take.map((x) => ({ dir: x.rel, files: fs.readdirSync(path.join(ROOT, x.rel)).filter((f) => /\.(md|py)$/.test(f)) }))
    : take.map((x) => x.rel);
  fs.writeFileSync(path.resolve(ROOT, OUT), JSON.stringify(payload, null, 2), "utf8");
  console.log(`\nчерга → ${OUT}${has("--with-files") ? " (зі списком файлів)" : ""}`);
}
