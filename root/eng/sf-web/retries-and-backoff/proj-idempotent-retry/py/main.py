import time
import uuid
import random
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class CircuitState(Enum):
    CLOSED = 1
    OPEN = 2
    HALF_OPEN = 3


@dataclass
class RetryConfig:
    max_retries: int = 3
    base_backoff: float = 0.1       # 100 мс
    max_backoff: float = 10.0       # 10 с
    budget_ratio: float = 0.2       # максимум 20% трафіку на повтори
    cb_failure_threshold: float = 0.5
    cb_recovery_timeout: float = 15.0  # 15 с остигання
    cb_min_requests: int = 10


class ResilientHttpClient:
    """Виробничий HTTP-клієнт із повним контуром самозахисту."""

    def __init__(self, config: Optional[RetryConfig] = None):
        self.cfg = config or RetryConfig()
        self._lock = threading.Lock()

        # Token Bucket для бюджету повторів
        self._tokens: float = 10.0
        self._max_tokens: float = 50.0

        # Circuit Breaker стан
        self._cb_state = CircuitState.CLOSED
        self._cb_last_state_change = time.monotonic()
        self._cb_window_success = 0
        self._cb_window_failure = 0

    def _allow_request(self) -> bool:
        """Перевірка стану запобіжника (Circuit Breaker)."""
        with self._lock:
            now = time.monotonic()
            if self._cb_state == CircuitState.OPEN:
                if now - self._cb_last_state_change > self.cfg.cb_recovery_timeout:
                    self._cb_state = CircuitState.HALF_OPEN
                    self._cb_last_state_change = now
                    return True
                return False
            return True

    def _record_result(self, success: bool) -> None:
        """Оновлення метрик запобіжника та бюджету повторів."""
        with self._lock:
            if success:
                self._tokens = min(self._max_tokens, self._tokens + self.cfg.budget_ratio)
                self._cb_window_success += 1
                if self._cb_state == CircuitState.HALF_OPEN:
                    self._cb_state = CircuitState.CLOSED
                    self._cb_window_success = 0
                    self._cb_window_failure = 0
            else:
                self._cb_window_failure += 1
                total = self._cb_window_success + self._cb_window_failure
                if total >= self.cfg.cb_min_requests:
                    fail_rate = self._cb_window_failure / total
                    if fail_rate >= self.cfg.cb_failure_threshold:
                        self._cb_state = CircuitState.OPEN
                        self._cb_last_state_change = time.monotonic()
                        self._cb_window_success = 0
                        self._cb_window_failure = 0

    def _can_retry(self) -> bool:
        """Перевірка наявності токенів у бюджеті повторів."""
        with self._lock:
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            return False

    def _compute_backoff(self, attempt: int, server_retry_after: Optional[float] = None) -> float:
        """Обчислення Full Jitter з урахуванням Retry-After."""
        if server_retry_after is not None and server_retry_after > 0:
            # Поважаємо вимогу сервера плюс невеликий позитивний джитер (0..100 мс)
            return server_retry_after + random.uniform(0.0, 0.1)

        upper_bound = min(self.cfg.max_backoff, self.cfg.base_backoff * (2 ** attempt))
        return random.uniform(0.0, upper_bound)

    def execute_request(self, method: str, url: str, headers: Dict[str, str], body: Optional[bytes] = None) -> Dict[str, Any]:
        """Виконання запиту з повним циклом повторів та ідемпотентності."""
        if not self._allow_request():
            raise RuntimeError("Circuit Breaker OPEN: виклики тимчасово заблоковано")

        # Прикріплюємо Idempotency-Key для мутуючих операцій
        req_headers = dict(headers)
        if method.upper() in ("POST", "PATCH", "PUT") and "Idempotency-Key" not in req_headers:
            req_headers["Idempotency-Key"] = str(uuid.uuid4())

        for attempt in range(self.cfg.max_retries + 1):
            try:
                # Симуляція виконання реального виклику через socket / requests
                response = self._raw_http_call(method, url, req_headers, body)
                status = response["status"]

                if status < 400:
                    self._record_result(success=True)
                    return response

                # Класифікація помилок: 429 та 5xx (крім деяких клієнтських) вважаємо минущими
                is_transient = status in (429, 502, 503, 504)
                if not is_transient or attempt == self.cfg.max_retries:
                    self._record_result(success=False)
                    return response

                # Перевірка бюджету повторів
                if not self._can_retry():
                    self._record_result(success=False)
                    raise RuntimeError(f"Retry Budget Exhausted: спробу {attempt + 1} відхилено")

                retry_after = response.get("retry_after_seconds")
                delay = self._compute_backoff(attempt, retry_after)
                time.sleep(delay)

            except (ConnectionError, TimeoutError) as net_err:
                if attempt == self.cfg.max_retries or not self._can_retry():
                    self._record_result(success=False)
                    raise net_err

                delay = self._compute_backoff(attempt)
                time.sleep(delay)

        raise RuntimeError("Вичерпано всі спроби повтору")

    def _raw_http_call(self, method: str, url: str, headers: Dict[str, str], body: Optional[bytes]) -> Dict[str, Any]:
        # Заглушка для демонстрації: повертає код стану
        return {"status": 200, "headers": {}, "body": b'{"status": "ok"}'}
