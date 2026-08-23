/* migrate-course.js — перенос КУРСУ в нове дерево. Агентів не треба:
   порядок кроків у курсі авторський, його не перекладають, а зберігають.
     node scripts/migrate/migrate-course.js guide/<курс> [--apply]
   Робить: власні статті `guide/<курс>/<модуль>/<slug>/` -> `root/course/<курс>/<slug>/`,
   переписує img-шляхи, пише manifest.json схеми 7, де модуль = група, розділ = розділ,
   а крок-`ref` лишається кроком-`ref` — він посилання й переїзду не потребує.
   Ідемпотентний: повторний запуск після обриву продовжує. Суха прогонка за замовчуванням. */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const R = path.resolve(__dirname, "../..");
const M = require("./_manifest.js");
const NL = String.fromCharCode(10);
const SKIP = new Set([".git", "node_modules", ".claude", ".github"]);
const args = process.argv.slice(2);
const BASE = args.find(a => !a.startsWith("--")), APPLY = args.includes("--apply");
if (!BASE) { console.error("ужиток: node scripts/migrate/migrate-course.js guide/<курс> [--apply]"); process.exit(2); }

const src = M.read(BASE, R);
if (src.form !== "guide" && src.form !== "guide-legacy") { console.error("це не курс: " + BASE); process.exit(2); }
const COURSE = src.slug, DEST = "root/course/" + COURSE;

function git(a) { const r = cp.spawnSync("git", a, { cwd: R, encoding: "utf8" });
  if (r.status !== 0) { console.error("СТОП git " + a.join(" ") + ": " + (r.stderr || "").trim()); process.exit(1); } }
function walk(d, o) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name);
  if (e.isDirectory()) { if (!SKIP.has(e.name)) walk(p, o) } else if (e.name.endsWith(".md")) o.push(p); } return o; }

/* слуг розділу: у курсі розділ має лише назву, а адресі потрібен слуг */
const UA = { а:"a",б:"b",в:"v",г:"h",ґ:"g",д:"d",е:"e",є:"ie",ж:"zh",з:"z",и:"y",і:"i",ї:"i",й:"i",к:"k",л:"l",м:"m",
  н:"n",о:"o",п:"p",р:"r",с:"s",т:"t",у:"u",ф:"f",х:"kh",ц:"ts",ч:"ch",ш:"sh",щ:"shch",ь:"",ю:"iu",я:"ia" };
function slugify(s, fallback) {
  const out = String(s || "").toLowerCase().split("").map(c => (UA[c] !== undefined ? UA[c] : c))
    .join("").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40);
  return out || fallback;
}
/* власні статті — тільки вони переїжджають; ref-кроки лишаються посиланнями */
const own = src.topics.filter(t => t.slug);
const refs = src.topics.filter(t => t.ref);
const bad = [], DONE = {};
let already = 0, mo = 0;
for (const t of own) {
  const srcOk = fs.existsSync(path.join(R, t.dir));
  const dstOk = fs.existsSync(path.join(R, DEST + "/" + t.slug));
  const unwritten = t.basic.status !== "done" && t.detailed.status !== "done" &&
                    ["done","update","deeper","recheck"].indexOf(t.basic.status) < 0 &&
                    ["done","update","deeper","recheck"].indexOf(t.detailed.status) < 0;
  if (srcOk && dstOk) bad.push("і джерело, і ціль існують: " + t.dir);
  else if (!srcOk && dstOk) { DONE[t.slug] = 1; already++; }
  else if (!srcOk && !dstOk) { if (unwritten) { t.manifestOnly = true; mo++; } else bad.push("нема ні джерела, ні цілі: " + t.dir); }
}
const seen = {};
for (const t of own) { if (seen[t.slug]) bad.push("слуг двічі: " + t.slug); seen[t.slug] = 1; }
if (bad.length) { console.error("СТОП:" + NL + "  " + bad.join(NL + "  ")); process.exit(1); }

const toMove = own.filter(t => !DONE[t.slug] && !t.manifestOnly);
console.log("курс " + COURSE + ": власних статей " + own.length + " (переносимо " + toMove.length +
  (already ? ", уже на місці " + already : "") + (mo ? ", лише запис " + mo : "") + "), кроків-ref " + refs.length + " — не чіпаємо");

