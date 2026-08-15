#!/usr/bin/env node
/* ============================================================================
   review-apply.js — вкласти в теки правки, які редактори ПОВЕРНУЛИ, а не зробили.

   ЧОМУ ТАК. Виміряно на прогоні 2026-08-15 (57 тем, 8.0 млн токенів):

     на тему   57 звернень до моделі   ·   вихід 68k, з них думання 54k
               17 окремих Edit · 9 Bash · 7 Read
               вміст теки, який справді треба прочитати: 28k

   Тобто платили не за читання теки, а за те, що кожна правка — окремий крок, і
   перед кожним кроком наново прокачується весь накопичений контекст (48% ваги
   прогону — саме читання кешу). Редактор, який замість Edit повертає перелік
   замін «було → стало», робить ~9 кроків замість 57. Заміни вкладає цей скрипт:
   детерміновано, без агента, без токенів.

   Ужиток:
     node scripts/claude/review-apply.js --run wf_xxx [--dry] [--book unix-linux --kind reference]
     node scripts/claude/review-apply.js --journal <шлях до journal.jsonl> --dry

   Що робить:
     1) бере з журналу кожен {dir, ok, fixes:[{file, old, new}]}
     2) вкладає заміни: old мусить траплятися у файлі РІВНО раз (інакше — відмова,
        бо неоднозначну заміну вгадувати не можна). Якщо точного збігу немає, пробує
        той самий текст із іншим перенесенням рядків — і більше нічого.
     3) якщо правили figs.py — перегенеровує фігури й ганяє svgcheck
     4) теми, де ВСІ заміни лягли й редактор дав ok, переводить recheck → done
     5) теми з хоч однією відмовою лишає в recheck і виписує їх окремо
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..", "..");
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 && argv[i + 1] ? argv[i + 1] : d; };
const DRY = argv.includes("--dry");

const RUN = arg("--run", "");
const JOURNAL = arg("--journal", RUN
  ? path.join(process.env.USERPROFILE || process.env.HOME || "", ".claude", "projects", "E--develop-courses",
      arg("--session", ""), "subagents", "workflows", RUN, "journal.jsonl")
  : "");
if (!JOURNAL || !fs.existsSync(JOURNAL)) {
  console.error("не знайшов журнал. Дай --journal <шлях до journal.jsonl>");
  process.exit(2);
}
const BOOK = arg("--book", "");
const KIND = arg("--kind", "reference");

/* ── читаємо результати ──────────────────────────────────────────────────── */
const results = [];
for (const line of fs.readFileSync(JOURNAL, "utf8").split(/\r?\n/)) {
  if (!line) continue;
  let j; try { j = JSON.parse(line); } catch { continue; }
  const r = j.type === "result" && j.result;
  if (r && typeof r === "object" && r.dir) results.push(r);
}
if (!results.length) { console.error("у журналі немає результатів із полем dir"); process.exit(2); }

/* ── пошук місця заміни ──────────────────────────────────────────────────── */
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
/* єдина поблажка: текст той самий, але переноси рядків інші (агент цитував з екрана) */
const loose = (s) => new RegExp(s.split(/\s+/).map(esc).join("\\s+"), "g");

/* Пом'якшений збіг дозволено ЛИШЕ прозі. У коді перенесення рядка — це синтаксис:
   2026-08-15 у rcu-read-copy-update саме він з'їв порожній рядок і склеїв два
   p.append() в один, давши SyntaxError. У .md таке нешкідливе, у .py — фатальне. */
function locate(text, old, allowLoose) {
  let i = text.indexOf(old);
  if (i >= 0) return text.indexOf(old, i + 1) >= 0 ? { err: "трапляється більше разу" } : { start: i, end: i + old.length };
  if (!allowLoose) return { err: "не знайдено (у коді збіг мусить бути точний)" };
  const m = [...text.matchAll(loose(old))];
  if (m.length === 1) return { start: m[0].index, end: m[0].index + m[0][0].length };
  if (m.length > 1) return { err: "трапляється більше разу" };
  return { err: "не знайдено" };
}

/* ── вкладання ───────────────────────────────────────────────────────────── */
const stat = { topics: 0, files: 0, applied: 0, failed: 0, figs: 0 };
const failures = [], cleanTopics = [], dirtyTopics = [];

