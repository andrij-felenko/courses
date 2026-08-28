const BATCH = 5000;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function backfill(
  db: Pool, replicaLagSeconds: () => Promise<number>,
): Promise<void> {
  let lastId = "0";
  for (;;) {
    // Порція ще не перелитих рядків за зростанням id (keyset-пагінація).
    // id як рядок — pg віддає bigint рядком, щоб не втратити точність.
    const { rows } = await db.query<{ id: string; temp_c: number }>(
      `SELECT id, temp_c FROM readings
       WHERE id > $1 AND temp_mc IS NULL
       ORDER BY id LIMIT $2`,
      [lastId, BATCH],
    );
    if (rows.length === 0) break;                        // усе перелито — кінець

    const ids = rows.map((r) => r.id);
    const mc = rows.map((r) => toMilliC(r.temp_c));
    // Один UPDATE на порцію через unnest; AND temp_mc IS NULL — ідемпотентність.
    await db.query(
      `UPDATE readings AS r SET temp_mc = v.mc
         FROM unnest($1::bigint[], $2::bigint[]) AS v(id, mc)
        WHERE r.id = v.id AND r.temp_mc IS NULL`,
      [ids, mc],
    );
    lastId = rows[rows.length - 1].id;                   // продовжити після рестарту

    // ТРОТЛІНГ: не женемо базу на межу.
    while ((await replicaLagSeconds()) > 5.0) await sleep(1000);
    await sleep((BATCH / 20_000) * 1000);                // темп ≈ 20 000 рядків/с
  }
}
