/* Нормалізація маніфестів book/catalog/reference:
   (1) ПІДІЙМАЄ вставки, помилково вкладені в basic/detailed, на рівень теми
       (їх читач не бачить узагалі — 1273 написані файли лежать мертвим вантажем);
   (2) зводить обидва формати (компактний і розгорнутий JSON) до одного канонічного v6.
   Гарантія: результат перепарсюється й ГЛИБОКО звіряється з очікуваним обʼєктом; інакше — відкат.
   Суха прогонка за замовчуванням; застосувати: --apply */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const APPLY = process.argv.includes("--apply");
const NL = String.fromCharCode(10);
const INS = ["hist", "comp", "math", "proj", "api"];
const KINDS = {
  book: ["physics", "math", "electronics", "programming", "communications", "algorithms", "philosophy"],
  catalog: ["boards", "connect", "sensors", "power", "actuators", "instruments", "components"],
  reference: ["unix-linux", "cpp-standards", "build-systems", "media-vision", "qgroundcontrol"],
};

function parse(src) { const w = { __BOOKS__: [] }; new Function("window", src)(w); return w.__BOOKS__[0]; }

/* Рекурсивний збір вставок: manifest-patch колись вкладав нову вставку ВСЕРЕДИНУ попередньої
   (hist → math → proj → hist → ...) і всередину basic/detailed. Читач такого не бачить узагалі.
   Тут ми обходимо всю піддерево теми, збираємо кожен {file,status} із типом, під яким він лежав,
   і перезбираємо плоскі масиви на рівні теми (дедуп за файлом, перший статус виграє). */
function collect(node, type, out) {
  if (typeof node.file === "string") out.push({ type: type, file: node.file, status: node.status });
  for (const k of Object.keys(node)) {
    if (k === "file" || k === "status") continue;
    if (INS.indexOf(k) >= 0) {
      const arr = Array.isArray(node[k]) ? node[k] : [node[k]];
      for (const it of arr) if (it && typeof it === "object") collect(it, k, out);
    }
    delete node[k];
  }
}
function lift(m) {
  let moved = 0;
  for (const sec of m.sections || []) for (const t of sec.topics || []) {
    const out = [];
    let deep = false;
    for (const v of ["basic", "detailed"]) {
      const o = t[v]; if (!o) continue;
      for (const k of Object.keys(o)) {
        if (k === "status") continue;
        deep = true;
        if (INS.indexOf(k) >= 0) {
          const arr = Array.isArray(o[k]) ? o[k] : [o[k]];
          for (const it of arr) if (it && typeof it === "object") collect(it, k, out);
        }
        delete o[k];
      }
    }
    for (const k of INS) {
      if (!t[k]) continue;
      const arr = Array.isArray(t[k]) ? t[k] : [t[k]];
      const before = out.length;
      for (const it of arr) if (it && typeof it === "object") collect(it, k, out);
      if (out.length - before > arr.length) deep = true;
      delete t[k];
    }
    if (!out.length) continue;
    const seen = {};
    for (const r of out) {
      const key = r.type + "|" + r.file;
      if (seen[key]) continue;
      seen[key] = 1;
      t[r.type] = t[r.type] || [];
      t[r.type].push({ file: r.file, status: typeof r.status === "string" ? r.status : "pending" });
    }
    if (deep) moved += out.length;
  }
  return moved;
}

/* мертві поля схеми v4 (у v5 їх прибрали): topic.status, topic.levels, topic.origin */
const DEAD = ["status", "levels", "origin"];
function stripLegacy(m) {
  let n = 0;
  for (const sec of m.sections || []) for (const t of sec.topics || [])
    for (const k of DEAD) if (Object.prototype.hasOwnProperty.call(t, k)) { delete t[k]; n++; }
  return n;
}

