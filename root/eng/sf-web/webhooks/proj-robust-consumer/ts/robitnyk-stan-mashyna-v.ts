const MAX_ATTEMPTS = 8;
type Ack = "ack" | "retry";                            // прибрати з черги / повернути

async function handle(eventId: string): Promise<Ack> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const { rows } = await client.query(
      `SELECT status, payload FROM webhook_inbox
       WHERE event_id = $1 FOR UPDATE`, [eventId]);     // замок на рядок
    const row = rows[0];
    if (!row || row.status === "done" || row.status === "dead") {
      await client.query("COMMIT");
      return "ack";                                     // уже зроблено/відкладено — тихо
    }

    await applySideEffect(client, row.payload);         // у ТІЙ САМІЙ транзакції
    await client.query(
      `UPDATE webhook_inbox SET status='done', processed_at=now()
       WHERE event_id = $1`, [eventId]);
    await client.query("COMMIT");                       // ефект і 'done' лягають РАЗОМ
    return "ack";
  } catch (err) {
    await client.query("ROLLBACK");                     // нічого не закомічено — стан чистий
    return onFailure(eventId, err);                     // attempts+1, можливо — в DLQ
  } finally {
    client.release();
  }
}

// Сам ефект теж ідемпотентний: умова paid=false робить повтор нічим.
async function applySideEffect(client: PoolClient, payload: any) {
  await client.query(
    `UPDATE invoices SET paid = true, paid_at = now()
     WHERE id = $1 AND paid = false`, [payload.data.invoice_id]);
}

async function onFailure(eventId: string, err: unknown): Promise<Ack> {
  const { rows } = await pool.query(
    `UPDATE webhook_inbox SET attempts = attempts + 1
     WHERE event_id = $1 RETURNING attempts`, [eventId]);
  if (rows[0].attempts >= MAX_ATTEMPTS) {
    await pool.query(`UPDATE webhook_inbox SET status='dead' WHERE event_id = $1`, [eventId]);
    alertHuman(eventId, err);                           // отруйна подія — хай гляне людина
    return "ack";                                       // прибрати з живої черги
  }
  return "retry";                                       // назад у чергу, з наростанням паузи
}
