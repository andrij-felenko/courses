#!/usr/bin/env node
/* ============================================================================
   guidelinks.js — чи веде посилання КУРСУ туди, де читач щось побачить.

   linkcheck.js питає «чи існує ціль»; цей скрипт питає інше — «чи є в цілі
   ЩОСЬ ГОТОВЕ». Тема може бути законно заведена в маніфесті (`pending`), лінк на
   неї не «битий», а читач курсу все одно впирається в порожнечу. Саме такі
   посилання й лишаються «незакритими».

   Дивимось два види посилань курсу:
     • КРОК-`ref` — сходинка курсу, що веде в book/catalog/reference;
     • ІНЛАЙН `book:`/`guide:` у прозі власних статей курсу.

   Вирок на ціль:
     ✖ ПОРОЖНЯ   — жодна версія не `done` (читач не побачить нічого)
     ▲ НЕМА ТЕМИ — цілі нема в жодному маніфесті (це вже справжня діра)
     ✓ готова    — є `done`-версія

   Запуск:  node scripts/guidelinks.js            (усі курси)
            node scripts/guidelinks.js unix       (один курс)
            node scripts/guidelinks.js --all      (перелічити кожне посилання)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const argv = process.argv.slice(2);
const showAll = argv.includes("--all");
const only = argv.filter((a) => !a.startsWith("--"));

/* --- 1. Індекс усіх тем корпусу: "<книга>/<slug>" → {done, статуси} --------- */
const TOPICS = new Map();
for (const r of ["book", "catalog", "reference"]) {
  for (const b of fs.readdirSync(path.join(ROOT, r))) {
    const mf = path.join(ROOT, r, b, "manifest.js");
    if (!fs.existsSync(mf)) continue;
    global.window = { __BOOKS__: [], __GUIDES__: [] };
    delete require.cache[mf];
    try { require(mf) } catch (e) { continue }
    const B = global.window.__BOOKS__[0];
    if (!B) continue;
    for (const s of (B.sections || [])) for (const t of (s.topics || [])) {
      const bs = (t.basic && t.basic.status) || "empty";
      const ds = (t.detailed && t.detailed.status) || "empty";
      TOPICS.set(b + "/" + t.slug, { book: r + "/" + b, section: s.slug, bs, ds, done: bs === "done" || ds === "done" });
    }
  }
}

/* --- 2. Обхід курсів -------------------------------------------------------- */
const GUIDES = fs.readdirSync(path.join(ROOT, "guide")).filter((g) => !only.length || only.includes(g));
const rows = [];

