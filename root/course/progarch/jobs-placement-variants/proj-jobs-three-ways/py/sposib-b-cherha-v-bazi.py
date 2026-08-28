from psycopg_pool import AsyncConnectionPool
from psycopg.types.json import Jsonb

async def upload_clip(pool: AsyncConnectionPool, home_id: int, url: str) -> int:
    async with pool.connection() as conn:          # транзакція — контекст
        async with conn.transaction():             # вихід без винятку → COMMIT
            row = await (await conn.execute(
                "INSERT INTO clips (home_id, url) VALUES (%s, %s) RETURNING id",
                (home_id, url))).fetchone()
            clip_id = row[0]
            await conn.execute(
                "INSERT INTO jobs (type, payload) VALUES ('transcode', %s)",
                (Jsonb({"clipId": clip_id}),))     # виняток усередині → ROLLBACK усього
        return clip_id
