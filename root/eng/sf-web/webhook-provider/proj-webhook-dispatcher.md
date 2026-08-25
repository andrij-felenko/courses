# ⚙️ Реалізація надійного диспетчера вебхуків

Побудова промислового провайдера вебхуків вимагає створення відмовостійкого конвеєра доставки, що поєднує вибірку подій із таблиці Transactional Outbox, керування пулом асинхронних HTTP-воркерів, криптографічний підпис запитів HMAC-SHA256, експоненційний ретрай із повним джитером, ізоляцію повільних споживачів (Fair-Share Queueing) та запобіжник несправних адрес (Circuit Breaker).

У цій вставці наведено практичну архітектуру, покроковий інженерний розбір та повну реалізацію ядра диспетчера доставки подій, здатного гарантувати надійність рівня At-Least-Once без блокування глобального пулу з'єднань збійними або повільними кінцевими адресами.

## 1. Архітектурні вимоги до диспетчера

Провайдер вебхуків кардинально відрізняється від звичайного HTTP-клієнта: він не контролює сервери, до яких звертається. Кінцеві точки споживачів можуть бути розміщені на повільних каналах зв'язку, зависати на десятки секунд під внутрішнім блокуванням бази даних, падати під навантаженням або навмисно утримувати відкриті з'єднання без надсилання байтів відповіді. Якщо побудувати конвеєр відправки наївно — як прямий виклик HTTP POST із черги в міру надходження, — система швидко зіткнеться з трьома критичними дефектами:

1. **Блокування пулу потоків (Head-of-Line Blocking):** якщо один клієнт налаштував ендпоінт, який зависає на 29 секунд до спрацьовування таймауту, воркери провайдера вичерпають доступні сокети та потоки виконання. Події для тисяч інших клієнтів, чиї сервери відповідають за 15 мілісекунд, застрягнуть у черзі й отримають штучні затримки в години.
2. **Синхронізація повторів (Thundering Herd):** якщо приймальний сервер великого споживача перезавантажується після аварії, детермінований ретрай призведе до того, що всі накопичені події вдарять по ньому одночасно в одну й ту саму секунду, спричиняючи повторний колапс.
3. **Неузгодженість стану при збої (Dual-Write Problem):** запис бізнес-даних у базу даних та відправка мережевого запиту не можуть бути об'єднані в одну атомарну операцію без спеціального патерну фіксації.

Розв'язання цих проблем вимагає комплексного конвеєра, у якому кожен компонент виконує суворо ізольовану функцію.

## 2. Модель даних: Transactional Outbox та історія спроб

Фундаментом надійності є таблиця Transactional Outbox. Коли користувач здійснює дію в системі (наприклад, створює замовлення `orders`), запис бізнес-сутності та створення події `outbox_events` виконуються в межах єдиної ACID-транзакції реляційної СУБД. Це гарантує, що подія не може бути створена без збереження даних, і навпаки — збережені дані ніколи не залишаться без відповідної події.

Диспетчер подій опитує базу даних пакетами. Щоб уникнути конфліктів між кількома паралельними екземплярами диспетчера (воркерами), використовується конструкція `FOR UPDATE SKIP LOCKED`. Вона наказує СУБД заблокувати рядки для поточного процесу та пропустити будь-які записи, які вже обробляються іншими воркерами, без очікування звільнення блокувань.

Нижче наведено промислову SQL-схему для PostgreSQL:

```sql
CREATE TYPE webhook_status AS ENUM ('pending', 'processing', 'delivered', 'failed', 'dead_letter');

CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    destination_url TEXT NOT NULL,
    secret_key VARCHAR(128) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    status webhook_status NOT NULL DEFAULT 'pending',
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 10,
    next_retry_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    locked_by VARCHAR(64),
    locked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Частковий індекс для швидкої вибірки лише тих подій, що готові до відправки
CREATE INDEX idx_outbox_poll ON outbox_events (next_retry_at, status) 
WHERE status IN ('pending', 'failed');

-- Таблиця аудиту спроб доставки для діагностики та надання логів користувачам
CREATE TABLE delivery_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES outbox_events(id) ON DELETE CASCADE,
    attempt_number INT NOT NULL,
    response_status INT,
    response_body TEXT,
    duration_ms INT NOT NULL,
    error_message TEXT,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_attempts_event ON delivery_attempts (event_id);
```

Запит вибірки для воркера захоплює партію доступних записів, позначає їх як `processing` і повертає диспетчеру:

