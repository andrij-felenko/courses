import { readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

const ROOT = "src";
const ADAPTER = join("src", "storage");                 // єдине легальне місце драйвера
const DRIVER = /^\s*import[^;]*\bfrom\s+["']pg["']/m;    // САМЕ import ... from "pg", не підрядок
const IGNORE = [/\.test\.ts$/, /[\\/]migrations[\\/]/];  // законні винятки — не наша межа
const ADR = "docs/adr/0007-telemetry-store.md";
const MODE = process.env.ARCH_MODE ?? "gate";            // warn | gate

function walk(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = join(dir, e.name);
    return e.isDirectory() ? walk(p) : [p];
  });
}

export function offenders(): string[] {
  return walk(ROOT)
    .filter((p) => p.endsWith(".ts") && !p.startsWith(ADAPTER))
    .filter((p) => !IGNORE.some((re) => re.test(p)))
    .filter((p) => DRIVER.test(readFileSync(p, "utf8")))
    .map((p) => relative(ROOT, p).replaceAll("\\", "/"))
    .sort();
}

export function report(fresh: string[]): void {
  console.error(`\nДрайвер БД імпортовано поза storage/ (${fresh.length}):`);
  fresh.forEach((p) => console.error("  src/" + p));
  console.error(`\n  Мощена дорога: TelemetryStore.energyByPeriod() — інтерфейс тримає базу замінною.`);
  console.error(`  Чому саме так:  ${ADR}\n`);
}
