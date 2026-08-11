#!/usr/bin/env node
/* ============================================================================
   finish-batch.js — ЄДИНЕ місце, де батч Antigravity торкається маніфесту.
   І торкається лише тоді, коли ВСІ теми батчу пройшли всі 16 перевірок.

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

/* ── 1. гейт ───────────────────────────────────────────────────────────────── */
console.log(`\n=== ГЕЙТ: ${dirs.length} тем батчу ${KIND}/${BOOK} ===`);
let gateCode = 0, gateOut = "";
try { gateOut = execSync(`node scripts/checks/gate.js --topics ${dirs.map((d) => `"${d}"`).join(" ")} --quiet`, { maxBuffer: 64 * 1024 * 1024 }).toString(); }
catch (e) { gateCode = e.status || 1; gateOut = ((e.stdout || "") + (e.stderr || "")).toString(); }
console.log(gateOut.split(/\r?\n/).filter((l) => /готово|у роботі|ЗАСТІЙ|готових тем/.test(l)).join("\n"));
if (gateCode !== 0) {
  console.error(`\n✖ МАНІФЕСТ НЕ ЧІПАЄМО: не всі теми пройшли гейт (код ${gateCode}).`);
  console.error(`  Доробити перелічене вище й прогнати finish-batch знову.`);
  process.exit(1);
}
console.log(`✓ усі ${dirs.length} тем пройшли всі 16 перевірок`);

/* ── 2. операції з диску ───────────────────────────────────────────────────── */
const ops = [];
const seen = [];
for (const dir of dirs) {
  const slug = path.basename(dir);
  const section = path.basename(path.dirname(dir));
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
  const hasD = files.includes(`${slug}-d.md`);
  const hasB = files.includes(`${slug}.md`);
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

console.log(`\n=== ЩО ЗАПИСУЄМО ===`);
seen.forEach((s) => console.log("  " + s));
if (fresh.length) {
  console.log(`  нові теми з черги (у чергу письма підуть ДЕТАЛЬНІ, наступним батчем):`);
  fresh.forEach((t) => console.log(`    + [${t.section}] ${t.slug} — ${t.title}   ← ${t.why}`));
} else console.log("  нових тем у черзі немає");

/* ── 4. маніфест ───────────────────────────────────────────────────────────── */
const OPS = path.join("scripts", "_finish", `_mfops-ag-${BOOK}.json`);
fs.mkdirSync(path.dirname(OPS), { recursive: true });
fs.writeFileSync(OPS, JSON.stringify(ops, null, 2), "utf8");
console.log(`\n=== manifest-patch (${APPLY ? "ЗАПИС" : "DRY — нічого не пишемо"}) ===`);
let code = 0, out = "";
try { out = execSync(`node scripts/manifest-patch.js "${MF}" --ops "${OPS}"${APPLY ? "" : " --dry"}`, { maxBuffer: 32 * 1024 * 1024 }).toString(); }
catch (e) { code = e.status || 1; out = ((e.stdout || "") + (e.stderr || "")).toString(); }
console.log(out.trimEnd());
if (code) { console.error(`\n✖ manifest-patch повернув ${code} — маніфест не змінено`); process.exit(code); }

if (APPLY && fresh.length) {
  fresh.forEach((t) => { t.applied = true; t.appliedAt = new Date().toISOString(); });
  fs.writeFileSync(QFILE, JSON.stringify(queue, null, 2), "utf8");
  console.log(`  чергу нових тем позначено відпрацьованою: ${QFILE}`);
}
console.log(APPLY ? `\n✓ батч закрито.` : `\nЦе був звіт. Щоб записати — той самий рядок із --apply.`);
