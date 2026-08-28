async function runOnce(db: Pool, key, userId, path, body): Promise<Stored> {
  const client = await db.connect();
  try {
    await client.query("BEGIN");

    // Ефект — у ТІЙ САМІЙ транзакції, що й завершення ключа.
    const p = await client.query(
      `INSERT INTO payments (user_id, amount, currency) VALUES ($1, $2, $3) RETURNING id`,
      [userId, body.amount, body.currency],
    );

    const stored: Stored = {
      status: 201,
      headers: { "Content-Type": "application/json", Location: `/payments/${p.rows[0].id}` },
      body: Buffer.from(JSON.stringify({ paymentId: p.rows[0].id, status: "charged" })),
    };

    await client.query(
      `UPDATE idempotency_keys
          SET state = 'completed', response_status = $1, response_headers = $2,
              response_body = $3, completed_at = now()
        WHERE user_id = $4 AND request_path = $5 AND key = $6`,
      [stored.status, stored.headers, stored.body, userId, path, key],
    );

    await client.query("COMMIT");             // ефект і 'completed' — атомарно разом
    return stored;
  } catch (e) {
    await client.query("ROLLBACK");           // ефект відкотився — звільняємо claim
    await db.query(
      `DELETE FROM idempotency_keys
        WHERE user_id = $1 AND request_path = $2 AND key = $3 AND state = 'in_progress'`,
      [userId, path, key],
    );
    throw e;
  } finally {
    client.release();
  }
}
