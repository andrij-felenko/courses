#!/usr/bin/env node
/* ============================================================================
   audit-layout.js — чи збігається ДИСК із МАНІФЕСТОМ у дереві v7.

   Це гейт «тек == тем» із `PLAN.md §4` (Фаза 2). У v7 тема лежить пласко під
   книгою, тож перевірка стала простою і повною:

     • тека теми є, а в маніфесті теми немає        → сирота на диску
     • тема в маніфесті є, а теки немає             → порожній запис
     • група в `manifest.json`, а файла `<група>.json` немає
     • файл `<група>.json` лежить, а в переліку груп його немає
     • той самий слуг двічі в одній книзі
     • тема без жодної версії (`basic` і `detailed` обидва `empty`)

   Ужиток:  node scripts/audit-layout.js              (усе дерево)
            node scripts/audit-layout.js sf-apps      (одна книга)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const M = require("./lib/manifest7.js");

const only = process.argv[2] || null;
const SKIP = new Set(["img"]);
let bad = 0, books = 0;

for (const [bslug, meta] of M.books()) {
  if (only && bslug !== only) continue;
  books++;
  const say = (s) => { console.log(`✖ ${meta.dir}/${bslug}: ${s}`); bad++; };

  const bk = M.loadBook(meta.bookDir);
  if (!bk) { say("нема або не парситься manifest.json"); continue; }

  /* групи: перелік у шапці проти файлів на диску */
  const listed = new Set(bk.manifest.groups || []);
  for (const g of listed) if (!bk.groups.has(g)) say(`група «${g}» у переліку, а файла ${g}.json немає`);
  for (const f of fs.readdirSync(meta.bookDir)) {
    if (!f.endsWith(".json") || f === "manifest.json") continue;
    const g = f.slice(0, -5);
    if (!listed.has(g)) say(`файл ${f} лежить, а в переліку груп його немає`);
  }

  /* теми: маніфест проти тек */
  const inManifest = new Map();
  const dupes = [];
  for (const t of M.allTopics(bk)) {
    if (!t.own) continue;
    if (inManifest.has(t.slug)) dupes.push(t.slug);
    else inManifest.set(t.slug, t);
  }
  [...new Set(dupes)].forEach((s) => say(`слуг «${s}» у маніфесті двічі`));

  const onDisk = new Set();
  for (const e of fs.readdirSync(meta.bookDir, { withFileTypes: true })) {
    if (!e.isDirectory() || SKIP.has(e.name)) continue;
    onDisk.add(e.name);
  }

  for (const s of onDisk) if (!inManifest.has(s)) say(`тека «${s}» є, а теми в маніфесті немає`);
  const WRITTEN = new Set(["done", "recheck", "update", "deeper"]);
  for (const [s, t] of inManifest) {
    const bs = (t.node.basic && t.node.basic.status) || "empty";
    const ds = (t.node.detailed && t.node.detailed.status) || "empty";
    if (!onDisk.has(s)) {
      /* pending без теки — це черга письма, а не поломка. Лається лише тоді, коли
         маніфест каже «написано», а на диску порожньо. */
      if (WRITTEN.has(bs) || WRITTEN.has(ds)) say(`тема «${s}» [${t.group}/${t.chapter}] значиться написаною (basic:${bs} detailed:${ds}), а теки немає`);
      continue;
    }
    if (bs === "empty" && ds === "empty") say(`тема «${s}» без жодної версії (обидві empty) — або писати, або прибрати`);
  }
}

console.log(`\nперевірено книг: ${books} · зауважень: ${bad}`);
process.exit(bad ? 1 : 0);
