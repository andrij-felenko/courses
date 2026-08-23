/* Перецілення лінків на прибраних двійників → на вцілілу статтю.
   Пише пари в scripts/migrate/link-changes.json (накопичувально — таблиця пар).
   Суха прогонка за замовчуванням; застосувати: --apply
   Свідомо БЕЗ регексів: рядкові операції не залежать від рівня екранування. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const APPLY = process.argv.includes("--apply");
const SKIP = new Set([".git", "node_modules", ".claude", ".github"]);
const OPEN = "](";

const MAP = [
  ["gaussian-distribution",     "book:math/normal-distribution"],
  ["central-limit-theorem",     "book:math/central-limit"],
  ["chernoff-bound",            "book:algorithms/chernoff-bound"],
  ["galois-field",              "book:math/finite-fields"],
  ["bipartite-graph",           "book:algorithms/bipartite-graph"],
  ["lambert-w-function",        "book:math/lambert-w"],
  ["kelvin-double-bridge",      "book:electronics/kelvin-bridge"],
  ["retro-reflector",           "book:physics/retroreflector"],
  ["alignment",                 "book:programming/memory-alignment"],
  ["context-switching",         "book:programming/context-switch"],
  ["trust-boundaries-failsafe", "book:programming/trust-boundaries"],
  ["coroutines",                "book:cpp-standards/coroutines"],
  ["gpu-command-submission",    "book:unix-linux/gpu-command-submission"],
  ["travelling-salesman",       "book:algorithms/traveling-salesperson-problem"],
  ["stereo-vision",             "guide:embedded/stereo-vision"],
  ["audit-subsystem",           "book:unix-linux/audit-framework"],
];
/* shot-noise прибрано лише в electronics — у physics лишається під тим самим слугом */
const EXACT = [["book:electronics/shot-noise", "book:physics/shot-noise"]];

function walk(d, o) { for (const e of fs.readdirSync(d, { withFileTypes: true })) {
  const p = path.join(d, e.name);
  if (e.isDirectory()) { if (!SKIP.has(e.name)) walk(p, o) } else if (e.name.endsWith(".md")) o.push(p);
} return o; }

/* Замінює ](book:БУДЬ-ЯКА-КНИГА/slug) на ](target). Книга — один сегмент без "/". */
function retargetBySlug(text, slug, target, tally) {
  const tail = "/" + slug + ")";
  let out = "", from = 0, i;
  while ((i = text.indexOf(tail, from)) >= 0) {
    const start = text.lastIndexOf(OPEN, i);
    const head = start < 0 ? null : text.slice(start, i);            // "](book:math"
    const okPrefix = head !== null && head.indexOf("](book:") === 0;
    const bookPart = okPrefix ? head.slice(7) : "";                  // "math"
    const okBook = bookPart.length > 0 && bookPart.indexOf("/") < 0 && bookPart.indexOf(" ") < 0;
    const already = okPrefix && okBook && (head.slice(2) + "/" + slug) === target;
    if (okPrefix && okBook && !already) {
      out += text.slice(from, start) + OPEN + target + ")";
      tally.push({ from: head.slice(2) + "/" + slug, to: target });
    } else {
      out += text.slice(from, i + tail.length);
    }
    from = i + tail.length;
  }
  return out + text.slice(from);
}

const files = walk(R, []);
const pairs = [], counts = {};
let nFiles = 0, nHits = 0;
for (const f of files) {
  const src = fs.readFileSync(f, "utf8");
  let out = src; const tally = [];
  for (const [slug, target] of MAP) out = retargetBySlug(out, slug, target, tally);
  for (const [from, to] of EXACT) {
    const needle = OPEN + from + ")";
    while (out.indexOf(needle) >= 0) { out = out.replace(needle, OPEN + to + ")"); tally.push({ from: from, to: to }); }
  }
  if (!tally.length) continue;
  nFiles++; nHits += tally.length;
  tally.forEach(t => { counts[t.from] = (counts[t.from] || 0) + 1; pairs.push({ from: t.from, to: t.to, file: path.relative(R, f) }); });
  if (APPLY) fs.writeFileSync(f, out, "utf8");
}
console.log((APPLY ? "перецілено" : "до перецілення") + ": " + nHits + " лінків у " + nFiles + " файлах");
Object.entries(counts).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => console.log("   " + String(v).padStart(3) + "  " + k));
if (APPLY) {
  const dst = path.join(__dirname, "link-changes.json");
  const prev = fs.existsSync(dst) ? JSON.parse(fs.readFileSync(dst, "utf8")) : [];
  fs.writeFileSync(dst, JSON.stringify(prev.concat(pairs), null, 2) + "\n", "utf8");
  console.log("пари дописано в link-changes.json (усього " + (prev.length + pairs.length) + ")");
}
