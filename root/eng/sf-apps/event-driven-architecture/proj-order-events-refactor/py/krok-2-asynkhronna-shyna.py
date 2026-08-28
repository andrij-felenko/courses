import asyncio
from collections import defaultdict
from typing import Awaitable, Callable

AsyncHandler = Callable[[object], Awaitable[None]]

class AsyncEventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[AsyncHandler]] = defaultdict(list)

    def subscribe(self, type_: str, handler: AsyncHandler) -> None:
        self._handlers[type_].append(handler)

    # повертається ОДРАЗУ; обробники плануються окремою задачею
    def publish(self, type_: str, event: object) -> None:
        handlers = list(self._handlers[type_])

        async def run() -> None:
            for handler in handlers:
                try:
                    await handler(event)         # збій одного не валить видавця…
                except Exception as err:         # …ловимо тут
                    print(f"handler for {type_} failed: {err!r}")

        asyncio.create_task(run())               # планує й одразу віддає керування
