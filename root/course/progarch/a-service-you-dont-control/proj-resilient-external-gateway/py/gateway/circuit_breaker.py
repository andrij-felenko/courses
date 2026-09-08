"""
Скінченний автомат запобіжника (Circuit Breaker) для запобігання каскадним аваріям.
"""

import asyncio
import time
from typing import Optional

from gateway.models import (
    CallResult,
    CircuitBreakerConfig,
    CircuitBreakerOpenException,
    CircuitState,
)
from gateway.sliding_window import SlidingWindow


class CircuitBreaker:
    """
    Скінченний автомат захисту (CLOSED -> OPEN -> HALF_OPEN -> CLOSED).
    
    Миттєво відсікає навантаження на зламаний зовнішній сервіс (fail-fast за 0 мс),
    надає йому час на охолодження та безпечно зондує відновлення невеликою квотою запитів.
    """

    def __init__(self, config: CircuitBreakerConfig = CircuitBreakerConfig()) -> None:
        self._config = config
        self._state = CircuitState.CLOSED
        self._window = SlidingWindow(config.window)
        self._opened_at: Optional[float] = None
        self._probe_count = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Поточний стан запобіжника."""
        return self._state

    @property
    def window(self) -> SlidingWindow:
        """Ковзне вікно метрик."""
        return self._window

    async def check_permission(self) -> bool:
        """
        Перевіряє, чи дозволено виконувати виклик до зовнішнього сервісу.
        
        Якщо запобіжник розімкнено (OPEN), негайно викидає CircuitBreakerOpenException,
        унеможливлюючи створення мережевого з'єднання та марнування ресурсів.
        """
        async with self._lock:
            now = time.monotonic()

            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                elapsed = now - (self._opened_at or 0.0)
                if elapsed >= self._config.recovery_timeout_s:
                    # Час охолодження сплив — переходимо до пробного зондування
                    self._state = CircuitState.HALF_OPEN
                    self._probe_count = 1
                    return True

                remaining = self._config.recovery_timeout_s - elapsed
                raise CircuitBreakerOpenException(
                    f"Запобіжник розімкнено (OPEN). Захист активний, охолодження ще {remaining:.2f}с"
                )

            if self._state == CircuitState.HALF_OPEN:
                if self._probe_count < self._config.half_open_probe_quota:
                    self._probe_count += 1
                    return True

                raise CircuitBreakerOpenException(
                    f"Запобіжник у стані HALF_OPEN: ліміт зондування "
                    f"({self._config.half_open_probe_quota}) вичерпано, очікування результатів"
                )

        return False

    async def record_result(self, result: CallResult) -> None:
        """
        Фіксує результат виконання запиту та здійснює переходи станів автомата.
        """
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                self._window.record(result)
                if self._window.should_trip():
                    self._state = CircuitState.OPEN
                    self._opened_at = time.monotonic()

            elif self._state == CircuitState.HALF_OPEN:
                if not result.is_success:
                    # Навіть одна невдача під час зондування повертає запобіжник в OPEN
                    self._state = CircuitState.OPEN
                    self._opened_at = time.monotonic()
                    self._probe_count = 0
                else:
                    # Успішний пробний запит: якщо квота випробувань виконана, замикаємо ланцюг
                    if self._probe_count >= self._config.half_open_probe_quota:
                        self._state = CircuitState.CLOSED
                        self._window.reset()
                        self._probe_count = 0
                        self._opened_at = None
