/* build-root-manifests.js — з проєктів томів у scripts/migrate/final будує
   root/course/<slug>/manifest.json за схемою 7: groups → chapters → topics.

   Проєкти писали 34 різні агенти, тож розкладка трапляється у двох діалектах:
     таблиця        | Назва кроку | `наявна` (`шлях`) |
     нумерований    3. Назва кроку · `наявна` (`шлях`)
   Стан кроку: наявна · +ref <шлях> · ВЛАСНА · НОВА → <шлях>
   Наявні кроки часто без слуга — їх упізнаємо за назвою в чинному маніфесті курсу.
*/
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const FIN = path.resolve(__dirname, "final");
const KINDS = /^(?:book|reference|catalog|guide)\//;

const MAP = { а:"a",б:"b",в:"v",г:"h",ґ:"g",д:"d",е:"e",є:"ie",ж:"zh",з:"z",и:"y",і:"i",ї:"i",
  й:"i",к:"k",л:"l",м:"m",н:"n",о:"o",п:"p",р:"r",с:"s",т:"t",у:"u",ф:"f",х:"kh",ц:"ts",
  ч:"ch",ш:"sh",щ:"shch",ь:"",ю:"iu",я:"ia" };
function slugify(s) {
  let out = "";
  for (const ch of String(s).toLowerCase()) {
    if (MAP[ch] !== undefined) out += MAP[ch];
    else if (/[a-z0-9]/.test(ch)) out += ch;
    else out += "-";
  }
  return out.replace(/-+/g, "-").replace(/^-|-$/g, "").slice(0, 60) || "krok";
}
function norm(s) {
  return String(s).toLowerCase()
    .replace(/[`*«»"'’ʼ()]/g, "")
    .replace(/[^a-zа-яіїєґ0-9]+/gi, " ")
    .trim();
}

/* ---- корпус ---- */
global.window = { __BOOKS__: [], __GUIDES__: [] };
for (const d of ["book", "reference", "catalog"])
  for (const b of fs.readdirSync(path.join(ROOT, d))) {
    const p = path.join(ROOT, d, b, "manifest.js");
    if (fs.existsSync(p)) { try { require(p); } catch (e) {} }
  }
for (const c of ["embedded", "progarch", "unix"]) {
  const p = path.join(ROOT, "guide", c, "manifest.js");
  if (fs.existsSync(p)) { try { require(p); } catch (e) {} }
}
const REAL = Object.create(null);
for (const b of window.__BOOKS__)
  for (const s of b.sections || [])
    for (const t of s.topics || []) REAL[b.slug + "/" + s.slug + "/" + t.slug] = 1;

/* назва кроку → крок чинного курсу */
const BYTITLE = Object.create(null);
for (const g of window.__GUIDES__)
  for (const m of g.modules || [])
    for (const ch of m.chapters || [])
      for (const st of ch.steps || []) BYTITLE[g.slug + "|" + norm(st.title)] = st;

/* ---- розбір ---- */
const CH_RE = [
  /^#{2,4}\s*§\s*\d+[.．]\s*(.+)$/,
  /^#{2,4}\s*Розділ\s+\d+[.．]\s*(.+)$/,
  /^#{2,4}\s*\d+\.\d+\.\s*(.+)$/,
  /^#{2,4}\s*\d+[.．]\s*(.+)$/,
];
const SKIP_CH = /^(розділи|карта|склад|числа|підсум|що на виході|спірн|діри|не лягло|заперечен|назва|перевірк|додат|резерв|метод|звірк|порядок|вихід|позначки|як влаштов)/i;
function chapterOf(ln) {
  for (const re of CH_RE) {
    const m = ln.match(re);
    if (m) {
      const t = m[1].replace(/\s*—\s*\d+.*$/, "").replace(/[*`]/g, "").trim();
      if (!t || SKIP_CH.test(t)) return null;
      return t;
    }
  }
  return null;
}
function cleanPath(p) { return p.replace(KINDS, ""); }

function classify(course, name, state) {
  const isNew = /НОВА/.test(state);
  const isOwnNew = /ВЛАСНА/.test(state);
  const isHave = /наявн/i.test(state);
  const pm = state.match(/([a-z0-9-]+\/[a-z0-9-]+(?:\/[a-z0-9-]+)?)/);
  const p = pm ? cleanPath(pm[1]) : null;

  if (isHave) {
    const src = BYTITLE[course + "|" + norm(name)];
    if (src && src.ref) return { kind: "ref", ref: src.ref, title: src.title };
    if (src && src.slug) return { kind: "own", slug: src.slug, src: src, title: src.title };
    if (p && p.split("/").length === 3 && REAL[p]) return { kind: "ref", ref: p, title: name };
    return { kind: "ownnew", slug: slugify(name), title: name };
  }
  if (isNew) {
    let full = p || "";
    if (full.split("/").length === 2) full += "/" + slugify(name);
    return { kind: "new", ref: full, title: name };
  }
  if (isOwnNew) return { kind: "ownnew", slug: slugify(name), title: name };
  if (p && p.split("/").length === 3) return { kind: "ref", ref: p, title: name };
  return null;
}

