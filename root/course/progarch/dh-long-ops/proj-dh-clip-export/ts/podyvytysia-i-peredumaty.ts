// GET /operations/:id — чисте читання; клієнт полить із відступом. Кеш заборонено.
app.get("/operations/:id", async (req, res) => {
  const op = await repo.find(req.params.id);
  if (!op) return res.status(404).end();
  res.setHeader("Cache-Control", "no-store");
  res.json({ id: op.id, status: op.status, progress: op.progress,
             result: op.result, error: op.error });
});

// POST /operations/:id:cancel — кооперативно: queued гасне одразу, running лишає прапорець.
app.post("/operations/:id\\:cancel", async (req, res) => {
  await db.query(
    `UPDATE operations
        SET status = CASE WHEN status = 'queued' THEN 'canceled' ELSE status END,
            cancel_requested = true
      WHERE id = $1 AND status IN ('queued','running')`, [req.params.id]);
  res.status(202).end();                          // «прийнято до скасування», не «скасовано»
});
