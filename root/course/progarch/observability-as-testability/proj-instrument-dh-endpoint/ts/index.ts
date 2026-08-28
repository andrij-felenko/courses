import { Counter, Histogram } from "prom-client";
import type { Request, Response } from "express";
import { gateway, log, TimeoutError, RejectedError } from "./deps";

// ── Сигнали оголошуємо РАЗ при старті: це assert-и, що чекають на трафік ──
// R+E: одна серія — і частота, і помилки; розрізняє мітка outcome.
// Мітки лише ОБМЕЖЕНІ: команд десятки, наслідків чотири. НІЯКОГО device.
const commands = new Counter({
  name: "dh_device_commands_total",
  help: "Команди пристроям за типом і наслідком.",
  labelNames: ["command", "outcome"] as const,
});

// D: розподіл тривалості; кошики навколо цілі SLO — 300 мс.
const latency = new Histogram({
  name: "dh_device_command_seconds",
  help: "Тривалість обробки команди пристрою, секунди.",
  labelNames: ["command"] as const,
  buckets: [0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 5],
});

// Інваріант у проді: не throw, що валить запит, а лічильник «неможливого».
const invariant = new Counter({
  name: "dh_invariant_violation_total",
  help: "Порушення інваріантів на гарячому шляху.",
  labelNames: ["name"] as const,
});

export async function sendCommand(req: Request, res: Response) {
  const start = process.hrtime.bigint();
  const tenant = req.auth.tenant;    // орендар — з автентифікації, НЕ з тіла
  const deviceId = req.params.id;
  const cmd = req.body as { name: string; arg?: number };

  let outcome: "ok" | "timeout" | "rejected" | "error";
  let ack = { battery: 0 };
  try {
    ack = await gateway.send(deviceId, cmd);
    outcome = "ok";
  } catch (e) {
    outcome = classify(e); // "timeout" | "rejected" | "error"
  }
  const elapsedMs = Number(process.hrtime.bigint() - start) / 1e6;

  latency.observe({ command: cmd.name }, elapsedMs / 1000);  // D
  commands.inc({ command: cmd.name, outcome });              // R+E

  // Інваріант як assert у проді: 0..100. Порушено — порахуй і затисни, НЕ кидай.
  if (outcome === "ok" && (ack.battery < 0 || ack.battery > 100)) {
    invariant.inc({ name: "battery_range" });
    log.error({ event: "invariant.broken", name: "battery_range",
                tenant, device: deviceId, got: ack.battery });
    ack.battery = Math.max(0, Math.min(100, ack.battery));
  }

  // Приклад-тест із проду: один рядок = повний контекст одного запиту.
  // СТАБІЛЬНІ ІДЕНТИФІКАТОРИ, не e-mail і не імʼя.
  log.info({ event: "device.command", tenant, device: deviceId,
             command: cmd.name, outcome, latencyMs: Math.round(elapsedMs) });

  res.status({ ok: 200, rejected: 409, timeout: 504 }[outcome] ?? 500).json(ack);
}

// classify зводить помилку шва до обмеженого набору наслідків — це й тримає
// кардинальність метрики малою: мітка outcome ніколи не «розповзеться».
function classify(e: unknown): "timeout" | "rejected" | "error" {
  if (e instanceof TimeoutError) return "timeout";
  if (e instanceof RejectedError) return "rejected";
  return "error";
}
