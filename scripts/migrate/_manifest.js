/* _manifest.js — ОДИН читач для всіх форм маніфесту, що є в корпусі.
   Форми:
     A) window.__BOOKS__  + sections -> topics            book/ catalog/ reference/
     B) window.__GUIDES__ + modules -> chapters -> steps  guide/ (нинішня)
     C) window.__GUIDES__ + sections -> topics            guide/ (легасі, підтримується рушієм)
     D) manifest.json схеми 7 + groups -> chapters -> topics   root/<вид>/<книга>/ (уже переїхале)
   Повертає { form, kind, slug, title, topics: [...] }, де кожна тема:
     { slug, title, basic, detailed, inserts:{hist,comp,math,proj,api},
       container, containerTitle, scope, dir, ref }
   `ref`-кроки курсів повертаються з ref !== null і dir === null — вони посилання,
   переїзду не потребують і в перенос не беруться. */
const fs = require("fs"), path = require("path");
const INS = ["hist", "comp", "math", "proj", "api"];

function loadRaw(file) {
  if (file.endsWith(".json")) return { json: JSON.parse(fs.readFileSync(file, "utf8")) };
  const w = { __BOOKS__: [], __GUIDES__: [] };
  new Function("window", fs.readFileSync(file, "utf8"))(w);
  return { book: w.__BOOKS__[0], guide: w.__GUIDES__[0] };
}
function pickInserts(t) {
  const o = {};
  for (const k of INS) if (Array.isArray(t[k]) && t[k].length) o[k] = t[k];
  return o;
}
function mkTopic(t, extra) {
  return Object.assign({
    slug: t.slug, title: t.title,
    basic: t.basic || { status: "empty" },
    detailed: t.detailed || { status: "empty" },
    inserts: pickInserts(t), ref: null,
  }, extra);
}
/* base — тека, у якій лежить маніфест, відносно кореня репо (напр. "book/physics") */
function read(base, R) {
  const dirAbs = path.join(R, base);
  const js = path.join(dirAbs, "manifest.js"), json = path.join(dirAbs, "manifest.json");
  const file = fs.existsSync(json) ? json : js;
  if (!fs.existsSync(file)) throw new Error("нема маніфесту: " + base);
  const raw = loadRaw(file);
  const topics = [];

  /* D) новий manifest.json: groups -> chapters -> topics */
  if (raw.json) {
    const m = raw.json;
    for (const g of m.groups || []) for (const c of g.chapters || []) for (const t of c.topics || [])
      topics.push(mkTopic(t, { container: g.slug, containerTitle: g.title, chapter: c.slug,
        scope: g.scope || "", dir: base + "/" + t.slug }));
    return { form: "json7", file: file, kind: m.kind, slug: m.slug, title: m.title, topics: topics };
  }

  /* A) книжкова форма: sections -> topics */
  if (raw.book) {
    const m = raw.book;
    for (const s of m.sections || []) for (const t of s.topics || [])
      topics.push(mkTopic(t, { container: s.slug, containerTitle: s.title, chapter: null,
        scope: s.scope || "", dir: base + "/" + s.slug + "/" + t.slug }));
    return { form: "books", file: file, kind: m.type, slug: m.slug, title: m.title, topics: topics };
  }

  /* B/C) курс: modules -> chapters -> steps, або легасі sections -> topics */
  if (raw.guide) {
    const m = raw.guide;
    const mods = (m.modules && m.modules.length) ? m.modules : (m.sections || []);
    for (const mo of mods) {
      const groups = (mo.chapters && mo.chapters.length) ? mo.chapters
                   : [{ title: "", steps: mo.topics || mo.steps || [] }];
      for (const c of groups) for (const st of (c.steps || c.topics || [])) {
        if (st.ref) {                                   // крок-посилання: не переїжджає
          topics.push({ slug: null, title: st.title, ref: st.ref, dir: null,
            container: mo.slug, containerTitle: mo.title, chapter: c.title || null,
            scope: mo.scope || "", basic: null, detailed: null, inserts: {} });
          continue;
        }
        if (!st.slug) continue;
        topics.push(mkTopic(st, { container: mo.slug, containerTitle: mo.title, chapter: c.title || null,
          scope: mo.scope || "", dir: base + "/" + mo.slug + "/" + st.slug }));
      }
    }
    const form = (m.modules && m.modules.length) ? "guide" : "guide-legacy";
    return { form: form, file: file, kind: "course", slug: m.slug, title: m.title, topics: topics };
  }
  throw new Error("маніфест не зареєстрував ні книгу, ні курс: " + base);
}
module.exports = { read: read, INS: INS };
