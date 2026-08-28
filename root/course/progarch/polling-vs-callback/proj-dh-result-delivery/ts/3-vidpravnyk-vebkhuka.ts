import { createHmac } from "node:crypto";

// Подія будується РАЗ, з id, стабільним на ВСІ повтори (id — ключ дедупу в приймача).
async function onFirmwareDone(job: Job) {
  const event = {
    id: `evt_${job.id}`,               // детермінований з задачі → той самий на кожен повтор і на звірку
    type: "firmware.updated",
    home: job.home, version: job.version, ok: job.ok,
    occurredAt: job.finishedAt,
  };
  for (const url of await hooks.for(job.home)) await deliver(url, event);
}

// Підпис Stripe-стилю: HMAC-SHA256 над `t.body` — підпис прикриває й тіло, й час.
function sign(body: string, secret: string, ts: number): string {
  const mac = createHmac("sha256", secret).update(`${ts}.${body}`).digest("hex");
  return `t=${ts},v1=${mac}`;
}

async function deliver(url: string, event: object) {
  const body = JSON.stringify(event);              // рівно ці байти й підписуємо, й шлемо
  const ts = Math.floor(Date.now() / 1000);
  const sig = sign(body, HOOK_SECRET, ts);
  const base = 1000, cap = 60_000, maxAttempts = 8;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "content-type": "application/json", "dh-signature": sig },
        body,                                      // тіло НЕ перебудовуємо — байти мусять збігтися з підписом
        signal: AbortSignal.timeout(5000),
      });
      if (r.status >= 200 && r.status < 300) return;                  // прийнято — по завершенню
      if (r.status >= 400 && r.status < 500 && r.status !== 429) break; // 4xx (крім 429) — не полагодиться повтором
    } catch { /* таймаут/обрив — падаємо у відступ нижче */ }

    const window = Math.min(cap, base * 2 ** attempt);
    await sleep(Math.random() * window);           // експонента + повний джитер
  }
  await deadLetters.put({ url, body, sig, failedAt: Date.now() });    // на розбір, не в нікуди
}
