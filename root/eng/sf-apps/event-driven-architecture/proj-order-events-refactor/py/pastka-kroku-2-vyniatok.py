# НЕПРАВИЛЬНО: та сама шина, але БЕЗ try/except
def publish(self, type_: str, event: object) -> None:
    handlers = list(self._handlers[type_])

    async def run() -> None:
        for handler in handlers:
            await handler(event)   # впав? виняток осяде у Task, який ніхто
                                   # не чекає (`await`) — і ТИХО пропаде
    asyncio.create_task(run())
# place_order давно повернулась. Лист не пішов. У метриках чисто.
