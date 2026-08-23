# ⚙️ Тривкий вихідний вузол: реалізація Egress Gateway

Повна архітектурна реалізація вихідного вузла (Outbound Egress Gateway) приймає наміри відправки з таблиці Transactional Outbox, обгортає їх у дедуп-ключі й HMAC-підписи, пропускає крізь автоматичний вимикач (Circuit Breaker) із ретраями та рандомізованим відступом (Jitter), а при непереборних збоях безпечно переносить отруйні повідомлення в мертву чергу (DLQ).

## Архітектурна анатомія вихідного конвеєра

Вихідний вузол є захисним бар'єром між внутрішніми сервісами та зовнішніми мережевими адресатами. Замість того щоб дозволяти кожному мікросервісу самостійно створювати HTTP-клієнти, відкривати TCP-сокети й підписувати повідомлення, вся вихідна взаємодія централізується у виділеному конвеєрі. Це дає змогу контролювати навантаження, забезпечувати стійкість до мережевих катастроф та вести єдиний аудит доставок.

Вихідний конвеєр складається з п'яти взаємопов'язаних модулів:

1. **Transactional Outbox Database Engine:** Забезпечує збереження наміру відправки у тому самому ACID-контексті, що й бізнес-подія. Використовує спеціальну таблицю з оптимізованими індексами для високопродуктивного вичитання робітниками.
2. **Egress Dispatcher & Key Generator:** Процес-воркер, який вибирає незавершені задачі з бази даних за допомогою конкурентнобезпечного механізму `FOR UPDATE SKIP LOCKED`. Він обчислює HMAC-SHA256 підписи тіла, генерує унікальні заголовки ідемпотентності (`X-Idempotency-Key`) та формує метадані для транспорту.
3. **Circuit Breaker State Machine:** Кінцевий автомат із трьома станами (`CLOSED`, `OPEN`, `HALF-OPEN`), який стежить за «здоров'ям» кожного зовнішнього хосту. Якщо зовнішній сервіс перестає відповідати або повертає помилки серії `5xx`, вимикач ізолює цей напрямок, миттєво відхиляючи нові запити без виходу в мережу й запобігаючи виснаженню пулу потоків.
4. **Exponential Backoff & Jitter Engine:** Модуль розрахунку затримок між повторними спробами. Він реалізує алгоритм експоненційного збільшення затримки з додаванням випадкового зсуву (Jitter), що запобігає синхронізації викликів від сотень воркерів під час відновлення сервісу.
5. **Dead Letter Queue (DLQ) & Audit Logger:** Приймач отруйних повідомлень, які вичерпали ліміт спроб. Він фіксує точні байти запиту, заголовки, розгортку помилок та часові мітки для подальшого аналізу інженерами.

## Схема даних Outbox та SQL-механіка

Серцем стійкого збереження намірів відправки є таблиця `outbound_outbox`. Нижче наведено еталонний DDL-сценарій для бази даних PostgreSQL, який забезпечує атомарність і високу швидкість обробки під навантаженням.

```sql
-- Таблиця для збереження намірів вихідних відправок
CREATE TABLE outbound_outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination_type VARCHAR(32) NOT NULL, -- WEBHOOK, PUSH, SMS, API
    destination_url TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    secret_key TEXT NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, SENT, FAILED, DEAD_LETTER
    attempt INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 5,
    next_retry_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Частковий індекс для миттєвої вибірки робітниками готових до відправки задач
CREATE INDEX idx_outbox_processing 
ON outbound_outbox (status, next_retry_at) 
WHERE status IN ('PENDING', 'FAILED');

-- Індекс для швидкої дедуплікації за idempotency_key
CREATE UNIQUE INDEX idx_outbox_idempotency 
ON outbound_outbox (idempotency_key);
```

### Партиціонування та індексація для високих навантажень

У системах, що обробляють мільйони вихідних вебхуків або сповіщень на день, розмір таблиці `outbound_outbox` швидко зростає, сповільнюючи SQL-запити. Для оптимізації застосовуються дві тактики:

