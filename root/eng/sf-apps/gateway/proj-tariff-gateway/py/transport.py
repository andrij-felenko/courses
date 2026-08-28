# http/transport.py — сира розмова з мережею + таймаут. Про тарифи не знає.
import asyncio, aiohttp
from dataclasses import dataclass
from typing import Any, Callable, Awaitable

class МережевийЗбій(Exception):     # обрив, таймаут — тимчасове
    pass

@dataclass
class СираВідповідь:
    статус: int
    тіло: Callable[[], Awaitable[Any]]

async def http_get(url: str, токен: str, таймаут_с: float = 3.0) -> СираВідповідь:
    заголовки = {"Authorization": f"Bearer {токен}"}
    сесія = aiohttp.ClientSession()
    try:
        # таймаут: не висіти вічно, якщо сервіс мовчить
        r = await сесія.get(url, headers=заголовки,
                            timeout=aiohttp.ClientTimeout(total=таймаут_с))
        return СираВідповідь(статус=r.status, тіло=r.json)
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        # обрив зʼєднання або таймаут — це ТИМЧАСОВЕ, кандидат на повтор
        raise МережевийЗбій(str(e))
    finally:
        await сесія.close()
