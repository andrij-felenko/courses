"""
Головний фасад стійкого клієнтського шлюзу (Resilient External Gateway).
"""

import asyncio
import inspect
import time
from typing import Any, Callable, Optional, Union

import httpx

from gateway.bulkhead import Bulkhead
from gateway.circuit_breaker import CircuitBreaker
from gateway.models import (
    BulkheadConfig,
    BulkheadFullException,
    CallResult,
    CircuitBreakerConfig,
    CircuitBreakerOpenException,
    GatewayResponse,
    RetryConfig,
    TimeoutConfig,
)
from gateway.retry import retry_with_jitter


class ResilientClient:
    """
    Фасадний HTTP-шлюз, що об'єднує таймаути, Bulkhead, Circuit Breaker,
    Retry з Full Jitter та механізм керованої деградації (Fallback).
    """

    def __init__(
        self,
        http_client: Optional[httpx.AsyncClient] = None,
        bulkhead: Optional[Bulkhead] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_config: Optional[RetryConfig] = None,
        timeout_config: Optional[TimeoutConfig] = None,
    ) -> None:
        self._owns_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient()
        self._bulkhead = bulkhead or Bulkhead(BulkheadConfig())
        self._circuit_breaker = circuit_breaker or CircuitBreaker(CircuitBreakerConfig())
        self._retry_config = retry_config or RetryConfig()
        self._timeout_config = timeout_config or TimeoutConfig()

    @property
    def bulkhead(self) -> Bulkhead:
        """Семафорна перебірка."""
        return self._bulkhead

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Автомат запобіжника."""
        return self._circuit_breaker

    async def aclose(self) -> None:
        """Закриває підлеглий HTTP-клієнт, якщо він був створений фасадом."""
        if self._owns_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> "ResilientClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    async def _invoke_fallback(
        self,
        fallback: Optional[Union[Callable[[Exception], Any], Any]],
        exc: Exception,
        duration_ms: float,
    ) -> GatewayResponse:
        """Викликає обробник аварійної деградації та повертає безпечну відповідь."""
        if fallback is None:
            raise exc

        if callable(fallback):
            if inspect.iscoroutinefunction(fallback):
                fallback_data = await fallback(exc)
            else:
                fallback_data = fallback(exc)
        else:
            fallback_data = fallback

        return GatewayResponse(
            status_code=200,
            data=fallback_data,
            is_fallback=True,
            duration_ms=duration_ms,
            error_message=str(exc),
        )

    async def execute(
        self,
        method: str,
        url: str,
        fallback: Optional[Union[Callable[[Exception], Any], Any]] = None,
        **kwargs: Any,
    ) -> GatewayResponse:
        """
        Виконує HTTP-запит через повний конвеєр захисту:
        1. Перевірка місткості Bulkhead (відсікання надлишкових запитів).
        2. Перевірка Circuit Breaker (fail-fast у стані OPEN за 0 мс).
        3. Роздільні таймаути (connect, read) та дедлайн операції.
        4. Повторні спроби з експоненційним відступом і Full Jitter.
        5. Реєстрація метрик у ковзному вікні.
        6. Аварійний Fallback при будь-якій фінальній помилці.
        """
        start_time = time.monotonic()

        # 1. Захист циклу подій семафорною перебіркою Bulkhead
        try:
            async with self._bulkhead.acquire():
                # 2. Перевірка стану запобіжника Circuit Breaker
                try:
                    await self._circuit_breaker.check_permission()
                except CircuitBreakerOpenException as cbe:
                    elapsed_ms = (time.monotonic() - start_time) * 1000.0
                    return await self._invoke_fallback(fallback, cbe, elapsed_ms)

                # 3. Виконання запиту з контролем таймаутів та ретраями
                deadline = start_time + self._timeout_config.total_deadline_s
                request_timeout = httpx.Timeout(
                    connect=self._timeout_config.connect_timeout_s,
                    read=self._timeout_config.read_timeout_s,
                    write=self._timeout_config.read_timeout_s,
                    pool=self._timeout_config.connect_timeout_s,
                )

                async def _attempt_call() -> httpx.Response:
                    response = await self._http_client.request(
                        method,
                        url,
                        timeout=request_timeout,
                        **kwargs,
                    )
                    # 5xx-помилки вважаються збоєм зовнішнього провайдера
                    if response.status_code >= 500:
                        response.raise_for_status()
                    return response

                try:
                    response = await retry_with_jitter(
                        _attempt_call,
                        config=self._retry_config,
                        deadline=deadline,
                    )
                    elapsed = time.monotonic() - start_time
                    is_slow = elapsed > self._circuit_breaker.window._config.slow_call_duration_s

                    # Фіксуємо успішний результат
                    await self._circuit_breaker.record_result(
                        CallResult(is_success=True, duration_s=elapsed, is_slow=is_slow)
                    )

                    try:
                        data = response.json()
                    except Exception:
                        data = response.text

                    return GatewayResponse(
                        status_code=response.status_code,
                        data=data,
                        is_fallback=False,
                        duration_ms=elapsed * 1000.0,
                    )

                except Exception as call_err:
                    elapsed = time.monotonic() - start_time
                    # Фіксуємо помилку у вікні метрик запобіжника
                    await self._circuit_breaker.record_result(
                        CallResult(is_success=False, duration_s=elapsed, error=call_err)
                    )
                    return await self._invoke_fallback(fallback, call_err, elapsed * 1000.0)

        except BulkheadFullException as bfe:
            elapsed_ms = (time.monotonic() - start_time) * 1000.0
            return await self._invoke_fallback(fallback, bfe, elapsed_ms)
