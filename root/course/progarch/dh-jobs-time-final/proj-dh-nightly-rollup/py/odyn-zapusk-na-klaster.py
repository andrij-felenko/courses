class CronLease:
    def __init__(self, pool, name, me, ttl_sec=60):
        self.pool, self.name, self.me, self.ttl = pool, name, me, ttl_sec

    async def acquire(self) -> int | None:
        """Взяти лізу (вільну або прострочену). None — хтось інший тримає ЖИВУ."""
        row = await self.pool.fetchrow(
            """INSERT INTO cron_lease (name, holder, fence, expires_at)
               VALUES ($1, $2, 1, now() + make_interval(secs => $3))
               ON CONFLICT (name) DO UPDATE
                  SET holder = EXCLUDED.holder,
                      fence  = cron_lease.fence + 1,      -- новий власник → новий токен
                      expires_at = EXCLUDED.expires_at
                  WHERE cron_lease.expires_at < now()     -- лише якщо стара прострочена
               RETURNING fence""",
            self.name, self.me, self.ttl)
        return row["fence"] if row else None

    async def renew(self, fence: int) -> bool:
        """Продовжити СВОЮ живу лізу тим самим токеном. False — лізу втрачено, СТОП."""
        tag = await self.pool.execute(
            """UPDATE cron_lease SET expires_at = now() + make_interval(secs => $3)
                WHERE name = $1 AND holder = $2 AND fence = $4 AND expires_at >= now()""",
            self.name, self.me, self.ttl, fence)
        return tag.endswith(" 1")            # 'UPDATE 1'
