#!/usr/bin/env node
/* ============================================================================
   manifest-patch.js — ЛОКАЛЬНИЙ детермінований редактор маніфесту (без агентів).
   Замінює «агент читає маніфест і робить точкові Edit-и» у фазі «Маніфест» батчу:
   агент лише кладе файл операцій і запускає цей скрипт — токени не витрачаються
   на читання 60-кілобайтного маніфесту й десятки правок.

   Запуск:
     node scripts/manifest-patch.js <manifest.js> --ops <ops.json> [--dry]
     node scripts/manifest-patch.js <manifest.js> --ops -            (ops із stdin)

   ops.json — масив операцій (або {ops:[…]}); кожна ідемпотентна:
     { op:"status",    slug, ver:"basic"|"detailed", status:"done" }
     { op:"status-if", slug, ver, from:"empty", to:"pending" }        // міняє, лише якщо зараз from
     { op:"insert",    slug, type:"hist|comp|math|proj|api", file:"proj-x.md", status?:"done", section? }
     { op:"topic",     section, slug, title, basic?:"empty", detailed?:"pending" }   // §3/§6: нове — у ДЕТАЛЬНУ

   Гарантії: після правок файл ПЕРЕПАРСЮЄТЬСЯ (new Function + перевірка структури);
   якщо результат не валідний — на диск НЕ пишеться, код виходу 2.
   Формат рядків зберігається (теми — по одному об'єкту в рядку, як у v6-маніфестах).
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

/* ── аргументи ─────────────────────────────────────────────────────────────── */
const argv = process.argv.slice(2);
const MF = argv.find((a) => !a.startsWith("--"));
const opsArgIdx = argv.indexOf("--ops");
const OPS_SRC = opsArgIdx >= 0 ? argv[opsArgIdx + 1] : null;
const DRY = argv.includes("--dry");
if (!MF || !OPS_SRC) {
  console.error("Ужиток: node scripts/manifest-patch.js <manifest.js> --ops <ops.json|-> [--dry]");
  process.exit(2);
}
if (!fs.existsSync(MF)) { console.error(`нема маніфесту: ${MF}`); process.exit(2); }

let opsRaw;
try {
  opsRaw = OPS_SRC === "-" ? fs.readFileSync(0, "utf8") : fs.readFileSync(OPS_SRC, "utf8");
} catch (e) { console.error(`не прочитати ops: ${e.message}`); process.exit(2); }
let ops;
try {
  const parsed = JSON.parse(opsRaw);
  ops = Array.isArray(parsed) ? parsed : (parsed && Array.isArray(parsed.ops) ? parsed.ops : null);
} catch (e) { console.error(`ops не JSON: ${e.message}`); process.exit(2); }
if (!ops) { console.error("ops має бути масивом або {ops:[…]}"); process.exit(2); }

/* ── парсер маніфесту (для валідації до й після) ───────────────────────────── */
function parseManifest(src) {
  const sb = {};
  new Function("window", src)(sb);
  const isGuide = Array.isArray(sb.__GUIDES__) && sb.__GUIDES__.length;
  const m = (isGuide ? sb.__GUIDES__ : sb.__BOOKS__ || [])[0];
  if (!m) throw new Error("маніфест не зареєстрував книгу/курс");
  return { m, isGuide };
}
function topicsOf(m, isGuide) {
  const out = [];
  if (isGuide) {
    for (const mod of m.modules || m.sections || [])
      for (const ch of mod.chapters || [{ steps: mod.steps || mod.topics || [] }])
        for (const s of ch.steps || ch.topics || []) if (s && s.slug && !s.ref) out.push(s);
  } else {
    for (const sec of m.sections || []) for (const t of sec.topics || []) out.push(t);
  }
  return out;
}

const ORIG = fs.readFileSync(MF, "utf8");
let before;
try { before = parseManifest(ORIG); } catch (e) { console.error(`маніфест не парситься ДО правок: ${e.message}`); process.exit(2); }
const EOL = ORIG.includes("\r\n") ? "\r\n" : "\n";
let lines = ORIG.split(/\r?\n/);

