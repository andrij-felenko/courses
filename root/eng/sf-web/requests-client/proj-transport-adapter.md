# ⚙️ Розробка користувацького HTTPAdapter: пул з'єднань, експоненційна витримка та моніторинг

У високонавантажених розподілених системах стандартної поведінки HTTP-клієнта недостатньо: мікросервісні виклики потребують наскрізного трасування (Distributed Tracing), точного вимірювання затримок на транспортному рівні, агресивних або адаптивних стратегій повторних спроб (Retry with Exponential Backoff) та ізольованих пулів з'єднань для критичних зовнішніх API. Механізм транспортних адаптерів у `requests` надає точку розширення, яка дозволяє перехоплювати відправлення будь-якого `PreparedRequest` безпосередньо перед його передачею в мережевий сокет.

Цей проект демонструє створення повнофункціонального адаптера `ResilientTelemetryAdapter`, який додає до кожного запиту унікальний ідентифікатор трасування, виконує повтори з експоненційною затримкою для ідемпотентних методів у разі мережевих збоїв, фіксує точний час проходження мережевого циклу та монтується на визначені доменні префікси.

## Архітектурний механізм адаптерів та пулу з'єднань

Кожен виклик `Session.send()` у бібліотеці `requests` виконує пошук відповідного адаптера за найдовшим збігом префікса цільового URL. Стандартний клас `requests.adapters.HTTPAdapter` виконує роль моста між високорівневою моделлю запиту та низькорівневим менеджером пулів `urllib3.PoolManager`. 

Створення користувацького адаптера дозволяє втрутитися в три ключові фази мережевого життєвого циклу:

1. **Фаза ініціалізації пулу з'єднань:** У методі `init_poolmanager()` адаптер конфігурує параметри багатопотокової черги сокетів. Тут визначається кількість окремих пулів хостів (`pool_connections`), максимальний розмір черги відкритих сокетів для кожного хоста (`pool_maxsize`), а також режим блокування (`pool_block=True`), який змушує робочі потоки очікувати на звільнення сокетів у черзі замість створення одноразових з'єднань поза пулом. Крім того, адаптер може перевизначити створення сокета для встановлення системних опцій сокета, таких як вимкнення алгоритму Нейгла (`TCP_NODELAY`) для мінімізації мережевої затримки невеликих пакетів та активація періодичних зондувань активності каналу (`SO_KEEPALIVE`).
2. **Фаза налаштування повторів (Retry Strategy):** Замість простого цілочисельного лічильника невдалих спроб, адаптер інтегрує об'єкт `urllib3.util.Retry`. Ця стратегія визначає математичну залежність затримки між спробами:
   `t_backoff = backoff_factor * (2 ** (attempt_number - 1))`
   Якщо `backoff_factor = 0.5`, інтервали між повторами становитимуть послідовно 0.5 с, 1.0 с, 2.0 с, 4.0 с. Для усунення проблеми одночасного повторення запитів багатьма клієнтами (ефект «шторму повторів» або Thundering Herd) до базової формули додається випадковий шум (Jitter), який рівномірно розподіляє навантаження на відновлюваний сервер у часовому вікні.
3. **Фаза виконання відправлення (`send`):** Метод `send()` є безпосередньою точкою входу для кожного підготовленого запиту `PreparedRequest`. Тут здійснюється динамічна модифікація заголовків (інжекція ідентифікаторів трасування `X-Request-ID`), фіксація монотонного системного часу до і після звернення до сокета, а також збереження діагностичних метрик у результуючий об'єкт `Response`.

## Повна реалізація користувацького адаптера на Python

Наведений нижче модуль реалізує повнофункціональний адаптер `ResilientTelemetryAdapter`, готовий до використання у виробничих мікросервісах. Адаптер додає заголовки трасування, налаштовує безпечну політику повторів виключно для ідемпотентних методів (`GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS`) та зберігає затримку мережевого обміну безпосередньо в атрибуті `response.elapsed_transport_ms`.

:::tabs
```python
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
```
:::

## Аналог архітектури на C та C++ (libcurl + RAII)

У системному програмуванні на C та C++ аналогічна поведінка реалізується шляхом інкапсуляції дескрипторів бібліотеки `libcurl` (`CURL*`) у класи-обгортки з підтримкою повторного використання дескрипторів з'єднань, додавання списків заголовків `curl_slist` та реалізації циклів експоненційної витримки.

