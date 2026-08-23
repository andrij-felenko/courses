/* Резолв колізій: прибирає з маніфестів ПОРОЖНІ записи-двійники (теки на диску немає).
   Диска не чіпає — лише рядок у маніфесті. Суха прогонка за замовчуванням; застосувати: --apply
   Верифікація: маніфест перечитується після правки — має зникнути рівно N тем і жодної зайвої. */
const NL = String.fromCharCode(10);
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const APPLY = process.argv.includes("--apply");

const DROP = [
  ["book/math",            "lambert-w-function",        "лишається lambert-w"],
  ["book/math",            "gaussian-distribution",     "лишається normal-distribution"],
  ["book/math",            "central-limit-theorem",     "лишається central-limit (написана)"],
  ["book/math",            "chernoff-bound",            "написана в algorithms"],
  ["book/math",            "galois-field",              "написана в algorithms як finite-fields"],
  ["book/math",            "bipartite-graph",           "написана в algorithms"],
  ["book/electronics",     "kelvin-double-bridge",      "лишається kelvin-bridge"],
  ["book/electronics",     "shot-noise",                "написана у physics"],
  ["book/electronics",     "retro-reflector",           "написана у physics як retroreflector"],
  ["book/programming",     "alignment",                 "лишається memory-alignment (написана)"],
  ["book/programming",     "context-switching",         "лишається context-switch (написана)"],
  ["book/programming",     "trust-boundaries-failsafe",  "лишається trust-boundaries (написана)"],
  ["book/programming",     "coroutines",                "написана в cpp-standards"],
  ["book/programming",     "gpu-command-submission",    "написана в unix-linux"],
  ["book/algorithms",      "travelling-salesman",       "лишається traveling-salesperson-problem"],
  ["book/algorithms",      "stereo-vision",             "порожній запис-двійник"],
  ["book/algorithms",      "where-next",                "службова «Куди далі», порожня"],
  ["reference/unix-linux", "audit-subsystem",           "лишається audit-framework (написана)"],
];

/* Вирізає запис теми з маніфесту в ОБОХ форматах:
   компактний однорядковий  { slug: "x", ... },
   розгорнутий JSON-стиль    {
  "slug": "x",
  ... 
},                         */
function cutTopic(src, slug) {
  const lines = src.split(NL);
  const n1 = 'slug: "' + slug + '"', n2 = '"slug": "' + slug + '"';
  const hits = [];
  lines.forEach(function (L, i) { if (L.indexOf(n1) >= 0 || L.indexOf(n2) >= 0) hits.push(i); });
  if (hits.length !== 1) return { err: "рядків із цим слугом: " + hits.length };
  const i = hits[0], L = lines[i].trim();
  if (L.charAt(0) === "{" && L.slice(-2) === "},") { lines.splice(i, 1); return { src: lines.join(NL) }; }
  // розгорнутий: назад до рядка-відкривача, далі вперед з лічильником дужок
  let open = -1;
  for (let k = i; k >= 0 && i - k < 6; k--) if (lines[k].trim().slice(-1) === "{") { open = k; break; }
  if (open < 0) return { err: "не знайдено відкривача блоку" };
  let depth = 0, close = -1;
  for (let k = open; k < lines.length && k - open < 200; k++) {
    for (const ch of lines[k]) { if (ch === "{") depth++; else if (ch === "}") depth--; }
    if (depth === 0) { close = k; break; }
  }
  if (close < 0) return { err: "не зійшлися дужки блоку" };
  lines.splice(open, close - open + 1);
  return { src: lines.join(NL) };
}

function parse(file) { const w = { __BOOKS__: [] };
  new Function("window", fs.readFileSync(file, "utf8"))(w); return w.__BOOKS__[0]; }
function topics(m) { const o = []; for (const s of m.sections || []) for (const t of s.topics || []) o.push(s.slug + "/" + t.slug); return o; }

let ok = 0, skip = 0;
const byBook = {};
for (const [book, slug, why] of DROP) (byBook[book] = byBook[book] || []).push([slug, why]);

for (const [book, list] of Object.entries(byBook)) {
  const file = path.join(R, book, "manifest.js");
  const before = parse(file), setB = new Set(topics(before));
  let src = fs.readFileSync(file, "utf8"), removed = [];
  for (const [slug, why] of list) {
    const onDisk = (before.sections || []).some(s => (s.topics || []).some(t =>
      t.slug === slug && fs.existsSync(path.join(R, book, s.slug, slug))));
    if (onDisk) { console.log("  ПРОПУСК " + book + "/" + slug + " — тека на диску Є, це не порожній двійник"); skip++; continue; }
    const cut = cutTopic(src, slug);
    if (cut.err) { console.log("  ПРОПУСК " + book + "/" + slug + " — " + cut.err); skip++; continue; }
    src = cut.src;
    removed.push(slug + "   — " + why);
  }
  if (!removed.length) continue;
  if (!APPLY) { console.log(book + ":  прибрати " + removed.length); removed.forEach(function (r) { console.log("     " + r) }); ok += removed.length; continue; }
  const tmp = file + ".tmp"; fs.writeFileSync(tmp, src, "utf8");
  let after; try { after = parse(tmp) } catch (e) { fs.unlinkSync(tmp); console.error("СТОП " + book + ": маніфест не парситься — відкат"); process.exit(1) }
  const setA = new Set(topics(after));
  const gone = [].concat([...setB]).filter(function (x) { return !setA.has(x) });
  const added = [].concat([...setA]).filter(function (x) { return !setB.has(x) });
  if (gone.length !== removed.length || added.length) {
    fs.unlinkSync(tmp); console.error("СТОП " + book + ": очікували -" + removed.length + ", вийшло -" + gone.length + " +" + added.length + " — відкат"); process.exit(1);
  }
  fs.renameSync(tmp, file);
  console.log("OK " + book + ":  -" + removed.length + " тем"); removed.forEach(function (r) { console.log("     " + r) });
  ok += removed.length;
}
console.log("\n" + (APPLY ? "прибрано" : "до прибирання") + ": " + ok + (skip ? "   пропущено: " + skip : ""));
