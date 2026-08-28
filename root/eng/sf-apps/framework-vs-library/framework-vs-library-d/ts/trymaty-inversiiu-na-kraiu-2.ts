// На краю: перекладач нічого не вирішує, рішення — звичайна чиста функція.
type Confirmation =
  | { ok: true; order: Order }
  | { ok: false; reason: string };

export function confirmOrder(order: Order, now: Date): Confirmation {
  if (order.status !== "new") return { ok: false, reason: "вже підтверджено" };
  return { ok: true, order: { ...order, status: "confirmed", confirmedAt: now } };
}

app.post("/orders/:id/confirm", async (req, res) => {
  const order = await repo.byId(req.params.id);
  const result = confirmOrder(order, new Date());
  if (!result.ok) return res.status(409).send(result.reason);
  await repo.save(result.order);
  res.json(result.order);
});
