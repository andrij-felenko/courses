MAX_ATTEMPTS = 5
VALID = {"open", "closed"}
_notify = lambda ev: None            # впорснемо в проді / у тесті
def set_notifier(fn): 
    global _notify; _notify = fn

# Повертає True, ЛИШЕ якщо твін справді змінився (новий пристрій або новіший seq).
async def apply_to_twin(cx, ev) -> bool:
    row = await cx.fetchrow(
        """INSERT INTO twin(device_id, state, seq) VALUES ($1, $2, $3)
           ON CONFLICT (device_id) DO UPDATE
             SET state = EXCLUDED.state, seq = EXCLUDED.seq, updated_at = now()
             WHERE EXCLUDED.seq > twin.seq            -- старіша подія НЕ перебиває новішу
           RETURNING device_id""",
        ev["device_id"], ev["state"], ev["seq"])
    return row is not None

async def handle_event(cx, ev) -> None:
    if ev["state"] not in VALID:
        raise ValueError(f"невідомий стан: {ev['state']}")   # отрута
    changed = await apply_to_twin(cx, ev)
    if changed:
        await _notify(ev)     # пуш ЛИШЕ на реальну зміну; notify — зі своїм дедупом

async def process_once(pool) -> bool:
    async with pool.acquire() as cx:
        tx = cx.transaction(); await tx.start()
        job = None
        try:
            job = await cx.fetchrow(
                """SELECT id, event_id, payload, attempts FROM jobs
                    WHERE run_after <= now() ORDER BY id
                      FOR UPDATE SKIP LOCKED LIMIT 1""")
            if job is None:
                await tx.commit(); return False
            ev = json.loads(job["payload"])
            await handle_event(cx, ev)                # твін + пуш
            await cx.execute("DELETE FROM jobs WHERE id = $1", job["id"])
            await tx.commit()                         # зміна твіна й зняття з черги — разом
            return True
        except Exception as err:
            await tx.rollback()                       # відкат УСЬОГО: твін не зачеплено
            await retry_or_bury(pool, job, err)       # облік спроби — окремою транзакцією
            return True

async def retry_or_bury(pool, job, err) -> None:
    if job is None:
        return
    n = job["attempts"] + 1
    if n >= MAX_ATTEMPTS:                             # отрута — у мертву чергу, геть із jobs
        await pool.execute(
            """WITH gone AS (DELETE FROM jobs WHERE id = $1 RETURNING event_id, payload)
               INSERT INTO dead_letter(event_id, payload, error)
               SELECT event_id, payload, $2 FROM gone""", job["id"], str(err))
    else:                                            # ще спробуємо — експоненційний відступ
        await pool.execute(
            "UPDATE jobs SET attempts = $1, run_after = now() + make_interval(secs => $2) WHERE id = $3",
            n, 2 ** n, job["id"])
