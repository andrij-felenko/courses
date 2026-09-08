"""
Повторні спроби з експоненційним відступом та випадковим тремтінням (Full Jitter).
"""

import asyncio
import random
import time
from typing import Awaitable, Callable, Optional, TypeVar

from gateway.models import (
    BulkheadFullException,
    CircuitBreakerOpenException,
    RetryConfig,
)

T = TypeVar("T")


def is_default_retryable(exc: Exception) -> bool:
    """
    Визначає, чи є виняток транзитним (тимчасовим) і вартим повторної спроби.
    
    Архітектурне правило: помилки відсікання контуру (CircuitBreakerOpen, BulkheadFull)
    або фатальні клієнтські помилки 4xx НЕ підлягають повторенню!
    """
    if isinstance(exc, (CircuitBreakerOpenException, BulkheadFullException)):
        return False
    return True


async def retry_with_jitter(
    operation: Callable[[], Awaitable[T]],
    config: RetryConfig = RetryConfig(),
    is_retryable: Callable[[Exception], bool] = is_default_retryable,
    deadline: Optional[float] = None,
) -> T:
    """
    Виконує асинхронну операцію з експоненційним відступом і Full Jitter.
    
    Формула випадкового тремтіння:
        delay = uniform(0, min(max_delay, base_delay * 2^attempt))
    
    Це розсіює пікові сплески навантаження («шторм повторів») і руйнує фазову
    синхронізацію клієнтів при відновленні відмовної служби.
    """
    attempt = 0
    while True:
        try:
            return await operation()
        except Exception as exc:
            if attempt >= config.max_retries or not is_retryable(exc):
                raise

            # Розрахунок експоненційного інтервалу
            exp_cap = min(config.max_delay_s, config.base_delay_s * (2 ** attempt))
            delay = random.uniform(0.0, exp_cap) if config.jitter else exp_cap

            # Контроль загального часового бюджету операції
            if deadline is not None and (time.monotonic() + delay) > deadline:
                raise TimeoutError(
                    f"Вичерпано загальний дедлайн операції перед черговою спробою {attempt + 1}"
                ) from exc

            await asyncio.sleep(delay)
            attempt += 1
