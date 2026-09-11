import asyncio
import time
from typing import Any, Callable, Coroutine, List, TypeVar

T = TypeVar("T")

async def hedged_call(
    replicas: List[Callable[[], Coroutine[Any, Any, T]]],
    hedge_delay_seconds: float,
    overall_timeout_seconds: float,
) -> T:
    """Виконує підстрахований виклик до пулу реплік для зрізання хвоста затримки."""
    if not replicas:
        raise ValueError("Список реплік не може бути порожнім")

    tasks: List[asyncio.Task] = []
    # Створюємо завдання для первинної репліки
    primary_task = asyncio.create_task(replicas[0]())
    tasks.append(primary_task)

    deadline = time.monotonic() + overall_timeout_seconds
    replica_idx = 1

    try:
        while tasks:
            # Час очікування до наступної підстраховки або вичерпання дедлайну
            now = time.monotonic()
            if now >= deadline:
                raise TimeoutError("Вичерпано загальний дедлайн виконання віялового запиту")

            # Чекаємо або hedge_delay, або завершення будь-якого з запущених завдань
            timeout_for_step = min(hedge_delay_seconds, deadline - now)
            done, pending = await asyncio.wait(
                tasks,
                timeout=timeout_for_step,
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Якщо якесь завдання успішно завершилося — повертаємо його результат
            for completed_task in done:
                try:
                    return completed_task.result()
                except Exception:
                    # Помилку окремої репліки ігноруємо, якщо є інші живі завдання
                    tasks.remove(completed_task)

            # Якщо жодне завдання не повернуло успіху й минув hedge_delay — запускаємо дублера
            if replica_idx < len(replicas) and time.monotonic() < deadline:
                backup_task = asyncio.create_task(replicas[replica_idx]())
                tasks.append(backup_task)
                replica_idx += 1

        raise RuntimeError("Усі опитані репліки завершилися аварійно")
    finally:
        # Обов'язково скасовуємо всі незавершені фонові запити, щоб не марнувати ресурси
        for t in tasks:
            if not t.done():
                t.cancel()
