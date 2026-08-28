import uuid
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter


class IdempotentHTTPAdapter(HTTPAdapter):
    """Транспортний адаптер з автоматичним додаванням Idempotency-Key."""

    def send(self, request, **kwargs):
        # Додаємо унікальний ключ для мутуючих методів, якщо він не заданий явно
        if request.method in ("POST", "PATCH", "PUT"):
            if "Idempotency-Key" not in request.headers:
                request.headers["Idempotency-Key"] = str(uuid.uuid4())
        return super().send(request, **kwargs)


def create_resilient_session() -> requests.Session:
    session = requests.Session()

    # Налаштування політики повторів:
    # total=3: максимум 3 спроби повтору
    # backoff_factor=0.5: інтервали очікування 0.5s, 1.0s, 2.0s...
    # status_forcelist: повторюємо лише тимчасові коди збоїв
    # allowed_methods: безпечні та ідемпотентні методи (POST додано під захистом Idempotency-Key)
    # respect_retry_after_header=True: суворе дотримання серверного Retry-After
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET", "HEAD", "PUT", "DELETE", "OPTIONS", "POST"]),
        raise_on_status=False,
        respect_retry_after_header=True
    )

    adapter = IdempotentHTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session
