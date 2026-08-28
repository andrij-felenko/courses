import { Pool } from "pg";

class CronLease {
  constructor(private db: Pool, private name: string,
              private me: string, private ttlSec = 60) {}

  // Взяти лізу (вільну або прострочену). null — хтось інший тримає ЖИВУ.
  async acquire(): Promise<{ fence: number } | null> {
    const { rows } = await this.db.query(
      `INSERT INTO cron_lease (name, holder, fence, expires_at)
       VALUES ($1, $2, 1, now() + make_interval(secs => $3))
       ON CONFLICT (name) DO UPDATE
          SET holder = EXCLUDED.holder,
              fence  = cron_lease.fence + 1,          -- новий власник → новий токен
              expires_at = EXCLUDED.expires_at
          WHERE cron_lease.expires_at < now()         -- лише якщо стара прострочена
       RETURNING fence`,
      [this.name, this.me, this.ttlSec]);
    return rows.length ? { fence: Number(rows[0].fence) } : null;
  }

  // Продовжити СВОЮ живу лізу тим самим токеном. false — лізу втрачено, СТОП.
  async renew(fence: number): Promise<boolean> {
    const { rowCount } = await this.db.query(
      `UPDATE cron_lease SET expires_at = now() + make_interval(secs => $3)
        WHERE name = $1 AND holder = $2 AND fence = $4 AND expires_at >= now()`,
      [this.name, this.me, this.ttlSec, fence]);
    return rowCount === 1;
  }
}