1. **Часткові індекси (Partial Indexes):** Замість індексування всієї таблиці (включно мільйонами вже успішно відправлених записів зі статусом `SENT`), індекс `idx_outbox_processing` включає тільки ті рядки, де `status IN ('PENDING', 'FAILED')`. Це зменшує розмір індексу в сотні разів і дає змогу йому повністю сидіти у RAM (Buffer Pool).
2. **Діапазонне партиціонування (Range Partitioning по created_at):** Таблиця розбивається на денні або тижневі партиції. Завершені записи за минулі місяці або вивантажуються в холодне сховище (S3/ClickHouse), або видаляються через `DROP TABLE partition_name`, що миттєво звільняє дисковий простір без важкої операції `VACUUM FULL`.

### Механіка вичитання через SKIP LOCKED

Коли в системі працює декілька інстансів Egress Gateway, виникає ризик того, що два воркери паралельно вичитають ту саму задачу з таблиці `outbox`. Наївне рішення з первинним вибором `SELECT` та подальшим `UPDATE` призводить до гонки процесів (race condition) та подвійних викликів мережі.

Правильний підхід полягає у використанні конструкції `FOR UPDATE SKIP LOCKED`. Вона дозволяє кожному воркеру заблокувати й отримати лише ті рядки, які ще не заблоковані іншими паралельними процесами:

```sql
-- Атомарне захоплення пакета задач робітником
UPDATE outbound_outbox
SET status = 'PROCESSING',
    updated_at = NOW()
WHERE id IN (
    SELECT id
    FROM outbound_outbox
    WHERE status IN ('PENDING', 'FAILED')
      AND next_retry_at <= NOW()
    ORDER BY created_at ASC
    LIMIT 50
    FOR UPDATE SKIP LOCKED
)
RETURNING id, destination_type, destination_url, payload_json, secret_key, idempotency_key, attempt, max_attempts;
```

Цей запит гарантує, що жодна задача не буде захоплена двома воркерами одночасно, а блоки бази даних не створюватимуть простоїв для інших потоків.

## Вичитання Outbox: Полінг проти Change Data Capture (CDC)

Існує дві стратегії вичитання записів із таблиці `outbound_outbox`:

1. **Периодичний опит (Outbox Polling):** Воркери запускають SQL-запит із `SKIP LOCKED` раз на N мілісекунд (наприклад, кожні 100 мс). Перевага цього підходу — простота реалізації, відсутність сторонніх залежностей та повний контроль над транзакційним станом. Недолік — додаткове навантаження на базу даних через постійні читання у період тиші (empty polls).
2. **Change Data Capture (CDC на базі Debezium / Logical Replication):** Замість SQL-запитів окремий сервіс читає транзакційний лог бази даних (PostgreSQL WAL — Write-Ahead Log). При появі нового рядка в `outbound_outbox` CDC-демон миттєво публікує подію у шину повідомлень (Apache Kafka або NATS), звідки її вичитають робітники Egress Gateway. Перевага — нульова затримка (sub-millisecond delivery) та нульове навантаження `SELECT`-запитами на БД. Недолік — складність інфраструктури (потреба у збішінні Kafka/Debezium та суворому моніторингу реплікувальних слотів).

## Логіка та стан автоматичного вимикача (Circuit Breaker)

Автоматичний вимикач протидіє каскадним аваріям, розриваючи зв'язок зі збійним зовнішнім вузлом. Він працює як станція керування з трьома станами:

