async def run_once(pool, key, user_id, path, body):
    async with pool.acquire() as conn:
        try:
            async with conn.transaction():
                payment_id = await conn.fetchval(
                    "INSERT INTO payments (user_id, amount, currency) VALUES ($1,$2,$3) RETURNING id",
                    user_id, body["amount"], body["currency"],
                )
                stored = {
                    "status": 201,
                    "headers": {"Content-Type": "application/json",
                                "Location": f"/payments/{payment_id}"},
                    "body": json.dumps({"paymentId": str(payment_id),
                                        "status": "charged"}).encode(),
                }
                await conn.execute(
                    """
                    UPDATE idempotency_keys
                       SET state='completed', response_status=$1, response_headers=$2::jsonb,
                           response_body=$3, completed_at=now()
                     WHERE user_id=$4 AND request_path=$5 AND key=$6
                    """,
                    stored["status"], json.dumps(stored["headers"]),
                    stored["body"], user_id, path, key,
                )
            return stored                       # транзакція зафіксована — ефект+'completed'
        except Exception:
            await pool.execute(                 # ефект відкотився — звільняємо claim
                """DELETE FROM idempotency_keys
                    WHERE user_id=$1 AND request_path=$2 AND key=$3 AND state='in_progress'""",
                user_id, path, key,
            )
            raise
