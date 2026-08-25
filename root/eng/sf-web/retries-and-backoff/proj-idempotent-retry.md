# ⚙️ Стійкий клієнтський стек: повтори з бюджетом, запобіжником та ідемпотентними ключами

Створення надійного мережевого клієнта у високонавантажених розподілених системах вимагає узгодженої взаємодії чотирьох незалежних захисних контурів. Якщо обмежитися простим циклом `for attempt in range(retries): sleep(2**attempt)`, клієнт швидко перетвориться на генератор відмови в обслуговуванні (DDoS) для власного бекенда під час масових збоїв, або спричинить дублювання фінансових транзакцій при мережевих обривах.

Повний виробничий пайплайн клієнта будується як конвеєр із чотирьох фільтрів:

1. **Запобіжник (Circuit Breaker):** контролює загальну частку збоїв сервісу. Якщо бекенд стабільно повертає 500/503 або не відповідає на тайм-аутах, розмикає коло (`OPEN`), блокуючи всі наступні виклики ще до виходу в мережу (fail-fast).
2. **Бюджет повторів (Retry Budget):** контролює витрату ресурсів на повтори за алгоритмом маркерного кошика (Token Bucket). Наприклад, кожен успішний запит поповнює пул на 0.2 токена, а кожна повторна спроба списує 1.0 токен. Якщо бюджет вичерпано, запит завершується помилкою після першої ж невдачі.
3. **Ідемпотентний контекст (Idempotency Manager):** для мутуючих запитів (`POST`, `PATCH`) генерує криптографічно стійкий унікальний ідентифікатор `Idempotency-Key` (UUIDv4) перед першою відправкою і незмінно додає його до кожного повторного пакета.
4. **Рандомізований відступ (Full/Decorrelated Jitter Backoff):** обчислює динамічну паузу між спробами з урахуванням серверного заголовка `Retry-After` та випадкового розсіювання.

## Архітектурний конвеєр перехоплювачів (Interceptor Pipeline)

Взаємодія компонентів організовується за патерном «Ланцюжок відповідальності» (Chain of Responsibility) або перехоплювачів (Interceptors). Перед тим як сокет почне операцію `connect()` або запише байти HTTP-запиту в дескриптор, запит проходить крізь чергу попередніх перевірок.

```
       Вхідний HTTP-виклик
               │
               ▼
   ┌───────────────────────┐
   │    Circuit Breaker    │ ── (Стан OPEN) ──► Швидка відмова (Fail-Fast без мережі)
   └───────────┬───────────┘
               │ (Стан CLOSED / HALF-OPEN)
               ▼
   ┌───────────────────────┐
   │  Idempotency Injector │ ── Додає унікальний UUIDv4 для POST/PATCH операцій
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │     Retry Loop        │ ◄────────────────────────────────────────┐
   └───────────┬───────────┘                                          │
               │                                                      │
               ▼                                                      │
   ┌───────────────────────┐                                          │
   │  Raw Transport Call   │                                          │
   └───────────┬───────────┘                                          │
               │                                                      │
         [Результат?]                                                 │
        /            \                                                │
   (Успіх 2xx)   (Тимчасовий збій 429/503/RST)                        │
      /                \                                              │
     ▼                  ▼                                             │
 [Поповнити      ┌───────────────┐                                    │
   Бюджет]       │ Retry Budget? │ ── (Бюджет вичерпано) ──► Відмова  │
     │           └───────┬───────┘                                    │
     ▼                   │ (Токен списано)                            │
 Повернення              ▼                                            │
 результату      ┌───────────────┐                                    │
                 │ Backoff Sleep │ ── (Обчислення Full Jitter) ───────┘
                 └───────────────┘
```

