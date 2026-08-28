export async function reconcile(db: Pool): Promise<[number, number]> {
  // Гейт: [скільки ще NULL, скільки розбіжностей]. Далі — лише коли ОБИДВА = 0.
  let nulls = 0, mismatches = 0, lastId = "0";
  for (;;) {
    const { rows } = await db.query<{ id: string; temp_c: number; temp_mc: number | null }>(
      `SELECT id, temp_c, temp_mc FROM readings
       WHERE id > $1 ORDER BY id LIMIT $2`,
      [lastId, 50_000],
    );
    if (rows.length === 0) break;
    for (const r of rows) {
      if (r.temp_mc === null) nulls++;
      else if (r.temp_mc !== toMilliC(r.temp_c)) mismatches++;  // ТОЙ САМИЙ перетвір
    }
    lastId = rows[rows.length - 1].id;
  }
  return [nulls, mismatches];
}