```sql
UPDATE outbox_events
SET status = 'processing',
    locked_by = $1,
    locked_at = NOW(),
    updated_at = NOW()
WHERE id IN (
    SELECT id FROM outbox_events
    WHERE (status = 'pending' OR status = 'failed')
      AND next_retry_at <= NOW()
    ORDER BY next_retry_at ASC
    LIMIT $2
    FOR UPDATE SKIP LOCKED
)
RETURNING *;
```

У високонавантажених системах для запобігання розростанню таблиці `outbox_events` (англ. table bloat) успішно доставлені записи видаляються або переміщуються у партиційований архів фоновим процесом (vacuum / archive job). 

Альтернативою транзакційному опитуванню (polling) на обсягах понад 50 000 подій на секунду є Change Data Capture (CDC) через читання журналу попереджувального запису СУБД (PostgreSQL WAL або MySQL binlog) за допомогою інструментів на кшталт Debezium. CDC повністю знімає навантаження опитування з таблиці, транслюючи кожен зафіксований рядок безпосередньо у брокер черг (Kafka або Redis Streams).

## 3. Криптографічний підпис та заголовки контракту

Автентифікація вебхука здійснюється шляхом передачі криптографічного коду автентифікації повідомлення (HMAC-SHA256), обчисленого на основі спільного секретного ключа клієнта.

Щоб захистити споживача від атак повторного відтворення (англ. replay attacks), коли перехоплений зловмисником валідний HTTP-запит відправляється повторно через кілька годин, підпис формується не лише від тіла повідомлення, але й від поточної мітки часу Unix epoch:

```
signature_payload = "t=" + timestamp + "." + raw_payload_bytes
signature_hash = HMAC_SHA256(secret_key, signature_payload)
```

Заголовок `X-Signature-256` передається у форматі: `t=1718800000,v1=a1b2c3...`. Отримувач зобов'язаний:
1. Перевірити, що різниця між поточним часом сервера та міткою `t` не перевищує допустимого вікна (наприклад, 300 секунд);
2. Розрахувати очікуваний HMAC на основі сирих байтів отриманого тіла та мітки `t`;
3. Виконати побайтове порівняння сталого часу (англ. constant-time comparison), щоб виключити витік інформації через атаки за часом виконання (англ. timing attacks).

Крім підпису, запит супроводжується заголовками:
- `X-Event-Id` — унікальний ідентифікатор події для ідемпотентної дедуплікації у вхідній скриньці (inbox);
- `X-Event-Type` — тип бізнес-події (наприклад, `payment.succeeded`);
- `X-Delivery-Attempt` — номер поточної спроби, що допомагає споживачеві відрізнити первинну доставку від повторів;
- `User-Agent` — ідентифікатор провайдера вебхуків із посиланням на документацію.

## 4. Алгоритм розрахунку інтервалів: Exponential Backoff з Full Jitter

Якщо виклик завершується тимчасовою помилкою (мережевий розрив, тайм-аут або коди HTTP 5xx / 429), повідомлення планується на повторну спробу.

Математична модель Full Jitter обчислює детерміновану експоненційну стелю для поточної спроби `V_n = min(t_max, t_0 · 2ⁿ)` і вибирає псевдовипадкове значення затримки, рівномірно розподілене на відрізку `[0, V_n]`:

```
delay = Uniform(0, min(max_delay, base_delay * 2^attempt))
```

Цей підхід розсіює пікову інтенсивність трафіку на порядок величини порівняно з детермінованим відступом, захищаючи відновлювані сервери клієнтів від нового колапсу.

## 5. Запобіжник (Circuit Breaker) для зовнішніх адрес

Якщо кінцевий сервер клієнта повністю вимкнено, перебуває в аварійному стані або постійно повертає HTTP 500, відправка кожної нової події з черги призводить до марного відкриття TCP-з'єднань і очікування таймаутів.

