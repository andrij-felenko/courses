#!/usr/bin/env node
/* ============================================================================
   finish-batch.js — ЄДИНЕ місце, де батч Antigravity торкається маніфесту.
   І торкається лише тоді, коли ВСІ теми батчу пройшли всі 17 перевірок.

   Ужиток:
     node scripts/antigravity/finish-batch.js --book unix-linux --kind reference          (звіт)
     node scripts/antigravity/finish-batch.js --book unix-linux --kind reference --apply  (запис)
     …  [--batch scripts/_finish/_batch-<книга>.json]   (дефолт саме цей файл)

   Список тем батчу — простий JSON: ["reference/unix-linux/devices/xyz", …]
   або {topics:[…]}. Його кладе оркестратор на старті батчу.

   Що робить:
     1. Ганяє gate.js по кожній темі. Хоч одна не готова → НІЧОГО не пише.
     2. Складає операції з ДИСКУ (диск — джерело правди: агент міг дописати
        вставку, про яку в журналі нічого нема):
          детальна на диску  → detailed: recheck
          базова на диску    → basic: recheck
          базової нема       → basic: pending → empty (лише якщо стояло pending)
          кожна вставка      → insert … recheck
        Саме recheck, а не done: конвеєр свою частину скінчив, але людина тексту
        ще не бачила. Рушій показує такі статті як чернетку — вони читаються й
        лишаються на очах. У done переводить людина. Перекрити: AG_WRITTEN_STATUS.
     3. Додає теми з черги scripts/_finish/_ag-newtopics-<книга>.json як
        basic:empty + detailed:pending — і позначає чергу відпрацьованою.
     4. Кличе manifest-patch.js (він валідує результат і сам відмовиться псувати файл).
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const argv = process.argv.slice(2);
const val = (n) => { const i = argv.indexOf("--" + n); return i >= 0 ? argv[i + 1] : null; };
const APPLY = argv.includes("--apply");
const M7 = require("../lib/manifest7.js");
const BOOK = val("book"), KIND = val("kind") || "book";   // KIND лишається для звіту: вид тепер випливає з книги
if (!BOOK) { console.error("Ужиток: node scripts/antigravity/finish-batch.js --book <книга> --kind <вид> [--apply]"); process.exit(3); }

const BOOKDIR = M7.bookDirOf(BOOK);
if (!BOOKDIR) { console.error(`нема книги «${BOOK}» у root/ — перевір слуг (root/shelf.json)`); process.exit(3); }
const MF = path.relative(process.cwd(), path.join(BOOKDIR, "manifest.json"));

const BATCH = val("batch") || path.join("scripts", "_finish", `_batch-${BOOK}.json`);
let dirs = [];
try {
  const j = JSON.parse(fs.readFileSync(BATCH, "utf8"));
  const list = Array.isArray(j) ? j : (j.topics || j.units || []);
  dirs = list.map((x) => (typeof x === "string" ? x : x.dir)).filter(Boolean);
} catch (e) { console.error(`не прочитати список батчу ${BATCH}: ${e.message}`); process.exit(3); }
if (!dirs.length) { console.error(`порожній список батчу: ${BATCH}`); process.exit(3); }

/* ── замок: другий finish-batch паралельно не запускаємо ─────────────────────
   Кожен прогін — сотні запусків node. Два одночасно не подвоюють швидкість, а
   ділять машину (заміряно: п'ять паралельних прогонів → тема замість ~30 с іде 55).
   Замок спільний із gate.js; дитині кажемо, що він уже наш, щоб вона не впиралась. */
