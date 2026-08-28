// Захоплено: рішення живе всередині чужого типу.
// Це не можна покликати ні з тесту, ні з іншої точки входу.
app.post("/orders/:id/confirm", async (req: Request, res: Response) => {
  const order = await db.orders.findById(req.params.id);
  if (order.status !== "new") return res.status(409).send("вже підтверджено");
  order.status = "confirmed";
  order.confirmedAt = new Date();
  await db.orders.save(order);
  res.json(order);
});
