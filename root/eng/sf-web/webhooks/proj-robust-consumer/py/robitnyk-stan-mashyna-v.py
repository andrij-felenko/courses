MAX_ATTEMPTS = 8

def handle(event_id: str) -> str:                # "ack" — прибрати; "retry" — повернути
    try:
        with pool.connection() as conn:          # вихід без винятку → COMMIT; виняток → ROLLBACK
            row = conn.execute(
                "SELECT status, payload FROM webhook_inbox "
                "WHERE event_id = %s FOR UPDATE", (event_id,)).fetchone()   # замок на рядок
            if row is None or row["status"] in ("done", "dead"):
                return "ack"                     # уже зроблено/відкладено — тихо

            apply_side_effect(conn, row["payload"])      # у ТІЙ САМІЙ транзакції
            conn.execute(
                "UPDATE webhook_inbox SET status='done', processed_at=now() "
                "WHERE event_id = %s", (event_id,))
        return "ack"                             # дійшли сюди → ефект і 'done' закомічені РАЗОМ
    except Exception as err:
        return on_failure(event_id, err)         # виняток → with уже відкотив; окремо attempts+1

def apply_side_effect(conn, payload):
    # Умова paid=false робить повтор нічим — сам ефект теж ідемпотентний.
    conn.execute(
        "UPDATE invoices SET paid = true, paid_at = now() "
        "WHERE id = %s AND paid = false", (payload["data"]["invoice_id"],))

def on_failure(event_id: str, err: Exception) -> str:
    with pool.connection() as conn:
        attempts = conn.execute(
            "UPDATE webhook_inbox SET attempts = attempts + 1 "
            "WHERE event_id = %s RETURNING attempts", (event_id,)).fetchone()["attempts"]
        if attempts >= MAX_ATTEMPTS:
            conn.execute("UPDATE webhook_inbox SET status='dead' WHERE event_id = %s", (event_id,))
            alert_human(event_id, err)           # отруйна подія — хай гляне людина
            return "ack"                         # прибрати з живої черги
    return "retry"                               # назад у чергу, з наростанням паузи
