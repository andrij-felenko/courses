// arch/no-raw-cross-service.ts — фітнес-тест: сирий міжсервісний HTTP дозволено ЛИШЕ в клієнті.
const CLIENT = "infra/service-client.ts";                  // єдине легальне місце
const SERVICES = new Set(["telemetry", "core", "video", "hub", "payments", "push"]);

// Сканер дав кожен вихідний HTTP-виклик: файл, рядок, хост (якщо статичний), текст.
type RawCall = { file: string; line: number; host: string; text: string };

export function violations(calls: RawCall[]): string[] {
  return calls
    .filter((c) => c.file !== CLIENT && SERVICES.has(c.host))   // йде в сусідній сервіс повз клієнт
    .map((c) => `${c.file}:${c.line} — сирий HTTP у «${c.host}» повз ServiceClient: ${c.text.trim()}`);
}

export function main(calls: RawCall[]): number {
  const bad = violations(calls);
  if (bad.length === 0) { console.log("усі міжсервісні виклики йдуть крізь клієнт"); return 0; }
  console.error("ЗРАДА КЛІЄНТА DH:");
  for (const b of bad) console.error("  " + b);
  return 1;                       // exit 1 → CI червоний → merge заблоковано
}
