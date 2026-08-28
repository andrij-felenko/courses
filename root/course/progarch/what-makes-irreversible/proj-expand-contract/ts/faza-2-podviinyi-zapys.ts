// Одна формула переливу — ОДНЕ місце на весь проєкт.
// Її вживають і подвійний запис, і бекфіл, і звірка — інакше вони розійдуться.
export function toMilliC(tempC: number): number {
  return Math.round(tempC * 1000);              // 23.5 °C → 23500
}

export async function insertReading(
  db: Pool, deviceId: number, ts: Date, tempC: number,
): Promise<void> {
  // Пишемо в ОБИДВІ колонки в ОДНОМУ INSERT — один рядок, одна транзакція.
  await db.query(
    `INSERT INTO readings (device_id, ts, temp_c, temp_mc)
     VALUES ($1, $2, $3, $4)`,
    [deviceId, ts, tempC, toMilliC(tempC)],
  );
}
