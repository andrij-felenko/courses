// READ: терпить застаріле на 2 хв; коли кеш прострочено — чесна відмова (дефолту НЕМА).
const readPolicy: Policy<Reading> = {
  op: "readState",
  cache: readingCache,
  staleBudgetMs: 120_000,
  smartDefault: null,        // прострочений кеш → Unavailable, а не тихе старе значення
};

function readState(id: string): Promise<Served<Reading>> {
  return withFallback(id, readPolicy, () => device.read(id));
}

// ҐЕЙТ (так/ні): кешу НЕМА (щоб не відтворити застаріле «дозволено»), дефолт = fail-closed.
// Для пейволла було б smartDefault: () => ({ allowed: true }) — fail-open.
const unlockGatePolicy: Policy<Decision> = {
  op: "canCommand:unlock",
  cache: null,
  staleBudgetMs: 0,
  smartDefault: () => ({ allowed: false }),   // не достукались до авторизації → забороняємо
};

async function unlock(user: string, id: string): Promise<void> {
  const gate = await withFallback(`${user}:${id}`, unlockGatePolicy,
    () => authz.canCommand(user, id, "unlock"));

  if (!gate.value.allowed) throw new Forbidden(user, id);  // fail-closed: не впустили — правильно
  await hub.send(id, "unlock");   // саму КОМАНДУ не фолбечимо — вона не ідемпотентна
}
