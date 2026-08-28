const LEASE = 30;            // оренда клейма, секунд: довше за очікуваний прогін задачі
const BASE = 2, CAP = 3600;  // відступ: база 2 c, стеля — година

// full jitter (Marc Brooker, AWS, 2015): рівномірно [0, стеля), а не рівний крок
function backoff(attempts: number): number {
  const ceiling = Math.min(CAP, BASE * 2 ** attempts);
  return Math.random() * ceiling;
}

async function worker(pool: Pool, run: Handler) {
  while (alive) {
    const job = await claim(pool, LEASE);          // атомарний UPDATE ... SKIP LOCKED
    if (!job) { await sleep(500); continue; }      // черга без готових — перепочити

    try {
      await run(job.payload);                      // САМА робота: flash / email / …
      await complete(pool, job.id);                // стан → done
    } catch (err) {
      await fail(pool, job.id, backoff(job.attempts), String(err)); // → retry або dead
    }
  }
}
