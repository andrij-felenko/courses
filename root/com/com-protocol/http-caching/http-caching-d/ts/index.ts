app.get("/api/orders/:id", async (req, res) => {
  // версія береться з бази одним дешевим читанням, без збирання тіла
  const version = await db.orderVersion(req.params.id);   // напр. 17
  if (version === null) return res.sendStatus(404);

  const etag = `"order-${req.params.id}-v${version}"`;
  res.setHeader("ETag", etag);
  res.setHeader("Cache-Control", "private, no-cache");

  if (req.headers["if-none-match"] === etag) {
    return res.status(304).end();       // тіло не збирали взагалі
  }

  const order = await db.loadOrder(req.params.id);        // ось тут дорога робота
  res.json(order);
});