const LOCK = path.join("scripts", "_finish", "_gate.lock");
const alive = (pid) => { try { process.kill(pid, 0); return true; } catch { return false; } };
try {
  const j = JSON.parse(fs.readFileSync(LOCK, "utf8"));
  if (alive(j.pid) && Date.now() - j.at < 3 * 3600e3) {
    console.error(`
✖ прогін по батчу вже йде: pid ${j.pid}, тем ${j.topics}, стартував ${new Date(j.at).toLocaleTimeString()}`);
    console.error(`  Дочекайся його або зніми той процес — паралельно буде тільки повільніше.`);
    process.exit(1);
  }
} catch { }
fs.mkdirSync(path.dirname(LOCK), { recursive: true });
fs.writeFileSync(LOCK, JSON.stringify({ pid: process.pid, at: Date.now(), topics: dirs.length }), "utf8");
process.on("exit", () => { try { const j = JSON.parse(fs.readFileSync(LOCK, "utf8")); if (j.pid === process.pid) fs.unlinkSync(LOCK); } catch { } });
process.env.GATE_LOCK_INHERITED = "1";

/* ── 1. гейт ───────────────────────────────────────────────────────────────── */
console.log(`\n=== ГЕЙТ: ${dirs.length} тем батчу ${BOOK} ===`);
let gateCode = 0, gateOut = "";
try { gateOut = execSync(`node scripts/checks/gate.js --topics ${dirs.map((d) => `"${d}"`).join(" ")} --quiet --cache`, { maxBuffer: 64 * 1024 * 1024, timeout: 3600000, killSignal: "SIGKILL" }).toString(); }
catch (e) { gateCode = e.status || 1; gateOut = ((e.stdout || "") + (e.stderr || "")).toString(); }
console.log(gateOut.split(/\r?\n/).filter((l) => /готово|у роботі|ЗАСТІЙ|готових тем/.test(l)).join("\n"));
if (gateCode !== 0) {
  console.error(`\n✖ МАНІФЕСТ НЕ ЧІПАЄМО: не всі теми пройшли гейт (код ${gateCode}).`);
  console.error(`  Доробити перелічене вище й прогнати finish-batch знову.`);
  process.exit(1);
}
console.log(`✓ усі ${dirs.length} тем пройшли всі 17 перевірок`);

/* Статус, який дістає щойно написане. НЕ "done": конвеєр закінчив свою частину, але текст
   ще не бачила людина, а «написано» і «перевірено» — різні речі. "recheck" означає рівно це:
   стаття читається (рушій показує її як чернетку), лишається в полі зору й чекає людського
   ока. У "done" її переводить людина, а не батч. */
const WRITTEN_STATUS = process.env.AG_WRITTEN_STATUS || "recheck";

/* ── 2. операції з диску ─────────────────────────────────────────────────────
   Тема в v7 лежить ПЛАСКО: root/<вид>/<книга>/<тема>/ — групи й розділу в шляху
   немає, вони тільки в маніфесті. Тому «секцію з теки» більше не вгадуємо: для
   вже записаної теми адресу знає маніфест, для нової — черга newtopic.js.        */
const ops = [];
const seen = [];
const unaddressed = [];
const book0 = M7.loadBook(BOOKDIR);
const known = new Map();                       // слуг → {group, chapter}
if (book0) for (const t of M7.allTopics(book0)) if (t.own) known.set(t.slug, { group: t.group, chapter: t.chapter });

for (const dir of dirs) {
  const slug = path.basename(dir);
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
  const hasD = files.includes(`${slug}-d.md`);
  const hasB = files.includes(`${slug}.md`);
  const inserts = files.filter((f) => /^(hist|comp|math|proj|api)-/.test(f));

  if (!known.has(slug)) {
    /* Написана тема, якої немає в маніфесті. Адресу взяти нізвідки — у шляху її
       більше немає. Кладемо в чергу «без адреси» й кажемо вголос: заводити тему
       наосліп у випадкову групу гірше, ніж не завести. */
    unaddressed.push(slug);
    continue;
  }
  const a = known.get(slug);
  if (hasD) ops.push({ op: "status", slug, ver: "detailed", status: WRITTEN_STATUS });
  if (hasB) ops.push({ op: "status", slug, ver: "basic", status: WRITTEN_STATUS });
  else ops.push({ op: "status-if", slug, ver: "basic", from: "pending", to: "empty" });
  inserts.forEach((f) => ops.push({ op: "insert", slug, type: f.split("-")[0], file: f, status: WRITTEN_STATUS }));
  seen.push(`${slug} [${a.group}/${a.chapter}]: детальна ${hasD ? WRITTEN_STATUS : "—"} · базова ${hasB ? WRITTEN_STATUS : "empty"} · вставок ${inserts.length}`);
}

