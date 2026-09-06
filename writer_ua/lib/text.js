#!/usr/bin/env node
/* ============================================================================
   text.js — ЛІЧИЛЬНИКИ КОНВЕЄРА writer_ua: проза, огорожі, код у файлах.

   Усе, що дає ЧИСЛО про написане. Жоден із цих лічильників нічого не судить про
   зміст — вони лише міряють, а вирок виносить етап, який їх покликав.

   ПРОЗА — НЕ ФАЙЛ. Слова рахуються без коду: без того, що між огорожами, без
   директив `:::`, без рядків таблиць і без картинок. Інакше код «дописував» би
   статтю замість тексту: у корпусі 28 тисяч директив, і кожна дала б фантомні
   слова саме там, де коду найбільше.

   КОД — НЕ ОГОРОЖА. Блок від DECAMP рядків справжньою мовою живе у файлі, тому
   міряється теками мов, а не текстом статті. `fencedCode` рахує те, що ще
   лишилось у прозі й мусить виїхати.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

/** Поріг винесення: від скількох рядків код їде з прози у файл. */
const DECAMP = 15;   // поріг автора: довше — виносимо у файл, коротше лишається в тексті

/**
 * Мітка огорожі → тека мови. Платформа — не мова: `arduino`, `esp-idf`, `stm32`
 * пишуться на C і лягають ПІД мову зайвим рівнем `c/<платформа>/`, щоб тека мови
 * лишалась чесною, а пара `c/`↔`cpp/` не плуталась.
 */
const LANGS = {
  c: "c", h: "c", arduino: "c", "esp-idf": "c", stm32: "c",
  cpp: "cpp", "c++": "cpp", hpp: "cpp",
  rust: "rust", go: "go", java: "java", cs: "cs", swift: "swift", kotlin: "kotlin",
  asm: "asm", nasm: "asm", verilog: "verilog", vhdl: "vhdl",
  python: "py", py: "py", micropython: "py",
  ts: "ts", typescript: "ts", js: "js", javascript: "js",
  ruby: "ruby", rb: "ruby", lua: "lua", perl: "perl", php: "php",
  r: "r", matlab: "matlab", dart: "dart",
  sh: "sh", bash: "sh", zsh: "sh", sql: "sql", cmake: "cmake", make: "make", makefile: "make",
};

/**
 * Мова з каркаса → ім'я теки. Каркас пише мову вільним рядком — «Python», «C++»,
 * «Arduino», — а тека мусить лишатися чесною: `py`, `cpp`, `c`. Невідому мову беремо
 * як є, малими: краще чесна незнайома тека, ніж мовчазна підміна.
 */
const langDir = (lang) => {
  const k = String(lang || "").trim().toLowerCase();
  return LANGS[k] || k.replace(/[^a-z0-9+.-]/g, "-") || "code";
};

/** Мови-«клей»: файл дістають, але їхній розмір нічого не каже. */
const GLUE = new Set(["sh", "sql", "cmake", "make"]);

/**
 * Не код проєкту. Відбір за ІМЕНЕМ, а не за розширенням: інакше `setup.py`,
 * `conanfile.py` і `noxfile.py` пролізли б у лік як звичайні модулі Python.
 */
const BUILD_FILES = new Set([
  "cmakelists.txt", "makefile", "gnumakefile", "meson.build", "build.ninja", "kconfig", "sdkconfig",
  "setup.py", "setup.cfg", "conanfile.py", "noxfile.py", "fabfile.py", "tasks.py",
  "pyproject.toml", "requirements.txt", "package.json", "package-lock.json", "tsconfig.json",
  "cargo.toml", "cargo.lock", "go.mod", "go.sum", "dockerfile", "build.gradle", "pom.xml",
  "platformio.ini", "readme.md", ".gitignore", ".clang-format", ".editorconfig",
]);
const BUILD_EXT = new Set([".cmake", ".mk", ".toml", ".json", ".yaml", ".yml", ".ini", ".cfg", ".lock", ".md", ".txt"]);

/** Тест не задає розміру проєкту: чи покриває він заявлене — судиться змістом. */
const TEST_RE = /(^|[\\/])(tests?|spec)([\\/]|$)|(^|[_.-])(test|spec)[_.-]|[_.-](test|spec)\.|^test_/i;

