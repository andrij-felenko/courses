// fetchState — pull стану з API партнера. Ін'єкція, щоб тест міг підставити фейк.
export async function reconcileDevice(
  deviceId: string,
  fetchState: (id: string) => Promise<{ state: string; seq: number }>,
): Promise<void> {
  const truth = await fetchState(deviceId);           // джерело правди — партнерів API
  const cx = await pool.connect();
  try {
    const changed = await applyToTwin(cx,
      { device_id: deviceId, state: truth.state, seq: truth.seq });
    if (changed) {                                     // твін відставав → пуш його пропустив
      await notify({ device_id: deviceId, ...truth });
      console.warn(`звірка: дрейф на ${deviceId} виправлено → ${truth.state}`);
    }
  } finally {
    cx.release();
  }
}

// Раз на N хвилин — по всіх пристроях, що DH веде.
setInterval(async () => {
  for (const id of await trackedDevices())
    await reconcileDevice(id, fetchAcmeState).catch(console.error);
}, 5 * 60_000);
