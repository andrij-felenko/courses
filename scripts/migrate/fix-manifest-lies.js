/* Статус каже «написано», а файлу немає → повертаємо статус у pending.
   Правки робить наявний scripts/manifest-patch.js (він сам перепарсює й валідує). */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const R = path.resolve(__dirname, "../..");
const APPLY = process.argv.includes("--apply");
const l = JSON.parse(fs.readFileSync(path.join(__dirname, "manifest-lies.json"), "utf8"));
const all = l.ghosts.concat(l.lies);
const by = {};
all.forEach(function (r) { (by[r.manifest] = by[r.manifest] || []).push(r); });
const opsDir = path.join(__dirname, "ops");
fs.mkdirSync(opsDir, { recursive: true });
let total = 0;
for (const mf of Object.keys(by)) {
  const recs = by[mf];
  const ops = recs.map(function (r) {
    return (r.ver === "basic" || r.ver === "detailed")
      ? { op: "status", slug: r.slug, ver: r.ver, status: "pending" }
      : { op: "insert", slug: r.slug, type: r.ver, file: r.file, status: "pending" };
  });
  const name = mf.split("/").join("_").split("\\").join("_");
  const opsFile = path.join(opsDir, name + ".json");
  fs.writeFileSync(opsFile, JSON.stringify(ops, null, 2), "utf8");
  const args = [path.join(R, "scripts/manifest-patch.js"), path.join(R, mf), "--ops", opsFile];
  if (!APPLY) args.push("--dry");
  const r = cp.spawnSync(process.execPath, args, { cwd: R, encoding: "utf8" });
  const tail = (r.stdout || "").trim().split("\n").slice(-2).join(" | ");
  console.log((r.status === 0 ? "OK  " : "СТОП ") + mf + "   ops " + ops.length + "   " + tail);
  if (r.status !== 0) console.error((r.stderr || "").trim());
  total += ops.length;
}
console.log("\n" + (APPLY ? "застосовано" : "суха прогонка") + ": " + total + " статусів → pending");
