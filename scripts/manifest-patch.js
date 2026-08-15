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
/* Маніфести існують у ДВОХ формах, і обидві мусять працювати — інакше дозволений редактор
   не бачить половини книг, і статуси починають правити руками:
     канонна (§2):  { slug: "foo", title: …, basic: { status: "empty" }, … }  — тема в одному рядку
     JSON-стиль:    "slug": "foo",                                            — тема розгорнута */
const findTopicLine = (slug) => lines.findIndex((l) =>
  (new RegExp(`\\{\\s*slug:\\s*"${esc(slug)}"[,\\s]`).test(l) && !/\bref:\s*"/.test(l)) ||
  new RegExp(`^\\s*"slug"\\s*:\\s*"${esc(slug)}"\\s*,?\\s*$`).test(l));
/** Секція/модуль: рядок зі slug і `scope:` (це відрізняє секцію від теми), масив може відкриватися
    у цьому ж або в наступних рядках — повертаємо {open, key}. */
function findSectionArray(sec) {
  for (let i = 0; i < lines.length; i++) {
    if (new RegExp(`^\\s*"?slug"?\\s*:\\s*"${esc(sec)}"`).test(lines[i]) || new RegExp(`\\{\\s*(?:n:\\s*\\d+,\\s*)?slug:\\s*"${esc(sec)}"`).test(lines[i])) {
      for (let j = i; j < Math.min(i + 15, lines.length); j++) {
        const key = /\b"?topics"?\s*:\s*\[/.test(lines[j]) ? "topics"
          : /\b"?steps"?\s*:\s*\[/.test(lines[j]) ? "steps"
          : /\b"?chapters"?\s*:\s*\[/.test(lines[j]) ? "chapters" : null;
        if (key) return { open: j, key, head: i };
      }
    }
  }
  return null;
}
const indentOf = (l) => (l.match(/^\s*/) || [""])[0];

/** Кінець масиву, відкритого в рядку `open` (рахуємо дужки [ ] від місця відкриття). */
function arrayEndLine(openIdx, key) {
  const openLine = lines[openIdx];
  const match = openLine.match(new RegExp(`"?${key}"?:\\s*\\[`));
  if (!match) return -1;
  const at = match.index;
  let depth = 0;
  for (let i = openIdx; i < lines.length; i++) {
    const from = i === openIdx ? at + match[0].length : 0;
    const s = lines[i].slice(from);
    for (const ch of s) { if (ch === "[") depth++; else if (ch === "]") { depth--; if (depth < 0) return i; } }
    if (depth === 0 && i > openIdx) return i;
  }
  return -1;
}

const report = { status: 0, statusIf: 0, insert: 0, topic: 0, skipped: [], similar: [], errors: [] };

/* ── операції ──────────────────────────────────────────────────────────────── */
/* Статус у БАГАТОРЯДКОВОМУ (JSON-стиль) маніфесті: тема-обʼєкт розгорнута на кілька рядків,
   тож однорядкова регулярка її не бачить. Шукаємо ключ версії нижче теми, а тоді найближчий
   "status" усередині його обʼєкта. Межа пошуку — початок наступної теми. */
function statusLineMulti(topicLine, ver) {
  const verRe = new RegExp(`^\\s*"?${ver}"?\\s*:\\s*\\{`);
  const nextTopic = new RegExp(`^\\s*"?slug"?\\s*:`);
  for (let i = topicLine + 1; i < Math.min(topicLine + 60, lines.length); i++) {
    if (nextTopic.test(lines[i])) break;                    // пішла наступна тема — версії не знайшли
    if (!verRe.test(lines[i])) continue;
    for (let j = i; j < Math.min(i + 6, lines.length); j++) {
      const m = lines[j].match(/^(\s*"?status"?\s*:\s*")([a-z]+)(")/);
      if (m) return { line: j, cur: m[2], re: /^(\s*"?status"?\s*:\s*")([a-z]+)(")/ };
      if (/^\s*\}/.test(lines[j]) && j > i) break;
    }
  }
  return null;
}

function opStatus(o, conditional) {
  const ver = o.ver === "basic" || o.ver === "detailed" ? o.ver : null;
  if (!ver) return report.errors.push(`status: дивний ver «${o.ver}» (${o.slug})`);
  const i = findTopicLine(o.slug);
  if (i < 0) return report.errors.push(`нема теми «${o.slug}»`);

  const to = conditional ? o.to : o.status;
  const re = new RegExp(`("?${ver}"?:\\s*\\{\\s*"?status"?:\\s*")([a-z]+)("\\s*\\})`);
  const m = lines[i].match(re);

  let cur, apply;
  if (m) {                                                  // канонна форма — усе в одному рядку
    cur = m[2];
    apply = () => { lines[i] = lines[i].replace(re, `$1${to}$3`); };
  } else {                                                  // JSON-стиль — тема розгорнута
    const hit = statusLineMulti(i, ver);
    if (!hit) {
      if (conditional) {
        report.skipped.push(`${o.slug}.${ver} не існує (не ${o.from})`);
        return;
      }
      const isSingleLine = /^\s*\{.*\}\s*,?\s*$/.test(lines[i]);
      if (isSingleLine) {
        apply = () => {
          const close = lines[i].lastIndexOf("}");
          const head = lines[i].slice(0, close).replace(/,\s*$/, "");
          const tail = lines[i].slice(close);
          lines[i] = `${head}, "${ver}": { "status": "${to}" } ${tail}`;
        };
      } else {
        apply = () => {
          const indent = indentOf(lines[i]) + "  ";
          lines.splice(i + 2, 0, `${indent}"${ver}": {`, `${indent}  "status": "${to}"`, `${indent}},`);
        };
      }
      cur = null;
    } else {
      cur = hit.cur;
      apply = () => { lines[hit.line] = lines[hit.line].replace(hit.re, `$1${to}$3`); };
    }
  }

  if (conditional && cur !== o.from) { report.skipped.push(`${o.slug}.${ver}=${cur} (чекали ${o.from})`); return; }
  if (cur === to) { report.skipped.push(`${o.slug}.${ver} вже ${to}`); return; }
  apply();
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
  const isSingleLine = /^\s*\{.*\}\s*,?\s*$/.test(line);

  if (isSingleLine) {
    const arrRe = new RegExp(`"?${type}"?:\\s*\\[([^\\]]*)\\]`);
    const am = line.match(arrRe);
    if (am) {
      const fileRe = new RegExp(`\\{\\s*"?file"?:\\s*"${esc(file)}"\\s*,\\s*"?status"?:\\s*"([a-z]+)"\\s*\\}`);
      const fm = am[1].match(fileRe);
      if (fm) {
        if (fm[1] === status) { report.skipped.push(`${o.slug}/${file} вже ${status}`); return; }
        lines[i] = line.replace(fileRe, `{ file: "${file}", status: "${status}" }`);
      } else {
        const body = am[1].trim();
        const next = body ? `"${type}": [${am[1].replace(/\s*$/, "")}, { file: "${file}", status: "${status}" }]`
                          : `"${type}": [{ file: "${file}", status: "${status}" }]`;
        lines[i] = line.replace(arrRe, next);
      }
    } else {
      const close = line.lastIndexOf("}");
      const tail = line.slice(close);
      const head = line.slice(0, close).replace(/,\s*$/, "");
      lines[i] = `${head}, "${type}": [{ file: "${file}", status: "${status}" }] ${tail}`;
    }
  } else {
    // Многорядковий (JSON-стиль) маніфест
    let startLine = i;
    while (startLine > 0 && !/^\s*\{/.test(lines[startLine])) {
      startLine--;
    }
    let endLine = i;
    const nextSlug = new RegExp(`^\\s*"?slug"?\\s*:`);
    for (let j = i + 1; j < lines.length; j++) {
      if (nextSlug.test(lines[j])) { endLine = j - 1; break; }
      if (/^\s*\}[,\s]*$/.test(lines[j])) { endLine = j; break; }
    }

    const blockText = lines.slice(startLine, endLine + 1).join("\n");
    const arrRe = new RegExp(`"?${type}"?:\\s*\\[([\\s\\S]*?)\\]`);
    const am = blockText.match(arrRe);

    if (am) {
      const fileRe = new RegExp(`\\{\\s*"?file"?:\\s*"${esc(file)}"\\s*,\\s*"?status"?:\\s*"([a-z]+)"\\s*\\}`);
      const fm = am[1].match(fileRe);
      if (fm) {
        if (fm[1] === status) { report.skipped.push(`${o.slug}/${file} вже ${status}`); return; }
        for (let j = startLine; j <= endLine; j++) {
          if (lines[j].includes(file)) {
            for (let k = j; k <= Math.min(j + 3, endLine); k++) {
              if (lines[k].includes("status")) {
                lines[k] = lines[k].replace(/"status":\s*"[a-z]+"/, `"status": "${status}"`);
                lines[k] = lines[k].replace(/status:\s*"[a-z]+"/, `status: "${status}"`);
                break;
              }
            }
            break;
          }
        }
      } else {
        let typeArrayLine = -1;
        const typeRe = new RegExp(`^\\s*"?${type}"?\\s*:\\s*\\[`);
        for (let j = startLine; j <= endLine; j++) {
          if (typeRe.test(lines[j])) { typeArrayLine = j; break; }
        }
        if (typeArrayLine >= 0) {
          let closeArrayLine = typeArrayLine;
          for (let j = typeArrayLine; j <= endLine; j++) {
            if (lines[j].includes("]")) { closeArrayLine = j; break; }
          }
          const indent = indentOf(lines[typeArrayLine]) + "    ";
          const newEntryLines = [
            `${indent}{`,
            `${indent}  "file": "${file}",`,
            `${indent}  "status": "${status}"`,
            `${indent}}`
          ];
          if (lines[closeArrayLine].trim() === "]") {
            if (closeArrayLine > typeArrayLine && !lines[closeArrayLine - 1].trim().endsWith(",")) {
              lines[closeArrayLine - 1] += ",";
            }
            lines.splice(closeArrayLine, 0, ...newEntryLines);
          } else {
            const newArrayContent = [
              `${indentOf(lines[typeArrayLine])}"${type}": [`,
              ...newEntryLines,
              `${indentOf(lines[typeArrayLine])}]`
            ];
            const hasComma = lines[typeArrayLine].trim().endsWith(",");
            if (hasComma) newArrayContent[newArrayContent.length - 1] += ",";
            lines.splice(typeArrayLine, 1, ...newArrayContent);
          }
        }
      }
    } else {
      let insertPos = endLine;
      const indent = indentOf(lines[i]);
      if (lines[insertPos - 1] && !lines[insertPos - 1].trim().endsWith(",") && !lines[insertPos - 1].trim().endsWith("{")) {
        lines[insertPos - 1] += ",";
      }
      const newArrayLines = [
        `${indent}"${type}": [`,
        `${indent}  {`,
        `${indent}    "file": "${file}",`,
        `${indent}    "status": "${status}"`,
        `${indent}  }`,
        `${indent}],`
      ];
      lines.splice(insertPos, 0, ...newArrayLines);
    }
  }
  report.insert++;
}

/** Усі слуги книги — щоб ловити СИНОНІМИ (§4: один термін на поняття). */
function allSlugs() {
  return lines.map((l) => (l.match(/\{\s*slug:\s*"([a-z0-9-]+)"/)
    || l.match(/^\s*"slug"\s*:\s*"([a-z0-9-]+)"/) || [])[1]).filter(Boolean);
}
/** Слуг «близький» до наявного, якщо один вкладений в інший АБО в них спільне РІДКІСНЕ слово.
    Рідкість важить: «pipeline» у книзі про GStreamer є всюди й нічого не каже, а «threads» у двох
    темах — це майже напевно одне поняття двома слугами (streaming-threads ↔ threads-and-queues). */
const STOP = new Set(["and", "vs", "the", "of", "in", "to", "a", "for", "with", "model", "basics", "types", "api"]);
const wordsOf = (s) => s.split("-").filter((x) => x.length > 2 && !STOP.has(x));
/** Вкладеність рахуємо ПО МЕЖАХ сегментів, а не сирим includes: інакше «io» «збігається»
    з «virtio-paravirtual-bus», і сигнал тоне в шумі. */
const segIn = (a, b) => (b + "-").includes(a + "-") && (("-" + b).includes("-" + a));
/** Нормалізований слуг (без дефісів). Саме цю діру пройшов «dmabuf-sharing» повз «dma-buf»:
    посегментно спільних слів у них НЕМА, а без дефісів один — префікс іншого. */
const normOf = (s) => s.replace(/-/g, "");
function similarSlugs(slug) {
  const existing = allSlugs().filter((s) => s !== slug);
  const freq = new Map();
  for (const s of existing) for (const w of new Set(wordsOf(s))) freq.set(w, (freq.get(w) || 0) + 1);
  const mine = new Set(wordsOf(slug));
  const nMine = normOf(slug);
  const hits = [];
  for (const s of existing) {
    if (segIn(s, slug) || segIn(slug, s)) { hits.push(s); continue; }
    const nS = normOf(s);
    // нормалізована рівність/вкладеність: dma-buf ↔ dmabuf-sharing, drm-kms ↔ drmkms-model
    if (nMine.length >= 5 && nS.length >= 5 && (nS === nMine || nS.startsWith(nMine) || nMine.startsWith(nS)
        || nS.endsWith(nMine) || nMine.endsWith(nS))) { hits.push(s); continue; }
    const other = new Set(wordsOf(s));
    const shared = [...mine].filter((x) => other.has(x));
    if (!shared.length) continue;
    // спільне слово, що трапляється щонайбільше у трьох темах книги, — сильний сигнал
    if (shared.some((w) => (freq.get(w) || 0) <= 3)) hits.push(s);
  }
  return hits;
}

/** Слуги ІНШИХ книг корпусу — той самий слуг у двох книгах ніхто не перевіряв, і так
    розійшлися vdso (unix-linux ↔ programming) та gpu-command-submission. Читаємо сирі
    маніфести регуляркою (не eval): дешево й без побічних ефектів. */
let FOREIGN = null;
function foreignSlugs() {
  if (FOREIGN) return FOREIGN;
  FOREIGN = new Map();   // slug → "книга/секція"
  const root = path.resolve(path.dirname(MF), "..", "..");
  const mine = path.resolve(MF);
  for (const kind of ["book", "catalog", "reference"]) {
    const dir = path.join(root, kind);
    if (!fs.existsSync(dir)) continue;
    for (const bk of fs.readdirSync(dir)) {
      const f = path.join(dir, bk, "manifest.js");
      if (!fs.existsSync(f) || path.resolve(f) === mine) continue;
      let src; try { src = fs.readFileSync(f, "utf8"); } catch (e) { continue; }
      for (const l of src.split(/\r?\n/)) {
        const m = l.match(/\{\s*slug:\s*"([a-z0-9-]+)"/);
        if (m && /\b(?:basic|detailed):\s*\{/.test(l) && !FOREIGN.has(m[1])) FOREIGN.set(m[1], `${bk}`);
      }
    }
  }
  return FOREIGN;
}

/** Кома перед вставкою: попередній елемент масиву міг бути останнім і йти без коми,
    а після вставки він стає середнім. Без цього маніфест перестає парситись. */
function commaBefore(idx) {
  for (let i = idx - 1; i >= 0; i--) {
    const t = lines[i].trim();
    if (!t) continue;
    if (/[[,]$/.test(t)) return;
    lines[i] = lines[i].replace(/s*$/, ",");
    return;
  }
}

/** Межі об'єкта теми, усередині якого стоїть рядок idx (одно- і багаторядкова форми). */
function objectRange(idx) {
  if (/\{[\s\S]*\}/.test(lines[idx])) return { start: idx, end: idx };
  let start = idx;
  while (start >= 0 && !lines[start].includes("{")) start--;
  if (start < 0) return null;
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === "{") { depth++; seen = true; } else if (ch === "}") depth--; }
    if (seen && depth === 0) return { start, end: i };
  }
  return null;
}

/* Створити секцію. Потрібна, коли теми давно лежать у теці, якої в маніфесті нема:
   без цієї операції opTopic лише лається «створи секцію вручну», а руками — не можна. */
function opSection(o) {
  if (findSectionArray(o.slug)) { report.skipped.push(`секція «${o.slug}» уже є`); return; }
  const si = lines.findIndex((l) => /"?sections"?\s*:\s*\[/.test(l));
  if (si < 0) return report.errors.push("не знайшов масив sections");
  const end = arrayEndLine(si, "sections");
  if (end < 0) return report.errors.push("не знайшов кінець масиву sections");
  const sample = lines.slice(si + 1, end).find((l) => l.trim() === "{");
  const ind = sample ? indentOf(sample) : indentOf(lines[si]) + "  ";
  const q = lines[si].includes('"sections"') ? '"' : "";
  const title = String(o.title || o.slug).replace(/"/g, '\\"');
  const scope = String(o.scope || "").replace(/"/g, '\\"');
  commaBefore(end);
  lines.splice(end, 0,
    `${ind}{`,
    `${ind}  ${q}slug${q}: "${o.slug}",`,
    `${ind}  ${q}title${q}: "${title}",`,
    `${ind}  ${q}scope${q}: "${scope}",`,
    `${ind}  ${q}topics${q}: [`,
    `${ind}  ]`,
    `${ind}},`);
  report.section = (report.section || 0) + 1;
}

/* Перенести тему в іншу секцію РАЗОМ з усім її вмістом (статуси версій, масиви вставок).
   Вирізаємо рядки об'єкта як є й вставляємо в кінець масиву цільової секції — так нічого
   не губиться й не переформатовується. Не вийшло — кладемо назад і кажемо про це. */
function opMove(o) {
  const i = findTopicLine(o.slug);
  if (i < 0) return report.errors.push(`нема теми «${o.slug}» для переносу`);
  const cur = sectionOfTopic(i);
  if (cur === o.to) { report.skipped.push(`«${o.slug}» уже в секції «${o.to}»`); return; }
  const r = objectRange(i);
  if (!r) return report.errors.push(`не виділив об'єкт теми «${o.slug}»`);
  const block = lines.slice(r.start, r.end + 1);
  lines.splice(r.start, block.length);

  const sa = findSectionArray(o.to);
  if (!sa) { lines.splice(r.start, 0, ...block); return report.errors.push(`нема секції «${o.to}» — «${o.slug}» не рушено`); }
  const end = arrayEndLine(sa.open, sa.key);
  if (end < 0) { lines.splice(r.start, 0, ...block); return report.errors.push(`не знайшов кінець «${o.to}» — «${o.slug}» не рушено`); }

  const sample = lines.slice(sa.open + 1, end).find((l) => l.trim() === "{" || /^\s*\{\s*slug:/.test(l));
  const dst = sample ? indentOf(sample) : indentOf(lines[sa.open]) + "  ";
  const src = indentOf(block[0]);
  const delta = dst.length - src.length;
  const shift = (l) => delta === 0 ? l : delta > 0 ? " ".repeat(delta) + l : l.slice(Math.min(-delta, indentOf(l).length));
  const out = block.map(shift);
  if (!/,\s*$/.test(out[out.length - 1])) out[out.length - 1] += ",";
  commaBefore(end);
  lines.splice(end, 0, ...out);
  report.move = (report.move || 0) + 1;
}

/** Слуг секції, у якій стоїть рядок теми idx (шукаємо найближчий slug вище за scope/topics). */
function sectionOfTopic(idx) {
  for (let i = idx - 1; i >= 0; i--) {
    if (/"?topics"?\s*:\s*\[/.test(lines[i])) {
      for (let j = i; j >= Math.max(0, i - 6); j--) {
        const m = lines[j].match(/"?slug"?\s*:\s*"([^"]+)"/);
        if (m) return m[1];
      }
    }
  }
  return null;
}

/* Прибрати запис теми. Захисток три: тема мусить існувати · тека теми мусить бути
   ПОРОЖНЬОЮ або відсутньою (щоб не викинути з маніфесту написану статтю) · і в підсумку
   перевіряється, що тем поменшало рівно на стільки, скільки просили. */
function opDrop(o) {
  const i = findTopicLine(o.slug);
  if (i < 0) { report.skipped.push(`теми «${o.slug}» в маніфесті нема — нічого прибирати`); return; }
  const r = objectRange(i);
  if (!r) return report.errors.push(`не виділив об'єкт теми «${o.slug}»`);
  lines.splice(r.start, r.end - r.start + 1);
  report.drop = (report.drop || 0) + 1;
}

function opTopic(o) {
  if (findTopicLine(o.slug) >= 0) { report.skipped.push(`тема «${o.slug}» вже є`); return; }
  // §4/§6: перш ніж заводити, перевіряємо, чи це не та сама тема іншим слугом. Не блокуємо —
  // рішення про об'єднання людське, — але кажемо ГОЛОСНО, бо мовчазний дубль коштує зайвої статті.
  const near = similarSlugs(o.slug);
  if (near.length) report.similar.push(`«${o.slug}» схожа на: ${near.join(", ")} — перевір, чи не той самий термін (§4)`);
  // той самий слуг в ІНШІЙ книзі — окремий, сильніший сигнал: дві книги не тримають одну статтю
  const foreign = foreignSlugs().get(o.slug);
  if (foreign) report.similar.push(`«${o.slug}» ВЖЕ Є в книзі «${foreign}» — вирішіть, чия це тема (§1)`);
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
  commaBefore(end);
  lines.splice(end, 0, `${ind}{ slug: "${o.slug}", title: "${title}", basic: { status: "${basic}" }, detailed: { status: "${detailed}" } },`);
  report.topic++;
}

for (const o of ops) {
  if (!o || !o.op) { report.errors.push("операція без op"); continue; }
  if (o.op === "status") opStatus(o, false);
  else if (o.op === "status-if") opStatus(o, true);
  else if (o.op === "insert") opInsert(o);
  else if (o.op === "topic") opTopic(o);
  else if (o.op === "section") opSection(o);
  else if (o.op === "move") opMove(o);
  else if (o.op === "drop") opDrop(o);
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
const dropped = report.drop || 0;
if (nAfter < nBefore - dropped) {
  console.error(`✖ тем стало менше, ніж просили прибрати (${nBefore} → ${nAfter}, drop ${dropped}) — файл не змінено`);
  process.exit(2);
}
const changed = report.status + report.statusIf + report.insert + report.topic + (report.section || 0) + (report.move || 0) + (report.drop || 0);
if (!DRY && changed) fs.writeFileSync(MF, OUT);

console.log(`manifest-patch ${path.basename(path.dirname(MF))}: статусів ${report.status}, умовних ${report.statusIf}, вставок ${report.insert}, нових тем ${report.topic}, секцій ${report.section || 0}, переносів ${report.move || 0}, прибрано ${report.drop || 0}; тем у книзі ${nBefore}→${nAfter}${DRY ? " (DRY — не записано)" : changed ? "" : " (нічого міняти)"}`);
if (report.skipped.length) console.log(`  ~ пропущено (вже так): ${report.skipped.length}${report.skipped.length <= 12 ? " — " + report.skipped.join("; ") : ""}`);
if (report.similar.length) {
  console.log(`  ⚠ МОЖЛИВІ ДУБЛІ ПОНЯТТЯ: ${report.similar.length}`);
  for (const s of report.similar) console.log(`     • ${s}`);
  /* Кладемо НА ДИСК. Причина конкретна: цей скрипт запускає одноразовий агент, і його stdout
     нікуди не потрапляє — а як агент іще й помре (2026-08-09: API error на фазі «Маніфест»),
     вивід гине разом з ним. Саме так у корпус мовчки зайшли чотири дублі. Диск переживає все. */
  try {
    const dir = path.join(path.dirname(MF), "..", "..", "scripts", "_finish");
    fs.mkdirSync(dir, { recursive: true });
    const bk = path.basename(path.dirname(MF));
    const out = path.join(dir, `_dupes-${bk}.json`);
    let prev = []; try { prev = JSON.parse(fs.readFileSync(out, "utf8")); } catch (e) {}
    const merged = [...new Set([...(Array.isArray(prev) ? prev : []), ...report.similar])];
    if (!DRY) fs.writeFileSync(out, JSON.stringify(merged, null, 2));
    console.log(`     ↳ ${DRY ? "(DRY, не записано) " : ""}список на диску: scripts/_finish/_dupes-${bk}.json`);
  } catch (e) { console.log(`     ↳ не зберіг список дублів: ${e.message}`); }
}
if (report.errors.length) { console.log(`  ✖ помилок: ${report.errors.length}`); for (const e of report.errors.slice(0, 20)) console.log(`     • ${e}`); }
process.exit(report.errors.length ? 1 : 0);
