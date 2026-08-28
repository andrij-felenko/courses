# fetch_state — pull стану з API партнера. Ін'єкція, щоб тест міг підставити фейк.
async def reconcile_device(pool, device_id, fetch_state) -> None:
    truth = await fetch_state(device_id)              # джерело правди — партнерів API
    async with pool.acquire() as cx:
        changed = await apply_to_twin(cx,
            {"device_id": device_id, "state": truth["state"], "seq": truth["seq"]})
        if changed:                                   # твін відставав → пуш його пропустив
            await _notify({"device_id": device_id, **truth})
            log.warning("звірка: дрейф на %s виправлено → %s", device_id, truth["state"])

# Раз на N хвилин — по всіх пристроях, що DH веде.
async def reconcile_loop(pool, fetch_state, every=300):
    while True:
        for device_id in await tracked_devices(pool):
            try:
                await reconcile_device(pool, device_id, fetch_state)
            except Exception as e:
                log.error("звірка %s: %s", device_id, e)
        await asyncio.sleep(every)
