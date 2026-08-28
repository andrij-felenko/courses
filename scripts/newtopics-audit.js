#!/usr/bin/env node
/* ============================================================================
   newtopics-audit.js — ЛОКАЛЬНИЙ (0 токенів) розбір тем, заведених одним комітом.

   Питання, на яке відповідає: «що з цього справді варте окремої теми?». Дешеве
   судить скрипт, дороге лишає моделі. Локально видно те, що читається з самого
   слуга й з корпусу: дублі понять, родові слуги, порушена конвенція книги,
   сирітство (на тему ніхто не посилається).

   Запуск:  node scripts/newtopics-audit.js                  (HEAD проти HEAD~1)
            node scripts/newtopics-audit.js <sha>            (інший коміт)
            node scripts/newtopics-audit.js --json out.json  (payload для суддів)
   ========================================================================== */
"use strict";
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const argv = process.argv.slice(2);
const jsonAt = argv.indexOf("--json");
const jsonOut = jsonAt >= 0 ? argv[jsonAt + 1] : null;
const SHA = argv.find((a, i) => !a.startsWith("--") && i !== jsonAt + 1) || "HEAD";

const git = (...a) => execFileSync("git", a, { cwd: ROOT, encoding: "utf8", maxBuffer: 128e6 });
const parse = (s) => { try { return JSON.parse(s) } catch (e) { return null } };

/* --- 1. Індекс УСЬОГО корпусу: <книга>/<слуг> -> тема ---------------------- */
const INDEX = new Map();
const BOOKS = new Map();
for (const kind of fs.readdirSync(path.join(ROOT, "root"))) {
  const kdir = path.join(ROOT, "root", kind);
  if (!fs.statSync(kdir).isDirectory()) continue;
  for (const book of fs.readdirSync(kdir)) {
    const bdir = path.join(kdir, book);
    if (!fs.statSync(bdir).isDirectory()) continue;
    const B = { kind, topics: [], anyDetailed: false, anyBasic: false };
    for (const f of fs.readdirSync(bdir)) {
      if (!f.endsWith(".json") || f === "manifest.json") continue;
      const j = parse(fs.readFileSync(path.join(bdir, f), "utf8"));
      if (!j) continue;
      for (const ch of (j.chapters || []))
        for (const t of (ch.topics || [])) {
          if (t.ref || !t.slug) continue;
          const bs = (t.basic && t.basic.status) || "empty";
          const ds = (t.detailed && t.detailed.status) || "empty";
          INDEX.set(book + "/" + t.slug, { kind, book, chapter: ch.slug, chapterTitle: ch.title, title: t.title || t.slug, bs, ds });
          B.topics.push(t.slug);
          if (ds !== "empty" && ds !== "pending") B.anyDetailed = true;
          if (bs !== "empty" && bs !== "pending") B.anyBasic = true;
        }
    }
    BOOKS.set(book, B);
  }
}

/* --- 2. Які теми додав коміт ----------------------------------------------- */
const changed = git("diff", "--name-only", SHA + "~1", SHA)
  .split(/\r?\n/).filter((f) => f.startsWith("root/") && f.endsWith(".json"));
const NEW = [];
for (const rel of changed) {
  if (!fs.existsSync(path.join(ROOT, rel))) continue;
  let oldSrc = null;
  try { oldSrc = git("show", SHA + "~1:" + rel) } catch (e) { }
  const A = parse(oldSrc || "{}") || {};
  const B = parse(fs.readFileSync(path.join(ROOT, rel), "utf8"));
  if (!B) continue;
  const old = new Set();
  for (const ch of (A.chapters || [])) for (const t of (ch.topics || [])) if (t.slug) old.add(t.slug);
  for (const ch of (B.chapters || []))
    for (const t of (ch.topics || [])) {
      if (t.ref || !t.slug || old.has(t.slug)) continue;
      NEW.push({
        book: B.book || rel.split("/")[2], kind: B.kind || rel.split("/")[1],
        group: B.slug, groupTitle: B.title, chapter: ch.slug, chapterTitle: ch.title,
        slug: t.slug, title: t.title || t.slug,
        bs: (t.basic && t.basic.status) || "empty", ds: (t.detailed && t.detailed.status) || "empty",
      });
    }
}