for (const g of GUIDES) {
  const mf = path.join(ROOT, "guide", g, "manifest.js");
  if (!fs.existsSync(mf)) continue;
  global.window = { __BOOKS__: [], __GUIDES__: [] };
  delete require.cache[mf];
  try { require(mf) } catch (e) { continue }
  const G = global.window.__GUIDES__[0];
  if (!G) continue;

  // власні статті курсу — теж можливі цілі inline-лінків «guide:<курс>/<slug>»
  const ownDone = new Map();
  const ownFiles = [];
  for (const m of (G.modules || G.sections || []))
    for (const ch of (m.chapters || [{ steps: m.topics || m.steps || [] }]))
      for (const st of (ch.steps || [])) {
        if (st.ref) {
          // крок-ref: перший сегмент — книга, останній — слуг теми (§2)
          const seg = String(st.ref).split("/");
          const key = seg[0] + "/" + seg[seg.length - 1];
          const T = TOPICS.get(key);
          rows.push({ guide: g, kind: "крок", from: `${m.slug || m.title} · ${st.title || st.ref}`, target: key,
            verdict: !T ? "нема" : T.done ? "ok" : "порожня", detail: T ? `${T.book} · basic:${T.bs} detailed:${T.ds}` : "" });
        } else if (st.slug) {
          const bs = (st.basic && st.basic.status) || "empty";
          const ds = (st.detailed && st.detailed.status) || "empty";
          ownDone.set(st.slug, bs === "done" || ds === "done");
          const dir = path.join(ROOT, "guide", g, m.slug || "", st.slug);
          if (fs.existsSync(dir)) for (const f of fs.readdirSync(dir)) if (f.endsWith(".md")) ownFiles.push(path.join(dir, f));
        }
      }

  // інлайн-лінки у прозі власних статей курсу
  for (const f of ownFiles) {
    const md = fs.readFileSync(f, "utf8");
    for (const m of md.matchAll(/\]\((book|guide):([a-z0-9-]+)\/([a-z0-9-]+)(?:\/[^)]+)?\)/g)) {
      const [, pfx, bk, slug] = m;
      if (pfx === "guide") {
        if (bk !== g) continue;                        // чужий курс — не наша справа
        if (!ownDone.has(slug)) { rows.push({ guide: g, kind: "інлайн", from: path.relative(ROOT, f).replace(/\\/g, "/"), target: `${bk}/${slug}`, verdict: "нема", detail: "власний крок курсу" }); continue }
        if (!ownDone.get(slug)) rows.push({ guide: g, kind: "інлайн", from: path.relative(ROOT, f).replace(/\\/g, "/"), target: `${bk}/${slug}`, verdict: "порожня", detail: "власний крок курсу" });
      } else {
        const T = TOPICS.get(bk + "/" + slug);
        if (!T) rows.push({ guide: g, kind: "інлайн", from: path.relative(ROOT, f).replace(/\\/g, "/"), target: `${bk}/${slug}`, verdict: "нема", detail: "" });
        else if (!T.done) rows.push({ guide: g, kind: "інлайн", from: path.relative(ROOT, f).replace(/\\/g, "/"), target: `${bk}/${slug}`, verdict: "порожня", detail: `${T.book} · basic:${T.bs} detailed:${T.ds}` });
      }
    }
  }
}

/* --- 3. Звіт ---------------------------------------------------------------- */
const V = { "нема": "▲ НЕМА ТЕМИ", "порожня": "✖ ПОРОЖНЯ (жодної done-версії)", ok: "✓ готова" };
console.log(`\n== ПОСИЛАННЯ КУРСІВ ==  курсів: ${GUIDES.length} · тем у корпусі: ${TOPICS.size}`);

for (const g of GUIDES) {
  const mine = rows.filter((r) => r.guide === g);
  if (!mine.length) continue;
  const bad = mine.filter((r) => r.verdict !== "ok");
  const steps = mine.filter((r) => r.kind === "крок");
  const badStep = bad.filter((r) => r.kind === "крок").length;
  console.log(`\n-- guide/${g} --  кроків-ref ${steps.length} (незакритих ${badStep}) · інлайн-лінків незакритих ${bad.length - badStep}`);
  if (!bad.length) { console.log("   ✓ усі посилання ведуть у готове"); continue }
  for (const v of ["нема", "порожня"]) {
    const grp = bad.filter((r) => r.verdict === v);
    if (!grp.length) continue;
    console.log(`   ${V[v]} — ${grp.length}`);
    const uniq = new Map();
    for (const r of grp) (uniq.get(r.target) || uniq.set(r.target, []).get(r.target)).push(r);
    const list = [...uniq.entries()];
    for (const [target, rs] of (showAll ? list : list.slice(0, 12)))
      console.log(`       ${target.padEnd(46)} ${rs[0].detail}${rs.length > 1 ? `  ×${rs.length}` : ""}`);
    if (!showAll && list.length > 12) console.log(`       … і ще ${list.length - 12} цілей (--all покаже всі)`);
  }
}

const bad = rows.filter((r) => r.verdict !== "ok");
const targets = new Set(bad.map((r) => r.target));
console.log(`\n  посилань перевірено ${rows.length} · незакритих ${bad.length} · різних цілей за ними ${targets.size}`);
console.log(`  (з них «нема теми» ${bad.filter((r) => r.verdict === "нема").length} — це справжня діра; «порожня» ${bad.filter((r) => r.verdict === "порожня").length} — тема заведена, але ще не написана)`);