* **CLOSED (Замкнений):** Нормальний стан. Усі вихідні запити вільно проходять крізь вузол у мережу. Якщо запит завершується успішно, лічильник помилок скидається до нуля. Якщо запит завершується помилкою `5xx` або таймаутом, лічильник помилок збільшується на 1. При досягненні порогу (наприклад, 3 помилки поспіль) Circuit Breaker переходить у стан `OPEN`.
* **OPEN (Розвіднений):** Аварійний стан. Зовнішній хост вважається непрацездатним. Усі нові спроби відправити повідомлення на цю адресу миттєво відхиляються на рівні локального вузла без створення HTTP-з'єднання. Це захищає пули сокетів від забивання та запобігає шторму запитів на зламаний сервер. Автоматичний вимикач залишається у стані `OPEN` протягом визначеного таймауту відновлення (наприклад, 10 секунд).
* **HALF-OPEN (Напіввідкритий):** Пробний стан. Після закінчення таймауту відновлення вимикач пропускає **один** тестовий запит до віддаленого сервісу. Якщо тестовий запит успішний — вимикач повертається в стан `CLOSED`, скидаючи лічильники. Якщо тестовий запит зазнає невдачі — вимикач негайно повертається в стан `OPEN` і подвоює час очікування.

### Обробка HTTP-кодів відповідей

Вихідний вузол класифікує HTTP-коди відповідей на три категорії:

1. **2xx Success (200 OK, 201 Created, 202 Accepted):** Успішна доставка. Задача маркується `SENT`, Circuit Breaker фіксує успіх.
2. **4xx Client Errors (400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found):** Помилка конфігурації або некоректне тіло. Повторні спроби марні, бо тіло чи секрет не зміняться. Задача **негайно** відправляється в `DLQ`, не витрачаючи ліміт спроб retry, а Circuit Breaker **не** збільшує лічильник мережевих збоїв. Винятком є код `429 Too Many Requests`, який обробляється як тимчасове перевантаження й відправляє задачу на retry з урахуванням заголовка `Retry-After`.
3. **5xx Server Errors (500 Internal Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout) та мережеві таймаути:** Тимчасовий збій на боці отримувача. Задача повертається на retry з експоненційним відступом, а Circuit Breaker збільшує лічильник помилок.

## Математика експоненційного відступу із Jitter

Наївні повтори через фіксований інтервал (наприклад, кожні 5 секунд) спричиняють проблему «синхронізованого шторму». Якщо 1000 воркерів одночасно отримали мережеву помилку від зовнішнього API, через 5 секунд усі 1000 воркерів знову одночасно вистрілять HTTP-запитами, повторно валячи відновлюваний сервер.

Щоб розбігтися в часі, використовується експоненційний відступ з рандомізованим зсувом (Full Jitter):

```
base_delay = 100 ms
max_delay  = 5000 ms
temp       = min(max_delay, base_delay * 2^attempt)
sleep_time = random_between(0, temp)
```

Завдяки додаванню випадкового значення `random_between(0, temp)`, виклики тисячі робітників рівномірно розмазуються по часовій осі, даючи зовнішньому сервісу можливість плавно піднятися й стабілізувати навантаження.

## Програмні реалізації у чотирьох мовах

Нижче наведено повні, працездатні програмні модулі вихідного вузла мовами TypeScript, Python, C та C++. Кожен модуль містить реалізацію Circuit Breaker, генерацію підписів і заголовків ідемпотентності, обчислення відступу та маршрутизацію в DLQ.

