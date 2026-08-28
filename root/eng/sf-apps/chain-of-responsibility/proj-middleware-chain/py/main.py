import asyncio, time
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional


@dataclass
class Ctx:
    method: str
    path: str
    ip: str
    token: Optional[str] = None
    user: Optional[str] = None
    status: int = 404
    body: str = ""


Next = Callable[[], Awaitable[None]]
Middleware = Callable[[Ctx, Next], Awaitable[None]]


def compose(chain: list[Middleware]) -> Callable[[Ctx], Awaitable[None]]:
    """Список ланок → одна функція. Складаємо РАЗ, на старті."""
    async def run(ctx: Ctx) -> None:
        last_called = -1                       # лічильник ЦЬОГО запиту, не спільний

        async def dispatch(i: int) -> None:
            nonlocal last_called
            if i <= last_called:
                raise RuntimeError("call_next() покликано двічі")
            last_called = i
            if i == len(chain):
                return                         # дно: call_next() найглибшої ланки — це «нічого»
            await chain[i](ctx, lambda: dispatch(i + 1))

        await dispatch(0)

    return run


async def logger(ctx: Ctx, call_next: Next) -> None:
    t0 = time.perf_counter()                   # монотонний годинник, не time.time()
    try:
        await call_next()
    finally:                                   # finally — інакше виняток глибше лишиться без логу
        ms = (time.perf_counter() - t0) * 1000
        print(f"{ctx.method} {ctx.path} → {ctx.status} за {ms:.1f} мс")


hits: dict[str, int] = {}                      # стан ЛАНЦЮГА: спільний для всіх запитів — навмисно


async def rate_limit(ctx: Ctx, call_next: Next) -> None:
    hits[ctx.ip] = hits.get(ctx.ip, 0) + 1     # квоту списано ВЖЕ ТУТ, до будь-яких перевірок
    if hits[ctx.ip] > 3:
        ctx.status, ctx.body = 429, "Забагато запитів"
        return
    await call_next()


async def auth(ctx: Ctx, call_next: Next) -> None:
    if ctx.token != "good-token":
        ctx.status, ctx.body = 401, "Потрібен токен"
        return                                 # коротке замикання: call_next() не кличемо
    ctx.user = "olena"                         # стан ЗАПИТУ живе в ctx, не в самій ланці
    await call_next()


async def app(ctx: Ctx, call_next: Next) -> None:
    ctx.status, ctx.body = 200, f"Привіт, {ctx.user}"


handle = compose([logger, rate_limit, auth, app])   # зібрали РАЗ


async def main() -> None:
    for token in ["good-token", "bad", "good-token", "good-token"]:
        ctx = Ctx(method="GET", path="/profile", ip="10.0.0.7", token=token)
        await handle(ctx)
        print("   відповідь:", ctx.status, ctx.body)


asyncio.run(main())
