import asyncio

async def sleep(ms): await asyncio.sleep(ms / 1000)
def backoff(n): return full_jitter(n)     # відступ із джитером — деталі в іншому кроці

async def tick(p, saga, steps):
    if saga.status != "running":
        return saga
    pivot = next(i for i, s in enumerate(steps) if s.kind is Kind.PIVOT)

    if saga.dir == "back":                            # ── задкуємо, відкочуючи ──
        if saga.cursor < 0:
            saga.status = "aborted"; await p.persist(saga); return saga
        step = steps[saga.cursor]
        await apply_step(p, saga, step, "back")       # компенсація + cursor-- атомарно
        if saga.cursor < 0: saga.status = "aborted"   # відкотили все → чисте скасування
        await p.persist(saga); return saga

    # ── ідемо вперед ──
    if saga.cursor >= len(steps):                     # курсор ЗА останнім кроком = ЗАВЕРШЕНО (термінал з курсора)
        saga.status = "done"; await p.persist(saga); return saga   # ідемпотентний сторож: закриває щілину крах-на-терміналі
    step = steps[saga.cursor]                         # тепер гарантовано в межах
    try:
        await apply_step(p, saga, step, "forward")    # ефект + cursor++ атомарно
        saga.attempts = 0
        if saga.cursor >= len(steps): saga.status = "done"   # ступили за останній → done уже цього такту
        await p.persist(saga)
    except WaitingForHuman as w:                      # awaitClaim паркується — не невдача
        saga.status = "waiting"; saga.deadline = w.until; await p.persist(saga)
    except Exception as err:
        if saga.cursor > pivot:                       # ПІСЛЯ півота: повторюй, тоді DLQ
            saga.attempts += 1
            if saga.attempts > MAX_ATTEMPTS:          # затято застрягло → мертва черга
                saga.status = "stuck"; await p.persist(saga); await p.alert(saga, step, err)
            else:
                await p.persist(saga); await sleep(backoff(saga.attempts))
        else:                                         # ДО півота: розворот
            saga.dir = "back"; saga.cursor -= 1; await p.persist(saga)
    return saga

async def drive(p, sid, steps):
    saga = await p.load(sid)
    while saga.status == "running":
        saga = await tick(p, saga, steps)
    return saga
