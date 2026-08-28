import { createHmac, timingSafeEqual } from "node:crypto";

const parseSig = (h: string): Record<string, string> =>
  Object.fromEntries(h.split(",").map((kv) => kv.split("=", 2)));  // "t=..,v1=.." → {t, v1}

// Сирі байти на ЦЬОМУ маршруті — express.raw, не express.json: парсинг зсунув би байти й зламав підпис.
app.post("/dh/webhook", express.raw({ type: "application/json" }), async (req, res) => {
  const raw = req.body as Buffer;
  const { t, v1 } = parseSig(req.get("dh-signature") ?? "");

  // 1 · ДОВІРА: HMAC над тими самими `t.body`, звірка у СТАЛИЙ час.
  const expected = createHmac("sha256", HOOK_SECRET).update(`${t}.`).update(raw).digest();
  const got = Buffer.from(v1 ?? "", "hex");
  if (got.length !== expected.length || !timingSafeEqual(got, expected))
    return res.status(401).end();                  // підпис не зійшовся — це не від DH

  // 2 · СВІЖІСТЬ: старий підпис міг би переграти зловмисник. Вікно 5 хв, як у Stripe.
  if (Math.abs(Date.now() / 1000 - Number(t)) > 300) return res.status(400).end();

  const event = JSON.parse(raw.toString());        // тепер тілу можна вірити

  // 3 · ДЕДУП + ЗАСТОСУВАННЯ РАЗ — в ОДНІЙ транзакції: ключ і ефект або разом, або ніяк.
  await db.tx(async (tx) => {
    const ins = await tx.query(
      "INSERT INTO inbox(event_id) VALUES ($1) ON CONFLICT DO NOTHING", [event.id]);
    if (ins.rowCount === 0) return;                // подію вже застосовували — тихо проковтнули повтор
    await applyFirmwareResult(tx, event);          // ефект застосовано РІВНО раз
  });

  res.status(200).end();                           // ACK після коміту — DH може забути про доставку
});
