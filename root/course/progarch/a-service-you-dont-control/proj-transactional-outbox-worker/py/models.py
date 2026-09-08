"""
Моделі даних, статуси та конфігурації для надійного Transactional Outbox.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class OutboxStatus(str, Enum):
    """Стани життєвого циклу події в таблиці Transactional Outbox."""
    PENDING = "PENDING"          # Очікує первинної вибірки або наступної спроби
    PROCESSING = "PROCESSING"    # Захоплено воркером під ексклюзивним локом/лізингом
    PROCESSED = "PROCESSED"      # Успішно доставлено зовнішній службі (кінцевий стан)
    DEAD_LETTER = "DEAD_LETTER"  # Вичерпано спроби або фатальна помилка (карантин)


class OutboxException(Exception):
    """Базовий виняток для підсистеми Transactional Outbox."""
    pass


class RetryableError(OutboxException):
    """
    Транзитний збій (5xx, 429, мережевий таймаут, скидання TCP-з'єднання).
    Операцію безпечно повторити з експоненційним відступом.
    """
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class NonRetryableError(OutboxException):
    """
    Фатальна помилка клієнта (4xx, крім 429), невалідне тіло або бізнес-відхилення.
    Повтори марні, повідомлення негайно скеровується в Dead Letter Queue (DLQ).
    """
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class OutboxEvent:
    """
    Модель події аутбоксу, збереженої в реляційній базі даних.
    Гарантує збереження наміру передачі даних сторонньому сервісу.
    """
    id: str                                  # Унікальний UUID запису
    aggregate_type: str                      # Тип доменного агрегату (наприклад, "Order")
    aggregate_id: str                        # Ідентифікатор сутності ("order-42")
    event_type: str                          # Тип події ("PaymentAuthorized")
    payload: dict[str, Any]                  # JSONB-корисне навантаження
    idempotency_key: str                     # Детермінований ключ ідемпотентності
    status: OutboxStatus = OutboxStatus.PENDING
    attempts: int = 0                        # Поточна кількість виконаних спроб
    max_attempts: int = 3                    # Поріг відсікання в DLQ
    next_retry_at: float = 0.0               # Unix timestamp наступного дозволеного виклику
    locked_at: Optional[float] = None        # Час захоплення блокування (для контролю лізингу)
    locked_by: Optional[str] = None          # Ідентифікатор воркера-власника блокування
    last_error: Optional[str] = None         # Текст останнього збою для діагностики
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class WorkerConfig:
    """Параметри конфігурації асинхронного диспетчера Outbox."""
    batch_size: int = 10                     # Розмір пачки для SELECT ... SKIP LOCKED
    poll_interval_s: float = 0.2             # Інтервал опитування БД при порожній черзі
    max_concurrent_tasks: int = 5            # Семафорний ліміт паралельних HTTP-запитів
    lease_timeout_s: float = 3.0             # Тривалість оренди рядка (захист від краху воркера)
    max_retries: int = 3                     # Максимальна кількість повторів для транзитних збоїв
    base_delay_s: float = 0.1                # Початкова затримка для алгоритму Full Jitter
    max_delay_s: float = 2.0                 # Верхня межа відступу між спробами
    http_timeout_s: float = 1.5              # Загальний дедлайн на окремий HTTP-виклик


@dataclass
class HttpResponse:
    """Уніфікований результат виконання вихідного HTTP-виклику."""
    status_code: int
    body: dict[str, Any]
    is_success: bool
    duration_ms: float
