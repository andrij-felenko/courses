// POST /cameras/:id/clips — прийняти, дедуплікувати за ключем, віддати 202 + Location.
app.post("/cameras/:id/clips", async (req, res) => {
  const key = req.header("Idempotency-Key");
  if (!key) return res.status(400).json({ code: "missing_idempotency_key" });

  const request = { cameraId: req.params.id, from: req.body.from, to: req.body.to };
  const id = "op-" + newId();

  // ОДНА вставка = і операція, і задача в черзі. UNIQUE(idempotency_key) розсудить гонку.
  const rows = await db.query(
    `INSERT INTO operations (id, idempotency_key, status, request, user_id, expires_at)
     VALUES ($1, $2, 'queued', $3, $4, now() + interval '30 days')
     ON CONFLICT (idempotency_key) DO NOTHING
     RETURNING id`,
    [id, key, request, req.userId]);

  if (rows.length === 1) {                       // ми ВИГРАЛИ гонку: рядок наш, рендер у черзі
    res.setHeader("Location", `/operations/${id}`);
    return res.status(202).json({ id, status: "queued" });
  }

  // 0 рядків → хтось із тим самим ключем нас випередив. Читаємо ЙОГО операцію.
  const { rows: [op] } = await db.query(
    `SELECT id, request FROM operations WHERE idempotency_key = $1`, [key]);

  // той самий ключ, але інші параметри — це помилка клієнта, а не мовчазний підмін наміру
  if (!sameRequest(op.request, request))
    return res.status(422).json({ code: "idempotency_key_reused" });

  res.setHeader("Location", `/operations/${op.id}`);
  return res.status(202).json({ id: op.id, status: "queued" });   // ТА САМА операція
});
