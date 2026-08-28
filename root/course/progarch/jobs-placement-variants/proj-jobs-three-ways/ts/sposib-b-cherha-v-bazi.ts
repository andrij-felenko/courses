import { Pool } from "pg";

async function uploadClip(pool: Pool, homeId: number, url: string): Promise<number> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const { rows } = await client.query(
      "INSERT INTO clips (home_id, url) VALUES ($1, $2) RETURNING id",
      [homeId, url]);
    const clipId = rows[0].id;
    await client.query(
      "INSERT INTO jobs (type, payload) VALUES ('transcode', $1::jsonb)",
      [JSON.stringify({ clipId })]);
    await client.query("COMMIT");     // кліп І задача лягають разом — або жоден
    return clipId;
  } catch (e) {
    await client.query("ROLLBACK");   // відкотилось — задачі теж нема, ніби й не було
    throw e;
  } finally {
    client.release();
  }
}
