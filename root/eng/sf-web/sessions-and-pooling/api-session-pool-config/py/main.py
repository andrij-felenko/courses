import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

# Налаштування стратегії повторних спроб
retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods={"HEAD", "GET", "PUT", "DELETE", "OPTIONS"},
    raise_on_status=False
)

# Монтування адаптера з параметрами пулу
adapter = HTTPAdapter(
    pool_connections=20,  # Кількість кешованих пулів хостів
    pool_maxsize=50,       # Максимум з'єднань на один хост
    max_retries=retries,   # Політика повторів
    pool_block=True        # Блокувати потік при вичерпанні ліміту
)

session.mount("https://", adapter)
session.mount("http://", adapter)