/* ── проза ─────────────────────────────────────────────────────────────────── */

/**
 * Слова прози. Поза ліком: огорожі коду, директиви `:::`, рядки-картинки, рядки
 * таблиць. Знято: інлайновий код, адреси посилань (текст лишається), маркери
 * заголовка, цитати, списку й наголосу.
 */
function proseWords(md) {
  let inCode = false, words = 0;
  for (let line of String(md == null ? "" : md).split(/\r?\n/)) {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; continue; }
    if (inCode) continue;
    if (/^:::/.test(t)) continue;
    if (/^!\[/.test(t)) continue;
    if (/^\|.*\|/.test(t)) continue;
    if (/^#{1,6}\s/.test(t)) line = t.replace(/^#{1,6}\s/, "");
    const s = line
      .replace(/`[^`]*`/g, " ")
      .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
      .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
      .replace(/^>\s*/, "").replace(/^[-*]\s+/, "").replace(/[*_#>`~]/g, " ");
    const m = s.match(/[\p{L}\p{N}’'\-]+/gu);
    if (m) words += m.length;
  }
  return words;
}

/**
 * Код, який ЩЕ лежить в огорожах і мусив би виїхати: мітка справжньої мови плюс
 * довжина від DECAMP. Огорожа без мітки (схема, дерево тек, вивід консолі) і
 * короткий фрагмент кодом у цьому сенсі не є — правило лишає їх у прозі.
 */
function fencedCode(md) {
  let inC = false, lang = null, n = 0, left = 0;
  for (const line of String(md == null ? "" : md).split(/\r?\n/)) {
    const m = line.match(/^\s*```+\s*([^\s`]*)/);
    if (m) {
      if (!inC) { inC = true; lang = (m[1] || "").trim().toLowerCase(); n = 0; }
      else { inC = false; if (LANGS[lang] && n >= DECAMP) left += n; }
      continue;
    }
    if (inC) n++;
  }
  return left;
}

/* ── код у файлах ──────────────────────────────────────────────────────────── */

/** Тека проєкту названа своїм `.md`-носієм — тому `proj` і `api` не стикаються. */
const projectDir = (topicDir, mdFile) => path.join(topicDir, path.basename(mdFile, ".md"));

/** Мовні теки, що СПРАВДІ лежать на диску для цього `.md`. */
function langDirs(topicDir, mdFile) {
  const root = projectDir(topicDir, mdFile);
  const known = new Set(Object.values(LANGS));
  let ents = [];
  try { ents = fs.readdirSync(root, { withFileTypes: true }); } catch { return []; }
  return ents
    .filter((e) => e.isDirectory() && known.has(e.name))
    .map((e) => ({ lang: e.name, glue: GLUE.has(e.name), dir: path.join(root, e.name) }))
    .sort((a, b) => a.lang.localeCompare(b.lang));
}

/**
 * Рядки коду в теці мови. Порожні рядки й коментарі рахуються: коментар у коді —
 * теж пояснення, а конвеєр міряє обсяг показаного, а не густину синтаксису.
 */
function codeLines(dir) {
  let lines = 0, files = 0, tests = 0, build = 0;
  const walk = (d, rel) => {
    let ents = [];
    try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of ents) {
      const p = path.join(d, e.name);
      const r = rel ? rel + "/" + e.name : e.name;
      if (e.isDirectory()) { walk(p, r); continue; }
      const low = e.name.toLowerCase();
      if (BUILD_FILES.has(low) || BUILD_EXT.has(path.extname(low))) { build++; continue; }
      if (TEST_RE.test(r)) { tests++; continue; }
      let t = ""; try { t = fs.readFileSync(p, "utf8"); } catch { continue; }
      if (!t.trim()) continue;
      files++;
      lines += t.replace(/\r\n?/g, "\n").replace(/\n+$/, "").split("\n").length;
    }
  };
  walk(dir, "");
  return { lines, files, tests, build };
}

module.exports = {
  DECAMP, LANGS, GLUE, BUILD_FILES, BUILD_EXT, TEST_RE,
  proseWords, fencedCode, projectDir, langDirs, langDir, codeLines,
};