if (!APPLY) { console.log("ціль: " + DEST + NL + "(суха прогонка; --apply щоб виконати)"); process.exit(0); }

fs.mkdirSync(path.join(R, DEST), { recursive: true });
let nImg = 0;
for (const t of toMove) {
  const to = DEST + "/" + t.slug;
  git(["mv", t.dir, to]);
  const OLD = "/" + t.dir + "/", NEW = "/" + to + "/";
  for (const f of walk(path.join(R, to), [])) {
    const s = fs.readFileSync(f, "utf8");
    if (s.indexOf(OLD) < 0) continue;
    nImg += s.split(OLD).length - 1;
    fs.writeFileSync(f, s.split(OLD).join(NEW), "utf8");
  }
}
console.log("перенесено тек: " + toMove.length + ", img-шляхів переписано: " + nImg);
/* manifest.json схеми 7: модуль -> група, розділ -> розділ, крок лишається кроком.
   Порядок збережено дослівно — він авторський. */
const raw = { __BOOKS__: [], __GUIDES__: [] };
new Function("window", fs.readFileSync(src.file, "utf8"))(raw);
const g0 = raw.__GUIDES__[0];
const mods = (g0.modules && g0.modules.length) ? g0.modules : (g0.sections || []);
const out = { schema: 7, kind: "course", slug: COURSE, title: g0.title, groups: [] };
let nOwn = 0, nRef = 0, chNo = 0;
for (const mo2 of mods) {
  const G = { slug: mo2.slug, title: mo2.title, scope: mo2.scope || "", chapters: [] };
  const chs = (mo2.chapters && mo2.chapters.length) ? mo2.chapters
            : [{ title: "", steps: mo2.topics || mo2.steps || [] }];
  for (const c of chs) {
    chNo++;
    const C = { slug: c.title ? slugify(c.title, "ch-" + chNo) : ".", title: c.title || "", topics: [] };
    for (const st of (c.steps || c.topics || [])) {
      if (st.ref) { C.topics.push({ ref: st.ref, title: st.title }); nRef++; continue; }
      if (!st.slug) continue;
      const e = { slug: st.slug, title: st.title };
      e.basic = { status: (st.basic && st.basic.status) || "empty" };
      e.detailed = { status: (st.detailed && st.detailed.status) || "empty" };
      for (const k of M.INS) if (st[k] && st[k].length) e[k] = st[k];
      C.topics.push(e); nOwn++;
    }
    G.chapters.push(C);
  }
  out.groups.push(G);
}
/* звірка вхід == вихід */
if (nOwn !== own.length || nRef !== refs.length) {
  console.error("СТОП: у маніфест мало лягти " + own.length + " своїх і " + refs.length + " ref, а лягло " + nOwn + " і " + nRef);
  process.exit(1);
}
const dirsN = fs.readdirSync(path.join(R, DEST), { withFileTypes: true }).filter(e => e.isDirectory()).length;
const expectDirs = own.length - own.filter(t => t.manifestOnly).length;
if (dirsN !== expectDirs) { console.error("СТОП: тек на диску " + dirsN + ", мало бути " + expectDirs); process.exit(1); }
fs.writeFileSync(path.join(R, DEST, "manifest.json"), JSON.stringify(out, null, 2) + NL, "utf8");
console.log("написано " + DEST + "/manifest.json   своїх " + nOwn + ", ref " + nRef + ", тек на диску " + dirsN + " ✓");

const shelfPath = path.join(R, "root/shelf.json");
const shelf = JSON.parse(fs.readFileSync(shelfPath, "utf8"));
const K = shelf.kinds.find(k => k.kind === "course");
if (K && K.books.indexOf(COURSE) < 0) { K.books.push(COURSE); K.books.sort();
  fs.writeFileSync(shelfPath, JSON.stringify(shelf, null, 2) + NL, "utf8");
  console.log("  реєстр: course <- " + COURSE); }
console.log(NL + "старий " + src.file.replace(R + path.sep, "").split(path.sep).join("/") + " лишається — знімати книгу з реєстру окремим кроком");
