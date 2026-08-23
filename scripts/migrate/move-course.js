/* move-course.js <курс> — переносить власні статті курсу з guide/<курс>/<модуль>/<слуг>/
   у root/course/<курс>/<слуг>/ (пласко) і переписує все, що на них указувало.

   Що переписується по всьому корпусу:
     guide:<курс>/…            → root:<курс>/…          (посилання в прозі, коротка форма)
     /guide/<курс>/<мод>/<слуг>/ → /root/course/<курс>/<слуг>/   (шляхи картинок від кореня репо)
     guide/<курс>/<мод>/<слуг>   → root/course/<курс>/<слуг>     (рядки у figs.py)

   Глибина вкладення не міняється (обидва шляхи — чотири рівні), тож sys.path у figs.py лишається
   робочим. Переміщення робить git mv, щоб історія файлів не обірвалася. */
const fs = require("fs");
const path = require("path");
const cp = require("child_process");

const course = process.argv[2];
if (!course) { console.error("вкажи курс"); process.exit(1); }
const ROOT = path.resolve(__dirname, "..", "..");
process.chdir(ROOT);

const SRC = path.join("guide", course);
const DST = path.join("root", "course", course);

/* 1. збираємо теми */
const moves = [];
for (const mod of fs.readdirSync(SRC)) {
  const mp = path.join(SRC, mod);
  if (!fs.statSync(mp).isDirectory() || mod[0] === "_") continue;
  for (const slug of fs.readdirSync(mp)) {
    const sp = path.join(mp, slug);
    if (!fs.statSync(sp).isDirectory()) continue;
    moves.push({ slug: slug, from: sp.replace(/\\/g, "/"), to: (DST + "/" + slug).replace(/\\/g, "/") });
  }
}
const dup = {};
for (const m of moves) { if (dup[m.slug]) { console.error("КОЛІЗІЯ СЛУГА: " + m.slug); process.exit(1); } dup[m.slug] = 1; }
console.log("тем до переносу: " + moves.length);

/* 2. git mv */
fs.mkdirSync(DST, { recursive: true });
let moved = 0;
for (const m of moves) {
  if (fs.existsSync(m.to)) { console.error("ціль уже існує: " + m.to); process.exit(1); }
  cp.execFileSync("git", ["mv", m.from, m.to]);
  moved++;
}
console.log("перенесено git mv: " + moved);

/* 3. карта старий шлях → новий, для картинок і figs.py */
const pathMap = moves.map(m => ({ from: m.from, to: m.to }));

function walk(dir, fn) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    let st; try { st = fs.statSync(p); } catch (e) { continue; }
    if (st.isDirectory()) { if (f === ".git" || f === "node_modules" || f === ".claude") continue; walk(p, fn); }
    else fn(p);
  }
}

let mdFiles = 0, mdHits = 0, pyFiles = 0, pyHits = 0;
walk(".", function (p) {
  const isMd = /\.md$/.test(p), isPy = /\.py$/.test(p);
  if (!isMd && !isPy) return;
  let s = fs.readFileSync(p, "utf8"); const before = s;
  if (isMd) {
    const a = s.split("guide:" + course + "/").length - 1;
    if (a) { s = s.split("guide:" + course + "/").join("root:" + course + "/"); mdHits += a; }
  }
  for (const m of pathMap) {
    const oldAbs = "/" + m.from + "/", newAbs = "/" + m.to + "/";
    const c1 = s.split(oldAbs).length - 1;
    if (c1) { s = s.split(oldAbs).join(newAbs); (isMd ? mdHits += c1 : pyHits += c1); }
    const c2 = s.split(m.from).length - 1;
    if (c2) { s = s.split(m.from).join(m.to); (isMd ? mdHits += c2 : pyHits += c2); }
  }
  if (isPy) {
    const c = s.split("guide/" + course).length - 1;
    if (c) { s = s.split("guide/" + course).join("root/course/" + course); pyHits += c; }
  }
  if (s !== before) { fs.writeFileSync(p, s); (isMd ? mdFiles++ : pyFiles++); }
});
console.log("переписано: .md — " + mdHits + " місць у " + mdFiles + " файлах · .py — " + pyHits + " у " + pyFiles);

/* 4. що лишилося в guide/<курс> */
const left = [];
walk(SRC, function (p) { left.push(p); });
console.log("у guide/" + course + " лишилося файлів: " + left.length);
left.slice(0, 8).forEach(x => console.log("   " + x.replace(/\\/g, "/")));
