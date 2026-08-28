LEASE, BEAT, HARD_CAP, MAX_TRIES = 30, 10, 5 * 60, 3

async def run_one(w: Deps, worker_id: str) -> bool:
    op = await w.store.claim(worker_id, LEASE)            # SELECT…SKIP LOCKED + UPDATE
    if op is None:
        return False                                     # черга порожня
    if op.attempt > MAX_TRIES:                            # падало забагато разів
        await w.store.finish(op.id, op.lease_id, "failed", None, {"code": "too_many_attempts"})
        return True

    deadline = time.monotonic() + HARD_CAP               # стеля на МОНОТОННОМУ годиннику
    fenced = asyncio.Event()
    progress = 0

    async def heartbeat():                               # ЗА ГОДИННИКОМ, не між шматками
        while not fenced.is_set():
            await asyncio.sleep(BEAT)
            mine = await w.store.heartbeat(op.id, op.lease_id, progress, LEASE)
            if not mine:                                 # 0 рядків → перехопили → фенс
                fenced.set()
                return
    beat = asyncio.create_task(heartbeat())

    try:
        for chunk in plan_chunks(op.request):
            if fenced.is_set() or time.monotonic() > deadline:
                return True                              # фенс/стеля — нічого не пишемо
            if await w.store.cancel_requested(op.id):
                await w.store.finish(op.id, op.lease_id, "canceled", None, None)
                return True
            await transcode(chunk)
            progress = chunk.percent                     # серцебиття прочитає при наступному тіку

        key = f"clips/{op.id}.mp4"                        # детермінований ключ → повтор перезапише об'єкт
        await w.objects.put(key, rendered_bytes(op.id))
        url = w.objects.signed_url(key, 15 * 60)         # підпис діє 15 хв
        result = {"url": url, "expiresAt": iso(time.time() + 15 * 60)}
        if await w.store.finish(op.id, op.lease_id, "succeeded", result, None):  # фенс у WHERE lease_id
            await w.notify.clip_ready(op.user_id, op.id) # пуш лише якщо ми справді закрили
        return True
    finally:
        fenced.set()
        await beat
