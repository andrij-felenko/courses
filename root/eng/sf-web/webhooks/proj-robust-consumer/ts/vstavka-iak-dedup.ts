// Одна вставка = дедуп. rowCount каже, ми поклали нову подію чи наштовхнулися на дубль.
async function inboxInsert(id: string, type: string, raw: Buffer): Promise<boolean> {
  const r = await pool.query(
    `INSERT INTO webhook_inbox (event_id, type, payload)
     VALUES ($1, $2, $3)
     ON CONFLICT (event_id) DO NOTHING`,
    [id, type, raw.toString("utf8")],
  );
  return r.rowCount === 1;          // 1 — вставили нову; 0 — конфлікт, уже бачили
}
