#!/usr/bin/env node
/* ============================================================================
   decamp.js — КОД З ОГОРОЖІ У ФАЙЛ. Локально, механічно, без агента.

   Правило «довгий код живе у файлі» стояло в `code.md` і не виконувалось нічим: заміряно
   на корпусі — 49 файлів, 7031 рядок коду в огорожах, і найгірші з них написані задовго
   до того, як з'явилась перевірка. Правило без виконавця — це не правило.

   Виконавець тут механічний, і саме тому надійний. Блок довший за поріг, із міткою
   СПРАВЖНЬОЇ мови, виймається у файл поруч, а на його місці лишається директива
   `:::code <шлях>`. Рушій підтягне вміст сам, і стаття перестає бути простирадлом.

   ⛔ ЦЕ НЕ ПРОЄКТ. Ми не заводимо одиницю коду, не питаємо архітектури й не збираємо
   збірку — просто виносимо шматок, щоб він не громадив текст. Проєкт — інша річ, його
   замовляє каркас.

   ⛔ ЧОГО НЕ ЧІПАЄ: огорожі без мітки мови (схема, дерево тек, вивід консолі, ASCII-таблиця)
   і блоки коротші за поріг. Вони в тексті на місці.

   Ужиток:
     node writer_ua/local/decamp.js <файл.md> [...]        показати, що буде
     node writer_ua/local/decamp.js <файл.md> --apply      винести
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const TXT = require("../lib/text.js");

/** Тека мови → розширення файла. Те, чого `LANGS` не знає: він мапить мітку на теку. */
const EXT = {
  c: "c", cpp: "cpp", py: "py", js: "js", ts: "ts", go: "go", rust: "rs", java: "java",
  cs: "cs", swift: "swift", kotlin: "kt", ruby: "rb", lua: "lua", perl: "pl", php: "php",
  r: "r", matlab: "m", dart: "dart", sh: "sh", sql: "sql", asm: "s", verilog: "v",
  vhdl: "vhd", cmake: "cmake", make: "mk",
};

/**
 * Ім'я файла — з першого оголошення в самому коді, а не порядковим номером: `crc32.c`
 * читається, `snippet-2.c` ні. Не знайшли оголошення — тоді вже номер.
 */
function nameOf(body, i) {
  const m = /(?:^|\s)(?:function|def|class|struct|typedef struct|fn|func|type)\s+([A-Za-z_]\w{2,})/.exec(body)
    || /^\s*(?:[A-Za-z_][\w *]*?\b)([a-z_]\w{3,})\s*\([^;]*\)\s*\{/m.exec(body);
  return (m ? m[1] : `snippet-${i}`).toLowerCase().replace(/_/g, "-");
}

/**
 * Що винесеться з одного файла. Нічого не пише — лише каже.
 * `carrier` — той самий `.md` без розширення, як і в коді проєктів: так `:::code`
 * резолвиться від теки теми однаково для винесеного шматка й для проєкту.
 */
function plan(file, { min = TXT.DECAMP } = {}) {
  const src = fs.readFileSync(file, "utf8");
  const lines = src.split(/\r?\n/);
  const carrier = path.basename(file, ".md");
  const out = [];
  let i = 0, n = 0;
  while (i < lines.length) {
    const open = /^\s*```([A-Za-z0-9+#._-]+)\s*$/.exec(lines[i]);
    if (!open) { i++; continue; }
    let j = i + 1;
    while (j < lines.length && !/^\s*```\s*$/.test(lines[j])) j++;
    const body = lines.slice(i + 1, j).join("\n");
    const dir = TXT.LANGS[open[1].toLowerCase()];
    if (dir && j - i - 1 >= min) {
      const name = nameOf(body, ++n);
      out.push({ from: i, to: j, body, rel: `${carrier}/${dir}/${name}.${EXT[dir] || dir}`, lines: j - i - 1 });
    }
    i = j + 1;
  }
  return { src, lines, out };
}

/** Винести: файли на диск, директиви на місце огорож. */
function decamp(file, { min = TXT.DECAMP, apply = false } = {}) {
  const { lines, out } = plan(file, { min });
  if (!out.length || !apply) return out;
  const dir = path.dirname(file);
  /* Ззаду наперед — інакше кожна заміна зсуває наступні межі. */
  for (const b of [...out].reverse()) {
    const p = path.join(dir, b.rel);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, b.body.replace(/\s*$/, "\n"), "utf8");
    lines.splice(b.from, b.to - b.from + 1, `:::code ${b.rel}`);
  }
  fs.writeFileSync(file, lines.join("\n"), "utf8");
  return out;
}

/* ── прогін ────────────────────────────────────────────────────────────────── */

function main(argv) {
  const apply = argv.includes("--apply");
  const files = argv.filter((a) => !a.startsWith("--"));
  if (!files.length) { process.stdout.write("decamp: дай хоч один .md\n"); return 2; }
  let blocks = 0, moved = 0;
  for (const f of files) {
    const out = decamp(f, { apply });
    if (!out.length) continue;
    process.stdout.write(`\n${f}\n`);
    for (const b of out) {
      blocks++; moved += b.lines;
      process.stdout.write(`  ${String(b.lines).padStart(4)} рядків → ${b.rel}\n`);
    }
  }
  process.stdout.write(`\nблоків: ${blocks}   рядків: ${moved}${apply ? "   винесено" : "   (додай --apply)"}\n`);
  return 0;
}

if (require.main === module) {
  try { process.exit(main(process.argv.slice(2))); }
  catch (e) { console.error("decamp: " + e.message); process.exit(3); }
}
module.exports = { plan, decamp, nameOf };
