/* scripts/recheck-build.js — генерує самодостатній воркфлоу scripts/recheck-run.js
   із ВБУДОВАНИМ батчем (обхід ліміту розміру args воркфлоу-тулзи).
   Запуск:  node scripts/recheck-build.js <book> [start=0] [count=5]
   Потім:   Workflow scriptPath="scripts/recheck-run.js"  (БЕЗ args). */
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const book = process.argv[2] || "algorithms";
const start = parseInt(process.argv[3] || "0", 10);
const count = parseInt(process.argv[4] || "5", 10);

const raw = execFileSync("node", [path.join(__dirname, "recheck-index.js"), book], { encoding: "utf8", maxBuffer: 1 << 26 });
const d = JSON.parse(raw);
const queue = d.queue[book] || [];
const topics = queue.slice(start, start + count);
if (!topics.length) { console.error(`Немає recheck-тем у "${book}" з offset ${start}.`); process.exit(2); }

const EMBED = { book, topics, index: d.index };
const tmpl = fs.readFileSync(path.join(__dirname, "recheck-audit.js"), "utf8");
if (!tmpl.includes("/*__EMBED__*/")) { console.error("У шаблоні recheck-audit.js немає маркера /*__EMBED__*/"); process.exit(3); }
const out = tmpl.replace("/*__EMBED__*/", "const EMBED = " + JSON.stringify(EMBED) + ";");
fs.writeFileSync(path.join(__dirname, "recheck-run.js"), out);

console.log(`wrote scripts/recheck-run.js — book=${book} start=${start} count=${topics.length} (queue total ${queue.length})`);
console.log("batch: " + topics.map(t => t.section + "/" + t.slug).join(", "));
