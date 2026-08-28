import asyncio

async def prove_exactly_once():
    executions = 0
    async def execute(_cmd):
        nonlocal executions
        executions += 1               # рахуємо КОЖНЕ справжнє виконання
        await asyncio.sleep(0.05)     # «робота» триває — саме поки летять повтори
        return {"ok": True, "ran_at": executions}

    hub = IdempotentExecutor(execute)
    key = "unlock-front-7f3"          # ОДИН ключ на всі повтори однієї команди
    cmd = {"type": "unlock", "door": "front"}

    # Хвиля 1: 10 ОДНОЧАСНИХ повторів — гонка на in-flight.
    wave1 = await asyncio.gather(*(hub.handle(key, cmd) for _ in range(10)))
    # Хвиля 2: ще 5 повторів ПІСЛЯ завершення — влучають у пам'ять про завершене.
    wave2 = await asyncio.gather(*(hub.handle(key, cmd) for _ in range(5)))

    allr = wave1 + wave2
    assert executions == 1, f"мало бути рівно одне виконання, а було {executions}"
    assert all(r is allr[0] for r in allr), "усі 15 повторів — той самий об'єкт-результат"
    print(f"✓ 15 повторів (10 одночасних + 5 пізніх) → виконань: {executions}")

asyncio.run(prove_exactly_once())
