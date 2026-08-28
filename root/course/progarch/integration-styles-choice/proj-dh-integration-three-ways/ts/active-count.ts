// billing/active-count.ts — білінг тримає з'єднання ДО БАЗИ ПРИСТРОЇВ
async function activeDeviceCount(devicesDb: Pool, homeId: number): Promise<number> {
  const { rows } = await devicesDb.query(
    `SELECT count(*)::int AS n
       FROM devices
      WHERE home_id = $1 AND active = true`,   // ← ім'я таблиці, колонки й зміст «active=true»
    [homeId],
  );
  return rows[0].n;
}
