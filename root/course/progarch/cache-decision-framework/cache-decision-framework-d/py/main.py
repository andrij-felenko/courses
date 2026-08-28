async def get_device_profile(id: str) -> Profile:
    key = f"device:{id}"
    hit = await cache.get(key)
    if hit:
        return Profile.parse(hit)                 # влучили — швидко, та, можливо, несвіже

    fresh = await db.load_profile(id)             # промах — ідемо до джерела
    await cache.set(key, fresh.dump(), ttl=60)    # TTL = бюджет несвіжості
    return fresh
    # пастка: якщо ключ протух і тисяча читань промахнулись РАЗОМ,
    # усі тисяча ринуть у джерело одночасно — «гримуча отара» (ворота 5)

async def rename_device(id: str, name: str) -> None:
    await db.rename(id, name)
    await cache.delete(f"device:{id}")            # інвалідація на запис: копію треба скинути