/* ── 3. черга нових тем ──────────────────────────────────────────────────────
   Кожен запис несе повну адресу (група + розділ) і, коли їх ще немає, назви для
   них. applyOps створить групу й розділ САМ — саме цього не вміла жодна ланка v6,
   через що тема з новою групою тихо гинула.                                     */
const QDIRP = path.join("scripts", "_finish");
const QFILE = path.join(QDIRP, `_ag-newtopics-${BOOK}.json`);
let queue = [];
try { queue = JSON.parse(fs.readFileSync(QFILE, "utf8")); } catch { }
const fresh = queue.filter((t) => !t.applied);
fresh.forEach((t) => ops.push({
  op: "topic", group: t.group, chapter: t.chapter, slug: t.slug, title: t.title,
  basic: "empty", detailed: "pending",
  groupTitle: t.groupTitle, groupScope: t.groupScope, chapterTitle: t.chapterTitle,
}));

if (unaddressed.length) {
  console.log(`\n⚠ НАПИСАНО, АЛЕ АДРЕСИ НЕМА (${unaddressed.length}) — статуси НЕ запишемо:`);
  unaddressed.forEach((s) => console.log(`     • ${s}`));
  console.log(`  Тема є на диску, але її немає в маніфесті, а група й розділ у шлях не входять,`);
  console.log(`  тож вгадати адресу нізвідки. Заведи її явно:`);
  console.log(`    node scripts/antigravity/newtopic.js --book ${BOOK} --group <група> --chapter <розділ> …`);
}

console.log(`\n=== ЩО ЗАПИСУЄМО ===`);
seen.forEach((s) => console.log("  " + s));
if (fresh.length) {
  console.log(`  нові теми з черги (у чергу письма підуть ДЕТАЛЬНІ, наступним батчем):`);
  fresh.forEach((t) => console.log(`    + [${t.group}/${t.chapter}] ${t.slug} — ${t.title}   ← ${t.why}`));
} else console.log("  нових тем у черзі немає");


/* ── Одне поняття, пояснене у вставках кількох тем ───────────────────────────
   §6: вставка розширює свою тему, а не пояснює чужу; назване поняття, пояснене
   вставкою вдруге, — це тема. Але автор виконати це правило сам не може: під час
   письма маніфест не чіпається, у чужу теку заходити не можна, і сестринські теми
   того самого батчу для нього невидимі. Крос-темовий погляд є рівно тут — у батчі,
   що бачить усі теки одразу.

   Судимо за заголовком H1 вставки: власне ім'я, якого немає в назві теми. Скрипт
   лише ПОКАЗУЄ — відрізнити «протокол, що заслуговує теми» від «діяча в історії»
   машина не вміє, і мовчки заводити теми за неї не можна. */
