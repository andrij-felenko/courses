// Робітник у контексті Відео: рендерить шматками, між шматками — три обов'язки.
async function renderClip(op: ClipOperation, lease: Lease) {
  const deadline = monotonicNow() + 5 * 60_000;          // тверда стеля тривалості
  for (const chunk of planChunks(op.request)) {
    if (await isCanceled(op.id)) return finish(op, "canceled");   // передумав — стоп
    if (monotonicNow() > deadline) return finish(op, "failed", "timeout");
    await transcode(chunk);
    await lease.heartbeat();                              // «я живий» — оренду продовжено
    await setProgress(op.id, chunk.percent);             // клієнт бачить рух
  }
  const url = await putToObjectStore(op.id);             // результат у сховище
  await finish(op, "succeeded", { url, expiresAt: in15min() });
}
