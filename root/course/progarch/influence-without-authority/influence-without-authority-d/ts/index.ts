import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const ADAPTER = join("src", "storage");     // єдине легальне місце для драйвера БД
const DRIVER = /\bfrom\s+["']pg["']/;       // import ... from "pg"

function walk(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = join(dir, e.name);
    return e.isDirectory() ? walk(p) : [p];
  });
}

const offenders = walk("src")
  .filter((p) => p.endsWith(".ts") && !p.startsWith(ADAPTER))
  .filter((p) => DRIVER.test(readFileSync(p, "utf8")));

if (offenders.length) {
  console.error("Драйвер БД імпортовано поза storage/:\n  " + offenders.join("\n  "));
  console.error("Ходи через TelemetryStore.energyByPeriod() — інтерфейс тримає базу замінною.");
  process.exit(1);            // білд червоний: правило тримає перевірка, не людина
}
