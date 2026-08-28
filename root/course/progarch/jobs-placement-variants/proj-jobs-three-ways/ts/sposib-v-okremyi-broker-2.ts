async function uploadClipOutbox(pool: Pool, homeId: number, url: string): Promise<number> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const { rows } = await client.query(
      "INSERT INTO clips (home_id, url) VALUES ($1, $2) RETURNING id", [homeId, url]);
    const clipId = rows[0].id;
    await client.query(
      "INSERT INTO outbox (topic, payload) VALUES ('transcode', $1::jsonb)",
      [JSON.stringify({ clipId })]);               // ← НАМІР у ТІЙ САМІЙ транзакції
    await client.query("COMMIT");                  // кліп + намір лягають атомарно
    return clipId;
  } catch (e) {
    await client.query("ROLLBACK");
    throw e;
  } finally {
    client.release();
  }
}

// Relay: злити недоправлене з outbox у брокер. Ганяється циклічно, окремо від застосунку.
async function relayOnce(pool: Pool, broker: FakeBroker): Promise<void> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const { rows } = await client.query(`
      SELECT id, topic, payload FROM outbox
       WHERE delivered_at IS NULL
       ORDER BY id
       LIMIT 100
       FOR UPDATE SKIP LOCKED`);                   // кілька relay-інстансів не переступлять одне одному
    for (const row of rows) {
      await broker.enqueue(row.topic, row.payload);// може доправити двічі → воркер ідемпотентний, дубль ок
      await client.query(
        "UPDATE outbox SET delivered_at = now() WHERE id = $1", [row.id]);
    }
    await client.query("COMMIT");
  } catch (e) {
    await client.query("ROLLBACK");                // не встигли позначити → на наступному колі перешлемо
    throw e;
  } finally {
    client.release();
  }
}
