/* Перевірка ref-цілей у файлі змісту.
   node scripts/migrate/check-refs.js <файл.md> [ще файли]
   Шукає `ref <книга>/<галузь>/<слуг>` і судить кожну ціль за маніфестами.
   Написано ⟺ detailed або basic має статус done|update|deeper|recheck (так рахує bookbuild.js:38).
   pending / empty / нема теми — ціль непридатна, курс на неї вести не може. */
const fs = require("fs"), path = require("path");
global.window = { __BOOKS__: [], __GUIDES__: [] };
const roots = ["book", "reference", "catalog"];
for (const r of roots) {
  let dirs = [];
  try { dirs = fs.readdirSync(path.resolve(r)); } catch (e) { continue; }
  for (const d of dirs) {
    const m = path.resolve(r, d, "manifest.js");
    if (fs.existsSync(m)) { try { require(m); } catch (e) { console.error("НЕ ЧИТАЄТЬСЯ", m); } }
  }
}
const W = function (s) { return s === "done" || s === "update" || s === "deeper" || s === "recheck"; };
const ST = {};
for (const b of window.__BOOKS__)
  for (const s of b.sections || [])
    for (const t of s.topics || [])
      ST[b.slug + "/" + s.slug + "/" + t.slug] = {
        d: (t.detailed || {}).status, b: (t.basic || {}).status, title: t.title
      };
console.log("завантажено книг: " + window.__BOOKS__.length + ", тем: " + Object.keys(ST).length);
for (const f of process.argv.slice(2)) {
  const txt = fs.readFileSync(f, "utf8");
  const re = /`ref +([a-z0-9\-]+\/[a-z0-9\-]+\/[a-z0-9\-]+)`/g;
  let m; const seen = {}; const miss = []; const dead = []; let n = 0; const dup = [];
  while ((m = re.exec(txt))) {
    const p = m[1]; n++;
    if (seen[p]) { dup.push(p); continue; }
    seen[p] = 1;
    const st = ST[p];
    if (!st) { miss.push(p); continue; }
    if (!W(st.d) && !W(st.b)) dead.push(p + "  (detailed:" + st.d + ", basic:" + st.b + ")");
  }
  console.log("\n=== " + path.basename(f));
  console.log("  ref-кроків: " + n + ", унікальних цілей: " + Object.keys(seen).length);
  console.log("  ПОВТОРЕНА ціль (та сама стаття двічі): " + dup.length);
  dup.slice(0, 20).forEach(function (x) { console.log("    ×2 " + x); });
  console.log("  ЦІЛІ, ЯКИХ НЕМА в маніфестах: " + miss.length);
  miss.slice(0, 40).forEach(function (x) { console.log("    ?  " + x); });
  console.log("  ЦІЛІ БЕЗ ТЕКСТУ (pending/empty): " + dead.length);
  dead.slice(0, 40).forEach(function (x) { console.log("    !  " + x); });
}
