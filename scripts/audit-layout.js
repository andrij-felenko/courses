#!/usr/bin/env node
/* ============================================================================
   audit-layout.js — розлади «диск ↔ маніфест» по всьому корпусу.

   Ужиток:
     node scripts/audit-layout.js                 # усі книги
     node scripts/audit-layout.js reference/unix-linux

   Коди виходу: 0 — чисто · 1 — є розлади (перелічено).

   ЩО ЛОВИТЬ і чому це болить:
     • тека-секція, якої нема в маніфесті — теми в ній не побачить ні читач, ні гейт;
     • тема лежить не в тій секції, де записана — manifest-patch шукає її не там,
       і батч гине на одній темі («finish-batch: секція з маніфесту» це терпить,
       але розкладка лишається брехливою);
     • ОДИН слуг у ДВОХ теках — найгірше: дві копії статті живуть паралельно, правки
       йдуть в одну, читач бачить іншу;
     • тека теми без запису в маніфесті — стаття написана, але для книги її нема;
     • секція в маніфесті без теки — норм, якщо просто ще не писали (не дефект).

   Теки, що починаються з «_» (напр. `_analysis`), — службові, їх не рахуємо.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const only = process.argv[2] ? path.resolve(ROOT, process.argv[2]) : null;

const dirsIn = (p) => fs.existsSync(p)
  ? fs.readdirSync(p).filter((f) => !f.startsWith("_") && fs.statSync(path.join(p, f)).isDirectory())
  : [];

function loadManifest(mf) {
  const sb = {};
  new Function("window", fs.readFileSync(mf, "utf8"))(sb);
  const guides = sb.__GUIDES__ || [], books = sb.__BOOKS__ || [];
  return guides.length ? { m: guides[0], guide: true } : { m: books[0], guide: false };
}

let bad = 0;
for (const kind of ["book", "catalog", "reference", "guide"]) {
  const kp = path.join(ROOT, kind);
  if (!fs.existsSync(kp)) continue;
  for (const slug of dirsIn(kp)) {
    const bp = path.join(kp, slug);
    if (only && path.resolve(bp) !== only) continue;
    const mf = path.join(bp, "manifest.js");
    if (!fs.existsSync(mf)) { console.log(`✖ ${kind}/${slug}: нема manifest.js`); bad++; continue; }

    let m, guide;
    try { ({ m, guide } = loadManifest(mf)); } catch (e) {
      console.log(`✖ ${kind}/${slug}: маніфест не парситься — ${e.message}`); bad++; continue;
    }
    if (!m) { console.log(`✖ ${kind}/${slug}: у маніфесті нема книги`); bad++; continue; }

    const groups = guide ? (m.modules || []) : (m.sections || []);
    const groupSlugs = new Set(groups.map((g) => g.slug));
    const topicsOf = (g) => guide
      ? (g.chapters || []).flatMap((c) => (c.steps || []).filter((s) => s.slug).map((s) => s.slug))
      : (g.topics || []).map((t) => t.slug);
    const inManifest = new Map();
    groups.forEach((g) => topicsOf(g).forEach((t) => inManifest.set(t, g.slug)));

    const diskGroups = dirsIn(bp);
    const onDisk = new Map();                       // слуг → [теки]
    for (const g of diskGroups) {
      for (const t of dirsIn(path.join(bp, g))) {
        if (!fs.readdirSync(path.join(bp, g, t)).some((f) => f.endsWith(".md"))) continue;
        if (!onDisk.has(t)) onDisk.set(t, []);
        onDisk.get(t).push(g);
      }
    }

    const extraGroups = diskGroups.filter((g) => !groupSlugs.has(g));
    const doubled = [...onDisk.entries()].filter(([, gs]) => gs.length > 1);
    const misplaced = [...onDisk.entries()]
      .filter(([t, gs]) => gs.length === 1 && inManifest.has(t) && inManifest.get(t) !== gs[0]);
    const unregistered = [...onDisk.keys()].filter((t) => !inManifest.has(t));
    const emptyGroups = [...groupSlugs].filter((g) => !diskGroups.includes(g));

    if (!extraGroups.length && !doubled.length && !misplaced.length && !unregistered.length) continue;
    console.log(`\n── ${kind}/${slug}`);
    if (extraGroups.length) { console.log(`  тека-секція не в маніфесті: ${extraGroups.join(", ")}`); bad++; }
    if (doubled.length) {
      console.log(`  ⚠ ОДИН СЛУГ У ДВОХ ТЕКАХ (дві копії статті):`);
      doubled.forEach(([t, gs]) => console.log(`     · ${t} → ${gs.join(" + ")}`));
      bad++;
    }
    if (misplaced.length) {
      console.log(`  тема не у своїй секції:`);
      misplaced.forEach(([t, gs]) => console.log(`     · ${t}: тека ${gs[0]} ≠ маніфест ${inManifest.get(t)}`));
      bad++;
    }
    if (unregistered.length) {
      console.log(`  тек тем без запису в маніфесті: ${unregistered.length}`);
      unregistered.slice(0, 10).forEach((t) => console.log(`     · ${onDisk.get(t)[0]}/${t}`));
      if (unregistered.length > 10) console.log(`     … ще ${unregistered.length - 10}`);
      bad++;
    }
    if (emptyGroups.length) console.log(`  (секція без теки — не дефект, просто ще не писали: ${emptyGroups.join(", ")})`);
  }
}

console.log(bad ? `\nрозладів: ${bad} — лагодити ДО батчу, а не посеред нього` : "\nрозкладка й маніфести збігаються");
process.exit(bad ? 1 : 0);