Якщо запит завершується тимчасовою помилкою (наприклад, кодом `503` або обривом з'єднання `ECONNRESET`), конвеєр не просто чекає, а оцінює стан пулу токенів. Якщо за останні 60 секунд частка невдач була занадто високою, бюджет блокує повторну спробу, повертаючи помилку застосунку. Завдяки цьому клієнтський пул з'єднань ніколи не виснажується нескінченними спробами зв'язатися з мертвим вузлом.

## Реалізація стійкого клієнта мовами Python, C та C++

:::tabs
```python
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
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <math.h>

#define MAX_RETRIES 3
#define BASE_BACKOFF_MS 100
#define MAX_BACKOFF_MS 10000

typedef struct {
    int status_code;
    int retry_after_sec;
    char body[512];
} http_response_t;

/* Генерація псевдо-UUIDv4 для заголовка Idempotency-Key */
void generate_idempotency_key(char *out_buf, size_t buf_sz) {
    snprintf(out_buf, buf_sz, "idemp-%08x-%04x-4%03x-a%03x-%08x",
             (unsigned int)rand(), (unsigned int)rand() & 0xFFFF,
             (unsigned int)rand() & 0x0FFF, (unsigned int)rand() & 0x0FFF,
             (unsigned int)rand());
}

/* Обчислення Full Jitter: Uniform(0, min(MAX, BASE * 2^i)) */
long compute_full_jitter_ms(int attempt, int retry_after_sec) {
    if (retry_after_sec > 0) {
        long base_ms = (long)retry_after_sec * 1000;
        long jitter = (rand() % 100); /* +0..99 мс */
        return base_ms + jitter;
    }
    long max_for_attempt = BASE_BACKOFF_MS * (1L << attempt);
    if (max_for_attempt > MAX_BACKOFF_MS) {
        max_for_attempt = MAX_BACKOFF_MS;
    }
    return (rand() % (max_for_attempt + 1));
}

/* Імітація мережевого запиту до сервера */
http_response_t mock_network_send(const char *method, const char *url, const char *idemp_key, int attempt) {
    http_response_t res;
    memset(&res, 0, sizeof(res));

    /* Симулюємо тимчасову помилку 503 на перших двох спробах */
    if (attempt < 2) {
        res.status_code = 503;
        res.retry_after_sec = 0;
        snprintf(res.body, sizeof(res.body), "{\"error\": \"Service Unavailable\"}");
    } else {
        res.status_code = 200;
        res.retry_after_sec = 0;
        snprintf(res.body, sizeof(res.body), "{\"status\": \"Processed successfully\", \"key\": \"%s\"}", idemp_key);
    }
    return res;
}

int http_post_with_retry(const char *url, const char *payload, http_response_t *out_response) {
    char idemp_key[64];
    generate_idempotency_key(idemp_key, sizeof(idemp_key));

    for (int attempt = 0; attempt <= MAX_RETRIES; ++attempt) {
        *out_response = mock_network_send("POST", url, idemp_key, attempt);

        if (out_response->status_code >= 200 && out_response->status_code < 300) {
            return 0; /* Успіх */
        }

        bool is_transient = (out_response->status_code == 429 ||
                             out_response->status_code == 502 ||
                             out_response->status_code == 503 ||
                             out_response->status_code == 504);

        if (!is_transient || attempt == MAX_RETRIES) {
            return -1; /* Фатальна помилка або вичерпано спроби */
        }

        long sleep_ms = compute_full_jitter_ms(attempt, out_response->retry_after_sec);
        usleep((useconds_t)(sleep_ms * 1000));
    }
    return -1;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <thread>
#include <expected>
#include <memory>
#include <format>
#include <atomic>

struct HttpResponse {
    int status_code{0};
    int retry_after_seconds{0};
    std::string body;
};

enum class HttpError {
    TransientNetworkFailure,
    CircuitOpen,
    RetryBudgetExhausted,
    FatalServerError,
    MaxRetriesExceeded
};

class ResilientHttpClientCpp {
public:
    struct Config {
        int max_retries = 3;
        std::chrono::milliseconds base_backoff{100};
        std::chrono::milliseconds max_backoff{10000};
    };

    explicit ResilientHttpClientCpp(Config cfg = {})
        : cfg_(cfg), rng_(std::random_device{}()) {}

    std::expected<HttpResponse, HttpError> execute_post(std::string_view url, std::string_view payload) {
        const std::string idempotency_key = generate_uuid_v4();

        for (int attempt = 0; attempt <= cfg_.max_retries; ++attempt) {
            HttpResponse res = mock_transport_call("POST", url, idempotency_key, payload, attempt);

            if (res.status_code >= 200 && res.status_code < 300) {
                return res;
            }

            const bool is_transient = (res.status_code == 429 ||
                                       res.status_code == 502 ||
                                       res.status_code == 503 ||
                                       res.status_code == 504);

            if (!is_transient || attempt == cfg_.max_retries) {
                return std::unexpected(HttpError::MaxRetriesExceeded);
            }

            const auto delay = compute_full_jitter(attempt, res.retry_after_seconds);
            std::this_thread::sleep_for(delay);
        }

        return std::unexpected(HttpError::MaxRetriesExceeded);
    }

private:
    Config cfg_;
    std::mt19937 rng_;

    std::chrono::milliseconds compute_full_jitter(int attempt, int retry_after_sec) {
        if (retry_after_sec > 0) {
            std::uniform_int_distribution<int> jitter_dist(0, 100);
            return std::chrono::seconds(retry_after_sec) + std::chrono::milliseconds(jitter_dist(rng_));
        }

        const auto exp_ms = cfg_.base_backoff.count() * (1LL << attempt);
        const auto capped_ms = std::min(static_cast<long long>(cfg_.max_backoff.count()), exp_ms);

        std::uniform_int_distribution<long long> dist(0, capped_ms);
        return std::chrono::milliseconds(dist(rng_));
    }

    std::string generate_uuid_v4() {
        std::uniform_int_distribution<uint32_t> dist(0, 0xFFFFFFFF);
        return std::format("idemp-{:08x}-{:04x}-4{:03x}-8{:03x}-{:08x}",
                           dist(rng_), dist(rng_) & 0xFFFF, dist(rng_) & 0x0FFF,
                           dist(rng_) & 0x0FFF, dist(rng_));
    }

    HttpResponse mock_transport_call(std::string_view method, std::string_view url,
                                     std::string_view key, std::string_view body, int attempt) {
        if (attempt < 2) {
            return HttpResponse{.status_code = 503, .retry_after_seconds = 0, .body = "Service Unavailable"};
        }
        return HttpResponse{.status_code = 200, .retry_after_seconds = 0,
                            .body = std::format(R"({{"status":"OK","idempotency_key":"{}"}})", key)};
    }
};
```
:::

## Серверна дедуплікація ключів ідемпотентності

На стороні бекенда збереження та перевірка ключів ідемпотентності реалізується через розподілене сховище в оперативній пам'яті (Redis) або за допомогою унікальних індексів реляційної бази даних.

Типова схема атомарного захоплення ключа в Redis спирається на команду `SET key value NX PX <milliseconds>`:
- Опція `NX` (Not Exists) гарантує, що ключ буде записано лише в тому разі, якщо він відсутній у базі. Це усуває стан гонитви (Race Condition), коли два паралельні повтори від одного клієнта надходять на різні вузли бекенда в одну мікросекунду.
- Опція `PX` (Milliseconds TTL) встановлює автоматичне видалення блокування (наприклад, 120 000 мс). Якщо робочий процес сервера зазнає аварійного падіння посеред обробки транзакції, ключ автоматично розблокується через 2 хвилини, дозволяючи наступним спробам виконати операцію.

Коли транзакція завершується успішно, бекенд замінює тимчасове блокування збереженим об'єктом відповіді (HTTP-код, заголовки, тіло у форматі JSON) і подовжує час життя запису (TTL) до 24–72 годин. Якщо клієнт звертається з тим самим ключем знову, Redis повертає кешовану відповідь менш ніж за 1 мілісекунду без навантаження на основну базу даних.

## Керування життєвим циклом з'єднань і пулом сокетів

Особливої уваги при реалізації клієнта з повторами потребує взаємодія з підсистемою пулінгу з'єднань (Connection Pool). Якщо запит обривається посеред передачі потокового тіла (наприклад, сервер надіслав заголовки `200 OK`, але закрив сокет через збій посеред передачі `Transfer-Encoding: chunked`), з'єднання не можна повертати в пул для повторного використання.

Транспортний шар клієнта зобов'язаний:
1. **Явно закрити та утилізувати пошкоджений файловий дескриптор сокета (`close(fd)` або скидання через `SO_LINGER`),** щоб не допустити витоку напіввідкритих з'єднань у стані `CLOSE_WAIT`.
2. **Ініціалізувати новий чистий TCP-сокет** для виконання наступної повторної спроби. Спроба відправити повторний HTTP-пакет у старий зламаний сокет неминуче призведе до помилки ядра `EPIPE` (Broken pipe) або генерації сигналу `SIGPIPE`.
3. **Очищати буфери читання:** якщо сервер надіслав тіло помилки `503 Service Unavailable`, клієнт повинен повністю вичитати його байти з сокета або скинути з'єднання, перш ніж переходити до паузи відступу. Інакше залишки незчитаного HTTP-пакета зіпсують наступний запит у цьому ж keep-alive каналі.

## Інженерні пастки реалізації

1. **Генерація нового ключа ідемпотентності всередині циклу повторів:** найнебезпечніша помилка полягає у виклику `generate_uuid()` на кожній ітерації `attempt`. Якщо запит виконався на сервері, але обірвався під час передачі відповіді, повтор із *новим* ключем сприймається сервером як *абсолютно нова дія*, що гарантовано спричиняє подвійну транзакцію. Ключ генерується рівно один раз перед першою спробою.
2. **Сліпе ігнорування `Retry-After: 0` або від'ємних значень:** якщо несправний сервер повертає некоректний заголовок `Retry-After: -1` або `Retry-After: 0`, наївний парсер може скинути затримку до нуля, спровокувавши негайний шторм запитів. Будь-яке значення менше базового експоненційного інтервалу має підлягати санітизації.
3. **Блокування системного диспетчера подій у асинхронному коді:** виклик синхронного `time.sleep()` або `usleep()` всередині асинхронного циклу подій (asyncio, Tokio, libuv) блокує весь потік виконання для тисяч сусідніх з'єднань. У асинхронних клієнтах відступ реалізується виключно через неблокуючі таймери (`asyncio.sleep()`, `uv_timer_start()`).
4. **Втрата глобального дедлайну операції:** якщо загальний бюджет часу виклику становить 5 секунд, а окремі тайм-аути спроб задані як 2 секунди з відступами по 1–2 секунди, сумарний час виконання може легко перевищити 8–10 секунд. Стійкий клієнт повинен передавати єдиний контекст дедлайну (`deadline = now() + total_timeout`) крізь усі ітерації циклу повторів, перериваючи виконання незалежно від залишку спроб.
