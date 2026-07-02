/* scripts/linkcheck.js — перевірка посилань під структуру AUTHORING.md (book/ · catalog/ · guide/).
   Перевіряє:
     • book:<книга>/<slug>[/<file>] — чи є така тема в маніфесті книги; status:"empty" = легітимний стаб.
     • зображення (/book/…/img/x.svg або відносні img/x.svg) — чи існує файл.
     • відносні .md-лінки — попереджає (за каноном крос-лінк має бути book:-попапом).
   Запуск: node scripts/linkcheck.js
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");

function read(p) { return fs.readFileSync(p, "utf8"); }
function exists(p) { try { fs.accessSync(p); return true; } catch (e) { return false; } }
function walk(dir, out) {
  if (!exists(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.isFile() && e.name.endsWith(".md")) out.push(p);
  }
  return out;
}
function loadReg(globKey, file) {
  if (!exists(file)) return [];
  try { return new Function("window", read(file) + `\nreturn window.${globKey}||[];`)({}); } catch (e) { return []; }
}

// індекс тем: "<книга>/<slug>" → { dir, status, files:Set }
const TOPICS = new Map();
for (const kind of ["book", "catalog"]) {
  const base = path.join(ROOT, kind);
  if (!exists(base)) continue;
  for (const d of fs.readdirSync(base)) {
    const mf = path.join(base, d, "manifest.js");
    const books = loadReg("__BOOKS__", mf);
    for (const b of books) for (const sec of b.sections || []) for (const t of sec.topics || []) {
      const dir = path.join(base, b.slug, sec.slug, t.slug);
      const files = new Set();
      const bs = (t.basic && t.basic.status) || "empty";
      const ds = (t.detailed && t.detailed.status) || "empty";
      if (bs !== "empty") files.add(t.slug + ".md");        // basic планована/наявна (done|pending|update|recheck)
      if (ds !== "empty") files.add(t.slug + "-d.md");      // detailed планована/наявна
      for (const k of ["hist", "comp", "math", "proj"]) for (const o of t[k] || []) files.add(typeof o === "string" ? o : o.file);
      TOPICS.set(b.slug + "/" + t.slug, { dir, status: bs, files });
    }
  }
}

// guide own-articles index: "<course>/<slug>" → {dir,status,files} (для guide:-лінків)
const GTOPICS = new Map();
{
  const gbase = path.join(ROOT, "guide");
  if (exists(gbase)) for (const d of fs.readdirSync(gbase)) {
    const guides = loadReg("__GUIDES__", path.join(gbase, d, "manifest.js"));
    for (const g of guides) for (const sec of (g.sections || g.modules || [])) for (const t of (sec.topics && sec.topics.length ? sec.topics : (sec.chapters || []).flatMap((c) => c.steps || []))) {
      if (!t.slug) continue;                          // ref-крок — не guide:-ціль
      const files = new Set();
      const bs = (t.basic && t.basic.status) || "empty";
      const ds = (t.detailed && t.detailed.status) || "empty";
      if (bs !== "empty") files.add(t.slug + ".md");
      if (ds !== "empty") files.add(t.slug + "-d.md");
      for (const k of ["hist", "comp", "math", "proj"]) for (const o of t[k] || []) files.add(typeof o === "string" ? o : o.file);
      GTOPICS.set(g.slug + "/" + t.slug, { dir: path.join(gbase, g.slug, sec.slug, t.slug), status: bs, files });
    }
  }
}

const reLink = /(!?)\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
const broken = [], warnMd = [], stubs = [];
const mdFiles = [].concat(walk(path.join(ROOT, "book"), []), walk(path.join(ROOT, "catalog"), []), walk(path.join(ROOT, "guide"), []));

for (const f of mdFiles) {
  const rel = path.relative(ROOT, f);
  const txt = read(f);
  let m;
  while ((m = reLink.exec(txt))) {
    const isImg = m[1] === "!";
    let href = m[2];
    if (/^(https?:|mailto:|tel:|#)/i.test(href)) continue;
    href = href.split("#")[0]; if (!href) continue;

    if (/^guide:/i.test(href)) {
      const segs = href.replace(/^guide:/i, "").split("/").filter(Boolean);
      const key = (segs[0] || "") + "/" + (segs[1] || "");
      const t = GTOPICS.get(key);
      if (!t) { broken.push(`${rel}: guide:${segs.join("/")} — кроку нема в жодному курсі`); continue; }
      if (segs[2]) { if (!t.files.has(segs[2]) && !exists(path.join(t.dir, segs[2]))) broken.push(`${rel}: guide:${segs.join("/")} — файла нема`); }
      else if (t.status !== "done") stubs.push(`${rel}: guide:${key} (${t.status}-стаб)`);
      continue;
    }
    if (/^book:/i.test(href)) {
      const segs = href.replace(/^book:/i, "").split("/").filter(Boolean);
      const key = (segs[0] || "") + "/" + (segs[1] || "");
      const t = TOPICS.get(key);
      if (!t) { broken.push(`${rel}: book:${segs.join("/")} — теми нема в жодному маніфесті`); continue; }
      if (segs[2]) { // конкретний файл (детальна/вставка)
        if (!t.files.has(segs[2]) && !exists(path.join(t.dir, segs[2]))) broken.push(`${rel}: book:${segs.join("/")} — файла нема`);
      } else if (t.status !== "done") stubs.push(`${rel}: book:${key} (${t.status}-стаб)`);
      continue;
    }
    // шлях від кореня репо (зображення/файл)
    const target = href.charAt(0) === "/" ? path.join(ROOT, href) : path.join(path.dirname(f), href);
    if (isImg || /\.(svg|png|jpg|jpeg|gif|webp)$/i.test(href)) {
      if (!exists(target)) broken.push(`${rel}: зображення ${href} — нема`);
    } else if (/\.md$/i.test(href)) {
      warnMd.push(`${rel}: відносний .md-лінк ${href} — за каноном має бути book:-попап`);
      if (!exists(target)) broken.push(`${rel}: .md-ціль ${href} — нема`);
    }
  }
}

console.log(`Перевірено .md: ${mdFiles.length} · тем у маніфестах: ${TOPICS.size}`);
console.log(`\n=== БИТІ (${broken.length}) ===`); broken.slice(0, 200).forEach((s) => console.log("  ✗ " + s));
console.log(`\n=== відносні .md-лінки, варто на book: (${warnMd.length}) ===`); warnMd.slice(0, 50).forEach((s) => console.log("  ⚠ " + s));
console.log(`\n=== лінки на empty-стаби (OK, ${stubs.length}) ===`);
process.exit(broken.length ? 1 : 0);
