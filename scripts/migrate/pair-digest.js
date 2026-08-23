/* Порівняльний витяг для 9 пар-дублів: заголовки, вступ, кінцівка, вставки, фігури, обсяг.
   Мета — судити ЯКІСТЬ і ПОКРИТТЯ, не читаючи 40 тис. слів. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const PAIRS = [
  ["book/physics/electromagnetism/dielectric-constant", "book/physics/electromagnetism/permittivity"],
  ["book/physics/electromagnetism/ferroelectrics", "book/physics/condensed-matter-physics/ferroelectricity"],
  ["book/physics/electromagnetism/magnetic-monopole", "book/physics/electromagnetism/magnetic-monopole-theory"],
  ["book/physics/electromagnetism/superconductor", "book/physics/condensed-matter-physics/superconductivity"],
  ["book/physics/condensed-matter-physics/shot-noise", "book/physics/condensed-matter-physics/shot-flicker-noise"],
  ["book/math/number-theory/quadratic-residues", "book/math/number-theory/quadratic-residue"],
  ["book/electronics/analog/opamp-integrator-differentiator", "book/electronics/analog/integrator-differentiator"],
  ["book/electronics/power-electronics/shockley-queisser-limit", "book/electronics/power-electronics/shockley-queisser"],
  ["reference/unix-linux/processes/rcu-read-copy-update", "reference/unix-linux/devices/rcu-mechanism"],
];
function prose(t) {
  return t.replace(/```[\s\S]*?```/g, " ").replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
          .replace(/^[>*|#-]+\s*/gm, " ").replace(/\s+/g, " ").trim();
}
function info(rel) {
  const dir = path.join(R, rel), slug = rel.split("/").pop();
  const out = { rel: rel, slug: slug };
  const files = fs.existsSync(dir) ? fs.readdirSync(dir) : [];
  out.inserts = files.filter(function (f) { return /^(hist|comp|math|proj|api)-/.test(f); });
  out.figs = fs.existsSync(path.join(dir, "img")) ? fs.readdirSync(path.join(dir, "img")).length : 0;
  const main = files.indexOf(slug + "-d.md") >= 0 ? slug + "-d.md" : (files.indexOf(slug + ".md") >= 0 ? slug + ".md" : null);
  out.file = main;
  if (!main) return out;
  const raw = fs.readFileSync(path.join(dir, main), "utf8");
  out.h1 = (raw.split("\n")[0] || "").replace(/^#\s*/, "");
  out.heads = raw.split("\n").filter(function (l) { return /^##\s/.test(l); }).map(function (l) { return l.replace(/^##\s*/, "") });
  const p = prose(raw.replace(/^#[^\n]*\n/, ""));
  out.words = p.split(" ").length;
  out.open = p.slice(0, 700);
  out.close = p.slice(-450);
  out.hasFormula = /\$|`[^`]*=[^`]*`/.test(raw);
  out.hasTabs = raw.indexOf(":::tabs") >= 0;
  return out;
}
let s = "";
PAIRS.forEach(function (pr, i) {
  s += "\n\n===== ПАРА " + (i + 1) + " =====\n";
  pr.forEach(function (rel, k) {
    const a = info(rel);
    s += "\n--- " + String.fromCharCode(65 + k) + ") " + rel + "   [" + a.file + "]  " + a.words + " сл   фігур " + a.figs +
         (a.hasFormula ? "  формули" : "") + (a.hasTabs ? "  tabs" : "") + "\n";
    s += "H1: " + a.h1 + "\n";
    s += "Розділи: " + (a.heads.length ? a.heads.join(" | ") : "(немає H2)") + "\n";
    s += "Вставки: " + (a.inserts.length ? a.inserts.join(", ") : "немає") + "\n";
    s += "ВСТУП: " + a.open + "\n";
    s += "КІНЕЦЬ: " + a.close + "\n";
  });
});
fs.writeFileSync(path.join(__dirname, "pair-digest.txt"), s, "utf8");
console.log("написано pair-digest.txt (" + Math.round(s.length / 1024) + " КБ), пар: " + PAIRS.length);