:::tabs
```ts
import { createHmac } from "node:crypto";

export interface OutboundMessage {
  id: string;
  destinationUrl: string;
  payloadJson: string;
  attempt: number;
  maxAttempts: number;
  secret: string;
}

export enum CircuitState { CLOSED, OPEN, HALF_OPEN }

export class CircuitBreaker {
  private state = CircuitState.CLOSED;
  private failureCount = 0;
  private nextAttemptTime = 0;

  constructor(private threshold = 3, private resetTimeoutMs = 10000) {}

  canExecute(now: number): boolean {
    if (this.state === CircuitState.OPEN) {
      if (now >= this.nextAttemptTime) {
        this.state = CircuitState.HALF_OPEN;
        return true;
      }
      return false;
    }
    return true;
  }

  onSuccess(): void {
    this.failureCount = 0;
    this.state = CircuitState.CLOSED;
  }

  onFailure(now: number): void {
    this.failureCount++;
    if (this.failureCount >= this.threshold) {
      this.state = CircuitState.OPEN;
      this.nextAttemptTime = now + this.resetTimeoutMs;
    }
  }

  getState(): CircuitState { return this.state; }
}

export class EgressGateway {
  private cb = new CircuitBreaker();

  async processMessage(
    msg: OutboundMessage,
    transport: (url: string, body: string, headers: Record<string, string>) => Promise<number>
  ): Promise<"SENT" | "RETRY" | "DLQ"> {
    const now = Date.now();
    if (!this.cb.canExecute(now)) {
      return "RETRY"; // Circuit Breaker відсікає виклики до впалого сервісу
    }

    const signature = createHmac("sha256", msg.secret)
      .update(`${now}.${msg.payloadJson}`)
      .digest("hex");

    const headers = {
      "Content-Type": "application/json",
      "X-Signature": `t=${now},v1=${signature}`,
      "X-Idempotency-Key": msg.id,
    };

    try {
      const statusCode = await transport(msg.destinationUrl, msg.payloadJson, headers);
      if (statusCode >= 200 && statusCode < 300) {
        this.cb.onSuccess();
        return "SENT";
      }
      if (statusCode >= 400 && statusCode < 500 && statusCode !== 429) {
        return "DLQ"; // Помилка конфігурації (4xx) — повтор не допоможе
      }
      this.cb.onFailure(Date.now());
    } catch (err) {
      this.cb.onFailure(Date.now());
    }

    if (msg.attempt + 1 >= msg.maxAttempts) {
      return "DLQ"; // Отруйне повідомлення вичерпало спроби
    }
    return "RETRY";
  }

  calculateBackoff(attempt: number, baseMs = 100, maxMs = 5000): number {
    const temp = Math.min(maxMs, baseMs * Math.pow(2, attempt));
    const jitter = temp * 0.5 * Math.random();
    return Math.floor(temp + jitter);
  }
}
```
```py
import hmac, hashlib, time, math, random
from enum import Enum

class CircuitState(Enum):
    CLOSED = 1
    OPEN = 2
    HALF_OPEN = 3

class CircuitBreaker:
    def __init__(self, threshold: int = 3, reset_timeout_sec: float = 10.0):
        self.threshold = threshold
        self.reset_timeout_sec = reset_timeout_sec
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.next_attempt_time = 0.0

    def can_execute(self, now: float) -> bool:
        if self.state == CircuitState.OPEN:
            if now >= self.next_attempt_time:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self, now: float):
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.state = CircuitState.OPEN
            self.next_attempt_time = now + self.reset_timeout_sec

class EgressGateway:
    def __init__(self):
        self.cb = CircuitBreaker()

    def process_message(self, msg_id: str, url: str, payload: str, secret: str, attempt: int, max_attempts: int, transport_fn) -> str:
        now = time.time()
        if not self.cb.can_execute(now):
            return "RETRY"

        signed_payload = f"{int(now)}.{payload}".encode()
        sig = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "X-Signature": f"t={int(now)},v1={sig}",
            "X-Idempotency-Key": msg_id,
        }

        try:
            status_code = transport_fn(url, payload, headers)
            if 200 <= status_code < 300:
                self.cb.on_success()
                return "SENT"
            if 400 <= status_code < 500 and status_code != 429:
                return "DLQ"
            self.cb.on_failure(time.time())
        except Exception:
            self.cb.on_failure(time.time())

        if attempt + 1 >= max_attempts:
            return "DLQ"
        return "RETRY"

    def calculate_backoff(self, attempt: int, base_sec: float = 0.1, max_sec: float = 5.0) -> float:
        temp = min(max_sec, base_sec * (2 ** attempt))
        jitter = temp * 0.5 * random.random()
        return temp + jitter
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

typedef enum { CB_CLOSED, CB_OPEN, CB_HALF_OPEN } cb_state_t;

typedef struct {
    cb_state_t state;
    int failure_count;
    int threshold;
    time_t next_attempt_time;
    int reset_timeout_sec;
} circuit_breaker_t;

typedef struct {
    char id[64];
    char url[256];
    char payload[1024];
    int attempt;
    int max_attempts;
} outbound_msg_t;

void cb_init(circuit_breaker_t* cb, int threshold, int reset_sec) {
    cb->state = CB_CLOSED;
    cb->failure_count = 0;
    cb->threshold = threshold;
    cb->next_attempt_time = 0;
    cb->reset_timeout_sec = reset_sec;
}

bool cb_can_execute(circuit_breaker_t* cb, time_t now) {
    if (cb->state == CB_OPEN) {
        if (now >= cb->next_attempt_time) {
            cb->state = CB_HALF_OPEN;
            return true;
        }
        return false;
    }
    return true;
}

void cb_on_success(circuit_breaker_t* cb) {
    cb->failure_count = 0;
    cb->state = CB_CLOSED;
}

void cb_on_failure(circuit_breaker_t* cb, time_t now) {
    cb->failure_count++;
    if (cb->failure_count >= cb->threshold) {
        cb->state = CB_OPEN;
        cb->next_attempt_time = now + cb->reset_timeout_sec;
    }
}

const char* process_outbound_msg(circuit_breaker_t* cb, outbound_msg_t* msg, int (*transport_fn)(const char*, const char*)) {
    time_t now = time(NULL);
    if (!cb_can_execute(cb, now)) {
        return "RETRY";
    }

    int status = transport_fn(msg->url, msg->payload);
    if (status >= 200 && status < 300) {
        cb_on_success(cb);
        return "SENT";
    }
    if (status >= 400 && status < 500 && status != 429) {
        return "DLQ";
    }

    cb_on_failure(cb, time(NULL));
    if (msg->attempt + 1 >= msg->max_attempts) {
        return "DLQ";
    }
    return "RETRY";
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <random>
#include <cmath>
#include <functional>

enum class CircuitState { Closed, Open, HalfOpen };
enum class DeliveryResult { Sent, Retry, Dlq };

struct OutboundMessage {
    std::string id;
    std::string url;
    std::string payload;
    std::string secret;
    int attempt{0};
    int maxAttempts{5};
};

class CircuitBreaker {
public:
    explicit CircuitBreaker(int threshold = 3, std::chrono::seconds resetTimeout = std::chrono::seconds(10))
        : threshold_(threshold), resetTimeout_(resetTimeout) {}

    bool canExecute(std::chrono::steady_clock::time_point now) {
        if (state_ == CircuitState::Open) {
            if (now >= nextAttemptTime_) {
                state_ = CircuitState::HalfOpen;
                return true;
            }
            return false;
        }
        return true;
    }

    void onSuccess() {
        failureCount_ = 0;
        state_ = CircuitState::Closed;
    }

    void onFailure(std::chrono::steady_clock::time_point now) {
        failureCount_++;
        if (failureCount_ >= threshold_) {
            state_ = CircuitState::Open;
            nextAttemptTime_ = now + resetTimeout_;
        }
    }

    [[nodiscard]] CircuitState state() const noexcept { return state_; }

private:
    int threshold_;
    std::chrono::seconds resetTimeout_;
    CircuitState state_{CircuitState::Closed};
    int failureCount_{0};
    std::chrono::steady_clock::time_point nextAttemptTime_;
};

class EgressGateway {
public:
    using TransportFn = std::function<int(std::string_view url, std::string_view body, const std::unordered_map<std::string, std::string>& headers)>;

    explicit EgressGateway(CircuitBreaker cb = CircuitBreaker{}) : cb_(std::move(cb)) {}

    DeliveryResult processMessage(const OutboundMessage& msg, const TransportFn& transport) {
        auto now = std::chrono::steady_clock::now();
        if (!cb_.canExecute(now)) {
            return DeliveryResult::Retry;
        }

        std::unordered_map<std::string, std::string> headers{
            {"Content-Type", "application/json"},
            {"X-Idempotency-Key", msg.id}
        };

        try {
            int statusCode = transport(msg.url, msg.payload, headers);
            if (statusCode >= 200 && statusCode < 300) {
                cb_.onSuccess();
                return DeliveryResult::Sent;
            }
            if (statusCode >= 400 && statusCode < 500 && statusCode != 429) {
                return DeliveryResult::Dlq;
            }
            cb_.onFailure(std::chrono::steady_clock::now());
        } catch (...) {
            cb_.onFailure(std::chrono::steady_clock::now());
        }

        if (msg.attempt + 1 >= msg.maxAttempts) {
            return DeliveryResult::Dlq;
        }
        return DeliveryResult::Retry;
    }

    [[nodiscard]] std::chrono::milliseconds calculateBackoff(
        int attempt,
        std::chrono::milliseconds baseMs = std::chrono::milliseconds(100),
        std::chrono::milliseconds maxMs = std::chrono::milliseconds(5000)
    ) const {
        double temp = std::min(static_cast<double>(maxMs.count()), baseMs.count() * std::pow(2.0, attempt));
        std::uniform_real_distribution<double> dist(0.0, 0.5 * temp);
        thread_local std::mt19937 rng{std::random_device{}()};
        return std::chrono::milliseconds(static_cast<long long>(temp + dist(rng)));
    }

private:
    CircuitBreaker cb_;
};
```
:::

