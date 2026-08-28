#!/usr/bin/env node
/* Зведення оцінок ВСТАВОК: три оцінювачі → середня → рівень → смуга → факт.
   Читає out-<книга>-{A,B,C}.txt (рядки "файл.md=N") з теки голосів,
   міряє прозу (proseWords — код у неї не входить) і рядки коду,
   кладе scripts/_levels/inserts/<книга>.{json,tsv}.

   node scripts/levels-inserts.js --votes <тека> [книга…]      */
const M7 = require("./lib/manifest7.js");
const L = require("./checks/_lib.js");
const fs = require("fs"), path = require("path");

const argv = process.argv.slice(2);
const vi = argv.indexOf("--votes");
const VOTES = vi >= 0 ? argv[vi + 1] : null;
if (!VOTES) { console.error("треба --votes <тека з out-*.txt>"); process.exit(1); }
const only = argv.filter((a, i) => i !== vi && i !== vi + 1 && !a.startsWith("--"));
const OUTDIR = path.join(__dirname, "_levels", "inserts");
fs.mkdirSync(OUTDIR, { recursive: true });

const RATERS = ["A", "B", "C"];
const r2 = (x) => Math.round(x * 100) / 100;

/* Рівень, який ВИТРИМУЄ наявний обсяг: найвищий, чия підлога ще не перевищена. */
function levelOfSize(kind, n) {
  let lv = 0;
  for (let i = 1; i <= L.LEVELS; i++) if (n >= L.bandOf(kind, i).floor) lv = i;
  return lv;
}
function levelOfCode(n) {
  let lv = 0;
  for (let i = 1; i <= L.LEVELS; i++) if (n >= L.CODE_FLOOR[i]) lv = i;
  return lv;
}

/* Які книги маємо голоси на всі три оцінювачі. */
const ready = new Set();
for (const f of fs.readdirSync(VOTES)) {
  const m = f.match(/^out-(.+)-([ABC])\.txt$/); if (!m) continue;
  const b = m[1];
  if (RATERS.every((r) => fs.existsSync(path.join(VOTES, `out-${b}-${r}.txt`)))) ready.add(b);
}
const books = only.length ? only : [...ready].sort();

const totals = [];
for (const BOOK of books) {
  if (!ready.has(BOOK)) { console.error(`${BOOK}\tнема всіх трьох голосів — пропущено`); continue; }
  const rec = M7.books().get(BOOK);
  if (!rec) { console.error(`${BOOK}\tнема в shelf`); continue; }
  const b = M7.loadBook(rec.bookDir);

  /* голоси: ключ "тема/файл", бо той самий файл трапляється у двох темах */
  const votes = {};
  for (const r of RATERS) {
    const txt = fs.readFileSync(path.join(VOTES, `out-${BOOK}-${r}.txt`), "utf8");
    const seq = [];
    for (const line of txt.split(/\r?\n/)) {
      const m = line.match(/^\s*([\w.-]+\.md)\s*=\s*([1-5])\s*$/); if (!m) continue;
      seq.push([m[1], +m[2]]);
    }
    votes[r] = seq;
  }

  /* порядок вставок у маніфесті = порядок рядків у голосах */
  const seqRef = [];
  for (const [gslug, g] of b.groups)
    for (const ch of g.data.chapters || []) for (const t of ch.topics || []) {
      if (!t.slug) continue;
      for (const type of M7.INSERT_TYPES) for (const ins of t[type] || []) {
        if (ins.status !== "recheck") continue;
        seqRef.push({ topic: t.slug, title: t.title || t.slug, group: g.data.title || gslug, file: ins.file, type });
      }
    }

  const bad = RATERS.filter((r) => votes[r].length !== seqRef.length);
  if (bad.length) {
    console.error(`${BOOK}\t✖ довжина не збігається: чекали ${seqRef.length}, ` +
      bad.map((r) => `${r}=${votes[r].length}`).join(" "));
    continue;
  }

  const rows = [];
  seqRef.forEach((ref, i) => {
    const v = RATERS.map((r) => votes[r][i][1]);
    const names = RATERS.map((r) => votes[r][i][0]);
    if (names.some((n) => n !== ref.file))
      console.error(`${BOOK}\t⚠ рядок ${i + 1}: чекали ${ref.file}, маємо ${names.join("/")}`);
    const mean = r2(v.reduce((a, c) => a + c, 0) / v.length);
    const level = L.clampLevel(Math.round(mean));
    const p = path.join(rec.bookDir, ref.topic, ref.file);
    const md = fs.existsSync(p) ? L.read(p) : null;
    const words = md === null ? null : L.proseWords(md);
    const code = md === null ? null : (L.NEEDS_CODE.has(ref.type) ? L.codeLines(md) : null);
    const band = L.bandOf(ref.type, level);
    const real = words === null ? null : levelOfSize(ref.type, words);
    const codeReal = code === null ? null : levelOfCode(code);
    rows.push({
      ...ref, votes: v, mean, level, spread: Math.max(...v) - Math.min(...v),
      words, real, delta: real === null ? null : level - real,
      floor: band.floor, max: band.max,
      code, codeFloor: band.needsCode ? band.codeFloor : null, codeReal,
      codeDelta: codeReal === null ? null : level - codeReal,
    });
  });

  fs.writeFileSync(path.join(OUTDIR, `${BOOK}.json`),
    JSON.stringify({ book: BOOK, kind: rec.kind, raters: RATERS, inserts: rows }, null, 1), "utf8");
  const H = ["тема", "група", "файл", "тип", "A", "B", "C", "середня", "рівень",
    "слів", "підлога", "Рфакт", "Δ", "коду", "підлКод", "Ркод", "Δкод"];
  fs.writeFileSync(path.join(OUTDIR, `${BOOK}.tsv`),
    [H.join("\t"), ...rows.map((r) => [r.topic, r.group, r.file, r.type, ...r.votes,
      r.mean, r.level, r.words ?? "", r.floor, r.real ?? "", r.delta ?? "",
      r.code ?? "", r.codeFloor ?? "", r.codeReal ?? "", r.codeDelta ?? ""].join("\t"))].join("\n") + "\n",
    "utf8");

  const need = rows.filter((r) => r.delta >= 2).length;
  const needCode = rows.filter((r) => r.codeDelta !== null && r.codeDelta >= 2).length;
  const meanAll = r2(rows.reduce((a, r) => a + r.level, 0) / rows.length);
  console.log(`${BOOK}\t${rows.length}\tсер.рівень ${meanAll}\tΔ≥2 проза ${need}\tΔ≥2 код ${needCode}`);
  totals.push({ book: BOOK, n: rows.length, mean: meanAll, need, needCode, rows });
}

if (totals.length > 1) {
  const all = totals.flatMap((t) => t.rows);
  console.log(`\nРАЗОМ ${all.length} вставок у ${totals.length} книгах`);
  const hist = {}; for (const r of all) hist[r.level] = (hist[r.level] || 0) + 1;
  console.log("рівні: " + [1, 2, 3, 4, 5].map((l) => `Р${l}=${hist[l] || 0}`).join("  "));
  console.log(`Δ≥2 за прозою: ${all.filter((r) => r.delta >= 2).length}` +
    `  ·  Δ≥2 за кодом: ${all.filter((r) => r.codeDelta !== null && r.codeDelta >= 2).length}`);
}
