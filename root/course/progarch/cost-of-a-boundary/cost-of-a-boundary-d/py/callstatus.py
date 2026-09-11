import enum
import time
import random
import uuid
from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")

class CallStatus(enum.Enum):
    """Тризначний статус результату перетину ненадійної межі."""
    SUCCESS = "success"              # Операція гарантовано виконана успішно
    FAILURE = "failure"              # Операція гарантовано відхилена без змін стану
    INDETERMINATE = "indeterminate"  # Стан операції невідомий (обрив каналу, таймаут)

@dataclass(frozen=True)
class CallResult(Generic[T]):
    """Результат виклику через архітектурну межу з контекстом стійкості."""
    status: CallStatus
    value: Optional[T] = None
    error: Optional[Exception] = None
    idempotency_key: Optional[str] = None

class CircuitState(enum.Enum):
    CLOSED = "closed"        # Штатний режим: виклики проходять
    OPEN = "open"            # Аварійний режим: виклики миттєво блокуються
    HALF_OPEN = "half_open"  # Тестовий режим: пропускаємо один пробний виклик

class CircuitBreaker:
    """Кінцевий автомат захисту від каскадних відмов на межі."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 10.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    def allow_execution(self) -> bool:
        """Перевіряє, чи дозволено здійснити виклик через межу."""
        now = time.monotonic()
        if self.state == CircuitState.OPEN:
            if now - self.last_failure_time >= self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def record_success(self) -> None:
        """Фіксація успішного виклику: повернення в штатний стан."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Фіксація збою: перехід у розімкнений стан при досягненні порогу."""
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

def execute_with_resilience(
    operation: Callable[[], T],
    circuit_breaker: CircuitBreaker,
    deadline_monotonic: float,
    idempotency_key: Optional[str] = None,
    max_retries: int = 3,
    base_delay_seconds: float = 0.1,
    max_delay_seconds: float = 2.0,
) -> CallResult[T]:
    """Виконує операцію через ненадійну межу з повним апаратом стійкості."""
    key = idempotency_key or str(uuid.uuid4())
    attempt = 0

    while True:
        now = time.monotonic()
        # 1. Перевірка наскрізного дедлайну
        if now >= deadline_monotonic:
            return CallResult(
                status=CallStatus.INDETERMINATE if attempt > 0 else CallStatus.FAILURE,
                error=TimeoutError("Вичерпано загальний дедлайн виконання операції"),
                idempotency_key=key,
            )

        # 2. Перевірка стану Circuit Breaker
        if not circuit_breaker.allow_execution():
            return CallResult(
                status=CallStatus.FAILURE,
                error=RuntimeError("Circuit Breaker у стані OPEN: виклик заблоковано"),
                idempotency_key=key,
            )

        attempt += 1
        try:
            # 3. Виконання віддаленої операції
            result_val = operation()
            circuit_breaker.record_success()
            return CallResult(
                status=CallStatus.SUCCESS,
                value=result_val,
                idempotency_key=key,
            )
        except (ConnectionResetError, BrokenPipeError, TimeoutError) as network_err:
            # Невизначені відмови: стан сервера невідомий
            circuit_breaker.record_failure()
            if attempt > max_retries:
                return CallResult(
                    status=CallStatus.INDETERMINATE,
                    error=network_err,
                    idempotency_key=key,
                )
        except Exception as business_err:
            # Детермінована бізнес-відмова: повторювати немає сенсу
            return CallResult(
                status=CallStatus.FAILURE,
                error=business_err,
                idempotency_key=key,
            )

        # 4. Розрахунок експоненційного відступу з повним дрижанням (Full Jitter)
        exp_delay = min(max_delay_seconds, base_delay_seconds * (2 ** (attempt - 1)))
        jittered_delay = random.uniform(0.0, exp_delay)

        # Не чекаємо довше за залишок загального дедлайну
        remaining_time = deadline_monotonic - time.monotonic()
        if remaining_time <= 0:
            return CallResult(
                status=CallStatus.INDETERMINATE,
                error=TimeoutError("Дедлайн вичерпано під час очікування повтору"),
                idempotency_key=key,
            )

        time.sleep(min(jittered_delay, remaining_time))
