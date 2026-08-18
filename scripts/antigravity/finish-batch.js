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
const BOOK = val("book"), KIND = val("kind") || "book";
if (!BOOK) { console.error("Ужиток: node scripts/antigravity/finish-batch.js --book <книга> --kind <вид> [--apply]"); process.exit(3); }

const MF = path.join(KIND, BOOK, "manifest.js");
if (!fs.existsSync(MF)) { console.error(`нема маніфесту: ${MF}`); process.exit(3); }

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
console.log(`\n=== ГЕЙТ: ${dirs.length} тем батчу ${KIND}/${BOOK} ===`);
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

/* ── 2. операції з диску ───────────────────────────────────────────────────── */
const ops = [];
const seen = [];
const mismatched = [];
const sb = {};
new Function("window", fs.readFileSync(MF, "utf8"))(sb);
const isGuide = Array.isArray(sb.__GUIDES__) && sb.__GUIDES__.length;
const m = (isGuide ? sb.__GUIDES__ : sb.__BOOKS__ || [])[0];
/* Слуг → секція, у якій тема ВЖЕ записана в маніфесті. Саме звідси беремо секцію для
   операцій: тека на диску може з нею розходитись (тему написали не в ту теку, або секцію
   в маніфесті перейменували), і тоді manifest-patch шукав би тему не там, де вона є.
   Раніше тут стояла ручна табличка підміни на одну книгу — вона лікувала симптом одного
   батчу й мовчки ламалася на будь-якому іншому розходженні. */
const sectionBySlug = new Map();
if (isGuide) {
  (m.modules || m.sections || []).forEach((mod) => {
    (mod.chapters || [{ steps: mod.steps || mod.topics || [] }]).forEach((ch) => {
      (ch.steps || ch.topics || []).forEach((s) => {
        if (s && s.slug && !s.ref) sectionBySlug.set(s.slug, mod.slug);
      });
    });
  });
} else {
  (m.sections || []).forEach((s) => (s.topics || []).forEach((t) => sectionBySlug.set(t.slug, s.slug)));
}
const existingSlugs = new Set(sectionBySlug.keys());
/* Для НОВОЇ теми секції в маніфесті ще нема — тоді (і лише тоді) беремо назву теки. */
const sectionOf = (slug, dirSection) => sectionBySlug.get(slug) || dirSection;

