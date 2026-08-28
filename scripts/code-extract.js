#!/usr/bin/env node
/* Механічне винесення коду з огорож у файли-проєкти.
   Ужиток: node scripts/code-extract.js --book <слуг> [--apply] [--limit N]

   Робить рівно одне й нічого понад: блок від EXTRACT_MIN рядків справжньою мовою
   виїжджає у файл, а на його місці в прозі стає `:::code <шлях від теки теми>`.
   Стаття не змінюється ні на слово — блок стояв там, посилання стоїть там само.

   ⛔ Розкладки «як у справжніх проєктах» цей прохід НЕ робить і не може: чотири
   блоки, показані в прозі один за одним, часто мають власні #include і власний
   main, тож автоматична склейка дала б те, що не збереться. Кожен зачеплений
   файл дістає `recode: true` — справжні модулі зліпить прохід recode з агентами.

   Файли, у яких тека проєкту ВЖЕ є, прохід не чіпає: там або вже переїхали, або
   код продубльовано, і те й те — робота для агента, не для лічильника.            */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("./lib/manifest7.js");
const L = require("./checks/_lib.js");

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const BOOK = arg("--book", "");
const APPLY = argv.includes("--apply");
const LIMIT = Number(arg("--limit", "0")) || 0;
if (!BOOK) { console.error("треба --book <слуг>"); process.exit(2); }

const rec = M7.books().get(BOOK);
if (!rec) { console.error(`нема книги «${BOOK}»`); process.exit(3); }
const book = M7.loadBook(rec.bookDir);
if (!book) { console.error("не читається маніфест"); process.exit(3); }

/* ── розширення теки мови ─────────────────────────────────────────────────── */
const PLAT_EXT = { arduino: "ino" };            /* платформа зі своїм розширенням */
const EXT = { c: "c", cpp: "cpp", py: "py", ts: "ts", js: "js", go: "go", rust: "rs",
  java: "java", cs: "cs", swift: "swift", kotlin: "kt", asm: "s", verilog: "v", vhdl: "vhd",
  ruby: "rb", lua: "lua", perl: "pl", php: "php", r: "R", matlab: "m", dart: "dart",
  sh: "sh", sql: "sql", cmake: "cmake", make: "mk" };
/* Заголовкові розширення — куди йде блок, що оголошує, а не робить. */
const HDR = { c: "h", cpp: "hpp" };
/* Базове ім'я для єдиного блоку мови. */
const MAIN = { ts: "index", js: "index", cmake: "CMakeLists", make: "Makefile" };

const UA = { а:"a",б:"b",в:"v",г:"h",ґ:"g",д:"d",е:"e",є:"ie",ж:"zh",з:"z",и:"y",і:"i",ї:"i",
  й:"i",к:"k",л:"l",м:"m",н:"n",о:"o",п:"p",р:"r",с:"s",т:"t",у:"u",ф:"f",х:"kh",ц:"ts",
  ч:"ch",ш:"sh",щ:"shch",ь:"",ю:"iu",я:"ia","'":"","’":"" };
const slugify = (s) => String(s).toLowerCase().split("").map((c) => (UA[c] !== undefined ? UA[c] : c))
  .join("").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").replace(/^(.{1,26})(-.*)?$/, "$1").replace(/-+$/, "") || "part";

