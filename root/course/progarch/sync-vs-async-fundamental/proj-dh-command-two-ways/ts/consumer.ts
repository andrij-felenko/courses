// consumer.ts — окремий процес: тягне з черги, дедуплікує, виконує ідемпотентно
commands.consume(async (c: LockCommand, ack, nack) => {
  // ── Дедуп-ворота. Той самий commandId міг уже пройти повний цикл.
  if (await processed.has(c.commandId)) {
    return ack();                 // уже виконували — тихо підтверджуємо й виходимо
  }
  await status.put({ commandId: c.commandId, state: "processing" });
  try {
    // Ефект. lock() ідемпотентна НА РІВНІ ПРИСТРОЮ — і це наш головний захист:
    // замкнути вже замкнене — то нічого не сталося (див. пастки нижче).
    const r = await withTimeout(hub.send(c.home, { cmd: "lock" }), 5_000);

    await processed.add(c.commandId);                                  // позначаємо ПІСЛЯ ефекту…
    await status.put({ commandId: c.commandId, state: "done", lock: r.state });
    await twin.merge(c.home, { lock: r.state });                       // кінцевий стан → у твін
    ack();                                                             // …і аж тепер підтверджуємо брокеру
  } catch (e) {
    // НЕ позначили як зроблене → брокер віддасть команду ще раз (повтор).
    await status.put({ commandId: c.commandId, state: "failed", reason: String(e) });
    nack();                       // після N спроб брокер сам зсуне команду в мертву чергу
  }
});

// processed — довговічне сховище вже виконаних commandId (Redis SET, таблиця з TTL…)
interface Processed {
  has(id: CommandId): Promise<boolean>;
  add(id: CommandId): Promise<void>;
}