for (const dir of dirs) {
  const slug = path.basename(dir);
  const dirSection = path.basename(path.dirname(dir));
  const section = sectionOf(slug, dirSection);
  if (existingSlugs.has(slug) && section !== dirSection) {
    mismatched.push(`${slug}: тека ${dirSection} ≠ маніфест ${section}`);
  }
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
  const hasD = files.includes(`${slug}-d.md`);
  const hasB = files.includes(`${slug}.md`);

  if (!existingSlugs.has(slug)) {
    let title = slug;
    const mainFile = hasD ? `${slug}-d.md` : (hasB ? `${slug}.md` : null);
    if (mainFile && fs.existsSync(path.join(dir, mainFile))) {
      const content = fs.readFileSync(path.join(dir, mainFile), "utf8");
      const match = content.match(/^#\s+(.+)$/m);
      if (match) title = match[1].trim();
    }
    ops.push({ op: "topic", section, slug, title, basic: hasB ? WRITTEN_STATUS : "empty", detailed: hasD ? WRITTEN_STATUS : "pending" });
    existingSlugs.add(slug);
  }

  if (hasD) ops.push({ op: "status", slug, ver: "detailed", status: WRITTEN_STATUS });
  if (hasB) ops.push({ op: "status", slug, ver: "basic", status: WRITTEN_STATUS });
  else ops.push({ op: "status-if", slug, ver: "basic", from: "pending", to: "empty" });
  files.filter((f) => /^(hist|comp|math|proj|api)-/.test(f)).forEach((f) =>
    ops.push({ op: "insert", slug, type: f.split("-")[0], file: f, status: WRITTEN_STATUS, section }));
  seen.push(`${slug}: детальна ${hasD ? WRITTEN_STATUS : "—"} · базова ${hasB ? WRITTEN_STATUS : "empty"} · вставок ${files.filter((f) => /^(hist|comp|math|proj|api)-/.test(f)).length}`);
}

/* ── 3. черга нових тем ────────────────────────────────────────────────────── */
const QDIRP = path.join("scripts", "_finish");
const QFILE = path.join(QDIRP, `_ag-newtopics-${BOOK}.json`);
let queue = [];
try { queue = JSON.parse(fs.readFileSync(QFILE, "utf8")); } catch { }
const fresh = queue.filter((t) => !t.applied);
fresh.forEach((t) => ops.push({ op: "topic", section: t.section, slug: t.slug, title: t.title, basic: "empty", detailed: "pending" }));

if (mismatched.length) {
  console.log(`\n⚠ ТЕКА ≠ СЕКЦІЯ МАНІФЕСТУ (${mismatched.length}) — статуси підуть у секцію з маніфесту,`);
  console.log(`  але розкладку варто полагодити: або git mv теки, або перенести тему в маніфесті.`);
  mismatched.forEach((x) => console.log(`     • ${x}`));
}
console.log(`\n=== ЩО ЗАПИСУЄМО ===`);
seen.forEach((s) => console.log("  " + s));
if (fresh.length) {
  console.log(`  нові теми з черги (у чергу письма підуть ДЕТАЛЬНІ, наступним батчем):`);
  fresh.forEach((t) => console.log(`    + [${t.section}] ${t.slug} — ${t.title}   ← ${t.why}`));
} else console.log("  нових тем у черзі немає");

/* Скільки тем написали — і скільки залежностей при цьому помітили. Нуль нових тем на
   великому батчі майже завжди означає не закриту книгу, а те, що 16-та відповідала на
   власний preknowlist: автор оголошує наявне, суддя підтверджує, що воно наявне, і
   поняття, якого ніхто не оголосив, лишається невидимим. Це не блокує запис — це те,
   що людина мусить побачити, поки батч ще свіжий. */
const queuedTotal = queue.length;
console.log("");
console.log(`  залежності: написано тем ${dirs.length} · заведено нових тем ${fresh.length} (усього в черзі ${queuedTotal})`);

/* Облік важеля, а не самих тем. «Нуль нових тем» саме по собі нічого не каже: воно
   означає і закриту книгу, і те, що до newtopic.js ніхто не дотягнувся. Розрізняє їх
   журнал відмов — якщо і черга порожня, і відмов нема, важіль просто не вживали.
   2026-08-15 саме так і було: батч фізики дав нуль тем при порожньому журналі. */
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

/* ── 4. маніфест ───────────────────────────────────────────────────────────── */
const OPS = path.join("scripts", "_finish", `_mfops-ag-${BOOK}.json`);
fs.mkdirSync(path.dirname(OPS), { recursive: true });
const topicOps = ops.filter((o) => o.op === "topic");
const otherOps = ops.filter((o) => o.op !== "topic");
const sortedOps = [...topicOps, ...otherOps];
fs.writeFileSync(OPS, JSON.stringify(sortedOps, null, 2), "utf8");
console.log(`\n=== manifest-patch (${APPLY ? "ЗАПИС" : "DRY — нічого не пишемо"}) ===`);
let code = 0, out = "";
try { out = execSync(`node scripts/manifest-patch.js "${MF}" --ops "${OPS}"${APPLY ? "" : " --dry"}`, { maxBuffer: 32 * 1024 * 1024, timeout: 600000, killSignal: "SIGKILL" }).toString(); }
catch (e) { code = e.status || 1; out = ((e.stdout || "") + (e.stderr || "")).toString(); }
console.log(out.trimEnd());
if (code) { console.error(`\n✖ manifest-patch повернув ${code} — маніфест не змінено`); process.exit(code); }

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
    const kind = F.take[0].kind || "book";
    const mf = path.join(kind, book, "manifest.js");
    if (!fs.existsSync(mf)) { console.log(`  ✖ ${book}: нема маніфесту ${mf} — лишаємо в черзі`); continue; }
    const src = fs.readFileSync(mf, "utf8");
    const ok = [], noSection = [];
    for (const t of F.take)
      (new RegExp(`slug\\s*:\\s*["']${t.section}["']`).test(src) ? ok : noSection).push(t);
    noSection.forEach((t) => console.log(`  ✖ ${book}/${t.slug}: секції «${t.section}» у ${mf} немає — лишаємо в черзі`));
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
