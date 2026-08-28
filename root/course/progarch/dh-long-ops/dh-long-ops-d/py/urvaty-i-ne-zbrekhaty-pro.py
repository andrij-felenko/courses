# Робітник у контексті Відео: рендерить шматками, між шматками — три обов'язки.
async def render_clip(op: ClipOperation, lease: Lease) -> None:
    deadline = monotonic_now() + 5 * 60           # тверда стеля тривалості, секунди
    for chunk in plan_chunks(op.request):
        if await is_canceled(op.id):
            return await finish(op, "canceled")           # передумав — стоп
        if monotonic_now() > deadline:
            return await finish(op, "failed", "timeout")
        await transcode(chunk)
        await lease.heartbeat()                           # «я живий» — оренду продовжено
        await set_progress(op.id, chunk.percent)          # клієнт бачить рух
    url = await put_to_object_store(op.id)                # результат у сховище
    await finish(op, "succeeded", {"url": url, "expires_at": in_15min()})