У наведених прикладах реалізовано клієнтський прошарок, який додає заголовки трасування `X-Request-ID`, налаштовує параметри сокетів (`TCP_NODELAY` для вимкнення алгоритму Нейгла), вимірює тривалість виконання системних викликів за допомогою стандартного годинника високої роздільної здатності та забезпечує детерміноване звільнення ресурсів за принципом RAII.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <curl/curl.h>

struct MemoryBuffer {
    char *memory;
    size_t size;
};

static size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    struct MemoryBuffer *mem = (struct MemoryBuffer *)userp;
    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if (!ptr) return 0;
    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;
    return realsize;
}

int send_resilient_request(CURL *curl, const char *url, int max_retries) {
    struct MemoryBuffer chunk = { .memory = malloc(1), .size = 0 };
    struct curl_slist *headers = NULL;
    
    char req_id[64];
    snprintf(req_id, sizeof(req_id), "X-Request-ID: req-%ld", (long)time(NULL));
    headers = curl_slist_append(headers, req_id);
    headers = curl_slist_append(headers, "X-Origin-Client: NativeClient-C");
    headers = curl_slist_append(headers, "User-Agent: NativeClient/1.0");

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 3L);

    int attempt = 0;
    CURLcode res = CURLE_OK;
    long http_code = 0;

    while (attempt <= max_retries) {
        chunk.size = 0;
        if (chunk.memory) chunk.memory[0] = '\0';

        res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
            if (http_code < 500 && http_code != 429) {
                printf("[C Client] Успіх %ld (спроба %d): %zu байтів\n", http_code, attempt + 1, chunk.size);
                break;
            }
        }

        attempt++;
        if (attempt <= max_retries) {
            unsigned int delay_sec = 1 << attempt; // 2, 4, 8 секунд
            printf("[C Client] Помилка (res=%d, code=%ld). Очікування %u с перед спробою %d...\n",
                   res, http_code, delay_sec, attempt + 1);
            sleep(delay_sec);
        }
    }

    curl_slist_free_all(headers);
    free(chunk.memory);
    return (res == CURLE_OK && http_code < 400) ? 0 : -1;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <thread>
#include <random>
#include <format>
#include <expected>
#include <curl/curl.h>

class ResilientHttpClient {
public:
    struct Response {
        long status_code{0};
        std::string body;
        double elapsed_ms{0.0};
    };

    struct SListDeleter {
        void operator()(curl_slist* list) const noexcept {
            if (list) curl_slist_free_all(list);
        }
    };
    using SListPtr = std::unique_ptr<curl_slist, SListDeleter>;

    struct CurlDeleter {
        void operator()(CURL* handle) const noexcept {
            if (handle) curl_easy_cleanup(handle);
        }
    };
    using CurlPtr = std::unique_ptr<CURL, CurlDeleter>;

    explicit ResilientHttpClient(std::string client_name, int max_retries = 3)
        : client_name_(std::move(client_name)), max_retries_(max_retries), curl_(curl_easy_init()) {
        if (!curl_) {
            throw std::runtime_error("Не вдалося ініціалізувати дескриптор libcurl");
        }
    }