/* Блок оголошує, а не робить: сторожі включення або самі прототипи. */
function looksHeader(lines, lang) {
  if (lang !== "c" && lang !== "cpp") return false;
  const t = lines.join("\n");
  if (/^\s*#pragma\s+once/m.test(t)) return true;
  if (/^\s*#ifndef\s+\w*_H\w*/m.test(t) && /#define\s+\w*_H/.test(t)) return true;
  const bodies = (t.match(/\)\s*\{/g) || []).length;
  const protos = (t.match(/\);\s*$/gm) || []).length;
  return protos >= 2 && bodies === 0;
}

/* Ім'я з коментаря в перших рядках: /* ring.c *​/ або // main.cpp */
function nameHint(lines, ext) {
  const head = lines.slice(0, 3).join("\n");
  const m = head.match(new RegExp("([\\w.-]+)\\." + ext + "\\b"));
  return m ? m[1] : null;
}

const FENCE = /^(\s*)```(.*)$/;
const changed = [], skipped = [], ops = [];
let totFiles = 0, totLines = 0, totMd = 0;

const topics = M7.allTopics(book).filter((t) => t.own);
for (const t of (LIMIT ? topics.slice(0, LIMIT) : topics)) {
  const dir = path.join(rec.bookDir, t.slug);
  if (!fs.existsSync(dir)) continue;
  const mds = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));

  for (const file of mds) {
    const p = path.join(dir, file);
    const base = file.replace(/\.md$/, "");
    if (L.langDirsOf(dir, file).length) { skipped.push(`${t.slug}/${file} — тека проєкту вже є`); continue; }

    const src = L.read(p);
    const lines = src.split(/\r?\n/);

    /* перший прохід: знайти блоки, порахувати мови, зібрати заголовки */
    const blocks = [];
    let inC = false, lang = null, start = 0, buf = [], indent = "", heading = "";
    for (let i = 0; i < lines.length; i++) {
      const ln = lines[i];
      const m = ln.match(FENCE);
      if (!inC && /^#{2,4}\s+/.test(ln)) heading = ln.replace(/^#+\s+/, "").trim();
      if (m) {
        if (!inC) { inC = true; indent = m[1]; lang = (m[2] || "").trim().split(/\s+/)[0].toLowerCase(); start = i; buf = []; }
        else { inC = false; const spec = L.LANGS[lang];
               if (spec && buf.length >= L.EXTRACT_MIN) blocks.push({ start, end: i, lang: spec[0], plat: spec[2] || "", body: buf.slice(), indent, heading }); }
        continue;
      }
      if (inC) buf.push(ln);
    }
    if (!blocks.length) continue;

    /* другий прохід: імена */
    const perLang = {};
    const keyOf = (b) => b.lang + (b.plat ? "/" + b.plat : "");
    for (const b of blocks) perLang[keyOf(b)] = (perLang[keyOf(b)] || 0) + 1;
    const used = {};
    for (const b of blocks) {
      const isHdr = looksHeader(b.body, b.lang);
      const ext = (isHdr && HDR[b.lang]) || PLAT_EXT[b.plat] || EXT[b.lang] || b.lang;
      let name = nameHint(b.body, ext);
      if (!name) {
        if (perLang[keyOf(b)] === 1) name = MAIN[b.lang] || "main";
        else if (b.heading) name = slugify(b.heading);
        else name = "part";
      }
      let cand = `${name}.${ext}`;
      if (b.lang === "cmake" && name === "CMakeLists") cand = "CMakeLists.txt";
      if (b.lang === "make") cand = "Makefile";
      const sub = keyOf(b);
      if (used[sub + "/" + cand]) { let n = 2; while (used[`${sub}/${name}-${n}.${ext}`]) n++; cand = `${name}-${n}.${ext}`; }
      used[sub + "/" + cand] = true;
      b.file = cand;
      b.sub = sub;                                  /* <мова>[/<платформа>] */
      b.rel = `${base}/${sub}/${cand}`;
    }

    /* третій прохід: переписати .md знизу вгору, щоб індекси не зсувались */
    const out = lines.slice();
    for (let k = blocks.length - 1; k >= 0; k--) {
      const b = blocks[k];
      out.splice(b.start, b.end - b.start + 1, `${b.indent}:::code ${b.rel}`);
    }

    if (APPLY) {
      for (const b of blocks) {
        const fp = path.join(dir, base, ...b.sub.split("/"), b.file);
        fs.mkdirSync(path.dirname(fp), { recursive: true });
        fs.writeFileSync(fp, b.body.join("\n").replace(/\s+$/, "") + "\n", "utf8");
      }
      fs.writeFileSync(p, out.join("\n"), "utf8");
    }

    const kind = L.classify(file, t.slug);
    if (kind === "basic" || kind === "detailed") ops.push({ op: "status", slug: t.slug, ver: kind, status: (t.node[kind] || {}).status || "recheck", recode: true });
    else if (L.INSERT_TYPES.includes(kind)) ops.push({ op: "insert", slug: t.slug, type: kind, file, status: (((t.node[kind] || []).find((x) => x.file === file)) || {}).status || "recheck", recode: true });

    totMd++; totFiles += blocks.length; totLines += blocks.reduce((a, b) => a + b.body.length, 0);
    changed.push({ topic: t.slug, file, n: blocks.length,
      langs: [...new Set(blocks.map((b) => b.sub))].sort().join("+"),
      names: blocks.map((b) => `${b.sub}/${b.file}`) });
  }
}

console.log(`\n=== ВИНЕСЕННЯ КОДУ · книга ${BOOK}${APPLY ? "" : "  (показ, нічого не записано)"} ===\n`);
console.log(`.md зачеплено: ${totMd} · файлів коду: ${totFiles} · рядків: ${totLines.toLocaleString("uk")}`);
if (skipped.length) console.log(`пропущено (тека вже є): ${skipped.length}`);
console.log("");
for (const c of changed.slice(0, 25))
  console.log(`  ${c.topic}/${c.file}\n      ${c.n} блок(ів) ${c.langs}: ${c.names.join(", ")}`);
if (changed.length > 25) console.log(`  … і ще ${changed.length - 25} файлів`);

if (APPLY && ops.length) {
  const qd = path.join(__dirname, "_finish");
  fs.mkdirSync(qd, { recursive: true });
  const qf = path.join(qd, `_recode-ops-${BOOK}.json`);
  fs.writeFileSync(qf, JSON.stringify(ops, null, 1), "utf8");
  console.log(`\nоперації recode → ${path.relative(process.cwd(), qf).replace(/\\/g, "/")}`);
  console.log(`застосувати: node scripts/manifest-patch.js --book ${BOOK} --ops scripts/_finish/_recode-ops-${BOOK}.json`);
} else if (!APPLY) console.log("\n(додай --apply, щоб записати)");
