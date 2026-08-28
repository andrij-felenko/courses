import express from "express";
import crypto from "node:crypto";

const app = express();
const SECRET = process.env.WEBHOOK_SECRET!;

// express.raw, НЕ express.json: інакше сирі байти, над якими рахувався
// підпис, будуть уже недоступні — лишиться тільки розібраний об'єкт.
app.post("/webhooks", express.raw({ type: "application/json" }), async (req, res) => {
  const raw = req.body as Buffer;                       // сирі байти тіла
  if (!verify(raw, req.header("X-Signature") ?? "")) {
    return res.sendStatus(401);                         // підпис не збігся — геть
  }

  let event: { id: string; type: string };
  try {
    event = JSON.parse(raw.toString("utf8"));           // розбір ЛИШЕ після перевірки
  } catch {
    return res.sendStatus(400);                         // криве тіло — не наша подія
  }

  try {
    if (await inboxInsert(event.id, event.type, raw)) { // нова — false, якщо дубль
      await enqueue(event.id);                          // роботу знімемо з гарячого шляху
    }
    return res.sendStatus(200);                         // 200 і новій, і дублю
  } catch {
    return res.sendStatus(500);                         // не зберегли — хай ПОВТОРЯТЬ, не 200!
  }
});

function verify(raw: Buffer, sig: string): boolean {
  const expected = crypto.createHmac("sha256", SECRET).update(raw).digest("hex");
  const a = Buffer.from(sig), b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);  // сталий час
}