for (const r of results) {
  const rel = String(r.dir).split(/[\\/]/).filter(Boolean).join("/").replace(/^E:\/develop\/courses\//, "");
  const dir = path.join(ROOT, rel);
  const fixes = Array.isArray(r.fixes) ? r.fixes : [];
  if (!fs.existsSync(dir)) { failures.push({ dir: rel, file: "", why: "теки немає" }); dirtyTopics.push(rel); continue; }
  stat.topics++;

  /* заміни одного файлу кладемо разом і пишемо файл один раз */
  const byFile = new Map();
  for (const f of fixes) {
    if (!f || !f.file || typeof f.old !== "string" || typeof f.new !== "string") continue;
    const name = path.basename(String(f.file));
    if (!byFile.has(name)) byFile.set(name, []);
    byFile.get(name).push(f);
  }

  let bad = 0;
  const touchedFigs = [];
  const snapshots = new Map();   /* шлях → текст до правки (лише код) */
  for (const [name, list] of byFile) {
    const abs = path.join(dir, name);
    if (!fs.existsSync(abs)) { list.forEach(() => stat.failed++); failures.push({ dir: rel, file: name, why: "файлу немає" }); bad++; continue; }
    const before = fs.readFileSync(abs, "utf8");
    let text = before;
    const isProse = name.endsWith(".md");
    if (!isProse) snapshots.set(abs, before);   /* код відкотимо, якщо не збереться */
    let hit = 0;
    for (const f of list) {
      if (f.old === f.new) continue;
      const pos = locate(text, f.old, isProse);
      if (pos.err) { stat.failed++; bad++; failures.push({ dir: rel, file: name, why: pos.err, old: f.old.slice(0, 90) }); continue; }
      text = text.slice(0, pos.start) + f.new + text.slice(pos.end);
      hit++; stat.applied++;
    }
    if (hit && !DRY) fs.writeFileSync(abs, text, "utf8");
    if (hit) { stat.files++; if (name === "figs.py") touchedFigs.push(dir); }
  }

  /* фігури: правили генератор — перемальовуємо (локально, 0 токенів) */
  for (const d of touchedFigs) {
    if (DRY) { stat.figs++; continue; }
    try {
      execFileSync("python", ["figs.py"], { cwd: d, stdio: "pipe", timeout: 120000 });
      execFileSync("python", [path.join(ROOT, "scripts", "svgcheck.py"), d, "--links"], { stdio: "pipe", timeout: 120000 });
      stat.figs++;
    } catch (e) {
      bad++;
      /* Зламаний генератор не лишаємо на диску: відкочуємо файл і кажемо, що сталось.
         Тема все одно піде на доробку, але тека буде такою, якою була. */
      let undone = "";
      for (const [abs, text] of snapshots) { fs.writeFileSync(abs, text, "utf8"); undone = " · файл відкочено"; }
      failures.push({ dir: rel, file: "figs.py", why: "перегенерація/svgcheck впали" + undone + ": " + String(e.stdout || e.stderr || e.message).slice(0, 200) });
    }
  }

  (bad === 0 && r.ok !== false ? cleanTopics : dirtyTopics).push(rel);
}

/* ── звіт ────────────────────────────────────────────────────────────────── */
const P = (n, w) => String(n).padStart(w);
console.log(`${DRY ? "[СУХИЙ ПРОГІН] " : ""}тем у журналі: ${results.length}`);
console.log(`  замін вкладено:   ${P(stat.applied, 5)}   у ${stat.files} файлах`);
console.log(`  замін не лягло:   ${P(stat.failed, 5)}`);
console.log(`  фігур перемальовано: ${stat.figs}`);
console.log(`  тем без жодної відмови: ${cleanTopics.length}   з відмовами: ${dirtyTopics.length}`);
if (failures.length) {
  console.log("\nвідмови (тема · файл · чому):");
  failures.slice(0, 40).forEach((f) => console.log(`  ${f.dir.split("/").pop()} · ${f.file} · ${f.why}${f.old ? `\n      «${f.old}…»` : ""}`));
  if (failures.length > 40) console.log(`  … ще ${failures.length - 40}`);
}

/* ── статуси: лише теми, де все лягло ────────────────────────────────────── */
const outDir = path.join(ROOT, "scripts", "_finish");
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "_review-apply-failed.json"), JSON.stringify(failures, null, 2), "utf8");
fs.writeFileSync(path.join(outDir, "_review-apply-retry.json"), JSON.stringify(dirtyTopics, null, 2), "utf8");

if (BOOK && cleanTopics.length && !DRY) {
  const slugs = cleanTopics.map((d) => d.split("/").pop()).join(",");
  const ops = `scripts/_finish/_review-ops-${BOOK}.json`;
  const run = (a) => console.log(execFileSync("node", a, { cwd: ROOT, encoding: "utf8" }).trim());
  run([path.join("scripts", "claude", "review-queue.js"), "--book", BOOK, "--kind", KIND, "--ops-done", "--json", ops, "--slugs", slugs]);
  run([path.join("scripts", "manifest-patch.js"), `${KIND}/${BOOK}/manifest.js`, "--ops", path.join(ROOT, ops), "--apply"]);
} else if (BOOK && cleanTopics.length) {
  console.log(`\n[сухий] у done пішло б тем: ${cleanTopics.length}`);
}
console.log(`\nна доробку: scripts/_finish/_review-apply-retry.json (${dirtyTopics.length})`);
