/* Злиття семи пар-дублів. На кожну пару: переможець забирає ЛИШЕ ті вставки донора,
   що справді про інше (дублі за темою не тягнемо), разом із фігурами, які вони згадують.
   Проза донора зникає з диска — лишається в git-історії.
   Суха прогонка за замовчуванням; застосувати: --apply */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const R = path.resolve(__dirname, "../.."), APPLY = process.argv.includes("--apply");
const SKIP = new Set([".git", "node_modules", ".claude", ".github"]);

const PAIRS = [
  { win: "book/physics/electromagnetism/permittivity",
    die: "book/physics/electromagnetism/dielectric-constant",
    take: ["math-debye-relaxation.md", "proj-dielectric-sim.md"],
    why: "частотна релаксація Дебая й симулятор спектра — інше за Клаузіуса-Моссотті й вимірювач" },
  { win: "book/physics/condensed-matter-physics/ferroelectricity",
    die: "book/physics/electromagnetism/ferroelectrics",
    take: ["proj-hysteresis-sim.md"],
    why: "у переможця не було proj-вставки взагалі" },
  { win: "book/physics/electromagnetism/magnetic-monopole",
    die: "book/physics/electromagnetism/magnetic-monopole-theory",
    take: [],
    why: "усі три вставки донора дублюють наявні за темою" },
  { win: "book/physics/condensed-matter-physics/superconductivity",
    die: "book/physics/electromagnetism/superconductor",
    take: ["api-superconductor-parameters.md", "comp-josephson-junction.md"],
    why: "перехід Джозефсона окремо від SQUID; api-таблиці параметрів не було" },
  { win: "book/electronics/analog/integrator-differentiator",
    die: "book/electronics/analog/opamp-integrator-differentiator",
    take: ["hist-miller-integrator.md", "math-opamp-integrator-transfer.md"],
    why: "Міллер — інша історія за аналогову ЕОМ; math-вставки не було" },
  { win: "book/electronics/power-electronics/shockley-queisser-limit",
    die: "book/electronics/power-electronics/shockley-queisser",
    take: ["math-detailed-balance-derivation.md"],
    why: "вивід детального балансу — інше за інтеграл ефективності" },
];
/* Особливий випадок: слуг переможця, тіло донора — донорська тека переїжджає під ім'я переможця */
const SWAP = { win: "book/math/number-theory/quadratic-residues",
               die: "book/math/number-theory/quadratic-residue",
               why: "краще ім'я в першої, краще тіло й 10 фігур у другої" };

function figsOf(file) {                       // які img/*.svg згадує цей .md
  const t = fs.readFileSync(file, "utf8"), out = new Set();
  let i = 0; const tag = "img/";
  while ((i = t.indexOf(tag, i)) >= 0) {
    const j = t.indexOf(".svg", i);
    if (j > 0 && j - i < 90) out.add(t.slice(i + 4, j + 4));
    i += 4;
  }
  return [...out];
}
function git(args) { const r = cp.spawnSync("git", args, { cwd: R, encoding: "utf8" });
  if (r.status !== 0) { console.error("СТОП git " + args.join(" ") + ": " + (r.stderr || "").trim()); process.exit(1); } }
function walk(d, o) { for (const e of fs.readdirSync(d, { withFileTypes: true })) {
  const p = path.join(d, e.name);
  if (e.isDirectory()) { if (!SKIP.has(e.name)) walk(p, o) } else if (e.name.endsWith(".md")) o.push(p);
} return o; }

const plan = [];
for (const P of PAIRS) {
  const moves = [];
  for (const ins of P.take) {
    const src = path.join(R, P.die, ins);
    if (!fs.existsSync(src)) { console.error("СТОП нема вставки " + P.die + "/" + ins); process.exit(1); }
    moves.push([P.die + "/" + ins, P.win + "/" + ins]);
    for (const f of figsOf(src)) {
      const from = P.die + "/img/" + f;
      if (!fs.existsSync(path.join(R, from))) continue;
      let to = P.win + "/img/" + f;
      if (fs.existsSync(path.join(R, to))) to = P.win + "/img/" + f.replace(/\.svg$/, "-alt.svg");   // колізія імені
      moves.push([from, to]);
    }
  }
  plan.push({ P: P, moves: moves });
}

