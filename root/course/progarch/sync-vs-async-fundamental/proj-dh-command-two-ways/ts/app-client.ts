// app-client.ts — 202 → «в обробці» → опитуємо → кінцевий стан на екрані
async function lockDoor(homeId: HomeId): Promise<void> {
  const { commandId } = await api.post(`/homes/${homeId}/lock`).json();
  ui.badge("в обробці…");                    // одразу після 202 — чесно, бо ще НЕ зроблено

  const final = await poll<CommandRecord>(`/commands/${commandId}`, {
    ready: (r) => r.state === "done" || r.state === "failed",
    everyMs: 1_000,
    giveUpMs: 30_000,
  });

  if (final.state === "done") {
    ui.badge(final.lock === "locked" ? "зачинено" : "відчинено");
  } else {
    ui.badge("не вдалося — повторити?");      // failed або вичерпали час опитування
  }
}

// поллінг з інтервалом і дедлайном — вертає останнє, що встиг побачити
async function poll<T>(url: string,
  o: { ready: (v: T) => boolean; everyMs: number; giveUpMs: number }): Promise<T> {
  const deadline = Date.now() + o.giveUpMs;
  for (;;) {
    const v = await api.get(url).json<T>();
    if (o.ready(v) || Date.now() > deadline) return v;
    await sleep(o.everyMs);
  }
}
