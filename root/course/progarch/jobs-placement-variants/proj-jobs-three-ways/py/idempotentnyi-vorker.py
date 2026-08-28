async def transcode(pool, clip_id, encode, profile="h264-720p"):
    async with pool.connection() as conn:
        row = await (await conn.execute(
            "SELECT 1 FROM renditions WHERE clip_id=%s AND profile=%s",
            (clip_id, profile))).fetchone()
        if row:
            return                                  # дубль доставки — нічого не робимо
        path = await encode(clip_id, profile)       # дорогий кодек — лише коли справді треба
        await conn.execute(
            "INSERT INTO renditions (clip_id, profile, path) VALUES (%s,%s,%s) "
            "ON CONFLICT (clip_id, profile) DO NOTHING",
            (clip_id, profile, path))