if (!APPLY) {
  for (const { P, moves } of plan) {
    console.log("\n" + path.basename(P.win) + "  <-  " + path.basename(P.die) + "   (" + P.why + ")");
    if (!moves.length) console.log("     переносів немає — донор просто зникає");
    moves.forEach(m => console.log("     " + m[0].split("/").pop() + "  ->  " + m[1].split("/").pop()));
  }
  console.log("\n" + path.basename(SWAP.win) + "  <=  ТІЛО " + path.basename(SWAP.die) + "   (" + SWAP.why + ")");
  console.log("\n(суха прогонка; --apply щоб виконати)");
  process.exit(0);
}

/* ── 1. звичайні шість ─────────────────────────────────────────────── */
for (const { P, moves } of plan) {
  for (const [a, b] of moves) git(["mv", a, b]);
  const OLD = "/" + P.die + "/", NEW = "/" + P.win + "/";
  for (const e of fs.readdirSync(path.join(R, P.win))) {
    if (!e.endsWith(".md")) continue;
    const p = path.join(R, P.win, e), s = fs.readFileSync(p, "utf8");
    if (s.indexOf(OLD) < 0) continue;
    fs.writeFileSync(p, s.split(OLD).join(NEW), "utf8");
  }
  git(["rm", "-r", "-q", P.die]);
  console.log("злито: " + path.basename(P.win) + "  <-  " + path.basename(P.die) + "   (перенесено " + moves.length + ")");
}

/* ── 2. обмін тілами для квадратичних лишків ───────────────────────── */
{
  const winSlug = path.basename(SWAP.win), dieSlug = path.basename(SWAP.die);
  git(["rm", "-r", "-q", SWAP.win]);
  git(["mv", SWAP.die, SWAP.win]);
  git(["mv", SWAP.win + "/" + dieSlug + "-d.md", SWAP.win + "/" + winSlug + "-d.md"]);
  const OLD = "/" + SWAP.die + "/", NEW = "/" + SWAP.win + "/";
  for (const e of fs.readdirSync(path.join(R, SWAP.win))) {
    if (!e.endsWith(".md") && !e.endsWith(".py")) continue;
    const p = path.join(R, SWAP.win, e), s = fs.readFileSync(p, "utf8");
    if (s.indexOf(OLD) < 0) continue;
    fs.writeFileSync(p, s.split(OLD).join(NEW), "utf8");
  }
  console.log("обмін тілами: " + winSlug + "  <=  " + dieSlug);
}

/* ── 3. лінки: слуг донора → слуг переможця ────────────────────────── */
const MAPL = PAIRS.map(P => [path.basename(P.die), path.basename(P.win)]).concat([[path.basename(SWAP.die), path.basename(SWAP.win)]]);
const pairsOut = []; let nl = 0, nf = 0;
for (const f of walk(R, [])) {
  const s = fs.readFileSync(f, "utf8"); let out = s, hit = 0;
  for (const [dieSlug, winSlug] of MAPL) {
    const tail = "/" + dieSlug + ")";
    let cur = out, acc = "", from = 0, i;
    while ((i = cur.indexOf(tail, from)) >= 0) {
      const st = cur.lastIndexOf("](", i), h = st < 0 ? "" : cur.slice(st, i);
      const book = h.indexOf("](book:") === 0 ? h.slice(7) : null;
      if (book !== null && book.indexOf("/") < 0 && book.length) {
        acc += cur.slice(from, st) + "](book:" + book + "/" + winSlug + ")"; hit++;
        pairsOut.push({ from: book + "/" + dieSlug, to: book + "/" + winSlug, file: path.relative(R, f) });
      } else acc += cur.slice(from, i + tail.length);
      from = i + tail.length;
    }
    out = acc + cur.slice(from);
  }
  if (!hit) continue;
  fs.writeFileSync(f, out, "utf8"); nl += hit; nf++;
}
console.log("лінків перецілено: " + nl + " у " + nf + " файлах");
const dst = path.join(__dirname, "link-changes.json");
const prev = fs.existsSync(dst) ? JSON.parse(fs.readFileSync(dst, "utf8")) : [];
fs.writeFileSync(dst, JSON.stringify(prev.concat(pairsOut), null, 2) + "\n", "utf8");
console.log("пар у link-changes.json: " + (prev.length + pairsOut.length));
