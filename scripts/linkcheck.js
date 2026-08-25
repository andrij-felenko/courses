/* scripts/linkcheck.js — перевірка посилань у дереві v7 (root/<вид>/<книга>/<тема>/).
   Перевіряє:
     • root:<книга>/<тема>[/<file>] — чи є така тема в маніфесті книги або курсу; status:"empty" = легітимний стаб.
     • зображення (/book/…/img/x.svg або відносні img/x.svg) — чи існує файл.
     • відносні .md-лінки — попереджає (за каноном крос-лінк має бути root:-попапом).
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

/* Індекс тем усього корпусу: "<книга>/<тема>" → { dir, status, files }.
   v7: один розбір на весь тулінг — scripts/lib/manifest7.js. Книга й курс лежать
   в ОДНОМУ просторі імен, бо префікс лінка тепер теж один (topic:). */
const M7 = require("./lib/manifest7.js");
const TOPICS = new Map();
const GTOPICS = new Map();                      // лишаємо ім'я: на нього дивиться решта файла
for (const [bslug, meta] of M7.books()) {
  const bk = M7.loadBook(meta.bookDir);
  if (!bk) continue;
  for (const t of M7.allTopics(bk)) {
    if (!t.own) continue;
    const n = t.node;
    const files = new Set();
    const bs = (n.basic && n.basic.status) || "empty";
    const ds = (n.detailed && n.detailed.status) || "empty";
    if (bs !== "empty") files.add(t.slug + ".md");
    if (ds !== "empty") files.add(t.slug + "-d.md");
    for (const k of M7.INSERT_TYPES) for (const x of n[k] || []) files.add(typeof x === "string" ? x : x.file);
    /* Доступна читачу, якщо done БУДЬ-ЯКА версія. У v6 дивилися лише на basic, і в v7
       це дало 48 тис. фальшивих «стабів»: тема з basic:empty + detailed:done — норма. */
    const avail = (bs === "done" || ds === "done") ? "done" : (ds !== "empty" ? ds : bs);
    TOPICS.set(bslug + "/" + t.slug, { dir: path.join(meta.bookDir, t.slug), status: avail, files, group: t.group });
  }
}

const reLink = /(!?)\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
const broken = [], warnMd = [], stubs = [], stale = [];
const mdFiles = walk(path.join(ROOT, "root"), []);

for (const f of mdFiles) {
  const rel = path.relative(ROOT, f);
  const txt = read(f);
  let m;
  while ((m = reLink.exec(txt))) {
    const isImg = m[1] === "!";
    let href = m[2];
    if (/^(https?:|mailto:|tel:|#)/i.test(href)) continue;
    href = href.split("#")[0]; if (!href) continue;

    if (/^root:/i.test(href)) {
      /* Резолв за PLAN §2.3: довга форма МІСТИТЬ коротку, тож беремо КНИГУ з першого
         сегмента і ТЕМУ з останнього змістовного — і коротка `книга/тема`, і довга
         `книга/група/розділ/тема` читаються одним правилом. Середина довгої — не адреса,
         а перевірка: розійшлася з маніфестом → адреса застаріла, а не бита.            */
      const segs = href.replace(/^root:/i, "").split("/").filter(Boolean);
      const book = segs[0] || "";
      const last = segs[segs.length - 1] || "";
      const isVer = /\.md$/i.test(last) || last === "detail" || last === "basic";
      const slug = (isVer ? segs[segs.length - 2] : last) || "";
      const ver = isVer ? last : null;
      const key = book + "/" + slug;
      const t = TOPICS.get(key) || GTOPICS.get(key);        // книга й курс — один простір імен
      if (!t) { broken.push(`${rel}: root:${segs.join("/")} — теми нема в жодному маніфесті`); continue; }
      /* Середні сегменти (група, розділ) — довідкові. Розбіжність із маніфестом ловимо
         окремим, мʼяким вироком: лінк робочий, але показує стару розкладку. */
      const mid = segs.slice(1, isVer ? segs.length - 2 : segs.length - 1);
      if (mid.length && t.group && mid[0] !== t.group) stale.push(`${rel}: root:${segs.join("/")} — група в адресі «${mid[0]}», у маніфесті «${t.group}»`);
      if (ver) {
        const want = ver === "detail" ? slug + "-d.md" : ver === "basic" ? slug + ".md" : ver;
        if (!t.files.has(want) && !exists(path.join(t.dir, want))) broken.push(`${rel}: root:${segs.join("/")} — файла нема`);
      } else if (t.status !== "done") stubs.push(`${rel}: root:${key} (${t.status}-стаб)`);
      continue;
    }
    // шлях від кореня репо (зображення/файл)
    const target = href.charAt(0) === "/" ? path.join(ROOT, href) : path.join(path.dirname(f), href);
    if (isImg || /\.(svg|png|jpg|jpeg|gif|webp)$/i.test(href)) {
      if (!exists(target)) broken.push(`${rel}: зображення ${href} — нема`);
    } else if (/\.md$/i.test(href)) {
      warnMd.push(`${rel}: відносний .md-лінк ${href} — за каноном має бути root:-попап`);
      if (!exists(target)) broken.push(`${rel}: .md-ціль ${href} — нема`);
    }
  }
}

console.log(`Перевірено .md: ${mdFiles.length} · тем у маніфестах: ${TOPICS.size}`);
console.log(`\n=== БИТІ (${broken.length}) ===`); broken.slice(0, 200).forEach((s) => console.log("  ✗ " + s));
console.log(`\n=== АДРЕСА ЗАСТАРІЛА (лінк робочий, показує стару розкладку) (${stale.length}) ===`); stale.slice(0, 30).forEach((s) => console.log("  ~ " + s));
console.log(`\n=== відносні .md-лінки, варто на root: (${warnMd.length}) ===`); warnMd.slice(0, 50).forEach((s) => console.log("  ⚠ " + s));
console.log(`\n=== лінки на empty-стаби (OK, ${stubs.length}) ===`);
process.exit(broken.length ? 1 : 0);
