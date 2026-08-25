#!/usr/bin/env node
/* ============================================================================
   prefix-to-root.js — звести префікс короткого лінка до канонного `root:`.

   ЧОМУ. `PLAN.md §2.1`: тека `root/` названа так, щоб шлях збігався з префіксом
   адреси **буква в букву**. `§2.3`: коротка форма `root:<книга>/<тема>` — та, що
   живе в прозі й не міняється ніколи.

   ЩО ЛАГОДИТЬ. У ніч на 2026-08-25 корпус помилково перевели на вигаданий префікс
   `topic:` (рішення, ухвалене повз цей план). Скрипт вертає його до `root:`.

   ОБЕРЕЖНО. Чіпаємо лише префікс: перед ним НЕ літера, за ним ОДРАЗУ слуг або
   `<плейсхолдер>`. Англійське «of this topic: a proof» не збігається, бо там пробіл.

   Ужиток:  node scripts/prefix-to-root.js            (звіт)
            node scripts/prefix-to-root.js --apply
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const APPLY = process.argv.includes("--apply");
/* Префікс — лише реальні його контексти. Прозове «the math of this topic:** a proof»
   й «of this topic: a proof» НЕ чіпаємо: після двокрапки там зірочка або пробіл. */
const RE = /(^|[^A-Za-z])topic:(?=[A-Za-z0-9<`$/[(-])/g;

/* Корпус — окремо від тулінгу: там тисячі файлів і один рядок звіту, тут одиниці й пофайлово. */
const CORPUS = path.join(ROOT, "root");
const TOOLING = [
  "AUTHORING.md", "AUTHORING.en.md", "CANON-v7-draft.md", "CLAUDE.md", "AGENTS.md",
  "agents/README.md", "agents/antigravity/pipeline.md",
  ".agents/rules/autonomy.md", ".agents/rules/pipeline.md",
  ".agents/agents/write-topic/agent.md", ".agents/agents/repair-topic/agent.md",
  ".agents/agents/check-all/agent.md", ".agents/workflows/write-batch.md",
  "scripts/linkcheck.js", "scripts/guidelinks.js", "scripts/retarget-books.js",
  "scripts/checks/05-links.js", "scripts/checks/16-promises.js",
  "scripts/antigravity/newtopic.js", "scripts/antigravity/finish-batch.js",
  "scripts/claude/write-batch.js", "scripts/claude/adjudicate-batch.js",
  "scripts/claude/recheck-audit.js", "scripts/claude/recheck-run.js", "scripts/claude/recheck-batch.js",
  "scripts/build_dc.py", "src/front/book.js",
  "scripts/migrate/final/CORPUS-DEFECTS.md",
];

function fix(p, quiet) {
  let src; try { src = fs.readFileSync(p, "utf8"); } catch { return 0 }
  const n = (src.match(RE) || []).length;
  if (!n) return 0;
  if (APPLY) {
    const out = src.replace(RE, (m, pre) => pre + "root:");
    fs.writeFileSync(p + ".tmp", out); fs.renameSync(p + ".tmp", p);
  }
  if (!quiet) console.log(`   ${String(n).padStart(5)}  ${path.relative(ROOT, p).replace(/\\/g, "/")}`);
  return n;
}

console.log(APPLY ? "ЗАСТОСОВАНО" : "ЗВІТ (нічого не записано)");
console.log("\n── тулінг і канон ──");
let tool = 0;
for (const rel of TOOLING) tool += fix(path.join(ROOT, rel));

let corp = 0, files = 0, touched = 0;
(function walk(d) {
  let e; try { e = fs.readdirSync(d, { withFileTypes: true }) } catch { return }
  for (const x of e) {
    const p = path.join(d, x.name);
    if (x.isDirectory()) { if (x.name === "img") continue; walk(p); continue }
    if (!x.name.endsWith(".md")) continue;
    files++;
    const n = fix(p, true);
    if (n) { corp += n; touched++ }
  }
})(CORPUS);

console.log(`\n── корпус ──\n   ${corp} префіксів у ${touched} файлах (переглянуто ${files})`);
console.log(`\nразом: ${tool + corp}`);
if (!APPLY) console.log(`\nЩоб записати: node scripts/prefix-to-root.js --apply`);