/* один запис може займати кілька рядків — зшиваємо й аж тоді судимо */
function flush(cur, buf, course) {
  if (!cur || !buf.length) return;
  const ln = buf.join(" ").replace(/\s+/g, " ").trim();
  let name = null, state = ln;
  const row = ln.match(/^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$/);
  const item = ln.match(/^\d+\.\s+(.+)$/);
  const bullet = ln.match(/^[-*]\s+(.+)$/);
  if (row) { name = row[1]; state = row[2]; }
  else if (item) {
    const parts = item[1].split(/\s+·\s+/);
    if (parts.length < 2) return;
    name = parts[0]; state = parts.slice(1).join(" · ");
  } else if (bullet) {
    const body = bullet[1];
    const q = body.match(/[«"]([^»"]{4,120})[»"]/);
    const dash = body.split(/\s+—\s+/);
    if (q) name = q[1];
    else if (dash.length > 1) name = dash[1].split(/\s+·\s+/)[0];
    else name = body.split(/\s+·\s+/)[0];
    state = body;
  } else return;
  name = String(name || "").replace(/\*\*/g, "").replace(/`[^`]*`/g, " ")
    .replace(/\[pending\]/gi, "").replace(/\s+/g, " ").trim();
  if (!name || name.length < 3 || /^крок$/i.test(name) || /^-+$/.test(name)) return;
  const t = classify(course, name, state);
  if (t) cur.topics.push(t);
}

function parseVolume(course, file) {
  const L = fs.readFileSync(file, "utf8").split(/\r?\n/);
  let volTitle = "";
  const chapters = [];
  let cur = null;
  const buf = [];
  for (const raw of L) {
    const ln = raw.trim();
    if (!volTitle) {
      const h = ln.match(/^#\s+(.+)$/);
      if (h) volTitle = h[1].replace(/[*`«»]/g, "").replace(/^Том\s+\d+[.．]?\s*/i, "")
        .replace(/\s+—.*$/, "").trim();
    }
    const ct = chapterOf(ln);
    if (ct) { flush(cur, buf, course); buf.length = 0; }
    if (ct) { cur = { title: ct, topics: [] }; chapters.push(cur); continue; }
    if (!cur) continue;

    if (/^\|/.test(ln) || /^\d+\.\s/.test(ln) || /^[-*]\s/.test(ln)) {
      flush(cur, buf, course); buf.length = 0; buf.push(ln);
    } else if (buf.length && ln && !/^#/.test(ln)) {
      buf.push(ln);
    } else { flush(cur, buf, course); buf.length = 0; }
  }
  flush(cur, buf, course);
  return { title: volTitle, chapters: chapters.filter(c => c.topics.length) };
}

/* ---- збірка ---- */
const COURSES = {
  embedded: { dir: "vols3", title: "Вбудована електроніка й автономні системи" },
  unix:     { dir: "vols-unix6", title: "Unix крок за кроком" },
  progarch: { dir: "vols-pg", title: "Архітектура програмних систем" },
};
const lines = [];
for (const slug of Object.keys(COURSES)) {
  const cfg = COURSES[slug];
  const dir = path.join(FIN, cfg.dir);
  const files = fs.readdirSync(dir).filter(f => /\.md$/.test(f)).sort();
  const groups = [];
  const st = { steps: 0, ref: 0, nw: 0, own: 0, ownnew: 0 };
  const broken = [], empty = [];
  for (const f of files) {
    const v = parseVolume(slug, path.join(dir, f));
    if (!v.chapters.length) { empty.push(f); continue; }
    const g = { slug: slugify(v.title), title: v.title, scope: "", chapters: [] };
    for (const c of v.chapters) {
      const chap = { slug: slugify(c.title), title: c.title, topics: [] };
      for (const t of c.topics) {
        st.steps++;
        if (t.kind === "ref") {
          st.ref++;
          if (!REAL[t.ref]) broken.push(t.ref);
          chap.topics.push({ ref: t.ref, title: t.title });
        } else if (t.kind === "new") {
          st.nw++;
          chap.topics.push({ ref: t.ref, title: t.title, todo: "нова тема в книзі" });
        } else if (t.kind === "own") {
          st.own++;
          chap.topics.push({ slug: t.slug, title: t.title,
            basic: t.src.basic || { status: "empty" },
            detailed: t.src.detailed || { status: "pending" } });
        } else {
          st.ownnew++;
          chap.topics.push({ slug: t.slug, title: t.title,
            basic: { status: "empty" }, detailed: { status: "pending" } });
        }
      }
      if (chap.topics.length) g.chapters.push(chap);
    }
    if (g.chapters.length) groups.push(g);
  }
  const man = { schema: 7, kind: "course", slug: slug, title: cfg.title, groups: groups };
  const out = path.join(ROOT, "root", "course", slug);
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "manifest.json"), JSON.stringify(man, null, 2) + "\n");
  lines.push(slug + ": томів " + groups.length + ", розділів " +
    groups.reduce((a, g) => a + g.chapters.length, 0) + ", кроків " + st.steps);
  lines.push("   ref " + st.ref + " · нових тем " + st.nw +
    " · власних наявних " + st.own + " · власних нових " + st.ownnew);
  if (empty.length) lines.push("   ⚠ не розібрано: " + empty.join(", "));
  if (broken.length) {
    const u = Array.from(new Set(broken));
    lines.push("   ✖ битих ref " + u.length + ": " + u.slice(0, 6).join(" · "));
  }
}
console.log(lines.join("\n"));