/* --- 3. Згадки в прозі + вхідні лінки (один прохід по книзі) --------------
   Сирітство «на тему ніхто не лінкує» майже нічого не розрізняє: Antigravity завів
   теми, а лінків не проставив, тож сиротами вийшли майже всі. Розрізняє інше — чи
   поняття ВЗАГАЛІ згадується в прозі книги. Нуль згадок = тема здогадана наперед,
   а не витягнута з написаного. Шукаємо за найдовшими словами НАЗВИ (проза
   українська, слуг — латиницею), і рахуємо файли, де є всі вибрані слова. */
const REFS = new Map();
const PROSE = new Map();          // книга -> [текст файлу, ...]
const DF = new Map();             // книга -> Map(основа -> у скількох файлах трапилась)
(function walk(dir, book) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (e.name !== "img") walk(p, book || (dir.endsWith(path.sep + "root") ? null : e.name)) }
    else if (e.name.endsWith(".md")) {
      const md = fs.readFileSync(p, "utf8");
      for (const m of md.matchAll(/\]\(root:([a-z0-9-]+)\/([a-z0-9-]+)/g))
        REFS.set(m[1] + "/" + m[2], (REFS.get(m[1] + "/" + m[2]) || 0) + 1);
      const rel = path.relative(path.join(ROOT, "root"), p).split(path.sep);
      const bk = rel[1];
      if (!bk) continue;
      const low = md.toLowerCase();
      const arr = PROSE.get(bk) || PROSE.set(bk, []).get(bk);
      arr.push(low);
      const d = DF.get(bk) || DF.set(bk, new Map()).get(bk);
      for (const w of new Set((low.match(/[Ѐ-ӿa-z0-9]{5,}/g) || []).map((x) => x.slice(0, 6))))
        d.set(w, (d.get(w) || 0) + 1);
    }
  }
})(path.join(ROOT, "root"), null);

const TITLE_STOP = new Set(["через", "після", "перед", "проти", "разом", "також", "більше", "менше",
  "інших", "інший", "інша", "якщо", "коли", "чому", "щоби", "щоб", "його", "їхні", "свої", "цього"]);
/* Українська відмінює, тож точне входження слова не працює («аварійного» не збігається
   з «аварійне»): ріжемо слово до ОСНОВИ — перших шести літер. Береться пара НАЙРІДШИХ
   основ назви: найдовші не годяться, бо в sys-dron «польотного» стоїть у кожному файлі
   й дає 133 фальшиві «згадки». */
const stem = (w) => w.slice(0, 6);
function keyStems(title, df) {
  const ws = [...new Set((title.toLowerCase().match(/[Ѐ-ӿa-z0-9]{5,}/g) || []).filter((w) => !TITLE_STOP.has(w)).map(stem))];
  return ws.sort((a, b) => (df.get(a) || 0) - (df.get(b) || 0)).slice(0, 2);
}

/* --- 4. Локальні ознаки ----------------------------------------------------- */
const STOP = new Set(["and", "or", "vs", "the", "of", "in", "to", "a", "for", "with", "on", "by", "as", "at",
  "model", "models", "basics", "types", "type", "api", "system", "systems", "data", "control", "design", "i", "ta"]);
const GENERIC = new Set(["cache", "timers", "timer", "memory", "buffer", "queue", "state", "signal", "power",
  "clock", "format", "protocol", "driver", "sensor", "filter", "index", "graph", "tree", "node", "link", "layer"]);

const WORDFREQ = new Map();
for (const [key, t] of INDEX) {
  const m = WORDFREQ.get(t.book) || WORDFREQ.set(t.book, new Map()).get(t.book);
  for (const w of new Set(key.split("/")[1].split("-"))) if (!STOP.has(w)) m.set(w, (m.get(w) || 0) + 1);
}
const nod = (s) => s.replace(/-/g, "");
const segIn = (a, b) => {
  const A = a.split("-"), B = b.split("-");
  for (let i = 0; i + A.length <= B.length; i++) if (A.every((x, k) => B[i + k] === x)) return true;
  return false;
};

