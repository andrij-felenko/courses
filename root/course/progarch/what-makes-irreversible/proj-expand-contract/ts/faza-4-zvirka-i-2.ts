export async function readTempMilliC(
  db: Pool, readingId: number, flags: Flags,
): Promise<number> {
  const { rows: [row] } = await db.query<{ temp_c: number; temp_mc: number | null }>(
    `SELECT temp_c, temp_mc FROM readings WHERE id = $1`, [readingId],
  );
  if (flags.readFromNew) {
    // Нове — джерело правди; у «тіньовому» режимі звіряємо й скаржимось.
    if (flags.shadowCompare && row.temp_mc !== toMilliC(row.temp_c)) {
      log.warn(`divergence id=${readingId} new=${row.temp_mc} old=${toMilliC(row.temp_c)}`);
    }
    return row.temp_mc!;
  }
  // Прапорець вимкнено → СТАРЕ. Дорога назад — один тумблер.
  return toMilliC(row.temp_c);
}
