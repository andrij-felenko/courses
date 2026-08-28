import { readFileSync, writeFileSync, existsSync } from "node:fs";

const BASELINE = ".arch-baseline.json";
const found = offenders();

// перший запуск — заморожуємо наявне; білд лишається зеленим
if (!existsSync(BASELINE)) writeFileSync(BASELINE, JSON.stringify(found, null, 2));
const base: string[] = JSON.parse(readFileSync(BASELINE, "utf8"));
const baseSet = new Set(base);

const fresh = found.filter((p) => !baseSet.has(p));   // нове поза базою → червоне
const survived = found.filter((p) => baseSet.has(p)); // старе, ще не полагоджене

// ХРАПОВИК: щойно старе порушення зникло — база всихає й НАЗАД не росте
if (survived.length < base.length) writeFileSync(BASELINE, JSON.stringify(survived, null, 2));

if (fresh.length) {
  report(fresh);
  if (MODE === "gate") process.exit(1);               // у 'warn' друкуємо, але білд зелений
}
