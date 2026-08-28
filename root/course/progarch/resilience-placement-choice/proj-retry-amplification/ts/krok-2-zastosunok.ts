import { randomUUID } from "node:crypto";

// Повний джитер: пауза рівномірно у вікні [0, min(cap, base·2^спроба)) мс.
const fullJitter = (attempt: number, base = 100, cap = 2000): number =>
  Math.random() * Math.min(cap, base * 2 ** attempt);
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

async function sendCommand(deviceId: string, action: string): Promise<boolean> {
  // КЛЮЧ ГЕНЕРУЄМО ОДИН РАЗ на логічну команду — і носимо крізь УСІ повтори.
  // Той самий ключ → сервіс команд упізнає дубль і виконає дію рівно раз.
  const idempotencyKey = randomUUID();
  const maxTries = 3;                       // єдиний ×k на всьому шляху — тут і лише тут

  for (let attempt = 0; attempt < maxTries; attempt++) {
    if (attempt > 0) await sleep(fullJitter(attempt - 1));
    const res = await fetch(`/v1/devices/${deviceId}/commands`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": idempotencyKey,  // ← той самий рядок на кожній спробі
      },
      body: JSON.stringify({ action }),
    });
    if (res.ok) return true;
    // 5xx / мережа — минуще, варте повтору; 4xx (крім 429) — назавжди, не повторюємо.
    if (res.status < 500 && res.status !== 429) return false;
  }
  return false;                             // бюджет спроб вичерпано
}
