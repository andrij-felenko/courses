import time
import uuid
import logging
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("http_telemetry")


class ResilientTelemetryAdapter(HTTPAdapter):
    """
    Користувацький транспортний адаптер:
    - Автоматично інжектує заголовок X-Request-ID для розподіленого трасування.
    - Застосовує експоненційну витримку (backoff) для транзитних помилок.
    - Вимірює точний час перебування запиту в транспортному конвеєрі.
    """

    def __init__(
        self,
        service_name: str,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        pool_connections: int = 20,
        pool_maxsize: int = 50,
        **kwargs: Any
    ) -> None:
        self.service_name = service_name
        
        # Конфігурація стратегії повторів urllib3
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS"],
            raise_on_status=False
        )

        super().__init__(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            **kwargs
        )

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool = False,
        timeout: Optional[Any] = None,
        verify: bool = True,
        cert: Optional[Any] = None,
        proxies: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        # 1. Додавання ідентифікатора трасування
        request_id = str(uuid.uuid4())
        request.headers["X-Request-ID"] = request_id
        request.headers["X-Origin-Client"] = self.service_name

        # 2. Фіксація початку транспортного обміну за монотонним таймером
        start_time = time.monotonic()
        logger.info("Вихідний запит: %s %s [ID: %s]", request.method, request.url, request_id)

        try:
            # 3. Передача запиту базовому адаптеру (urllib3 PoolManager)
            response = super().send(
                request,
                stream=stream,
                timeout=timeout,
                verify=verify,
                cert=cert,
                proxies=proxies
            )
            duration_ms = (time.monotonic() - start_time) * 1000.0
            
            # Додавання телеметричної мітки до об'єкта відповіді
            response.elapsed_transport_ms = duration_ms  # type: ignore[attr-defined]
            
            logger.info(
                "Відповідь отримана: %s %s -> %d OK (%.2f мс) [ID: %s]",
                request.method, request.url, response.status_code, duration_ms, request_id
            )
            return response

        except requests.exceptions.RequestException as exc:
            duration_ms = (time.monotonic() - start_time) * 1000.0
            logger.error(
                "Транспортний збій: %s %s після %.2f мс: %s [ID: %s]",
                request.method, request.url, duration_ms, str(exc), request_id
            )
            raise


# Демонстрація монтування адаптера в клієнтську сесію
def run_client() -> None:
    session = requests.Session()

    # Створюємо екземпляр адаптера для критичного платіжного шлюзу
    resilient_adapter = ResilientTelemetryAdapter(
        service_name="BillingService/2.4",
        max_retries=3,
        backoff_factor=0.3,
        pool_connections=10,
        pool_maxsize=20
    )

    # Монтуємо адаптер виключно на цільовий базовий URL
    session.mount("https://httpbin.org", resilient_adapter)

    # Виконуємо запит
    try:
        resp = session.get("https://httpbin.org/status/200", timeout=(3.0, 5.0))
        print(f"Статус: {resp.status_code}, Затримка транспорту: {resp.elapsed_transport_ms:.2f} мс")
        print(f"Echo X-Request-ID: {resp.request.headers.get('X-Request-ID')}")
    finally:
        session.close()


if __name__ == "__main__":
    run_client()