Для кожного унікального хоста призначення створюється екземпляр Circuit Breaker із трьома станами:
- **CLOSED (Замкнений):** нормальний стан. Усі події надсилаються у звичайному режимі. Ведеться підрахунок кількості послідовних збоїв або відсотка помилок у ковзному вікні часу. Якщо лічильник помилок перевищує поріг (наприклад, 5 помилок поспіль), запобіжник розмикається.
- **OPEN (Розімкнений):** режим аварійної паузи. Будь-які запити до цього хоста негайно блокуються на рівні диспетчера без здійснення мережевого виклику. Події одразу переплановуються у чергу ретраїв. Запобіжник залишається в цьому стані протягом інтервалу охолодження (cooldown period, наприклад, 60 секунд).
- **HALF-OPEN (Напіврозімкнений):** після вичерпання таймера охолодження запобіжник дозволяє відправити рівно один пробний запит. Якщо пробний виклик повертає успішний статус HTTP 2xx, хост вважається здоровим, і запобіжник повертається в стан `CLOSED`. Якщо пробний виклик знову завершується невдачею, стан повертається в `OPEN`, а таймер охолодження збільшується за експоненційним законом.

## 6. Багатотенантна ізоляція (Fair Scheduling)

Щоб один клієнт із масивним обсягом подій або дуже повільним сервером не забивав пропускну здатність диспетчера, застосовується алгоритм маркерного кошика (англ. Token Bucket) або черг із дефіцитним круговим обслуговуванням (Deficit Round Robin).

