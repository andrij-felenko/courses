type Encode = (clipId: number, profile: string) => Promise<string>;

async function transcode(pool: Pool, clipId: number, encode: Encode,
                         profile = "h264-720p"): Promise<void> {
  // Ключ ідемпотентності: якщо результат уже є — ця доставка дубль, виходимо.
  const done = await pool.query(
    "SELECT 1 FROM renditions WHERE clip_id = $1 AND profile = $2", [clipId, profile]);
  if (done.rowCount) return;                       // уже перекодовано — no-op, дорогого кодека не чіпаємо

  const path = await encode(clipId, profile);      // ← єдине дороге місце

  await pool.query(
    `INSERT INTO renditions (clip_id, profile, path) VALUES ($1, $2, $3)
       ON CONFLICT (clip_id, profile) DO NOTHING`, // ← навіть гонка двох воркерів згортається в 1 рядок
    [clipId, profile, path]);
}
