/* scripts/fix-figrefs.js — лагодить БИТІ посилання на фігури після часткових правок (rate-limit/збій агента).
   Патерн збою: агент зробив git mv fig-NN-MM-<name>.svg → <name>.svg, але НЕ оновив ![..](img/fig-...) у .md.
   Скрипт: для кожного битого img-рефа в .md дістає описовий «хвіст» (після fig-<індекси>-), і якщо <хвіст>.svg
   існує в img/ теми — переписує реф на корене-абсолютний /book/.../img/<хвіст>.svg. Якщо файлу нема — лишає, репортує.
   Запуск:  node scripts/fix-figrefs.js            (усе root/)
            node scripts/fix-figrefs.js root/hw/hw-digital/dac   (одна тека) */
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const arg = process.argv[2];

function walkMd(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walkMd(p, out);
    else if (e.isFile() && e.name.endsWith(".md")) out.push(p);
  }
}
const mdFiles = [];
walkMd(arg ? path.resolve(ROOT, arg) : path.join(ROOT, "root"), mdFiles);

const reImg = /!\[[^\]]*\]\(([^)]+\.svg)\)/g;
let fixed = 0, stillBroken = [];
for (const md of mdFiles) {
  let txt = fs.readFileSync(md, "utf8");
  const dir = path.dirname(md);
  let changed = false;
  txt = txt.replace(reImg, (full, ref) => {
    // абсолютний шлях цілі
    const abs = ref.charAt(0) === "/" ? path.join(ROOT, ref) : path.join(dir, ref);
    if (fs.existsSync(abs)) return full;                       // не битий — лишаємо
    // дістати описовий хвіст: fig-<число[літера]>-...-<НАЗВА>.svg → НАЗВА
    const base = path.basename(ref);
    const m = base.match(/^fig-(?:[0-9]+[a-z]*-)+(.+)\.svg$/i);
    const tail = m ? m[1] : base.replace(/\.svg$/i, "");
    // тека теми = тека .md (фігури в ./img/ поруч); обчислити /book-відносний шлях
    const imgDir = path.join(dir, "img");
    const cand = path.join(imgDir, tail + ".svg");
    if (fs.existsSync(cand)) {
      const rel = "/" + path.relative(ROOT, cand).split(path.sep).join("/");
      fixed++; changed = true;
      return full.replace(ref, rel);
    }
    stillBroken.push(`${path.relative(ROOT, md)}: ${ref} (хвіст «${tail}» — нема ${tail}.svg)`);
    return full;
  });
  if (changed) fs.writeFileSync(md, txt);
}
console.log(`Перепинено рефів: ${fixed}`);
if (stillBroken.length) { console.log(`Лишилось битих (нема перейменованого файлу): ${stillBroken.length}`); stillBroken.slice(0, 20).forEach(s => console.log("  ✗ " + s)); }
else console.log("Усі биті фіг-рефи полагоджено (або битих не було).");
