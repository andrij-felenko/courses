// Ефект + просування саги та подія — атомарно. Напрям вирішує, run це чи compensate.
async function applyStep(p: Ports, saga: Saga, step: Step, dir: Dir): Promise<void> {
  const key = `${saga.id}:${step.name}:${dir}`;           // ключ на крок І напрям
  const action = dir === "forward" ? step.run : step.compensate;
  if (action) await action({ homeId: saga.homeId, idemKey: key });  // ефект; повтор — тихий no-op на тому боці

  await p.txn(async (tx) => {                              // стан + подія — В ОДНІЙ транзакції
    if (await p.seen(tx, key)) return;                     // дубль → уся транзакція нічого не робить
    await p.mark(tx, key);
    saga.cursor += dir === "forward" ? 1 : -1;
    await p.saveIn(tx, saga);
    await p.outbox(tx, { sagaId: saga.id, step: step.name, dir });
  });
}