const q = function (s) { return JSON.stringify(String(s)); };
function serTopic(t) {
  const p = [];
  p.push("slug: " + q(t.slug));
  p.push("title: " + q(t.title));
  for (const v of ["basic", "detailed"]) if (t[v]) p.push(v + ": { status: " + q(t[v].status) + " }");
  const keys = INS.concat(Object.keys(t).filter(function (k) {
    return ["slug", "title", "basic", "detailed"].indexOf(k) < 0 && INS.indexOf(k) < 0; }));
  for (const k of keys) {
    if (!t[k]) continue;
    if (!Array.isArray(t[k])) { p.push(k + ": " + JSON.stringify(t[k])); continue; }
    if (!t[k].length) { p.push(k + ": []"); continue; }   // порожній масив зберігаємо як є
    const isIns = t[k].every(function (i) { return i && typeof i === "object" && typeof i.file === "string"; });
    if (!isIns) { p.push(k + ": " + JSON.stringify(t[k])); continue; }   // не вставки — дослівно
    p.push(k + ": [" + t[k].map(function (i) {
      return "{ file: " + q(i.file) + ", status: " + q(i.status) + " }"; }).join(", ") + "]");
  }
  return "        { " + p.join(", ") + " },";
}
function serialize(head, m) {
  const L = [];
  L.push(head.replace(/\s*$/, ""));
  L.push("(window.__BOOKS__ = window.__BOOKS__ || []).push({");
  L.push("  type: " + q(m.type) + ", slug: " + q(m.slug) + ", title: " + q(m.title) + (m.subtitle ? ", subtitle: " + q(m.subtitle) : "") + ",");
  L.push("  sections: [");
  for (const sec of m.sections || []) {
    L.push("    { slug: " + q(sec.slug) + ", title: " + q(sec.title) + ", scope: " + q(sec.scope || "") + ",");
    L.push("      topics: [");
    for (const t of sec.topics || []) L.push(serTopic(t));
    L.push("      ] },");
  }
  L.push("  ]");
  L.push("});");
  return L.join(NL) + NL;
}

/* звірка НЕ чутлива до порядку ключів: масиви лишаються впорядкованими, обʼєкти канонізуються */
function canon(x) {
  if (Array.isArray(x)) return x.map(canon);
  if (x && typeof x === "object") {
    const o = {};
    Object.keys(x).sort().forEach(function (k) { o[k] = canon(x[k]); });
    return o;
  }
  return x;
}
function deepEq(a, b) { return JSON.stringify(canon(a)) === JSON.stringify(canon(b)); }

let totLift = 0, totBooks = 0, totDead = 0;
for (const [kind, slugs] of Object.entries(KINDS)) for (const s of slugs) {
  const file = path.join(R, kind, s, "manifest.js");
  const src = fs.readFileSync(file, "utf8");
  const m = parse(src); if (!m) continue;
  const cut = src.indexOf("(window.__BOOKS__");
  const head = cut > 0 ? src.slice(0, cut) : "/* manifest */" + NL;
  const n = lift(m);
  const dead = stripLegacy(m);
  const out = serialize(head, m);
  const back = parse(out);
  if (!back || !deepEq(back, m)) {
    console.error("СТОП " + kind + "/" + s + ": результат не збігається з очікуваним — не чіпаю");
    // показати ПЕРШУ розбіжність, щоб було що лагодити
    outer: for (let a = 0; a < (m.sections || []).length; a++) {
      const S1 = m.sections[a], S2 = (back.sections || [])[a] || { topics: [] };
      for (let b2 = 0; b2 < (S1.topics || []).length; b2++) {
        const T1 = S1.topics[b2], T2 = (S2.topics || [])[b2];
        if (!deepEq(T1, T2)) {
          console.error("   перша розбіжність: " + S1.slug + "/" + T1.slug);
          console.error("     очікували: " + JSON.stringify(canon(T1)).slice(0, 260));
          console.error("     вийшло:    " + JSON.stringify(canon(T2)).slice(0, 260));
          break outer;
        }
      }
    }
    continue;
  }
  let topics = 0; for (const sec of m.sections || []) topics += (sec.topics || []).length;
  if (n) { totLift += n; totBooks++; }
  totDead += dead;
  console.log((n ? "піднято " + String(n).padStart(4) : "  чисто    ") + "   " + (kind + "/" + s).padEnd(24) +
    "тем " + String(topics).padStart(4) + (dead ? "   мертвих полів −" + dead : "") + (APPLY ? "   записано" : ""));
  if (APPLY) fs.writeFileSync(file, out, "utf8");
}
console.log((APPLY ? NL + "ПІДНЯТО" : NL + "до підняття") + ": " + totLift + " вставок у " + totBooks + " книгах;   мертвих полів v4 прибрано: " + totDead);
