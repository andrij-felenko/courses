// async-enqueue.ts — приймаємо команду й ОДРАЗУ відповідаємо 202
app.post("/homes/:id/lock", async (req, res) => {
  // Ключ ідемпотентності. Якщо застосунок ретраїть той самий POST (бо 202 загубився
  // у дорозі), ми НЕ заведемо другу команду — той самий ключ = та сама команда.
  const commandId = req.header("Idempotency-Key") ?? randomUUID();

  // enqueue мусить бути ідемпотентним за commandId (upsert), а не сліпим push.
  await commands.enqueue({ commandId, home: req.params.id, cmd: "lock" });
  await status.put({ commandId, state: "accepted" });

  res.status(202)
     .location(`/commands/${commandId}`)                    // ← ось де опитувати статус
     .json({ accepted: true, commandId });                  // 202 «прийняв, спитай пізніше»
});
