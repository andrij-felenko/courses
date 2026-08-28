# http/retry.py — повтор ЛИШЕ тимчасового, з експоненційним відкатом + jitter.
import asyncio, random
from http.transport import МережевийЗбій

async def з_повтором(спроба, разів: int = 3, базова_с: float = 0.2):
    for n in range(разів):
        try:
            return await спроба()
        except МережевийЗбій:
            # повторюємо ЛИШЕ тимчасове; доменні помилки сюди не долітають
            if n >= разів - 1:
                raise
            пауза = базова_с * 2 ** n * (0.5 + random.random() * 0.5)  # відкат + jitter
            await asyncio.sleep(пауза)
