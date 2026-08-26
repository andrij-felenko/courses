#!/usr/bin/env node
/* ============================================================================
   guidelinks.js — чи веде посилання КУРСУ туди, де читач щось побачить.

   `linkcheck.js` питає «чи існує ціль»; цей скрипт питає інше — «чи є в цілі
   ЩОСЬ ГОТОВЕ». Тему можна законно завести в маніфесті зі статусом `pending`:
   лінк на неї не битий, а читач курсу все одно впирається в порожнечу. Саме такі
   кроки й лишаються «незакритими».

   Дивимось два види посилань курсу (дерево v7, `root/course/<курс>/`):
     • крок-`ref` — сходинка курсу, що веде в будь-яку книгу дерева;
     • інлайн `root:<книга>/<тема>` у прозі власних статей курсу.

   Вирок на ціль:
     ✖ ПОРОЖНЯ   — жодна версія не `done` (читач не побачить нічого)
     ▲ НЕМА ТЕМИ — цілі нема в жодному маніфесті (це вже справжня діра)
     ✓ готова    — є `done`-версія

   Ужиток:  node scripts/guidelinks.js            (усі курси)
            node scripts/guidelinks.js unix       (один курс)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const M = require("./lib/manifest7.js");

const only = process.argv.slice(2).filter((a) => !a.startsWith("--"));

/* Індекс усього корпусу: "<книга>/<тема>" → чи є готова версія. */
/* Читач щось побачить, якщо текст Є. `recheck`/`update`/`deeper` — готові статті
   з позначкою чернетки, а не порожнеча; порожні лише `pending` і `empty`. */
const written = (s) => s === "done" || s === "update" || s === "deeper" || s === "recheck";

const T = new Map();
for (const [bslug, meta] of M.books()) {
  const bk = M.loadBook(meta.bookDir);
  if (!bk) continue;
  for (const t of M.allTopics(bk)) {
    if (!t.own) continue;
    const b = (t.node.basic && t.node.basic.status) || "empty";
    const d = (t.node.detailed && t.node.detailed.status) || "empty";
    T.set(bslug + "/" + t.slug, { book: bslug, bs: b, ds: d, done: written(b) || written(d) });
  }
}

/* Ціль лінка → ключ «книга/тема»: книга з першого сегмента, тема з останнього
   змістовного (PLAN §2.3 — довга форма містить коротку). */
function keyOf(addr) {
  const segs = addr.split("#")[0].split("/").filter(Boolean);
  if (segs.length < 2) return null;
  const last = segs[segs.length - 1];
  const isVer = /\.md$/i.test(last) || last === "detail" || last === "basic";
  return segs[0] + "/" + (isVer ? segs[segs.length - 2] : last);
}

const rows = [];
const courses = [...M.books()].filter(([s, m]) => m.kind === "course" && (!only.length || only.includes(s)));

for (const [cslug, meta] of courses) {
  const bk = M.loadBook(meta.bookDir);
  if (!bk) continue;
  let refs = 0, refBad = 0, inline = 0, inlineBad = 0;

  for (const t of M.allTopics(bk)) {
    /* крок-ref — сходинка в чужу книгу */
    if (t.ref) {
      refs++;
      const k = keyOf(t.ref);
      const x = k && T.get(k);
      if (!x) { refBad++; rows.push({ c: cslug, kind: "крок", from: `${t.group}/${t.chapter}`, target: t.ref, verdict: "НЕМА ТЕМИ" }); }
      else if (!x.done) { refBad++; rows.push({ c: cslug, kind: "крок", from: `${t.group}/${t.chapter}`, target: t.ref, verdict: "ПОРОЖНЯ", detail: `basic:${x.bs} detailed:${x.ds}` }); }
      continue;
    }
    /* інлайн-лінки у прозі власної статті курсу */
    const dir = path.join(meta.bookDir, t.slug);
    let files = []; try { files = fs.readdirSync(dir).filter((f) => f.endsWith(".md")); } catch { continue }
    for (const f of files) {
      const md = fs.readFileSync(path.join(dir, f), "utf8");
      for (const m of md.matchAll(/\]\(root:([^)\s]+)\)/g)) {
        inline++;
        const k = keyOf(m[1]);
        const x = k && T.get(k);
        if (!x) { inlineBad++; rows.push({ c: cslug, kind: "інлайн", from: `${t.slug}/${f}`, target: m[1], verdict: "НЕМА ТЕМИ" }); }
        else if (!x.done) { inlineBad++; rows.push({ c: cslug, kind: "інлайн", from: `${t.slug}/${f}`, target: m[1], verdict: "ПОРОЖНЯ", detail: `basic:${x.bs} detailed:${x.ds}` }); }
      }
    }
  }
  console.log(`-- ${cslug} --  кроків-ref ${refs} (незакритих ${refBad}) · інлайн-лінків ${inline} (незакритих ${inlineBad})`);
}

console.log(`\n== ПОСИЛАННЯ КУРСІВ ==  курсів: ${courses.length} · тем у корпусі: ${T.size} · незакритих: ${rows.length}`);
rows.slice(0, 40).forEach((r) => console.log(`  ${r.verdict === "НЕМА ТЕМИ" ? "▲" : "✖"} ${r.c} · ${r.kind} · ${r.from} → ${r.target}${r.detail ? "  (" + r.detail + ")" : ""}`));
if (rows.length > 40) console.log(`  … і ще ${rows.length - 40}`);