/* ── помічники по рядках ───────────────────────────────────────────────────── */
const esc = (s) => String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const findTopicLine = (slug) => lines.findIndex((l) => new RegExp(`\\{\\s*slug:\\s*"${esc(slug)}"[,\\s]`).test(l) && !/\bref:\s*"/.test(l));
/** Секція/модуль: рядок зі slug і `scope:` (це відрізняє секцію від теми), масив може відкриватися
    у цьому ж або в наступних рядках — повертаємо {open, key}. */
function findSectionArray(sec) {
  const si = lines.findIndex((l) => new RegExp(`\\{\\s*(?:n:\\s*\\d+,\\s*)?slug:\\s*"${esc(sec)}"`).test(l) && /\bscope:/.test(l));
  if (si < 0) return null;
  for (let i = si; i < Math.min(si + 4, lines.length); i++) {
    const key = /\btopics:\s*\[/.test(lines[i]) ? "topics"
      : /\bsteps:\s*\[/.test(lines[i]) ? "steps"
      : /\bchapters:\s*\[/.test(lines[i]) ? "chapters" : null;
    if (key) return { open: i, key, head: si };
  }
  return null;
}
const indentOf = (l) => (l.match(/^\s*/) || [""])[0];

/** Кінець масиву, відкритого в рядку `open` (рахуємо дужки [ ] від місця відкриття). */
function arrayEndLine(openIdx, key) {
  const openLine = lines[openIdx];
  const at = openLine.indexOf(`${key}: [`);
  if (at < 0) return -1;
  let depth = 0;
  for (let i = openIdx; i < lines.length; i++) {
    const from = i === openIdx ? at + key.length + 2 : 0;
    const s = lines[i].slice(from);
    for (const ch of s) { if (ch === "[") depth++; else if (ch === "]") { depth--; if (depth < 0) return i; } }
    if (depth === 0 && i > openIdx) return i;
  }
  return -1;
}

const report = { status: 0, statusIf: 0, insert: 0, topic: 0, skipped: [], similar: [], errors: [] };

/* ── операції ──────────────────────────────────────────────────────────────── */
function opStatus(o, conditional) {
  const ver = o.ver === "basic" || o.ver === "detailed" ? o.ver : null;
  if (!ver) return report.errors.push(`status: дивний ver «${o.ver}» (${o.slug})`);
  const i = findTopicLine(o.slug);
  if (i < 0) return report.errors.push(`нема теми «${o.slug}»`);
  const re = new RegExp(`(${ver}:\\s*\\{\\s*status:\\s*")([a-z]+)("\\s*\\})`);
  const m = lines[i].match(re);
  if (!m) return report.errors.push(`у теми «${o.slug}» нема поля ${ver}`);
  const cur = m[2];
  const to = conditional ? o.to : o.status;
  if (conditional && cur !== o.from) { report.skipped.push(`${o.slug}.${ver}=${cur} (чекали ${o.from})`); return; }
  if (cur === to) { report.skipped.push(`${o.slug}.${ver} вже ${to}`); return; }
  lines[i] = lines[i].replace(re, `$1${to}$3`);
  conditional ? report.statusIf++ : report.status++;
}

function opInsert(o) {
  const type = String(o.type || "").replace(/-$/, "");
  if (!/^(hist|comp|math|proj|api)$/.test(type)) return report.errors.push(`insert: дивний type «${o.type}» (${o.file})`);
  const file = String(o.file || "");
  if (!file.endsWith(".md")) return report.errors.push(`insert: файл без .md — «${file}»`);
  const status = o.status || "done";
  const i = findTopicLine(o.slug);
  if (i < 0) return report.errors.push(`нема теми «${o.slug}» для вставки ${file}`);
  const line = lines[i];
  const arrRe = new RegExp(`${type}:\\s*\\[([^\\]]*)\\]`);
  const am = line.match(arrRe);
  if (am) {
    const fileRe = new RegExp(`\\{\\s*file:\\s*"${esc(file)}"\\s*,\\s*status:\\s*"([a-z]+)"\\s*\\}`);
    const fm = am[1].match(fileRe);
    if (fm) {
      if (fm[1] === status) { report.skipped.push(`${o.slug}/${file} вже ${status}`); return; }
      lines[i] = line.replace(fileRe, `{ file: "${file}", status: "${status}" }`);
    } else {
      const body = am[1].trim();
      const next = body ? `${type}: [${am[1].replace(/\s*$/, "")}, { file: "${file}", status: "${status}" }]`
                        : `${type}: [{ file: "${file}", status: "${status}" }]`;
      lines[i] = line.replace(arrRe, next);
    }
  } else {
    // масиву типу ще нема — додаємо перед закриттям об'єкта теми (останнє " }" у рядку)
    const close = line.lastIndexOf("}");
    const tail = line.slice(close);                      // "}," або "}"
    const head = line.slice(0, close).replace(/,\s*$/, "");
    lines[i] = `${head}, ${type}: [{ file: "${file}", status: "${status}" }] ${tail}`;
  }
  report.insert++;
}

/** Усі слуги книги — щоб ловити СИНОНІМИ (§4: один термін на поняття). */
function allSlugs() {
  return lines.map((l) => (l.match(/\{\s*slug:\s*"([a-z0-9-]+)"/) || [])[1]).filter(Boolean);
}
/** Слуг «близький» до наявного, якщо один вкладений в інший АБО в них спільне РІДКІСНЕ слово.
    Рідкість важить: «pipeline» у книзі про GStreamer є всюди й нічого не каже, а «threads» у двох
    темах — це майже напевно одне поняття двома слугами (streaming-threads ↔ threads-and-queues). */
const STOP = new Set(["and", "vs", "the", "of", "in", "to", "a", "for", "with", "model", "basics", "types", "api"]);
const wordsOf = (s) => s.split("-").filter((x) => x.length > 2 && !STOP.has(x));
function similarSlugs(slug) {
  const existing = allSlugs().filter((s) => s !== slug);
  const freq = new Map();
  for (const s of existing) for (const w of new Set(wordsOf(s))) freq.set(w, (freq.get(w) || 0) + 1);
  const mine = new Set(wordsOf(slug));
  const hits = [];
  for (const s of existing) {
    if (s.includes(slug) || slug.includes(s)) { hits.push(s); continue; }
    const other = new Set(wordsOf(s));
    const shared = [...mine].filter((x) => other.has(x));
    if (!shared.length) continue;
    // спільне слово, що трапляється щонайбільше у трьох темах книги, — сильний сигнал
    if (shared.some((w) => (freq.get(w) || 0) <= 3)) hits.push(s);
  }
  return hits;
}

function opTopic(o) {
  if (findTopicLine(o.slug) >= 0) { report.skipped.push(`тема «${o.slug}» вже є`); return; }
  // §4/§6: перш ніж заводити, перевіряємо, чи це не та сама тема іншим слугом. Не блокуємо —
  // рішення про об'єднання людське, — але кажемо ГОЛОСНО, бо мовчазний дубль коштує зайвої статті.
  const near = similarSlugs(o.slug);
  if (near.length) report.similar.push(`«${o.slug}» схожа на: ${near.join(", ")} — перевір, чи не той самий термін (§4)`);
  const basic = o.basic || "empty";
  const detailed = o.detailed || "pending";           // §3/§6: у чергу йде ДЕТАЛЬНА
  const sa = findSectionArray(o.section);
  if (!sa) return report.errors.push(`нема секції «${o.section}» для теми «${o.slug}» (створи секцію вручну)`);
  if (sa.key === "chapters") return report.errors.push(`«${o.section}» — модуль guide із розділами: додай крок вручну (${o.slug})`);
  const si = sa.open, key = sa.key;
  const end = arrayEndLine(si, key);
  if (end < 0) return report.errors.push(`не знайшов кінець масиву ${key} секції «${o.section}»`);
  // відступ — як у сусідньої теми, інакше +4 від секції
  const sample = lines.slice(si + 1, end).find((l) => /\{\s*slug:\s*"/.test(l));
  const ind = sample ? indentOf(sample) : indentOf(lines[si]) + "  ";
  const title = String(o.title || o.slug).replace(/"/g, '\\"');
  lines.splice(end, 0, `${ind}{ slug: "${o.slug}", title: "${title}", basic: { status: "${basic}" }, detailed: { status: "${detailed}" } },`);
  report.topic++;
}

for (const o of ops) {
  if (!o || !o.op) { report.errors.push("операція без op"); continue; }
  if (o.op === "status") opStatus(o, false);
  else if (o.op === "status-if") opStatus(o, true);
  else if (o.op === "insert") opInsert(o);
  else if (o.op === "topic") opTopic(o);
  else report.errors.push(`невідома op «${o.op}»`);
}

/* ── валідація й запис ─────────────────────────────────────────────────────── */
const OUT = lines.join(EOL);
let after;
try { after = parseManifest(OUT); } catch (e) {
  console.error(`✖ після правок маніфест НЕ парситься (${e.message}) — файл не змінено`);
  process.exit(2);
}
const nBefore = topicsOf(before.m, before.isGuide).length;
const nAfter = topicsOf(after.m, after.isGuide).length;
if (nAfter < nBefore) {
  console.error(`✖ тем стало менше (${nBefore} → ${nAfter}) — файл не змінено`);
  process.exit(2);
}
const changed = report.status + report.statusIf + report.insert + report.topic;
if (!DRY && changed) fs.writeFileSync(MF, OUT);

console.log(`manifest-patch ${path.basename(path.dirname(MF))}: статусів ${report.status}, умовних ${report.statusIf}, вставок ${report.insert}, нових тем ${report.topic}; тем у книзі ${nBefore}→${nAfter}${DRY ? " (DRY — не записано)" : changed ? "" : " (нічого міняти)"}`);
if (report.skipped.length) console.log(`  ~ пропущено (вже так): ${report.skipped.length}${report.skipped.length <= 12 ? " — " + report.skipped.join("; ") : ""}`);
if (report.similar.length) { console.log(`  ⚠ МОЖЛИВІ ДУБЛІ ПОНЯТТЯ: ${report.similar.length}`); for (const s of report.similar) console.log(`     • ${s}`); }
if (report.errors.length) { console.log(`  ✖ помилок: ${report.errors.length}`); for (const e of report.errors.slice(0, 20)) console.log(`     • ${e}`); }
process.exit(report.errors.length ? 1 : 0);
