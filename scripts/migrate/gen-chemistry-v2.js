/* scripts/migrate/gen-chemistry-v2.js — крок 1 міграції: маніфест v2 для course/basic-chemistry.
   Джерела: guide/basic-chemistry/manifest.js (порядок) + book/chemistry/manifest.js (статуси, вставки).
   Нічого не переносить: лише пише course/basic-chemistry/manifest_v2.json. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");

function load(file, key) {
  const w = { __BOOKS__: [], __GUIDES__: [] };
  new Function("window", fs.readFileSync(path.join(R, file), "utf8"))(w);
  return w[key][0];
}
const course = load("guide/basic-chemistry/manifest.js", "__GUIDES__");
const book = load("book/chemistry/manifest.js", "__BOOKS__");

// slug теми → її запис у книзі (статуси + вставки), плюс стара секція для файлу переносу
const TOPIC = {};
for (const sec of book.sections || [])
  for (const t of sec.topics || []) TOPIC[t.slug] = { t, oldSection: sec.slug };

// слуги розділів (у v2 розділ — сегмент адреси, тож потребує слуга)
const CH = {
  "Хімія і речовини": "substances", "Атом": "atom", "Періодична таблиця": "periodic",
  "Хімічний зв'язок": "bonds", "Формули, валентність і моль": "formulas-valence-mole",
  "Як влаштовані тверді речовини": "solids",
  "Що таке реакція насправді": "what-is-reaction", "Енергія: чому горить і гріє": "energy",
  "Швидкість і рівновага": "rate-equilibrium",
  "Вода і розчини": "solutions", "Кислоти й основи": "acids-bases",
  "Оксиди, солі та карта неорганіки": "oxides-salts", "Метали й елементи навколо нас": "metals",
  "Карбон і його ланцюги": "carbon-chains", "Кисень приєднується: спирти, кислоти, жири": "oxygen-groups",
  "Молекули життя": "life-molecules",
  "Кількість речовини: моль": "amount", "Масова частка": "fractions",
  "Розрахунки за рівнянням": "by-equation", "Складніші задачі: гази, надлишок, вихід": "harder-problems",
};
// томи без номерів у слузі: порядок дає маніфест (AUTHORING §2)
const VOL = { "m1-atoms": "atoms", "m2-bonds": "bonds", "m3-reactions": "reactions",
              "m4-inorganic": "inorganic", "m5-organic": "organic", "m6-counting": "counting" };
// 7 тем, яких курс не мав: {slug: [розділ, після якого вставити]}
const ORPHANS = {
  "isotopes": ["atom", "element"], "radioactivity": ["atom", "isotopes"],
  "intermolecular-forces": ["bonds", "metallic-bond"],
  "reaction-direction": ["rate-equilibrium", "equilibrium"],
  "electrode-potential": ["metals", "activity-corrosion"],
  "isomers": ["carbon-chains", "hydrocarbons"],
  "dna": ["life-molecules", "fats-proteins"],
};

function topicEntry(slug, title) {
  const rec = TOPIC[slug];
  if (!rec) throw new Error("нема в book/chemistry: " + slug);
  const t = rec.t, out = { slug: slug, title: title || t.title };
  out.basic = { status: (t.basic && t.basic.status) || "empty" };
  out.detailed = { status: (t.detailed && t.detailed.status) || "empty" };
  for (const k of ["hist", "comp", "math", "proj"]) if (t[k] && t[k].length) out[k] = t[k];
  rec.placed = true;
  return out;
}

const groups = [];
for (const m of course.modules || []) {
  const g = { slug: VOL[m.slug] || m.slug, title: m.title, scope: m.scope || "", chapters: [] };
  for (const c of m.chapters || []) {
    const ch = { slug: CH[c.title] || null, title: c.title, topics: [] };
    if (!ch.slug) throw new Error("нема слуга для розділу: " + c.title);
    for (const s of c.steps || []) {
      const slug = String(s.ref || s.slug).split("/").pop();
      ch.topics.push(topicEntry(slug, s.title));
      // сироти чіпляються ланцюжком: одна може стояти "після" іншої сироти
      let anchor = slug, again = true;
      while (again) {
        again = false;
        for (const [osl, [och, after]] of Object.entries(ORPHANS))
          if (och === ch.slug && after === anchor && !TOPIC[osl].placed) {
            ch.topics.push(topicEntry(osl)); anchor = osl; again = true; break;
          }
      }
    }
    g.chapters.push(ch);
  }
  groups.push(g);
}

const missed = Object.keys(TOPIC).filter(s => !TOPIC[s].placed);
if (missed.length) throw new Error("не розміщено: " + missed.join(", "));

const out = { schema: 7, kind: "course", slug: "basic-chemistry", title: course.title, groups: groups };
const dst = path.join(R, "guide/basic-chemistry/manifest_v2.json");
fs.writeFileSync(dst, JSON.stringify(out, null, 2) + "\n", "utf8");

let nt = 0, nc = 0;
groups.forEach(g => g.chapters.forEach(c => { nc++; nt += c.topics.length; }));
console.log("написано " + path.relative(R, dst));
console.log("  томів " + groups.length + " · розділів " + nc + " · тем " + nt + " / " + Object.keys(TOPIC).length);
// файл переносу (крок 4): звідки → куди
const moves = [];
groups.forEach(g => g.chapters.forEach(c => c.topics.forEach(t => moves.push({
  slug: t.slug,
  from: "book/chemistry/" + TOPIC[t.slug].oldSection + "/" + t.slug,
  to: "course/basic-chemistry/" + t.slug,
  addr: "course/basic-chemistry/" + g.slug + "/" + c.slug + "/" + t.slug,
}))));
fs.writeFileSync(path.join(R, "scripts/migrate/moves-chemistry.json"), JSON.stringify(moves, null, 2) + "\n", "utf8");
console.log("написано scripts/migrate/moves-chemistry.json  (" + moves.length + " переносів)");
