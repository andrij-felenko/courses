import { Pool } from "pg";

const CLAIM = `
UPDATE jobs SET run_at = now() + make_interval(secs => $2),
                attempts = attempts + 1, locked_by = $3
 WHERE id IN (SELECT id FROM jobs
               WHERE status = 'ready' AND run_at <= now()
                 AND attempts < max_attempts
               ORDER BY run_at, id LIMIT $1 FOR UPDATE SKIP LOCKED)
RETURNING id, kind, payload, attempts, max_attempts`;

const LEASE_S = 60;

export type Job = {
  id: string;              // bigint приходить рядком — не втрачаємо точності
  kind: string;
  payload: unknown;
  attempts: number;
  max_attempts: number;
};

export type Handler = (job: Job, signal: AbortSignal) => Promise<void>;

export async function runWorker(pool: Pool, me: string, handle: Handler, stop: AbortSignal) {
  while (!stop.aborted) {
    const { rows } = await pool.query<Job>(CLAIM, [1, LEASE_S, me]);
    if (rows.length === 0) {                       // черга порожня — почекати з розкидом
      await sleep(500 + Math.random() * 500);
      continue;
    }
    for (const job of rows) await runOne(pool, me, handle, job);
  }
}

async function runOne(pool: Pool, me: string, handle: Handler, job: Job) {
  // дедлайн задачі коротший за оренду — щоб не працювати після її кінця
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), (LEASE_S - 5) * 1000);
  let failure: string | null = null;
  try {
    await handle(job, ctl.signal);
  } catch (e) {
    failure = e instanceof Error ? e.message : String(e);
  } finally {
    clearTimeout(timer);
  }

  try {
    if (failure === null) {
      await pool.query(`DELETE FROM jobs WHERE id = $1 AND locked_by = $2`, [job.id, me]);
    } else if (job.attempts >= job.max_attempts) {
      await pool.query(
        `UPDATE jobs SET status = 'dead', last_error = $2, run_at = now()
          WHERE id = $1 AND locked_by = $3`, [job.id, failure, me]);
    } else {
      await pool.query(
        `UPDATE jobs SET run_at = now() + make_interval(secs => $2), last_error = $3
          WHERE id = $1 AND locked_by = $4`, [job.id, backoff(job.attempts), failure, me]);
    }
  } catch (e) {
    // рядок не закрито — задачу поверне оренда, тож просто пишемо в журнал
    console.error(`задача ${job.id}: рядок не закрито`, e);
  }
}

/** Затримка в секундах: база·2^(спроба−1), зі стелею й розкидом. */
function backoff(attempt: number): number {
  const base = 5, ceil = 3600;
  const d = Math.min(ceil, base * 2 ** (attempt - 1));
  return d / 2 + Math.random() * d / 2;            // розкид: [d/2 .. d]
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
