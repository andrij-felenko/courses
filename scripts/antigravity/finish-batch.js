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
          детальна на диску  → detailed: done
          базова на диску    → basic: done
          базової нема       → basic: pending → empty (лише якщо стояло pending)
          кожна вставка      → insert … done
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
(m.sections || []).forEach((s) => (s.topics || []).forEach((t) => sectionBySlug.set(t.slug, s.slug)));
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
    ops.push({ op: "topic", section, slug, title, basic: hasB ? "done" : "empty", detailed: hasD ? "done" : "pending" });
    existingSlugs.add(slug);
  }

  if (hasD) ops.push({ op: "status", slug, ver: "detailed", status: "done" });
  if (hasB) ops.push({ op: "status", slug, ver: "basic", status: "done" });
  else ops.push({ op: "status-if", slug, ver: "basic", from: "pending", to: "empty" });
  files.filter((f) => /^(hist|comp|math|proj|api)-/.test(f)).forEach((f) =>
    ops.push({ op: "insert", slug, type: f.split("-")[0], file: f, status: "done", section }));
  seen.push(`${slug}: детальна ${hasD ? "done" : "—"} · базова ${hasB ? "done" : "empty"} · вставок ${files.filter((f) => /^(hist|comp|math|proj|api)-/.test(f)).length}`);
}

/* ── 3. черга нових тем ────────────────────────────────────────────────────── */
const QFILE = path.join("scripts", "_finish", `_ag-newtopics-${BOOK}.json`);
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
if (dirs.length >= 10 && fresh.length === 0) {
  console.log(`  ⚠ НУЛЬ НОВИХ ТЕМ на ${dirs.length} написаних. Так буває, коли книга справді закрита,`);
  console.log(`    але частіше — коли перевірка 16 звіряла лише preknowlist. Перечитай кілька статей`);
  console.log(`    і спитай себе: на що вони спираються мовчки, без пояснення й без лінка?`);
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
console.log(APPLY ? `\n✓ батч закрито.` : `\nЦе був звіт. Щоб записати — той самий рядок із --apply.`);
