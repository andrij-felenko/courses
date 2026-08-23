/* Точкова правка статусу ВСТАВКИ: знаходимо ім'я файлу, далі найближчий status і міняємо значення.
   Працює в обох форматах маніфесту. Після правки — перепарс і звірка кількості тем; інакше відкат. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const APPLY = process.argv.includes("--apply");
const l = JSON.parse(fs.readFileSync(path.join(__dirname, "manifest-lies.json"), "utf8"));
const all = l.ghosts.concat(l.lies).filter(function (r) { return r.ver !== "basic" && r.ver !== "detailed"; });

function parse(file) { const w = { __BOOKS__: [], __GUIDES__: [] };
  new Function("window", fs.readFileSync(file, "utf8"))(w);
  return (w.__BOOKS__[0] || w.__GUIDES__[0]); }
function count(m) { let n = 0; for (const s of m.sections || []) n += (s.topics || []).length;
  for (const mo of m.modules || []) for (const c of mo.chapters || []) n += (c.steps || []).length; return n; }

const by = {}; all.forEach(function (r) { (by[r.manifest] = by[r.manifest] || []).push(r); });
let done = 0, miss = 0;
for (const mf of Object.keys(by)) {
  const file = path.join(R, mf);
  const before = count(parse(file));
  let src = fs.readFileSync(file, "utf8"), changed = [];
  for (const r of by[mf]) {
    const q = '"' + r.file + '"';
    const i = src.indexOf(q);
    if (i < 0) { console.log("  нема запису: " + r.file); miss++; continue; }
    const win = src.slice(i, i + 160);
    const si = win.indexOf("status");
    if (si < 0) { console.log("  нема status біля: " + r.file); miss++; continue; }
    const abs = i + si;
    const ci = src.indexOf(":", abs);              // двокрапка після ключа (обидва формати)
    const q1 = src.indexOf('"', ci);               // відкривна лапка ЗНАЧЕННЯ
    const q2 = src.indexOf('"', q1 + 1);
    const cur = src.slice(q1 + 1, q2);
    if (cur === "pending") { continue; }
    src = src.slice(0, q1 + 1) + "pending" + src.slice(q2);
    changed.push(r.file + "  " + cur + " → pending");
  }
  if (!changed.length) continue;
  if (!APPLY) { console.log(mf + ":  " + changed.length); changed.forEach(function (c) { console.log("     " + c) }); done += changed.length; continue; }
  const tmp = file + ".tmp"; fs.writeFileSync(tmp, src, "utf8");
  let after; try { after = count(parse(tmp)) } catch (e) { fs.unlinkSync(tmp); console.error("СТОП " + mf + ": не парситься — відкат"); process.exit(1) }
  if (after !== before) { fs.unlinkSync(tmp); console.error("СТОП " + mf + ": тем було " + before + ", стало " + after + " — відкат"); process.exit(1) }
  fs.renameSync(tmp, file);
  console.log("OK " + mf + ":  " + changed.length); changed.forEach(function (c) { console.log("     " + c) });
  done += changed.length;
}
console.log("\n" + (APPLY ? "виправлено" : "до виправлення") + ": " + done + (miss ? "   не знайдено: " + miss : ""));