for (const n of NEW) {
  const flags = [], near = [];
  const B = BOOKS.get(n.book) || { topics: [] };
  const freq = WORDFREQ.get(n.book) || new Map();
  for (const other of B.topics) {
    if (other === n.slug) continue;
    if (segIn(n.slug, other) || segIn(other, n.slug)) { near.push(other + " [вкладений слуг]"); continue }
    if (nod(n.slug).includes(nod(other)) || nod(other).includes(nod(n.slug))) { near.push(other + " [вкладений без дефісів]"); continue }
    const shared = n.slug.split("-").filter((w) => !STOP.has(w) && other.split("-").includes(w) && (freq.get(w) || 0) <= 3);
    if (shared.length) near.push(other + " [спільне рідкісне: " + shared.join(", ") + "]");
  }
  for (const [key, t] of INDEX) if (key.endsWith("/" + n.slug) && t.book !== n.book) near.push(key + " [той самий слуг в іншій книзі]");
  if (near.length) flags.push("схожі");
  const parts = n.slug.split("-");
  if (parts.length === 1 && GENERIC.has(n.slug)) flags.push("родовий слуг");
  if (n.slug === n.chapter) flags.push("слуг = розділ");
  if (n.title === n.slug) flags.push("назва = слуг");
  if (parts.length > 6) flags.push("слуг задовгий (" + parts.length + ")");
  if (B.anyBasic && !B.anyDetailed && n.ds === "pending") flags.push("книга пише лише базові — detailed:pending поза конвенцією");
  n.refs = REFS.get(n.book + "/" + n.slug) || 0;
  const texts = PROSE.get(n.book) || [];
  const df = DF.get(n.book) || new Map();
  const kw = keyStems(n.title, df);
  n.kw = kw;
  n.mentions = kw.length ? texts.filter((t) => kw.every((w) => t.includes(w))).length : -1;
  n.dfMin = kw.length ? Math.min(...kw.map((w) => df.get(w) || 0)) : -1;
  if (n.mentions === 0) flags.push("поняття в прозі книги не зустрічається");
  n.flags = flags;
  n.near = [...new Set(near)].slice(0, 4);
}

/* --- 5. Звіт ---------------------------------------------------------------- */
const byBook = {};
for (const n of NEW) (byBook[n.kind + "/" + n.book] = byBook[n.kind + "/" + n.book] || []).push(n);
const rows = Object.entries(byBook).sort((a, b) => b[1].length - a[1].length);
console.log(`\n== НОВІ ТЕМИ КОМІТУ ${SHA} ==  усього ${NEW.length}, книг ${rows.length}\n`);
console.log("книга".padEnd(26) + "нових".padStart(6) + "схожі".padStart(7) + "0 згадок".padStart(10) + "інше".padStart(7));
let fSim = 0, fOrph = 0, fOther = 0;
for (const [b, list] of rows) {
  const sim = list.filter((n) => n.flags.includes("схожі")).length;
  const orph = list.filter((n) => n.mentions === 0).length;
  const oth = list.filter((n) => n.flags.some((f) => f !== "схожі" && f !== "поняття в прозі книги не зустрічається")).length;
  fSim += sim; fOrph += orph; fOther += oth;
  console.log(b.padEnd(26) + String(list.length).padStart(6) + String(sim).padStart(7) + String(orph).padStart(10) + String(oth).padStart(7));
}
console.log("\n  зі схожими поруч " + fSim + " · без згадок у прозі " + fOrph + " · інші зауваги " + fOther +
  " · чистих " + NEW.filter((n) => !n.flags.length).length);

if (jsonOut) { fs.writeFileSync(jsonOut, JSON.stringify(NEW, null, 1), "utf8"); console.log("  payload → " + jsonOut) }
