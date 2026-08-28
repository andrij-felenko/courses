// arch/boundary.test.ts — сторож ADR-021. Ганяється в CI на кожен PR:  node --test
// Кодує розкрій: ядро не імпортує нутрощі винесених сервісів,
// а телеметрію/відео чіпає лише через порт і спільні контракти.
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";
import assert from "node:assert/strict";

const SRC = join(fileURLToPath(new URL(".", import.meta.url)), "..", "src");

type Zone = "core" | "telemetry" | "video" | "ports" | "contracts";
const ZONES: Zone[] = ["core", "telemetry", "video", "ports", "contracts"];

// Кожен модуль належить зоні за верхньою текою під src/.
const zoneOf = (rel: string): Zone | null =>
  ZONES.find((z) => rel === z || rel.startsWith(z + "/")) ?? null;

// Дозволені напрямки залежності. Чого тут немає — заборонено. Це та сама таблиця,
// що й на малюнку: ядро й сервіси — лише до портів/контрактів, не одне в одного.
const ALLOWED: Record<Zone, Zone[]> = {
  core:      ["ports", "contracts"],   // ядро — лише крізь порти й контракти
  telemetry: ["ports", "contracts"],   // винесений сервіс не лазить у ядро
  video:     ["ports", "contracts"],
  ports:     ["contracts"],            // порт — чистий інтерфейс над контрактами
  contracts: [],                       // контракти нікого не тягнуть
};

// Усі *.ts під src/ (шлях відносно src/, прямі слеші), крім самих тестів.
function sources(dir = SRC, base = ""): string[] {
  const out: string[] = [];
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const rel = base ? base + "/" + e.name : e.name;
    if (e.isDirectory()) out.push(...sources(join(dir, e.name), rel));
    else if (e.name.endsWith(".ts") && !e.name.endsWith(".test.ts")) out.push(rel);
  }
  return out;
}

// Крос-зонні імпорти йдуть через аліас "@dh/<zone>/…" (глибокі "../" крізь зони
// заборонені окремим lint-правилом — тож досить ловити аліас).
const CROSS = /from\s+["'`]@dh\/([\w-]+)/g;

test("ADR-021: ядро не імпортує нутрощі винесених сервісів", () => {
  const breaches: string[] = [];
  for (const file of sources()) {
    const from = zoneOf(file);
    if (!from) continue;
    const code = readFileSync(join(SRC, file), "utf8");
    for (const [, target] of code.matchAll(CROSS)) {
      const to = zoneOf(target);
      if (!to || to === from) continue;                 // своя зона — вільно
      if (!ALLOWED[from].includes(to))
        breaches.push(`${file}  →  @dh/${target}   (${from} ✗ ${to})`);
    }
  }
  assert.deepEqual(breaches, [],
    "Розкрій ADR-021 пробито:\n  " + breaches.join("\n  "));
});
