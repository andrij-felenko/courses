/* Чи не суперечать інструкції тому, що робить newtopic.js насправді. */
const fs = require("fs");
const R = "E:/develop/courses/";
const files = [
  ".agents/rules/autonomy.md", ".agents/rules/pipeline.md", "agents/antigravity/pipeline.md",
  ".agents/agents/write-topic/agent.md", ".agents/agents/repair-topic/agent.md",
  ".agents/agents/check-all/agent.md", ".agents/workflows/write-batch.md", "AGENTS.md",
  "scripts/checks/16-promises.js", "scripts/claude/review-batch.js", "scripts/antigravity/newtopic.js",
];
const problems = [];
for (const f of files) {
  const s = fs.readFileSync(R + f, "utf8");
  const mentions = /newtopic/.test(s);
  if (!mentions) continue;
  const showsCmd = /newtopic\.js\s+--book/.test(s) || /newtopic\.js --book/.test(s);
  const hasAlso = /--also/.test(s);
  const hasMeets = /--meets|дві ознаки|ДВОХ|2 з 4|двох/.test(s);
  const crossBook = /--book math|ІНШУ книгу|іншої книги|ІНШОЮ книгою|чужої галузі/.test(s);
  const hasCap = /стел[яі]|дві нові теми|CAP/i.test(s);
  const oldBar = /(самостійне поняття, на яке стаття лише \*\*?спирається\*\*?\.\s*Ознака: про нього можна)/.test(s);
  const saysWritten = /--also <слуг (вже|уже) написаної/.test(s);
  if (showsCmd && !hasMeets) problems.push(`${f}: показує виклик БЕЗ --meets (агент дістане код 5)`);
  if (!hasMeets) problems.push(`${f}: не згадує планку «три ознаки з пʼяти»`);
  if (/обовʼязковий `--also|--also обов|без нього тему не візьм|Немає `--also`.*не буде/.test(s)) problems.push(`${f}: досі подає --also як обовʼязковий гейт`);
  /* у newtopic.js судимо сам перелік CRITERIA, а не історичний коментар про старі редакції */
  const bar = f.endsWith("newtopic.js") ? (s.split("const CRITERIA = {")[1] || "").split("};")[0] : s;
  if (/subject:|leaned:|з пʼяти ознак|три ознаки з/.test(bar)) problems.push(`${f}: досі несе стару планку (subject / leaned / пʼять ознак)`);
  if (!crossBook) problems.push(`${f}: не каже, що поняття чужої галузі йде в ІНШУ книгу`);
  if (saysWritten) problems.push(`${f}: вимагає «вже написану» тему в --also, а скрипт приймає й заплановану`);
  if (oldBar) problems.push(`${f}: стара, нижча планка теми (без умови «прийде не лише ця стаття»)`);
  console.log(`${f.padEnd(42)} команда:${showsCmd ? "є" : "—"}  2-з-4:${hasMeets ? "є" : "—"}  --also:${hasAlso ? "є" : "—"}  стеля:${hasCap ? "є" : "—"}`);
}

/* Чи згадані коди виходу справді ті, що в скрипті */
const nt = fs.readFileSync(R + "scripts/antigravity/newtopic.js", "utf8");
const codes = {};
for (const m of nt.matchAll(/refuse\("([a-z-]+)"[\s\S]{0,90}?\n\s*process\.exit\((\d)\)/g)) codes[m[1]] = m[2];
console.log("\nкоди відмов у скрипті: " + JSON.stringify(codes));
for (const [f, want] of [[".agents/rules/autonomy.md", { "код 5": /no-also|also-unknown/, "код 4": /cap/ }]]) {
  const s = fs.readFileSync(R + f, "utf8");
  if (/код 5/.test(s) && !(codes["few-criteria"] === "5")) problems.push(`${f}: обіцяє код 5, а скрипт дає інший`);
  if (/код 4/.test(s) && codes["cap"] !== "4") problems.push(`${f}: обіцяє код 4, а скрипт дає інший`);
}

console.log("\n" + (problems.length ? "ЗНАЙДЕНО РОЗБІЖНОСТЕЙ: " + problems.length : "✓ розбіжностей немає"));
problems.forEach((p) => console.log("  ✖ " + p));
