async function handleCharge(req, res) {
  const key = req.get("Idempotency-Key");
  if (!key || !KEY_RE.test(key))
    return res.status(400).json({ error: "потрібен коректний Idempotency-Key" });

  const userId = req.auth.userId;
  const path = req.path;
  const raw: Buffer = req.rawBody;                     // ТОЧНІ байти, як прийшли
  const hash = fingerprint(req.method, path, raw);
  const expiresAt = new Date(Date.now() + KEY_TTL_MS);

  const c = await claim(pool, key, userId, path, hash, expiresAt);

  if (!c.won) {
    const row = c.row;
    if (!row.request_hash.equals(hash))                // той самий ключ, інше тіло
      return res.status(422).json({ error: "Idempotency-Key уже вжито з іншим тілом запиту" });
    if (row.state === "in_progress") {                 // переможець ще рахує
      res.set("Retry-After", "1");
      return res.status(409).json({ error: "запит із цим ключем ще виконується" });
    }
    return send(res, toStored(row), true);             // completed → точне відтворення
  }

  const stored = await runOnce(pool, key, userId, path, JSON.parse(raw.toString()));
  return send(res, stored, false);                     // свіжий результат — рівно раз
}
