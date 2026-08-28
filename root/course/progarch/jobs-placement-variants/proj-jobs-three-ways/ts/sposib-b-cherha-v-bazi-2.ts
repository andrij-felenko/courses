async function claim(pool: Pool, workerId: string): Promise<Job | null> {
  const { rows } = await pool.query(claimSql, [workerId]);   // SQL вище
  return rows[0] ?? null;      // pg сам розбирає jsonb payload в обʼєкт
}

async function runOnce(pool: Pool, workerId: string,
                       handle: (job: Job) => Promise<void>): Promise<boolean> {
  const job = await claim(pool, workerId);   // короткий такт: вихопили
  if (!job) return false;
  await handle(job);                          // довгий такт: кодуємо, БЕЗ відкритої транзакції
  await pool.query("UPDATE jobs SET status = 'done' WHERE id = $1", [job.id]);
  return true;
}
