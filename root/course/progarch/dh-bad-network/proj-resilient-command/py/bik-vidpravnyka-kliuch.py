import asyncio, time, uuid, random
import httpx  # ідіоматичний асинхронний HTTP-клієнт

class RetryableError(Exception): ...   # мережа, таймаут, 5xx, 429 — «не знаю», варте повтору
class TerminalError(Exception): ...    # 4xx — команда негодяща, повтор не врятує

# Одна спроба зі СВОЄЮ стелею. Ключ їде заголовком Idempotency-Key.
async def post(client: httpx.AsyncClient, url: str, cmd: dict, key: str, timeout: float) -> dict:
    try:
        r = await client.post(url, json=cmd,
                              headers={"Idempotency-Key": key},  # ключ у заголовку
                              timeout=timeout)                    # стеля саме цієї спроби
    except httpx.TransportError as e:              # обрив / таймаут / DNS — «не знаю»
        raise RetryableError(str(e)) from e
    if r.status_code >= 500 or r.status_code == 429:
        raise RetryableError(str(r.status_code))   # мине
    if r.status_code >= 400:
        raise TerminalError(str(r.status_code))    # вирок команді
    return r.json()

async def send_command(client: httpx.AsyncClient, url: str, cmd: dict) -> dict:
    key = uuid.uuid4().hex                 # ОДИН ключ на команду — крізь усі спроби
    deadline = time.monotonic() + 10.0     # весь бюджет 10 с, МОНОТОННИЙ годинник
    backoff = 0.5
    while True:
        left = deadline - time.monotonic()
        if left <= 0:
            raise RetryableError("бюджет вичерпано — чесне «не знаю»")
        try:
            return await post(client, url, cmd, key, timeout=min(left, 3.0))
        except TerminalError:
            raise                          # 4xx — повторювати нема сенсу
        except RetryableError:
            pause = min(backoff + random.random() * backoff,
                        deadline - time.monotonic())
            if pause <= 0:
                raise RetryableError("бюджет вичерпано перед повтором")
            await asyncio.sleep(pause)     # відступ + розкид
            backoff *= 2                    # 0.5 → 1 → 2 → 4 с
