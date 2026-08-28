const MAX_ATTEMPTS = 5;
const VALID = new Set(["open", "closed"]);
let notify: (ev: any) => Promise<void> = async () => {};   // впорснемо в проді / у тесті
export const setNotifier = (fn: typeof notify) => { notify = fn; };

// Повертає true, ЛИШЕ якщо твін справді змінився (новий пристрій або новіший seq).
async function applyToTwin(cx: any, ev: any): Promise<boolean> {
  const r = await cx.query(
    `INSERT INTO twin(device_id, state, seq) VALUES ($1, $2, $3)
     ON CONFLICT (device_id) DO UPDATE
       SET state = EXCLUDED.state, seq = EXCLUDED.seq, updated_at = now()
       WHERE EXCLUDED.seq > twin.seq                 -- старіша подія НЕ перебиває новішу
     RETURNING device_id`,
    [ev.device_id, ev.state, ev.seq]);
  return r.rowCount === 1;
}

async function handleEvent(cx: any, ev: any): Promise<void> {
  if (!VALID.has(ev.state)) throw new Error(`невідомий стан: ${ev.state}`);  // отрута
  const changed = await applyToTwin(cx, ev);
  if (changed) await notify(ev);      // пуш ЛИШЕ на реальну зміну; notify — зі своїм дедупом
}

export async function processOnce(): Promise<boolean> {
  const cx = await pool.connect();
  let job: any;
  try {
    await cx.query("BEGIN");
    const { rows } = await cx.query(
      `SELECT id, event_id, payload, attempts FROM jobs
        WHERE run_after <= now() ORDER BY id
          FOR UPDATE SKIP LOCKED LIMIT 1`);
    if (rows.length === 0) { await cx.query("COMMIT"); return false; }
    job = rows[0];
    await handleEvent(cx, job.payload);               // твін + пуш
    await cx.query("DELETE FROM jobs WHERE id = $1", [job.id]);
    await cx.query("COMMIT");                          // зміна твіна й зняття з черги — разом
    return true;
  } catch (err) {
    await cx.query("ROLLBACK");                        // відкат УСЬОГО: твін не зачеплено
    await retryOrBury(job, err);                       // облік спроби — окремою транзакцією
    return true;
  } finally {
    cx.release();
  }
}

async function retryOrBury(job: any, err: unknown): Promise<void> {
  if (!job) return;
  const n = job.attempts + 1;
  if (n >= MAX_ATTEMPTS)                               // отрута — у мертву чергу, геть із jobs
    await pool.query(
      `WITH gone AS (DELETE FROM jobs WHERE id = $1 RETURNING event_id, payload)
       INSERT INTO dead_letter(event_id, payload, error)
       SELECT event_id, payload, $2 FROM gone`, [job.id, String(err)]);
  else                                                // ще спробуємо — експоненційний відступ
    await pool.query(
      `UPDATE jobs SET attempts = $1, run_after = now() + make_interval(secs => $2)
        WHERE id = $3`, [n, 2 ** n, job.id]);
}
