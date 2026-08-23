/* Витяг для крос-книжних дублів (обсяги близькі): заголовки, вступ, кінцівка, вставки, фігури. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const c = JSON.parse(fs.readFileSync(path.join(__dirname, "collisions.json"), "utf8"));
const near = c.sameSlug.filter(function (x) {
  const w = x.items.map(i => i.words).filter(Boolean);
  return w.length >= 2 && Math.min.apply(null, w) / Math.max.apply(null, w) > 0.7;
});
function prose(t) { return t.replace(/```[\s\S]*?```/g, " ").replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
  .replace(/<preknowlist>[\s\S]*?<\/preknowlist>/g, " ").replace(/^[>*|#-]+\s*/gm, " ").replace(/\s+/g, " ").trim(); }
function info(rel) {
  const dir = path.join(R, rel), slug = rel.split("/").pop(), o = { rel: rel };
  const files = fs.existsSync(dir) ? fs.readdirSync(dir) : [];
  o.ins = files.filter(f => /^(hist|comp|math|proj|api)-/.test(f));
  o.figs = fs.existsSync(path.join(dir, "img")) ? fs.readdirSync(path.join(dir, "img")).length : 0;
  o.file = files.indexOf(slug + "-d.md") >= 0 ? slug + "-d.md" : (files.indexOf(slug + ".md") >= 0 ? slug + ".md" : null);
  if (!o.file) return o;
  const raw = fs.readFileSync(path.join(dir, o.file), "utf8");
  o.h1 = (raw.split("\n")[0] || "").replace(/^#\s*/, "");
  o.heads = raw.split("\n").filter(l => /^##\s/.test(l)).map(l => l.replace(/^##\s*/, ""));
  o.tabs = raw.indexOf(":::tabs") >= 0;
  const p = prose(raw.replace(/^#[^\n]*\n/, ""));
  o.words = p.split(" ").length; o.open = p.slice(0, 560); o.close = p.slice(-320);
  return o;
}
let s = "";
near.forEach(function (g, i) {
  s += "\n\n##### " + (i + 1) + ". " + g.key + "\n";
  g.items.forEach(function (it, k) {
    const a = info(it.path);
    s += "\n" + String.fromCharCode(65 + k) + ") " + it.path + "  [" + a.file + "] " + a.words + " сл, фігур " + a.figs + (a.tabs ? ", tabs" : "") + "\n";
    s += "H1: " + a.h1 + "\n";
    s += "H2: " + (a.heads.length ? a.heads.join(" | ") : "НЕМАЄ") + "\n";
    s += "вставки: " + (a.ins.length ? a.ins.join(", ") : "немає") + "\n";
    s += "ВСТУП: " + a.open + "\n";
    s += "КІНЕЦЬ: " + a.close + "\n";
  });
});
fs.writeFileSync(path.join(__dirname, "cross-digest.txt"), s, "utf8");
console.log("пар: " + near.length + "  → cross-digest.txt (" + Math.round(s.length / 1024) + " КБ)");
