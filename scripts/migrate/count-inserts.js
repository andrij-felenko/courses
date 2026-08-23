/* Рахує ВСІ обʼєкти-вставки в маніфесті на будь-якій глибині + скільки з них видно читачу
   (тобто лежать плоским масивом на рівні теми) + скільки файлів реально є на диску. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const INS = ["hist", "comp", "math", "proj", "api"];
const KINDS = { book: ["physics","math","electronics","programming","communications","algorithms","philosophy"],
  catalog: ["boards","connect","sensors","power","actuators","instruments","components"],
  reference: ["unix-linux","cpp-standards","build-systems","media-vision","qgroundcontrol"] };
function parse(f){const w={__BOOKS__:[]};new Function("window",fs.readFileSync(f,"utf8"))(w);return w.__BOOKS__[0]}
function deepFiles(node, acc) {
  if (!node || typeof node !== "object") return acc;
  if (Array.isArray(node)) { node.forEach(function (x) { deepFiles(x, acc) }); return acc; }
  if (typeof node.file === "string") acc.push(node.file);
  Object.keys(node).forEach(function (k) { if (k !== "file" && k !== "status") deepFiles(node[k], acc) });
  return acc;
}
let deep = 0, flat = 0, disk = 0;
for (const [kind, slugs] of Object.entries(KINDS)) for (const s of slugs) {
  const m = parse(path.join(R, kind, s, "manifest.js")); if (!m) continue;
  for (const sec of m.sections || []) for (const t of sec.topics || []) {
    deep += deepFiles(t, []).length;
    for (const k of INS) for (const i of (Array.isArray(t[k]) ? t[k] : [])) {
      if (typeof i.file !== "string") continue;
      flat++;
      if (fs.existsSync(path.join(R, kind, s, sec.slug, t.slug, i.file))) disk++;
    }
  }
}
console.log("вставок усього (будь-яка глибина): " + deep);
console.log("видно читачу (плоско на темі):     " + flat + "   з них файл є на диску: " + disk);
console.log("НЕВИДИМИХ:                         " + (deep - flat));
