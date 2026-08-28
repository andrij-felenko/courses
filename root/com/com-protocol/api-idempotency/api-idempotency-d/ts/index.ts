async function handleCharge(req, res) {
  const key = req.header("Idempotency-Key");
  if (!key) return res.status(400).send("потрібен Idempotency-Key");

  // Атомарно: або застовпили ключ за собою, або дізналися, що він уже є.
  const claimed = await store.insertIfAbsent(key);   // false, якщо ключ уже був
  if (!claimed) {
    const saved = await store.getResult(key);         // це повтор
    return res.status(saved.status).json(saved.body); // та сама відповідь
  }

  const result = await charge(req.body.amount);       // робота — рівно раз
  await store.saveResult(key, result);
  return res.status(result.status).json(result.body);
}