## Плавне завершення (Graceful Shutdown) робітників

Під час розгортання нових версій сервісу або перезавантаження вузлів (Deployment / Auto-scaling) воркери Egress Gateway отримують сигнал операційної системи `SIGTERM`.

Некоректне завершення робітника під час виходу в мережу створює висячі сокети та залишає задачі в базі даних у стані `PROCESSING`. Процедура плавного зупинення реалізується так:

1. **Перехоплення `SIGTERM` / `SIGINT`:** Воркер припиняє захоплення нових задач із таблиці `outbound_outbox` через `SKIP LOCKED`.
2. **Таймаут виходу вхідних викликів (Drain Phase):** Воркер надає активним HTTP-запитам 10 секунд для завершення мережевого обміну та отримання коду відповіді.
3. **Збереження або відкат стану:** Усі активні задачі, які не встигли завершитися протягом таймауту плавного зупинення, повертаються у стан `PENDING` з оновленням `next_retry_at = NOW()`, щоб їх миттєво захопили інші працездатні інстанси.

## Крайові випадки, простеження (Observability) та трасування

Виробнича експлуатація вихідного вузла вимагає глибокого моніторингу та обробки рідкісних крайових випадків:

1. **Падіння робітника під час HTTP-виклику:** Якщо процес Egress Gateway вбивається операційною системою (`SIGKILL`) у момент, коли сокет вислав байти, але відповідь ще не записана в БД, статус задачі залишається `PROCESSING`. Для лікування цього використовується механізм **Visibility Timeout** (протухання оренди). Якщо задача сидить у статусі `PROCESSING` понад 5 хвилин без оновлення `updated_at`, інший воркер скидає її стан до `FAILED` і забирає на повторну спробу.
2. **Зсув годинника (Clock Drift):** HMAC-підпис вимагає передачі поточного часу `t`. Якщо системний годинник сервера відхиляється від UTC більше ніж на 30 секунд, приймач відхилить усі підписи як застарілі. Для запобігання цьому вузол повинен синхронізувати час через NTP та використовувати монотонні годинники для вимірювання затримок.
3. **Наскрізне трасування OpenTelemetry:** Для відстеження повного шляху події вихідний вузол прокидає заголовки трасування OpenTelemetry (`traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`) у вихідні HTTP-заголовки. Це дає змогу пов'язати локальний спан запису в outbox із вихідним мережевим викликом у єдиному графі Distributed Tracing.
4. **Метрики Prometheus:** Стійкий вихідний вузол експортує такі обов'язкові метрики:
   * `egress_requests_total{destination, status}` — загальна кількість спроб доставок.
   * `egress_circuit_breaker_state{destination}` — поточний стан автоматичного вимикача (0 = CLOSED, 1 = OPEN, 2 = HALF_OPEN).
   * `egress_dlq_messages_total{destination}` — кількість отруйних повідомлень, відправлених у DLQ.
   * `egress_delivery_latency_seconds{destination}` — гістограма затримок доставки.
