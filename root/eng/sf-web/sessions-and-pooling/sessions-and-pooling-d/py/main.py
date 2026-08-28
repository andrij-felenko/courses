import concurrent.futures
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def build_resilient_session() -> requests.Session:
    """Створює налаштовану потокобезпечну сесію з розширеним пулом з'єднань."""
    session = requests.Session()

    # 1. Задаємо базові заголовки сесії
    session.headers.update({
        "User-Agent": "OrderProcessingService/2.4.0",
        "Accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    })

    # 2. Налаштовуємо стратегію автоматичних повторів для мережевих розривів
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,  # Паузи: 0.3с, 0.6с, 1.2с
        status_forcelist=[502, 503, 504],
        allowed_methods={"HEAD", "GET", "PUT", "DELETE", "OPTIONS"},
        raise_on_status=False
    )

    # 3. Налаштовуємо транспортний адаптер із розширеним пулом
    adapter = HTTPAdapter(
        pool_connections=10,  # Кількість пулів різних хостів
        pool_maxsize=25,       # До 25 відкритих сокетів на кожен хост
        max_retries=retry_strategy,
        pool_block=True        # Блокувати потік при вичерпанні ліміту сокетів
    )

    # Прив'язуємо адаптер до протоколів
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def fetch_resource(session: requests.Session, item_id: int) -> dict:
    url = f"https://api.example.com/items/{item_id}"
    # Кортеж таймаутів: (таймаут на підключення, таймаут на читання)
    response = session.get(url, timeout=(3.05, 5.0))
    response.raise_for_status()
    return response.json()


# Використання єдиної сесії в пулі з 10 паралельних потоків
if __name__ == "__main__":
    http_session = build_resilient_session()
    item_ids = list(range(100, 150))

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_resource, http_session, item_id) for item_id in item_ids]
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                # Обробка отриманих даних
            except requests.exceptions.RequestException as err:
                print(f"Помилка запиту: {err}")
