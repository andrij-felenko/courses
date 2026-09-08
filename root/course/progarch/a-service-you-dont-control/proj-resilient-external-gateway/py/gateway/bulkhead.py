"""
Семафорна перебірка (Bulkhead) для ізоляції ресурсів та обмеження паралелізму.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from gateway.models import BulkheadConfig, BulkheadFullException


class Bulkhead:
    """
    Обмежує максимальну кількість одночасних мережевих запитів.
    
    Захищає цикл подій asyncio та системні ресурси (пул сокетів, файлові
    дескриптори) від вичерпання за законом Літтла (L = lambda * W).
    """

    def __init__(self, config: BulkheadConfig = BulkheadConfig()) -> None:
        self._config = config
        self._active_calls = 0
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(config.max_concurrent)

    @property
    def active_calls(self) -> int:
        """Поточна кількість запитів у процесі виконання."""
        return self._active_calls

    @property
    def max_concurrent(self) -> int:
        """Максимальна місткість перебірки."""
        return self._config.max_concurrent

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[None]:
        """
        Асинхронний контекстний менеджер для резервування слота в перебірці.
        
        Якщо місткість вичерпана, миттєво відхиляє запит без блокування циклу подій.
        """
        async with self._lock:
            if self._active_calls >= self._config.max_concurrent:
                raise BulkheadFullException(
                    f"Перебірку Bulkhead переповнено: активних {self._active_calls}/"
                    f"{self._config.max_concurrent} запитів (захист циклу подій)"
                )
            self._active_calls += 1

        try:
            yield
        finally:
            async with self._lock:
                self._active_calls -= 1
