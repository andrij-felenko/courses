"""
Верифікаційний тестовий стенд для перевірки стійкості шлюзу ResilientClient.
"""

import asyncio
import sys
import time
from typing import Any, Dict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx

from gateway.bulkhead import Bulkhead
from gateway.circuit_breaker import CircuitBreaker
from gateway.client import ResilientClient
from gateway.models import (
    BulkheadConfig,
    CircuitBreakerConfig,
    CircuitState,
    RetryConfig,
    SlidingWindowConfig,
    TimeoutConfig,
)


class MockExternalService:
    """Керований емулятор зовнішнього API для перевірки реакції на збої."""

    def __init__(self) -> None:
        self.status_code = 200
        self.delay_s = 0.0
        self.total_requests = 0

    async def handler(self, request: httpx.Request) -> httpx.Response:
        self.total_requests += 1
        if self.delay_s > 0:
            await asyncio.sleep(self.delay_s)

        if self.status_code >= 500:
            return httpx.Response(
                self.status_code,
                json={"error": "Внутрішня аварія зовнішнього партнера"},
                request=request,
            )

        return httpx.Response(
            200,
            json={"status": "success", "currency": "UAH/USD", "rate": 41.50},
            request=request,
        )


async def main() -> None:
    print("=" * 70)
    print(" ТЕСТУВАННЯ СТІЙКОГО АСИНХРОННОГО ШЛЮЗУ (RESILIENT EXTERNAL GATEWAY)")
    print("=" * 70)

    # 1. Налаштування емулятора зовнішнього партнера
    service_mock = MockExternalService()
    transport = httpx.MockTransport(service_mock.handler)
    http_client = httpx.AsyncClient(transport=transport, base_url="https://api.partner.ext")

    # 2. Конфігурація захисного контуру
    bulkhead = Bulkhead(BulkheadConfig(max_concurrent=3))
    breaker_cfg = CircuitBreakerConfig(
        recovery_timeout_s=0.6,
        half_open_probe_quota=2,
        window=SlidingWindowConfig(
            window_size=6,
            min_call_threshold=4,
            failure_rate_threshold=0.5,
            slow_call_duration_s=0.2,
        ),
    )
    circuit_breaker = CircuitBreaker(breaker_cfg)
    retry_cfg = RetryConfig(max_retries=2, base_delay_s=0.02, max_delay_s=0.1, jitter=True)
    timeout_cfg = TimeoutConfig(connect_timeout_s=0.2, read_timeout_s=0.5, total_deadline_s=1.0)

    # Запасні дані для деградації (кеш курсу валют)
    fallback_cache: Dict[str, Any] = {
        "status": "degraded_cached",
        "currency": "UAH/USD",
        "rate": 41.20,
        "note": "Дані з локального кешу через недоступність партнера",
    }

    async with ResilientClient(
        http_client=http_client,
        bulkhead=bulkhead,
        circuit_breaker=circuit_breaker,
        retry_config=retry_cfg,
        timeout_config=timeout_cfg,
    ) as gateway:

        # -------------------------------------------------------------
        # ЕТАП 1: Нормальна робота (стан CLOSED)
        # -------------------------------------------------------------
        print("\n[ЕТАП 1] Нормальна робота партнера (стан CLOSED)")
        service_mock.status_code = 200
        service_mock.delay_s = 0.0

        for i in range(1, 4):
            resp = await gateway.execute("GET", "/v1/rates", fallback=fallback_cache)
            print(f"  Запит {i}: status={resp.status_code}, fallback={resp.is_fallback}, "
                  f"rate={resp.data.get('rate')}, час={resp.duration_ms:.1f}мс")
            assert not resp.is_fallback, "Штатний запит не повинен повертати fallback!"
            assert resp.data["rate"] == 41.50

        assert gateway.circuit_breaker.state == CircuitState.CLOSED
        print("  -> Запобіжник стабільно у стані CLOSED.")

        # -------------------------------------------------------------
        # ЕТАП 2: Перевірка ізоляції семафорної перебірки (Bulkhead)
        # -------------------------------------------------------------
        print("\n[ЕТАП 2] Сплеск навантаження та семафорна перебірка Bulkhead")
        service_mock.delay_s = 0.08  # Штучна затримка, щоб запити наклалися у часі

        async def run_burst(idx: int) -> bool:
            r = await gateway.execute("GET", "/v1/rates", fallback=fallback_cache)
            return r.is_fallback

        # Запускаємо 8 одночасних запитів при ліміті Bulkhead = 3
        results = await asyncio.gather(*(run_burst(i) for i in range(8)))
        bulkhead_rejected = sum(1 for is_fb in results if is_fb)
        print(f"  Одночасних запитів: 8, ліміт: 3. Відсічено перебіркою у fallback: {bulkhead_rejected}")
        assert bulkhead_rejected > 0, "Bulkhead мусить відсікати надлишкове навантаження!"
        service_mock.delay_s = 0.0

        # -------------------------------------------------------------
        # ЕТАП 3: Аварія провайдера та спрацювання Circuit Breaker (OPEN)
        # -------------------------------------------------------------
        print("\n[ЕТАП 3] Аварія зовнішньої служби (503 Service Unavailable)")
        service_mock.status_code = 503

        # Надсилаємо серію викликів до вичерпання min_call_threshold і переходу в OPEN
        for i in range(1, 6):
            resp = await gateway.execute("GET", "/v1/rates", fallback=fallback_cache)
            print(f"  Аварійний виклик {i}: fallback={resp.is_fallback}, "
                  f"запобіжник={gateway.circuit_breaker.state.value}")

        assert gateway.circuit_breaker.state == CircuitState.OPEN, "Запобіжник повинен розімкнутися в OPEN!"
        print("  -> Поріг збоїв перевищено! Circuit Breaker перейшов у стан OPEN.")

        # -------------------------------------------------------------
        # ЕТАП 4: Миттєва відсічка (Fail-fast за 0 мс) та Fallback
        # -------------------------------------------------------------
        print("\n[ЕТАП 4] Перевірка миттєвої відсічки (Fail-fast)")
        reqs_before = service_mock.total_requests
        start_ff = time.monotonic()
        resp_ff = await gateway.execute("GET", "/v1/rates", fallback=fallback_cache)
        ff_duration_ms = (time.monotonic() - start_ff) * 1000.0
        reqs_after = service_mock.total_requests

        print(f"  Fail-fast виклик: час={ff_duration_ms:.2f}мс, fallback={resp_ff.is_fallback}, "
              f"запитів до мережі={reqs_after - reqs_before}")
        assert resp_ff.is_fallback, "У стані OPEN відповідь мусить повертатися з fallback!"
        assert reqs_after == reqs_before, "У стані OPEN запити до мережі не повинні надсилатися!"
        assert ff_duration_ms < 5.0, "Fail-fast повинен спрацьовувати майже миттєво (<5мс)!"

        # -------------------------------------------------------------
        # ЕТАП 5: Охолодження, зондування (HALF_OPEN) та самозцілення
        # -------------------------------------------------------------
        print("\n[ЕТАП 5] Відновлення партнера, зондування HALF_OPEN та замикання в CLOSED")
        cooldown = breaker_cfg.recovery_timeout_s + 0.1
        print(f"  Очікування періоду охолодження ({cooldown:.1f}с)...")
        await asyncio.sleep(cooldown)

        # Партнер відновився і знову віддає 200 OK
        service_mock.status_code = 200

        # Пробні запити квоти зондування
        for probe_i in range(1, breaker_cfg.half_open_probe_quota + 1):
            p_resp = await gateway.execute("GET", "/v1/rates", fallback=fallback_cache)
            print(f"  Пробний запит {probe_i}: стан={gateway.circuit_breaker.state.value}, "
                  f"fallback={p_resp.is_fallback}")
            assert not p_resp.is_fallback

        assert gateway.circuit_breaker.state == CircuitState.CLOSED, "Запобіжник мусить повернутися в CLOSED!"
        print("  -> Самозцілення успішне! Circuit Breaker замкнено назад у CLOSED.")

        # Контрольний штатний запит
        final_resp = await gateway.execute("GET", "/v1/rates", fallback=fallback_cache)
        print(f"  Фінальний запит: status={final_resp.status_code}, rate={final_resp.data['rate']}")
        assert final_resp.data["rate"] == 41.50

    print("\n" + "=" * 70)
    print(" ВСІ ВЕРИФІКАЦІЙНІ ТЕСТИ ДЕГРАДАЦІЇ ТА СТІЙКОСТІ ПРОЙДЕНО УСПІШНО! ")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
