// СЕРВЕР DH — статус для тих, хто ОПИТУЄ. Має бути ДЕШЕВОЮ: її б'ють N/T разів на секунду.
app.get("/jobs/:id", async (req, res) => {
  const job = await jobs.get(req.params.id);        // одне читання за ключем — і по всьому
  if (!job) return res.status(404).json({ error: "unknown job" });

  const terminal = job.status === "done" || job.status === "failed";
  res.set("Cache-Control", terminal ? "public, max-age=3600" : "no-store"); // done — можна; running — ні

  res.json({
    jobId: job.id,
    status: job.status,                             // queued | running | done | failed
    result: terminal ? job.result : null,           // {version, ok} на done; {code, message} на failed
    updatedAt: job.updatedAt,                       // точка відліку для клієнта Й для звірки
  });
});
