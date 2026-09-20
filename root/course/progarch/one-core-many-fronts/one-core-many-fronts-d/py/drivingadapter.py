import asyncio
import logging
from typing import Any, Coroutine, Protocol, Sequence, TypeVar

T = TypeVar("T")
logger = logging.getLogger("shutdown")

# Контракт зупинки драйвуючого адаптера
class DrivingAdapter(Protocol):
    @property
    def name(self) -> str: ...
    async def stop(self) -> None: ...

# Контракт керованого адаптера сховища або зовнішнього з'єднання
class DisposableResource(Protocol):
    @property
    def name(self) -> str: ...
    async def close(self) -> None: ...

# Відстежувач активних операцій усередині прикладного ядра
class ActiveOperationsTracker:
    def __init__(self) -> None:
        self._active_count = 0
        self._drain_event = asyncio.Event()
        self._drain_event.set()

    @property
    def count(self) -> int:
        return self._active_count

    async def track(self, coro: Coroutine[Any, Any, T]) -> T:
        self._active_count += 1
        self._drain_event.clear()
        try:
            return await coro
        finally:
            self._active_count -= 1
            if self._active_count == 0:
                self._drain_event.set()

    async def wait_for_drain(self, timeout_seconds: float) -> bool:
        if self._active_count == 0:
            return True
        try:
            await asyncio.wait_for(self._drain_event.wait(), timeout=timeout_seconds)
            return True
        except asyncio.TimeoutError:
            return False

# Координована узгоджена зупинка в композиційному корені
async def graceful_shutdown(
    adapters: Sequence[DrivingAdapter],
    tracker: ActiveOperationsTracker,
    resources: Sequence[DisposableResource],
    timeout_seconds: float = 10.0,
) -> int:
    # Фаза 1: закриття мережевих сокетів і зупинка читання з черг
    async def stop_adapter(adapter: DrivingAdapter) -> None:
        try:
            await adapter.stop()
        except Exception as exc:
            logger.error("Збій під час зупинки адаптера %s: %s", adapter.name, exc)

    await asyncio.gather(*(stop_adapter(a) for a in adapters), return_exceptions=True)

    # Фаза 2: очікування завершення активних прикладних сценаріїв
    drained = await tracker.wait_for_drain(timeout_seconds)

    # Фаза 3: закриття з'єднань із базами даних та вивільнення дескрипторів
    has_errors = not drained
    for resource in resources:
        try:
            await resource.close()
        except Exception as exc:
            logger.error("Збій під час закриття ресурсу %s: %s", resource.name, exc)
            has_errors = True

    return 1 if has_errors else 0
