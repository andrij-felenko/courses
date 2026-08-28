const LEASE_MS = 30_000, BEAT_MS = 10_000, HARD_CAP_MS = 5 * 60_000, MAX_TRIES = 3;

async function runOne(w: Deps, workerId: string): Promise<boolean> {
  const op = await w.store.claim(workerId, LEASE_MS);   // SELECT…SKIP LOCKED + UPDATE
  if (!op) return false;                                 // черга порожня
  if (op.attempt > MAX_TRIES) {                          // падало забагато разів
    await w.store.finish(op.id, op.leaseId, "failed", null, { code: "too_many_attempts" });
    return true;
  }

  // Стеля часу через AbortController; монотонний годинник — performance.now(), НЕ Date.now().
  const ctrl = new AbortController();
  const capAt = performance.now() + HARD_CAP_MS;
  let progress = 0;

  // Серцебиття ЗА ГОДИННИКОМ, не між шматками: подовжує оренду, несе поступ, ловить фенс.
  const beat = setInterval(async () => {
    const mine = await w.store.heartbeat(op.id, op.leaseId, progress, LEASE_MS);
    if (!mine) ctrl.abort();                              // 0 рядків → перехопили → рвемо роботу
  }, BEAT_MS);

  try {
    for (const chunk of planChunks(op.request)) {
      if (ctrl.signal.aborted || performance.now() > capAt) return true; // фенс/стеля — нічого не пишемо
      if (await w.store.cancelRequested(op.id)) {
        await w.store.finish(op.id, op.leaseId, "canceled", null, null);
        return true;
      }
      await transcode(chunk, ctrl.signal);
      progress = chunk.percent;                          // серцебиття прочитає при наступному тіку
    }

    const key = `clips/${op.id}.mp4`;                    // детермінований ключ → повтор перезапише той самий об'єкт
    await w.objects.put(key, renderedBytes(op.id));
    const url = w.objects.signedUrl(key, 15 * 60);       // підпис діє 15 хв
    const result = { url, expiresAt: new Date(Date.now() + 15 * 60_000).toISOString() };

    if (await w.store.finish(op.id, op.leaseId, "succeeded", result, null)) // фенс у WHERE lease_id
      await w.notify.clipReady(op.userId, op.id);        // пуш лише якщо ми справді закрили
    return true;
  } finally {
    clearInterval(beat);
  }
}
