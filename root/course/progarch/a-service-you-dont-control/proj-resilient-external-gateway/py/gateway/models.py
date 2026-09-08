"""
Моделі даних, конфігурації та структури станів стійкого асинхронного шлюзу.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class CircuitState(str, Enum):
    """Стани скінченного автомата запобіжника (Circuit Breaker)."""
    CLOSED = "CLOSED"        # Нормальний стан: запити проходять без перешкод
    OPEN = "OPEN"            # Аварійний стан: миттєва відсічка навантаження (fail-fast)
    HALF_OPEN = "HALF_OPEN"  # Зондування: обмежена кількість запитів для перевірки відновлення


class ResilienceException(Exception):
    """Базовий клас винятків контуру стійкості шлюзу."""
    pass


class BulkheadFullException(ResilienceException):
    """Викидається при перевищенні ліміту одночасних викликів у Bulkhead."""
    pass


class CircuitBreakerOpenException(ResilienceException):
    """Викидається при спробі виконання виклику через розімкнений запобіжник."""
    pass


class ServiceUnavailableException(ResilienceException):
    """Викидається у разі остаточної невдачі виклику після вичерпання ретраїв."""
    pass


@dataclass(frozen=True)
class BulkheadConfig:
    """Конфігурація семафорної перебірки (Bulkhead)."""
    max_concurrent: int = 5         # Максимальна кількість одночасних активних запитів
    max_wait_ms: float = 0.0        # Час очікування місця в черзі (0.0 — миттєвий fail-fast)


@dataclass(frozen=True)
class SlidingWindowConfig:
    """Конфігурація ковзного вікна оцінки надійності."""
    window_size: int = 10           # Розмір кільцевого буфера викликів
    min_call_threshold: int = 5     # Мінімальна вибірка N_min для усунення дисперсії малих вибірок
    failure_rate_threshold: float = 0.5  # Поріг відмов theta (50%), при якому ланцюг розмикається
    slow_call_rate_threshold: float = 0.8 # Поріг частки повільних відповідей
    slow_call_duration_s: float = 1.0     # Тривалість запиту, що класифікується як повільна


@dataclass(frozen=True)
class CircuitBreakerConfig:
    """Конфігурація запобіжника (Circuit Breaker)."""
    recovery_timeout_s: float = 1.5       # Пауза охолодження перед спробою перейти в HALF_OPEN
    half_open_probe_quota: int = 2        # Кількість тестових запитів під час зондування
    window: SlidingWindowConfig = field(default_factory=SlidingWindowConfig)


@dataclass(frozen=True)
class RetryConfig:
    """Параметри повторних спроб з експоненційним відступом і Full Jitter."""
    max_retries: int = 3            # Максимальна кількість повторів
    base_delay_s: float = 0.05      # Початковий відступ
    max_delay_s: float = 1.0        # Верхня межа затримки між спробами
    jitter: bool = True             # Використання рандомізованого тремтіння


@dataclass(frozen=True)
class TimeoutConfig:
    """Трирівнева конфігурація таймаутів та часових бюджетів."""
    connect_timeout_s: float = 0.5  # Таймаут встановлення TCP-з'єднання
    read_timeout_s: float = 1.5     # Таймаут очікування даних із сокета
    total_deadline_s: float = 3.0   # Загальний дедлайн на всю операцію включно з ретраями


@dataclass
class CallResult:
    """Результат виконання окремого HTTP-виклику."""
    is_success: bool
    duration_s: float
    is_slow: bool = False
    error: Optional[Exception] = None


@dataclass
class GatewayResponse:
    """Канонічна відповідь шлюзу для вищого бізнес-шару."""
    status_code: int
    data: Any = None
    is_fallback: bool = False
    duration_ms: float = 0.0
    error_message: Optional[str] = None