const insName = {};
for (const dir of dirs) {
  const topic = path.basename(dir);
  const words = topic.replace(/-/g, " ").toLowerCase();
  let files = [];
  try { files = fs.readdirSync(dir); } catch { continue; }
  for (const f of files) {
    if (!/^(hist|comp|math|proj|api)-.*\.md$/.test(f)) continue;
    let h1 = "";
    try { h1 = (fs.readFileSync(path.join(dir, f), "utf8").match(/^#\s+(.+)$/m) || [, ""])[1]; } catch { continue; }
    const names = [...new Set(h1.replace(/[^\p{L}\p{N}\s+.-]/gu, " ").match(/[A-Z][A-Za-z0-9+.-]{3,}/g) || [])];
    for (const n of names) {
      if (words.includes(n.toLowerCase())) continue;
      (insName[n] = insName[n] || []).push({ topic, f });
    }
  }
}
const doubled = Object.entries(insName).filter(([, v]) => new Set(v.map((x) => x.topic)).size >= 2);
if (doubled.length) {
  console.log(`
  ⚠ ОДНЕ ПОНЯТТЯ — ВСТАВКИ В КІЛЬКОХ ТЕМАХ БАТЧУ (§6):`);
  doubled.forEach(([n, v]) => console.log(`     «${n}» у ${new Set(v.map((x) => x.topic)).size} темах: ${v.map((x) => x.topic + "/" + x.f).join(", ")}`));
    console.log(`     Заведи через newtopic.js і лиши у вставках по реченню з лінком.`);
}

let refused = [];
try { refused = JSON.parse(fs.readFileSync(path.join("scripts", "_finish", "_ag-newtopic-refused.json"), "utf8")); } catch { }
const mine = refused.filter((r) => r.book === BOOK);
const byWhy = {};
mine.forEach((r) => (byWhy[r.why] = (byWhy[r.why] || 0) + 1));
const elsewhere = [];
for (const f of fs.existsSync(path.join("scripts", "_finish")) ? fs.readdirSync(path.join("scripts", "_finish")) : []) {
  const m = f.match(/^_ag-newtopics-(.+)\.json$/);
  if (!m || m[1] === BOOK) continue;
  try {
    JSON.parse(fs.readFileSync(path.join("scripts", "_finish", f), "utf8"))
      .filter((t) => !t.applied && t.from && t.from.includes(`/${BOOK}/`))
      .forEach((t) => elsewhere.push(`${m[1]}/${t.slug}`));
  } catch { }
}

console.log(`  важіль newtopic: заведено ${fresh.length} · відмовлено ${mine.length}${mine.length ? " (" + Object.entries(byWhy).map(([k, v]) => `${k}: ${v}`).join(", ") + ")" : ""}`);
if (elsewhere.length) console.log(`  теми, віддані ІНШИМ книгам: ${elsewhere.join(", ")}`);

if (fresh.length === 0 && mine.length === 0 && dirs.length >= 5) {
  console.log(`\n  ⚠ ВАЖІЛЬ НЕ ВЖИВАЛИ: на ${dirs.length} написаних тем нуль заведених і нуль відмов.`);
  console.log(`    Це не «книга закрита» — це означає, що newtopic.js не кликали жодного разу.`);
  console.log(`    Планка низька навмисно: ДВІ ознаки з чотирьох (too-big · key · eases · searchable),`);
  console.log(`    і поняття чужої галузі не відкидають, а заводять у ЙОГО книгу (--book math).`);
  console.log(`    Перечитай кілька написаних статей і спитай: на що вони спираються мовчки?`);
  console.log(`    Нуль — законна відповідь, але тільки після того, як питання поставлено.`);
} else if (dirs.length >= 10 && fresh.length === 0) {
  console.log(`  ⚠ нуль заведених при ${mine.length} відмовах — важіль вживали, планка не пустила.`);
  console.log(`    Подивись у scripts/_finish/_ag-newtopic-refused.json, чи справедливо.`);
}

/* ── 4. маніфест ─────────────────────────────────────────────────────────────
   Пишемо через manifest7: JSON парситься й серіалізується, тож редагування
   безпечне за побудовою — на відміну від v6, де manifest-patch правив ТЕКСТ
   JS-файла рядок за рядком і мусив сам стежити за комами.                        */
console.log(`\n=== МАНІФЕСТ (${APPLY ? "ЗАПИС" : "DRY — нічого не пишемо"}) ===`);
const rep = M7.applyOps(BOOKDIR, ops, { dry: !APPLY });
console.log(`  ${MF}`);
console.log(`  груп +${rep.group || 0} · розділів +${rep.chapter || 0} · тем +${rep.topic || 0} · статусів ${rep.status || 0} · вставок ${rep.insert || 0}`);
if ((rep.skipped || []).length) {
  console.log(`  пропущено (уже так): ${rep.skipped.length}`);
  rep.skipped.slice(0, 10).forEach((s) => console.log(`     · ${s}`));
}
if ((rep.errors || []).length) {
  console.error(`\n✖ помилок ${rep.errors.length} — маніфест не змінено`);
  rep.errors.forEach((e) => console.error(`     ✖ ${e}`));
  process.exit(4);
}


if (APPLY && fresh.length) {
  fresh.forEach((t) => { t.applied = true; t.appliedAt = new Date().toISOString(); });
  fs.writeFileSync(QFILE, JSON.stringify(queue, null, 2), "utf8");
  console.log(`  чергу нових тем позначено відпрацьованою: ${QFILE}`);
}

/* ── 5. теми, віддані ЧУЖИМ книгам ──────────────────────────────────────────
   Поняття з іншої галузі заводять у ту книгу, якій воно належить: стаття з фізики
   кладе тему в math, з unix-linux — в electronics. Досі така тема лягала в чергу
   чужої книги й чекала ЇЇ батчу — а якщо тієї книги Antigravity не пише взагалі
   (electronics і programming пише Клод), вона не реєструвалася ніколи, і лінк на неї
   лишався висіти. Тому цей батч реєструє й їх: одна атомарна topic-операція на книгу,
   тим самим manifest-patch, який сам валідує результат і відмовиться псувати файл.

   Межа: секція мусить існувати в маніфесті книги-господаря. Немає — тему лишаємо в
   черзі й кажемо вголос, бо вигадувати секцію в чужій книзі не наша справа. */
const foreign = {};
for (const f of fs.existsSync(QDIRP) ? fs.readdirSync(QDIRP) : []) {
  const m = f.match(/^_ag-newtopics-(.+)\.json$/);
  if (!m || m[1] === BOOK) continue;
  let q = []; try { q = JSON.parse(fs.readFileSync(path.join(QDIRP, f), "utf8")); } catch { continue; }
  const mineHere = q.filter((t) => !t.applied && t.from && t.from.includes(`/${BOOK}/`));
  if (mineHere.length) foreign[m[1]] = { file: path.join(QDIRP, f), all: q, take: mineHere };
}
if (Object.keys(foreign).length) {
  console.log(`\n=== ТЕМИ, ВІДДАНІ ЧУЖИМ КНИГАМ ===`);
  for (const [book, F] of Object.entries(foreign)) {
    const fbd = M7.bookDirOf(book);
    const mf = fbd ? path.relative(process.cwd(), path.join(fbd, "manifest.json")) : `root/?/${book}/manifest.json`;
    const fbk = fbd ? M7.loadBook(fbd) : null;
    if (!fbk) { console.log(`  ✖ ${book}: нема маніфесту ${mf} — лишаємо в черзі`); continue; }
    const fgroups = M7.groupSlugs(fbk);
    const ok = [], noSection = [];
    for (const t of F.take) ((t.group && fgroups.has(t.group)) || t.groupTitle ? ok : noSection).push(t);
    noSection.forEach((t) => console.log(`  ✖ ${book}/${t.slug}: групи «${t.group}» у ${mf} немає і назви для неї не дано — лишаємо в черзі`));
    if (!ok.length) continue;
    const fops = path.join(QDIRP, `_mfops-ag-foreign-${book}.json`);
    fs.writeFileSync(fops, JSON.stringify(ok.map((t) => ({ op: "topic", section: t.section, slug: t.slug, title: t.title, basic: "empty", detailed: "pending" })), null, 2), "utf8");
    let fout = "", fcode = 0;
    try { fout = execSync(`node scripts/manifest-patch.js "${mf}" --ops "${fops}"${APPLY ? "" : " --dry"}`, { maxBuffer: 32e6, timeout: 600000 }).toString(); }
    catch (e) { fcode = e.status || 1; fout = ((e.stdout || "") + (e.stderr || "")).toString(); }
    console.log(`  ${book}: ${ok.map((t) => t.slug).join(", ")}`);
    console.log("    " + fout.trim().split("\n").pop());
    if (fcode) { console.log(`    ✖ manifest-patch повернув ${fcode} — ${book} не змінено, теми лишаються в черзі`); continue; }
    if (APPLY) {
      ok.forEach((t) => { t.applied = true; t.appliedAt = new Date().toISOString(); });
      fs.writeFileSync(F.file, JSON.stringify(F.all, null, 2), "utf8");
    }
  }
}
console.log(APPLY ? `\n✓ батч закрито.` : `\nЦе був звіт. Щоб записати — той самий рядок із --apply.`);