Кожен клієнт (`tenant_id`) отримує індивідуальну квоту на кількість одночасно виконуваних запитів (наприклад, щонайбільше 20 активних HTTP-з'єднань на тенанта) та ліміт частоти відправки (наприклад, 50 запитів на секунду). Якщо ліміт вичерпано, події даного тенанта залишаються в черзі, тоді як події інших користувачів негайно переходять до пулу вільних воркерів.

## 7. Керування сокетами та мережеві тонкощі

Високонавантажений провайдер вебхуків створює десятки тисяч вихідних TCP-з'єднань до сотень різних хостів в інтернеті. Неграмотне налаштування мережевого стека операційної системи та HTTP-клієнта призводить до типових апаратних збоїв:

- **Вичерпання ефемерних портів (Ephemeral Port Exhaustion):** коли клієнт відкриває та швидко закриває TCP-з'єднання, сокет переходить у стан `TIME_WAIT` на 60 секунд (для гарантії доставки запізнілих пакетів за стандартом TCP). Якщо провайдер генерує понад 1000 запитів на секунду без повторного використання з'єднань, операційна система вичерпує діапазон портів (типово порти 32768–60999), і нові виклики падають із помилкою `EADDRNOTAVAIL`. Рішення — увімкнення пулу з'єднань HTTP Keep-Alive з налаштуванням `maxSockets` та `freeSocketTimeout`.
- **Завислі напіввідкриті з'єднання (TCP Half-Open):** якщо віддалений сервер аварійно перезавантажився без надсилання пакету `TCP FIN` або `RST`, локальний сокет залишатиметься відкритим доти, доки не спрацює таймаут операційної системи (за замовчуванням у Linux це може тривати понад 15 хвилин через механізм TCP keepalive probes). Диспетчер зобов'язаний явно встановлювати три рівні таймаутів:
  - `Connect Timeout` (1–2 секунди на встановлення TCP-з'єднання та завершення TLS-рукостискання);
  - `Write Timeout` (1–3 секунди на передачу тіла POST-запиту);
  - `Read Timeout` (5–10 секунд на отримання заголовків і перших байтів відповіді).

## 8. Повна реалізація диспетчера доставки

Нижче наведено закінчену програмну реалізацію ядра диспетчера вебхуків двома мовами: TypeScript (Node.js) та сучасним стандартом C++20. Обидва варіанти містять повноцінний пул з'єднань, генератор підписів, розрахунок Full Jitter, логіку Circuit Breaker та класифікацію результатів доставки.

:::tabs
```ts
import crypto from "node:crypto";
import http from "node:http";
import https from "node:https";

export interface OutboxEvent {
  id: string;
  tenantId: string;
  destinationUrl: string;
  secretKey: string;
  eventType: string;
  payload: Record<string, unknown>;
  attempts: number;
  maxAttempts: number;
}

export interface DeliveryResult {
  statusCode?: number;
  durationMs: number;
  error?: string;
  body?: string;
}

// ── 1. Експоненційний відступ із повним джитером ────────────────────────────
export function calculateFullJitterBackoff(
  attempt: number,
  baseDelayMs = 1000,
  maxDelayMs = 3600000
): number {
  const maxCeiling = Math.min(maxDelayMs, baseDelayMs * Math.pow(2, attempt));
  return Math.floor(Math.random() * maxCeiling);
}

// ── 2. Криптографічний підпис HMAC-SHA256 ──────────────────────────────────
export function generateWebhookHeaders(
  event: OutboxEvent,
  rawPayload: string,
  timestamp = Math.floor(Date.now() / 1000)
): Record<string, string> {
  const signaturePayload = `t=${timestamp}.${rawPayload}`;
  const signature = crypto
    .createHmac("sha256", event.secretKey)
    .update(signaturePayload)
    .digest("hex");

  return {
    "Content-Type": "application/json",
    "User-Agent": "WebhookEngine/2.0 (+https://provider.example.com)",
    "X-Event-Id": event.id,
    "X-Event-Type": event.eventType,
    "X-Delivery-Attempt": String(event.attempts + 1),
    "X-Timestamp": String(timestamp),
    "X-Signature-256": `t=${timestamp},v1=${signature}`,
  };
}

// ── 3. Запобіжник (Circuit Breaker) для хостів ─────────────────────────────
export enum CircuitState {
  CLOSED,
  OPEN,
  HALF_OPEN,
}

export class HostCircuitBreaker {
  private state = CircuitState.CLOSED;
  private consecutiveFailures = 0;
  private lastStateChange = Date.now();
  private readonly failureThreshold: number;
  private readonly cooldownMs: number;

  constructor(failureThreshold = 5, cooldownMs = 60000) {
    this.failureThreshold = failureThreshold;
    this.cooldownMs = cooldownMs;
  }

  public canAttempt(): boolean {
    const now = Date.now();
    if (this.state === CircuitState.OPEN) {
      if (now - this.lastStateChange >= this.cooldownMs) {
        this.state = CircuitState.HALF_OPEN;
        this.lastStateChange = now;
        return true;
      }
      return false;
    }
    return true;
  }

  public recordSuccess(): void {
    this.consecutiveFailures = 0;
    this.state = CircuitState.CLOSED;
    this.lastStateChange = Date.now();
  }

  public recordFailure(): void {
    this.consecutiveFailures++;
    if (
      this.state === CircuitState.HALF_OPEN ||
      this.consecutiveFailures >= this.failureThreshold
    ) {
      this.state = CircuitState.OPEN;
      this.lastStateChange = Date.now();
    }
  }

  public getState(): CircuitState {
    return this.state;
  }
}

// ── 4. Диспетчер доставки та керування пулом ────────────────────────────────
export class WebhookDispatcher {
  private breakers = new Map<string, HostCircuitBreaker>();
  private httpAgent: http.Agent;
  private httpsAgent: https.Agent;

  constructor(maxSockets = 100) {
    this.httpAgent = new http.Agent({ keepAlive: true, maxSockets });
    this.httpsAgent = new https.Agent({ keepAlive: true, maxSockets });
  }

  private getHost(urlStr: string): string {
    try {
      return new URL(urlStr).hostname;
    } catch {
      return urlStr;
    }
  }

  private getBreaker(host: string): HostCircuitBreaker {
    let cb = this.breakers.get(host);
    if (!cb) {
      cb = new HostCircuitBreaker();
      this.breakers.set(host, cb);
    }
    return cb;
  }

  public async deliver(event: OutboxEvent, timeoutMs = 10000): Promise<DeliveryResult> {
    const host = this.getHost(event.destinationUrl);
    const breaker = this.getBreaker(host);

    if (!breaker.canAttempt()) {
      return {
        durationMs: 0,
        error: `CircuitBreaker: delivery paused for host ${host} (state: OPEN)`,
      };
    }

    const payloadStr = JSON.stringify(event.payload);
    const headers = generateWebhookHeaders(event, payloadStr);
    const startTime = Date.now();

    try {
      const url = new URL(event.destinationUrl);
      const isHttps = url.protocol === "https:";
      const agent = isHttps ? this.httpsAgent : this.httpAgent;

      const result = await new Promise<DeliveryResult>((resolve) => {
        const req = (isHttps ? https : http).request(
          url,
          {
            method: "POST",
            headers,
            agent,
            timeout: timeoutMs,
          },
          (res) => {
            let resBody = "";
            res.setEncoding("utf8");
            res.on("data", (chunk) => (resBody += chunk));
            res.on("end", () => {
              const durationMs = Date.now() - startTime;
              resolve({
                statusCode: res.statusCode,
                durationMs,
                body: resBody.slice(0, 1024),
              });
            });
          }
        );

        req.on("timeout", () => {
          req.destroy(new Error(`HTTP request timed out after ${timeoutMs}ms`));
        });

        req.on("error", (err) => {
          const durationMs = Date.now() - startTime;
          resolve({
            durationMs,
            error: err.message,
          });
        });

        req.write(payloadStr);
        req.end();
      });

      if (result.statusCode && result.statusCode >= 200 && result.statusCode < 300) {
        breaker.recordSuccess();
      } else if (
        !result.statusCode ||
        result.statusCode >= 500 ||
        result.statusCode === 429 ||
        result.statusCode === 408
      ) {
        breaker.recordFailure();
      }

      return result;
    } catch (err: any) {
      breaker.recordFailure();
      return {
        durationMs: Date.now() - startTime,
        error: err?.message ?? "Unknown network error",
      };
    }
  }

  public classifyOutcome(
    result: DeliveryResult,
    event: OutboxEvent
  ): { nextStatus: "delivered" | "failed" | "dead_letter"; retryDelayMs?: number } {
    if (result.statusCode && result.statusCode >= 200 && result.statusCode < 300) {
      return { nextStatus: "delivered" };
    }

    const isPermanentClientError =
      result.statusCode &&
      result.statusCode >= 400 &&
      result.statusCode < 500 &&
      result.statusCode !== 408 &&
      result.statusCode !== 429;

    const nextAttempt = event.attempts + 1;

    if (isPermanentClientError || nextAttempt >= event.maxAttempts) {
      return { nextStatus: "dead_letter" };
    }

    const retryDelayMs = calculateFullJitterBackoff(nextAttempt);
    return { nextStatus: "failed", retryDelayMs };
  }
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <memory>
#include <unordered_map>
#include <expected>
#include <optional>
#include <algorithm>

// ── 1. Типи даних та структури подій ───────────────────────────────────────
struct OutboxEvent {
    std::string id;
    std::string tenant_id;
    std::string destination_url;
    std::string secret_key;
    std::string event_type;
    std::string payload_json;
    int attempts = 0;
    int max_attempts = 10;
};

struct DeliveryResult {
    std::optional<int> status_code;
    std::chrono::milliseconds duration;
    std::string body;
    std::string error_message;
};

enum class DeliveryStatus {
    Delivered,
    RetryableFailed,
    DeadLetter
};

// ── 2. Алгоритм розрахунку Full Jitter ──────────────────────────────────────
class BackoffCalculator {
public:
    static std::chrono::milliseconds calculate_full_jitter(
        int attempt,
        std::chrono::milliseconds base_delay = std::chrono::milliseconds(1000),
        std::chrono::milliseconds max_delay = std::chrono::milliseconds(3600000)
    ) {
        int safe_shift = std::min(attempt, 30);
        uint64_t multiplier = 1ULL << safe_shift;
        uint64_t calculated = base_delay.count() * multiplier;
        uint64_t ceiling = std::min(static_cast<uint64_t>(max_delay.count()), calculated);

        static thread_local std::mt19937_64 rng(std::random_device{}());
        std::uniform_int_distribution<uint64_t> dist(0, ceiling);

        return std::chrono::milliseconds(dist(rng));
    }
};

// ── 3. Автомат станів Circuit Breaker ──────────────────────────────────────
enum class CircuitState { Closed, Open, HalfOpen };

class HostCircuitBreaker {
public:
    explicit HostCircuitBreaker(int threshold = 5, std::chrono::milliseconds cooldown = std::chrono::seconds(60))
        : failure_threshold_(threshold), cooldown_(cooldown),
          state_(CircuitState::Closed), consecutive_failures_(0),
          last_state_change_(std::chrono::steady_clock::now()) {}

    bool can_attempt() {
        auto now = std::chrono::steady_clock::now();
        if (state_ == CircuitState::Open) {
            if (now - last_state_change_ >= cooldown_) {
                state_ = CircuitState::HalfOpen;
                last_state_change_ = now;
                return true;
            }
            return false;
        }
        return true;
    }

    void record_success() {
        consecutive_failures_ = 0;
        state_ = CircuitState::Closed;
        last_state_change_ = std::chrono::steady_clock::now();
    }

    void record_failure() {
        consecutive_failures_++;
        if (state_ == CircuitState::HalfOpen || consecutive_failures_ >= failure_threshold_) {
            state_ = CircuitState::Open;
            last_state_change_ = std::chrono::steady_clock::now();
        }
    }

    CircuitState state() const { return state_; }

private:
    int failure_threshold_;
    std::chrono::milliseconds cooldown_;
    CircuitState state_;
    int consecutive_failures_;
    std::chrono::steady_clock::time_point last_state_change_;
};

// ── 4. Класифікатор наслідків доставки ──────────────────────────────────────
class OutcomeClassifier {
public:
    struct Decision {
        DeliveryStatus status;
        std::chrono::milliseconds next_retry_delay{0};
    };

    static Decision evaluate(const DeliveryResult& result, const OutboxEvent& event) {
        if (result.status_code.has_value() && *result.status_code >= 200 && *result.status_code < 300) {
            return Decision{DeliveryStatus::Delivered, std::chrono::milliseconds(0)};
        }

        bool is_permanent_4xx = result.status_code.has_value() &&
                                *result.status_code >= 400 && *result.status_code < 500 &&
                                *result.status_code != 408 && *result.status_code != 429;

        int next_attempt = event.attempts + 1;
        if (is_permanent_4xx || next_attempt >= event.max_attempts) {
            return Decision{DeliveryStatus::DeadLetter, std::chrono::milliseconds(0)};
        }

        auto delay = BackoffCalculator::calculate_full_jitter(next_attempt);
        return Decision{DeliveryStatus::RetryableFailed, delay};
    }
};
```
:::

## 9. Розподілена координація та кластерний масштаб

У багатосерверному середовищі диспетчер масштабується горизонтально як набір безстанних подів Kubernetes або віртуальних машин. Це породжує питання розподіленої координації:

1. **Конкуренція за записи Outbox:** завдяки вибірці `SELECT ... FOR UPDATE SKIP LOCKED` екземпляри не блокують один одного. Кожен інстанс бере власну неперетинну порцію рядків.
2. **Розподілений Circuit Breaker:** у пам'яті локального процесу стан запобіжника може розходитися між нодами. Для кластерів із десятками нод стан помилок хостів зберігається у спільному Redis-кеші з використанням ковзного вікна на основі Redis Sorted Sets або структур HyperLogLog. Це дозволяє миттєво відключити відправку на несправний хост на всіх серверах одночасно.
3. **Очищення завислих блокувань (Orphan Lock Reaper):** якщо один із серверів-воркерів зазнає апаратного крешу посеред виконання HTTP-запиту, захоплені ним рядки залишаться у статусі `processing` із міткою `locked_by`. Фоновий процес-наглядач періодично виконує запит відновлення:
```sql
UPDATE outbox_events
SET status = 'pending',
    locked_by = NULL,
    locked_at = NULL
WHERE status = 'processing'
  AND locked_at < NOW() - INTERVAL '5 minutes';
```
Цей механізм гарантує, що жодне повідомлення не загубиться навіть при раптовому вимкненні живлення всього центру обробки даних.

## 10. Покрокове трасування обробки подій

Простежимо повний шлях повідомлення крізь систему диспетчера від миті генерації до завершення:

1. **Фіксація в Outbox (`t = 0.000s`):** Бізнес-сервіс білінгу у транзакції створює підписку та записує рядок у `outbox_events` зі статусом `pending`, `next_retry_at = NOW()`.
2. **Вибірка воркером (`t = 0.015s`):** Воркер викликає SQL `UPDATE ... SKIP LOCKED`. Рядок переходить у статус `processing`, `locked_by = 'worker-node-4'`.
3. **Формування запиту (`t = 0.016s`):** Генератор підпису рахує HMAC-SHA256, додає заголовки `X-Signature-256`, `X-Event-Id`, `X-Timestamp`.
4. **Перевірка Circuit Breaker (`t = 0.017s`):** Для хоста `api.client.com` стан запобіжника `CLOSED`. Запит дозволено.
5. **Мережева спроба 1 (`t = 0.018s`):** Вихідний сокет підключається до хоста. Через 10.0 секунд сервер споживача повертає код `HTTP 504 Gateway Timeout`.
6. **Класифікація помилки (`t = 10.019s`):** Код 504 є тимчасовим збоєм. Лічильник помилок Circuit Breaker стає `1`. Спроба `1` менша за ліміт `10`.
7. **Розрахунок затримки (`t = 10.020s`):** Функція `calculateFullJitterBackoff(attempt=1, base=1000ms)` генерує випадкове число на інтервалі `[0, 2000]`, наприклад `1420` мс.
8. **Оновлення бази (`t = 10.025s`):** Воркер оновлює рядок: `status = 'failed'`, `attempts = 1`, `next_retry_at = NOW() + 1.42s`. В історію `delivery_attempts` записується звіт про збій 504 тривалістю 10001 мс.
9. **Спроба 2 (`t = 11.450s`):** Після закінчення інтервалу 1.42с воркер знову захоплює подію. Цього разу сервер споживача відповідає `HTTP 200 OK` за 45 мс.
10. **Фіналізація (`t = 11.498s`):** Запобіжник скидає лічильник невдач у `0`. Статус події оновлюється на `delivered`. Рядок готовий до архівування.

## 11. Захист від вразливостей: SSRF та DNS Rebinding

Специфіка провайдера вебхуків полягає в тому, що система виконує вихідні HTTP-запити на URL-адреси, які задаються довільними зовнішніми користувачами. Це створює прямий ризик підробки міжсерверних запитів (англ. Server-Side Request Forgery, SSRF).

Якщо зловмисник вказує адресу `http://169.254.169.254/latest/meta-data/` (ендпоінт метаданих хмарних інстансів AWS/GCP) або `http://127.0.0.1:6379/` (внутрішній порт кешу Redis), небезпечний диспетчер може надіслати HTTP POST всередину захищеного периметра інфраструктури провайдера, розкривши ключі шифрування або облікові дані IAM.

Надійний диспетчер зобов'язаний реалізувати триетапний захист:

1. **Валідація протоколу та порту:** дозволяються виключно схеми `https://` (порт 443) та у виняткових випадках `http://` (порт 80). Будь-які незвичні порти (22, 3306, 5432, 6379, 8080) блокуються на рівні конфігурації.
2. **Фільтрація IP-адрес за чорним списком (Bogon / Private ranges):** перед відкриттям сокета доменне ім'я перетворюється на IP-адресу через системний DNS-резолвер. Якщо отримана IP-адреса належить до приватних, локальних або службових мереж, запит негайно відхиляється:
   - `127.0.0.0/8` (Loopback-адреси хоста);
   - `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (Приватні підмережі локальної мережі);
   - `169.254.0.0/16` (Link-Local та хмарні метадані);
   - `::1/128`, `fc00::/7`, `fe80::/10` (Аналогічні діапазони для протоколу IPv6).
3. **Захист від атак підміни DNS (DNS Rebinding):** атакуючий сервер може повернути валідну публічну IP-адресу під час попередньої перевірки URL, але на момент реального виконання HTTP-запиту його DNS-сервер поверне `127.0.0.1`. Щоб виключити цю вразливість, HTTP-клієнт провайдера повинен відкривати TCP-з'єднання безпосередньо за попередньо перевіреною IP-адресою, передаючи оригінальне доменне ім'я виключно в HTTP-заголовку `Host` та у полі TLS SNI (Server Name Indication).

## 12. Експлуатаційні метрики та життєвий цикл DLQ

Надійність роботи провайдера визначається прозорістю його метрик та керованістю черги збійних повідомлень.

Коли кількість невдалих спроб досягає порогу `max_attempts` або сервер повертає перманентну помилку HTTP 410 (Gone), подія переходить у статус `dead_letter`. Це поглинальний стан, який вимагає дій від користувача або оператора:

1. **Інформування споживача:** система надсилає автоматичне сповіщення (email або системний алерт) розробникам клієнта про те, що доставка на їхній ендпоінт призупинена через серійні збої.
2. **Панель діагностики (Delivery Logs UI):** провайдер надає користувачам доступ до історії викликів із таблиці `delivery_attempts`, показуючи точний час, затримку, код статусу та уривок тіла відповіді клієнтського сервера.
3. **API повторного відтворення (Manual Replay API):** після того, як розробники клієнта виправлять помилку в обробнику або піднімуть упалий сервер, вони викликають API провайдера `POST /api/v1/webhooks/replay`, передаючи ідентифікатор події або часовий діапазон. Диспетчер оновлює статус подій із `dead_letter` назад на `pending`, скидає лічильник спроб на `attempts = 0` і повертає їх у чергу регулярної доставки.
4. **Автоматичне вивантаження та партиціювання архіву:** події зі статусами `delivered` та `dead_letter`, старші за 30 днів, автоматично переміщуються у довготривале «холодне» об'єктне сховище (S3/GCS) у форматі Parquet, запобігаючи деградації продуктивності основної оперативної бази даних.
