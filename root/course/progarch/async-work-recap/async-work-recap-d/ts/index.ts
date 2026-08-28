// ЗАПИС ЗАДАЧІ — річ першого класу, а не «викликав і забув»
type Job = {
  id: string;
  key: string;                 // ключ ідемпотентності: `${hubId}:${version}`
  state: "queued" | "running" | "done" | "dead";
  attempts: number;
  runAfter: number;            // монотонний дедлайн: «не чіпати раніше»
};

// ВЕБ-БІК: обробник лише ставить задачі в чергу й одразу відповідає 202
app.post("/homes/:id/firmware/:version", async (req, res) => {
  const hubs = await hubsOf(req.params.id);
  const jobs = hubs.map(h => ({ key: `${h}:${req.params.version}` }));
  const batchId = await queue.enqueueAll(jobs, { runAfter: nextNightWindow() });
  res.status(202).json({ batchId, total: jobs.length }); // «прийнято», НЕ «зроблено»
});

// ВОРКЕР-БІК: тягне задачу, дедупить за ключем, повторює або складає в мертву чергу
queue.consume(async (job: Job) => {
  if (await alreadyApplied(job.key)) return ok(job);     // ідемпотентність: повтор — no-op
  try {
    await hub.flash(job.key);
    await markDone(job.key);                             // стан → done, поступ видно родині
  } catch (e) {
    if (job.attempts >= 10) return deadLetter(job);      // здалися → людина розбере
    return retryWithBackoff(job);                        // ще спроба, з відступом
  }
});
