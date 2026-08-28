import asyncio

async def fan_out(subscribers, payload, concurrency: int = 20):
    """Розкладаємо подію на НЕЗАЛЕЖНІ одиниці й женемо пулом."""
    queue: asyncio.Queue = asyncio.Queue()
    for s in subscribers:
        job = DeliveryJob(url=s["url"], payload=payload)
        await queue.put((job, s["secret"]))

    async def worker():
        while not queue.empty():
            job, secret = await queue.get()
            signed = sign_webhook(job.payload, secret)
            ok = await deliver_with_retry(job.url, signed, job.delivery_id)
            if not ok:
                await dead_letter(job)          # вичерпав спроби → мертві листи
            queue.task_done()

    # Пул робітників: рівно `concurrency` доставок «у польоті» водночас.
    await asyncio.gather(*(worker() for _ in range(concurrency)))
    # мрець тримає СВОГО робітника; інші не чекають на нього
