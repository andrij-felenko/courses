// billing/projection.ts — згортаємо ПОДІЮ у власну табличку
async function onDeviceEvent(db: Pool, e: DeviceEvent): Promise<void> {
  const active = e.type === "device.activated";
  await db.query(
    `INSERT INTO home_device_state (device_id, home_id, active, at)
     VALUES ($1, $2, $3, $4)
     ON CONFLICT (device_id) DO UPDATE
       SET active = EXCLUDED.active, at = EXCLUDED.at
       WHERE EXCLUDED.at > home_device_state.at`,   // дубль/стара подія → пустий хід
    [e.deviceId, e.homeId, active, e.at],
  );
}

// нарахування читає ВЛАСНУ табличку — ні виклику, ні чужої схеми, ні чужого «вгорі»
async function activeDeviceCount(db: Pool, homeId: number): Promise<number> {
  const { rows } = await db.query(
    `SELECT count(*)::int AS n
       FROM home_device_state
      WHERE home_id = $1 AND active = true`,
    [homeId],
  );
  return rows[0].n;
}
