#!/usr/bin/env node
/* Черга переписування коду: які файли чекають на справжній проєкт.
   Ужиток: node scripts/claude/recode-queue.js --book <слуг> [--limit N] [--fences] [--write]

   Робота ФАЙЛОВА, не темна: код належить конкретному .md, і тека проєкту названа
   саме ним (<тема>/<ім'я .md без розширення>/<мова>/). У 56% тем поруч живуть
   `proj` і `api` — темна черга злила б два різні проєкти в одну одиницю роботи.

   Два джерела черги:
     дефолт   — маніфестний прапорець `recode: true`. Його ставить finish-batch.js
                Antigravity КОЖНОМУ своєму файлу з кодом: прозу той конвеєр пише
                краще, ніж код, тож код звідти за означенням чекає на переписування;
     --fences — файли, де код ще лежить в огорожах (≥ EXTRACT_MIN рядків справжньою
                мовою) і теки проєкту немає. Це решта корпусу, написана до правила.

   Рівень береться з готових оцінок (scripts/_levels/…): він потрібен НЕ письменникові,
   а гейтові — підлога коду росте з рівня. Письменник рівня не бачить (див. recode-batch).  */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("../lib/manifest7.js");
const L = require("../checks/_lib.js");

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const has = (k) => argv.includes(k);

const BOOK = arg("--book", "");
const LIMIT = Number(arg("--limit", "0")) || 0;
const FENCES = has("--fences");
const WRITE = has("--write");
if (!BOOK) { console.error("треба --book <слуг> (див. root/shelf.json)"); process.exit(2); }

const rec = M7.books().get(BOOK);
if (!rec) { console.error(`нема книги «${BOOK}» у root/`); process.exit(3); }
const book = M7.loadBook(rec.bookDir);
if (!book) { console.error(`не читається маніфест книги «${BOOK}»`); process.exit(3); }

/* ── рівні з готових оцінок ───────────────────────────────────────────────── */
const lvJson = (p) => { try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch { return null; } };
const topicLv = new Map();
const insLv = new Map();                       // "тема/файл" → рівень
{
  const t = lvJson(path.join(__dirname, "..", "_levels", `${BOOK}.json`));
  for (const x of (t && t.topics) || []) if (x.level) topicLv.set(x.slug, x.level);
  const i = lvJson(path.join(__dirname, "..", "_levels", "inserts", `${BOOK}.json`));
  for (const x of (i && i.inserts) || []) if (x.level) insLv.set(`${x.topic}/${x.file}`, x.level);
}

/* ── чи є в огорожах код справжньою мовою від EXTRACT_MIN рядків ──────────── */
const FENCE = /^\s*```(.*)$/;
function fencedCode(md) {
  const out = {};
  let inC = false, lang = null, n = 0;
  for (const ln of md.split(/\r?\n/)) {
    const m = ln.match(FENCE);
    if (m) {
      if (!inC) { inC = true; lang = (m[1] || "").trim().split(/\s+/)[0].toLowerCase(); n = 0; }
      else { inC = false; const L2 = L.LANGS[lang]; if (L2 && n >= L.EXTRACT_MIN) out[L2[0]] = (out[L2[0]] || 0) + n; }
      continue;
    }
    if (inC) n++;
  }
  return out;                                   // { тека мови: рядків }
}

/* ── збір ─────────────────────────────────────────────────────────────────── */
const units = [];
for (const t of M7.allTopics(book)) {
  if (!t.own) continue;
  const dir = path.join(rec.bookDir, t.slug);
  if (!fs.existsSync(dir)) continue;

  const cand = [];
  if (t.node.detailed) cand.push({ file: `${t.slug}-d.md`, role: "detailed", node: t.node.detailed });
  if (t.node.basic) cand.push({ file: `${t.slug}.md`, role: "basic", node: t.node.basic });
  for (const ty of M7.INSERT_TYPES) for (const i of t.node[ty] || []) cand.push({ file: i.file, role: ty, node: i });

  for (const c of cand) {
    const p = path.join(dir, c.file);
    if (!fs.existsSync(p)) continue;
    const flagged = !!c.node.recode;
    const dirs = L.langDirsOf(dir, c.file);
    const fenced = fencedCode(L.read(p));
    const hasFenced = Object.keys(fenced).length > 0;

    /* дефолт — лише позначені; --fences — ще й ті, де код досі в огорожах */
    if (!flagged && !(FENCES && hasFenced && !dirs.length)) continue;
    if (dirs.length && !flagged) continue;      // уже переїхало й боргу не має

    units.push({
      dir: path.relative(process.cwd(), dir).replace(/\\/g, "/"),
      slug: t.slug,
      title: t.title || t.slug,
      file: c.file,
      role: c.role,
      ver: c.role === "detailed" || c.role === "basic" ? c.role : null,
      type: c.role === "detailed" || c.role === "basic" ? null : c.role,
      status: c.node.status || "",
      why: flagged ? "recode" : "огорожі",
      level: c.role === "detailed" || c.role === "basic"
        ? (topicLv.get(t.slug) || null)
        : (insLv.get(`${t.slug}/${c.file}`) || null),
      langs: Object.keys(fenced).sort(),
      fencedLines: Object.values(fenced).reduce((a, b) => a + b, 0),
      moved: dirs.map((d) => d.lang),
    });
  }
}

/* Найважчі — першими: там, де коду більше, переписування дає найбільше. */
units.sort((a, b) => b.fencedLines - a.fencedLines || a.slug.localeCompare(b.slug));
const out = LIMIT ? units.slice(0, LIMIT) : units;

/* ── звіт ─────────────────────────────────────────────────────────────────── */
const byRole = {};
for (const u of units) byRole[u.role] = (byRole[u.role] || 0) + 1;
const noLevel = units.filter((u) => !u.level).length;
console.log(`книга ${BOOK} · у черзі ${units.length} файлів` + (LIMIT ? ` (беремо ${out.length})` : ""));
console.log("  за роллю: " + Object.entries(byRole).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(" · "));
console.log("  рядків коду в огорожах: " + units.reduce((a, u) => a + u.fencedLines, 0).toLocaleString("uk"));
if (noLevel) console.log(`  ⚠ без оцінки рівня: ${noLevel} — гейт судитиме їх за підлогою Р1 (10 рядків)`);
if (!units.length) console.log("  порожньо: нема ні прапорців recode, ні коду в огорожах" + (FENCES ? "" : " (спробуй --fences)"));

if (WRITE) {
  const qdir = path.join(__dirname, "..", "_finish");
  fs.mkdirSync(qdir, { recursive: true });
  const qf = path.join(qdir, `_recode-${BOOK}.json`);
  fs.writeFileSync(qf, JSON.stringify(out, null, 1), "utf8");
  console.log(`\nзаписано ${path.relative(process.cwd(), qf).replace(/\\/g, "/")} — подавай його воркфлоу recode-batch`);
} else {
  console.log("\n(додай --write, щоб покласти чергу у scripts/_finish/_recode-<книга>.json)");
  out.slice(0, 12).forEach((u) => console.log(`  ${String(u.fencedLines).padStart(5)} рядків  ${u.langs.join("+") || "—"}  ${u.slug}/${u.file}` + (u.level ? `  Р${u.level}` : "  Р?")));
  if (out.length > 12) console.log(`  … і ще ${out.length - 12}`);
}
