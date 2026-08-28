// СИНХРОННО — обробник тримає запит відкритим, доки хаб не відповість
app.post("/homes/:id/lock", async (req, res) => {
  const r = await hub.send(req.params.id, { cmd: "lock" }); // ← чекаємо ТУТ
  res.json({ state: r.state });                    // лише тепер: 200 OK «зачинено»
});

// АСИНХРОННО — обробник кладе команду в чергу й одразу відповідає
app.post("/homes/:id/lock", async (req, res) => {
  const id = await commands.enqueue({ home: req.params.id, cmd: "lock" });
  res.status(202).json({ accepted: true, commandId: id }); // 202 «прийнято», НЕ «зроблено»
});
// окремий споживач виконає команду, коли хаб оживе (може прийти двічі — тому lock ідемпотентна):
commands.consume((c) => hub.send(c.home, c));
