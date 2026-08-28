import asyncio, random
import httpx

BASE_MS = 1_000        # база: 1 секунда
CAP_MS = 300_000       # стеля: 5 хвилин
MAX_ATTEMPTS = 10      # далі — здаємося (dead-letter)

def backoff_delay(attempt: int) -> float:
    """Скільки чекати перед спробою №attempt (0-based), у секундах: повне тремтіння."""
    window = min(CAP_MS, BASE_MS * 2 ** attempt)
    return random.uniform(0, window) / 1000.0        # random(0, window)

async def deliver_with_retry(url: str, d: SignedDelivery, delivery_id: str) -> bool:
    async with httpx.AsyncClient(timeout=10.0) as client:   # жорсткий тайм-аут
        for attempt in range(MAX_ATTEMPTS):
            if attempt > 0:
                await asyncio.sleep(backoff_delay(attempt - 1))
            try:
                res = await client.post(
                    url, content=d.body,
                    headers={**d.headers, "Idempotency-Key": delivery_id},
                )
                if res.is_success:                          # 2xx — доставлено
                    return True
                if 400 <= res.status_code < 500 and res.status_code != 429:
                    return False   # 4xx (крім 429) — наша помилка, повтор дарма
                # 5xx / 429 — тимчасово; падаємо у наступну ітерацію
            except httpx.RequestError:
                pass               # мережа/тайм-аут — тимчасово, повторюємо
    return False                   # спроби вичерпано
