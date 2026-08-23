/* Витяг для розсуду колізій: на кожну групу — шляхи, обсяги і перші рядки прози. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const c = JSON.parse(fs.readFileSync(path.join(__dirname, "collisions.json"), "utf8"));
function excerpt(dirRel, slug, n) {
  for (const f of [slug + "-d.md", slug + ".md"]) {
    const p = path.join(R, dirRel, f);
    if (!fs.existsSync(p)) continue;
    let t = fs.readFileSync(p, "utf8");
    t = t.replace(/^#[^\n]*\n/, "").replace(/<preknowlist>[\s\S]*?<\/preknowlist>/g, "")
         .replace(/```[\s\S]*?```/g, " ").replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
         .replace(/^[>*|#-]+\s*/gm, "").replace(/\s+/g, " ").trim();
    return t.slice(0, n);
  }
  return "(немає файлу)";
}
const groups = [...c.sameSlug, ...c.sameTitle].filter(g => {
  const w = g.items.map(i => i.words);
  return !w.some(v => v === 0);                       // порожні вже відсіяно локально
});
let out = "";
groups.forEach((g, i) => {
  out += "\n### " + (i + 1) + ". [" + g.kind + "] " + g.key + "\n";
  g.items.forEach(it => {
    const slug = it.slug || g.key;
    out += "  • " + it.path + "   (" + it.words + " сл)" + (it.title ? "  «" + it.title + "»" : "") + "\n";
    out += "     " + excerpt(it.path, slug, 340) + "\n";
  });
});
fs.writeFileSync(path.join(__dirname, "collision-digest.txt"), out, "utf8");
console.log("груп на розсуд: " + groups.length + "   → scripts/migrate/collision-digest.txt (" + Math.round(out.length/1024) + " КБ)");