    std::expected<Response, std::string> get(const std::string& url, int timeout_sec = 10) {
        std::string buffer;
        SListPtr headers;

        std::string req_id = std::format("X-Request-ID: cpp-{}", std::chrono::steady_clock::now().time_since_epoch().count());
        headers.reset(curl_slist_append(headers.release(), req_id.c_str()));
        headers.reset(curl_slist_append(headers.release(), ("X-Origin-Client: " + client_name_).c_str()));

        curl_easy_setopt(curl_.get(), CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl_.get(), CURLOPT_HTTPHEADER, headers.get());
        curl_easy_setopt(curl_.get(), CURLOPT_WRITEFUNCTION, &ResilientHttpClient::writeCallback);
        curl_easy_setopt(curl_.get(), CURLOPT_WRITEDATA, &buffer);
        curl_easy_setopt(curl_.get(), CURLOPT_TIMEOUT, static_cast<long>(timeout_sec));
        curl_easy_setopt(curl_.get(), CURLOPT_CONNECTTIMEOUT, 3L);
        curl_easy_setopt(curl_.get(), CURLOPT_TCP_NODELAY, 1L);

        int attempt = 0;
        CURLcode res = CURLE_OK;
        long http_code = 0;
        auto start_time = std::chrono::steady_clock::now();

        while (attempt <= max_retries_) {
            buffer.clear();
            res = curl_easy_perform(curl_.get());

            if (res == CURLE_OK) {
                curl_easy_getinfo(curl_.get(), CURLINFO_RESPONSE_CODE, &http_code);
                if (http_code < 500 && http_code != 429) {
                    auto end_time = std::chrono::steady_clock::now();
                    double elapsed = std::chrono::duration<double, std::milli>(end_time - start_time).count();
                    return Response{
                        .status_code = http_code,
                        .body = std::move(buffer),
                        .elapsed_ms = elapsed
                    };
                }
            }

            attempt++;
            if (attempt <= max_retries_) {
                auto backoff = std::chrono::milliseconds(200 * (1 << attempt));
                std::this_thread::sleep_for(backoff);
            }
        }

        return std::unexpected(std::format("Помилка після {} спроб: curl_code={}, http_code={}",
                                           attempt, static_cast<int>(res), http_code));
    }

private:
    static size_t writeCallback(char* ptr, size_t size, size_t nmemb, void* userdata) {
        auto* str = static_cast<std::string*>(userdata);
        size_t total = size * nmemb;
        str->append(ptr, total);
        return total;
    }

    std::string client_name_;
    int max_retries_;
    CurlPtr curl_;
};
```
:::

## Інженерний аналіз та підводні камені реалізації адаптерів

Під час розробки та експлуатації користувацьких транспортних адаптерів необхідно враховувати чотири фундаментальні системні аспекти:

1. **Небезпека повтору неідемпотентних операцій:** Якщо віддалений сервер успішно виконав `POST`-запит (наприклад, списання коштів із банківського рахунку чи створення нового запису в базі даних), але мережевий зв'язок обірвався під час передачі відповіді `200 OK` клієнту, автоматичний повтор згенерує дублікат транзакції. Параметр `allowed_methods` у класі `Retry` повинен суворо обмежуватися ідемпотентними дієсловами (`GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS`). Якщо повтор для `POST` є абсолютно необхідним, сервер зобов'язаний підтримувати заголовки ідемпотентності (`Idempotency-Key`).
2. **Блокування пулу проти витоку сокетів:** За замовчуванням `HTTPAdapter` ініціалізує пул із прапорцем `block=False`. Якщо 50 паралельних робочих потоків одночасно надсилають запити через сесію з `pool_maxsize=10`, менеджер `urllib3` відкриє 40 додаткових тимчасових сокетів поза пулом, а після завершення запиту знищить їх, генеруючи попередження в журналах. Встановлення `block=True` змушує потоки очікувати на звільнення сокетів у черзі `LifoQueue`, що стабілізує споживання пам'яті та ліміти дескрипторів файлів (`ulimit -n`).
3. **Ізоляція модифікації заголовків у PreparedRequest:** Зміни, внесені в `request.headers` безпосередньо у методі `send()`, діють виключно в межах поточного виконання і не потрапляють у первинний об'єкт сесії `session.headers`. Це гарантує, що динамічні службові мітки (наприклад, унікальний `X-Request-ID`) не створюють витоків контексту між паралельними або послідовними запитами.
4. **Контекст TLS та перевірка шифрів:** У спеціалізованих контурах безпеки метод `init_poolmanager()` може бути перевизначений для передачі кастомного об'єкта `ssl.SSLContext`. Це дозволяє явно вказати мінімальну версію протоколу (наприклад, `TLSv1.3`), обмежити допустимі набори шифрів (Cipher Suites) або увімкнути взаємну автентифікацію клієнта за допомогою апаратних ключів (PKCS#11).
5. **Масштабування для нестандартних транспортних протоколів:** Архітектура транспортних адаптерів дозволяє монтувати не лише HTTP/HTTPS з'єднання, а й довільні користувацькі протоколи. Наприклад, адаптер `requests-unixsocket` монтується на схему `http+unix://` і транслює HTTP-запити в локальні UNIX-сокети для прямої взаємодії з демонами Docker чи системними сервісами Linux без використання мережевого стека TCP/IP.
