# ⚙️ Розподілений диспетчер розсилки: батчинг, ліміти й конвеєр доставки

У високонавантажених веб-сервісах вузол розсилки сповіщень (Notification Fanout Dispatcher) є критичною інфраструктурною ланкою між внутрішніми подіями платформи (створення замовлення, новий коментар, критичне сповіщення безпеки) та зовнішніми провайдерами доставки (Apple APNs, Google FCM, транзакційні SMTP-шлюзи).

Пряме відправлення мережевого запиту на кожного користувача в синхронному коді призводить до миттєвого вичерпання пулу з'єднань, блокування потоків виконання та бану з боку провайдерів за перевищення лімітів (Rate Limits).

## Інженерні вимоги до ядра диспетчера

Надійний диспетчер розсилки повинен гарантувати стабільність за будь-якого обсягу вхідного навантаження, спираючись на п'ять ключових архітектурних механізмів:
1. **Батчинг та сегментація (Chunking):** розбиття великих масивів адрес на фіксовані пакети (наприклад, по 500 токенів для FCM або пакети мультиплексованих стрімів для APNs).
2. **Контроль темпу відправки (Rate Limiting):** алгоритм Token Bucket для обмеження вихідного потоку відповідно до контракту та репутації пулу IP-адрес.
3. **Шардування та паралельна обробка:** пул незалежних воркерів із керованим протитиском (Backpressure), що запобігає переповненню черг пам'яті.
4. **Зворотний зв'язок (Feedback Loop):** асинхронний збір застарілих та невалідних токенів пристроїв (коди `410 Gone`, `400 BadDeviceToken`) для негайного видалення з бази даних.
5. **Маршрутизація відмов (Dead Letter Queue, DLQ):** ізоляція повідомлень із фатальними помилками або перевищенням кількості повторів.

## Життєвий цикл події у конвеєрі диспетчера

Конвеєр обробки повідомлення складається з послідовності чітко розмежованих стадій:
1. **Зчитування з брокера:** воркер вичитує завдання розсилки з черги (наприклад, топіка Apache Kafka або черги RabbitMQ).
2. **Валідація та збагачення (Enrichment):** перевірка налаштувань користувача (Do Not Disturb, часовий пояс), вибір актуальних токенів пристроїв зі сховища сесій.
3. **Пакування в батчі:** групування токенів за типом цільового провайдера (iOS APNs, Android FCM, Web Push) у чанки фіксованого розміру.
4. **Проходження крізь Rate Limiter:** списання токенів пропускної здатності. Якщо токенів недостатньо, потік призупиняється без блокування вхідної черги.
5. **Мережева доставка:** передача батча через пул довгоживучих з'єднань із мультиплексуванням.
6. **Класифікація результатів:** парсинг індивідуальних статусів відповідей, маршрутизація успішних, повторюваних та невалідних токенів.

## Порівняльний аналіз алгоритмів обмеження темпу

Вибір алгоритму Rate Limiter визначає поведінку системи під час сплесків трафіку:

| Алгоритм | Принцип роботи | Реакція на сплеск | Пам'ять на інстанс | Сфера застосування |
| :--- | :--- | :--- | :--- | :--- |
| **Token Bucket** | Поповнення токенів зі швидкістю `R`, списання при відправці | Дозволяє сплески до розміру `Capacity` | `O(1)` (лічильник + мітка часу) | **Вихідні шлюзи APNs/FCM** |
| **Leaky Bucket** | Черга постійної ємності з фіксованою швидкістю витікання | Згладжує сплески до строго рівної швидкості | `O(Queue Size)` | **SMTP та SMS-шлюзи** |
| **Sliding Window Log** | Збереження міток часу кожного запиту в ZSet | Точний облік без граничних стрибків | `O(Requests per Window)` | **API захист від спаму** |
| **Fixed Window** | Лічильник скидається на початку кожної секунди | Допускає подвійний сплеск на межі вікон | `O(1)` | **Простий захист бекенду** |

Для розсилки push-сповіщень оптимальним є **Token Bucket**, оскільки зовнішні шлюзи Apple та Google допускають короткочасні вибухові сплески (bursts) за умови дотримання середнього секундного ліміту.

## Архітектура пулу воркерів та неблокувального введення-виведення

Для досягнення максимальної продуктивності конвеєр диспетчера організовано як модель каналів (Actor/Channel Architecture):
- **Потік-демультиплексор (Reader Thread):** відповідає виключно за вичитування батчів завдань із брокера Kafka та розкидання їх у внутрішні неблокувальні черги (Lock-free MPMC Queues) окремих воркерів за ключем шардування.
- **Пул мережевих воркерів (Worker Pool):** кожен воркер обслуговує власний набір відкритих сокетів через системний виклик `epoll` у Linux або `kqueue` у BSD/macOS. Воркери реєструють дескриптори сокетів з прапорцями `EPOLLIN | EPOLLOUT | EPOLLET` (Edge-Triggered Mode), що забезпечує мінімальну кількість перемикань контексту ядра.
- **Потік скидання зворотного зв'язку (Feedback Drainer):** окремий фоновий потік із низьким пріоритетом, який вичитує буфер `expired_tokens_feedback_`, групує токени у великі пакети по 10 000 елементів і виконує пакетний `UPDATE` у базі даних сесій.

## Порівняння форматів серіалізації всередині конвеєра

Під час передачі батча між стадіями конвеєра формат серіалізації визначає навантаження на процесор:
- **JSON (Текстовий):** висока читабельність, але дорогий парсинг (до 30% процесорного часу воркера витрачається на парсинг рядків через `nlohmann::json` чи `JSON.parse`).
- **Protocol Buffers (Двійковий):** компактний розмір, сувора типізація, швидка серіалізація через кодогенерацію (у 4–6 разів швидше за JSON).
- **FlatBuffers (Zero-Copy):** доступ до полів повідомлення безпосередньо в бінарному буфері без проміжного розпакування в купі, що забезпечує нульові накладні витрати пам'яті.

## Реалізація диспетчера розсилки

Нижче наведено робочу архітектурну реалізацію ядра диспетчера. Вона демонструє розбиття на батчі, потокобезпечний Token Bucket, симуляцію мультиплексованого відправлення через адаптер провайдера та розділення результатів на успішні відправки, інвалідацію токенів і карантин у DLQ.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <chrono>
#include <thread>
#include <mutex>
#include <queue>
#include <optional>
#include <span>
#include <algorithm>

// Статус доставки окремого пристрою від зовнішнього шлюзу
enum class DeliveryStatus {
    Success,
    TokenExpired,    // HTTP 410 Gone / NotRegistered -> у Feedback Service
    RateLimited,     // HTTP 429 Too Many Requests -> повторити з backoff
    InvalidPayload,  // HTTP 400 BadPayload -> у Dead Letter Queue
    NetworkError     // Тимчасовий збій з'єднання
};

struct DeviceNotification {
    std::string device_token;
    std::string title;
    std::string body;
    std::string payload_json;
};

struct DeliveryResult {
    std::string device_token;
    DeliveryStatus status;
    std::string error_message;
};

// Потокобезпечний обмежувач темпу (Token Bucket)
class TokenBucketRateLimiter {
public:
    TokenBucketRateLimiter(double rate_per_second, double capacity)
        : rate_(rate_per_second), capacity_(capacity), tokens_(capacity),
          last_refill_(std::chrono::steady_clock::now()) {}

    bool try_acquire(double tokens = 1.0) {
        std::lock_guard<std::mutex> lock(mutex_);
        refill();
        if (tokens_ >= tokens) {
            tokens_ -= tokens;
            return true;
        }
        return false;
    }

    void acquire(double tokens = 1.0) {
        while (!try_acquire(tokens)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

private:
    void refill() {
        auto now = std::chrono::steady_clock::now();
        double elapsed = std::chrono::duration<double>(now - last_refill_).count();
        tokens_ = std::min(capacity_, tokens_ + elapsed * rate_);
        last_refill_ = now;
    }

    const double rate_;
    const double capacity_;
    double tokens_;
    std::chrono::steady_clock::time_point last_refill_;
    std::mutex mutex_;
};

// Абстрактний транспортний адаптер (APNs HTTP/2 або FCM v1)
class IPushProviderAdapter {
public:
    virtual ~IPushProviderAdapter() = default;
    virtual std::vector<DeliveryResult> send_batch(std::span<const DeviceNotification> batch) = 0;
};

// Симулятор мережевого адаптера APNs / FCM з обробкою статус-кодів
class MockPushProviderAdapter : public IPushProviderAdapter {
public:
    std::vector<DeliveryResult> send_batch(std::span<const DeviceNotification> batch) override {
        std::vector<DeliveryResult> results;
        results.reserve(batch.size());

        for (const auto& item : batch) {
            // Симуляція різних статусів провайдера на основі патерну токена
            if (item.device_token.rfind("invalid_", 0) == 0) {
                results.push_back({item.device_token, DeliveryStatus::TokenExpired, "410 Unregistered token"});
            } else if (item.device_token.rfind("bad_", 0) == 0) {
                results.push_back({item.device_token, DeliveryStatus::InvalidPayload, "400 Malformed JSON"});
            } else {
                results.push_back({item.device_token, DeliveryStatus::Success, ""});
            }
        }
        return results;
    }
};

// Ядро конвеєра диспетчера розсилки
class NotificationDispatcher {
public:
    NotificationDispatcher(std::shared_ptr<IPushProviderAdapter> adapter,
                           double max_rps, size_t batch_size)
        : adapter_(std::move(adapter)),
          rate_limiter_(max_rps, max_rps * 2.0),
          batch_size_(batch_size) {}

    void dispatch_fanout(const std::vector<std::string>& target_tokens,
                         std::string_view title, std::string_view body) {
        if (target_tokens.empty()) return;

        // 1. Формування повного списку нотифікацій
        std::vector<DeviceNotification> notifications;
        notifications.reserve(target_tokens.size());
        for (const auto& token : target_tokens) {
            notifications.push_back({token, std::string(title), std::string(body), "{}"});
        }

        // 2. Розбиття на батчі (Chunking) та відправка через rate limiter
        size_t total = notifications.size();
        for (size_t offset = 0; offset < total; offset += batch_size_) {
            size_t current_chunk = std::min(batch_size_, total - offset);
            std::span<const DeviceNotification> chunk(&notifications[offset], current_chunk);

            // Очікування доступного токена пропускної здатності
            rate_limiter_.acquire(static_cast<double>(current_chunk));

            // Відправка батча в провайдер
            auto results = adapter_->send_batch(chunk);

            // 3. Маршрутизація результатів за категоріями
            process_results(results);
        }
    }

    std::vector<std::string> drain_expired_tokens() {
        std::lock_guard<std::mutex> lock(feedback_mutex_);
        std::vector<std::string> out = std::move(expired_tokens_feedback_);
        expired_tokens_feedback_.clear();
        return out;
    }

    std::vector<DeviceNotification> drain_dead_letter_queue() {
        std::lock_guard<std::mutex> lock(dlq_mutex_);
        std::vector<DeviceNotification> out = std::move(dead_letter_queue_);
        dead_letter_queue_.clear();
        return out;
    }

private:
    void process_results(const std::vector<DeliveryResult>& results) {
        for (const auto& res : results) {
            switch (res.status) {
                case DeliveryStatus::Success:
                    // Успішно доставлено
                    break;
                case DeliveryStatus::TokenExpired: {
                    std::lock_guard<std::mutex> lock(feedback_mutex_);
                    expired_tokens_feedback_.push_back(res.device_token);
                    break;
                }
                case DeliveryStatus::InvalidPayload:
                case DeliveryStatus::RateLimited:
                case DeliveryStatus::NetworkError: {
                    std::lock_guard<std::mutex> lock(dlq_mutex_);
                    dead_letter_queue_.push_back({res.device_token, "Alert", "Error occurred", "{}"});
                    break;
                }
            }
        }
    }

    std::shared_ptr<IPushProviderAdapter> adapter_;
    TokenBucketRateLimiter rate_limiter_;
    const size_t batch_size_;

    std::vector<std::string> expired_tokens_feedback_;
    std::mutex feedback_mutex_;

    std::vector<DeviceNotification> dead_letter_queue_;
    std::mutex dlq_mutex_;
};

int main() {
    auto adapter = std::make_shared<MockPushProviderAdapter>();
    // Ліміт: 1000 повідомлень/с, розмір батча: 500
    NotificationDispatcher dispatcher(adapter, 1000.0, 500);

    std::vector<std::string> tokens = {
        "valid_token_001",
        "invalid_token_002", // Повинен потрапити у Feedback Service
        "valid_token_003",
        "bad_token_004"      // Повинен потрапити у DLQ
    };

    dispatcher.dispatch_fanout(tokens, "Термінова новина", "Сервіс оновлено успішно.");

    auto expired = dispatcher.drain_expired_tokens();
    auto dlq = dispatcher.drain_dead_letter_queue();

    std::cout << "Очищено застарілих токенів: " << expired.size() << "\n";
    std::cout << "Направлено у Dead Letter Queue: " << dlq.size() << "\n";

    return 0;
}
```
```ts
import { EventEmitter } from "node:events";

export enum DeliveryStatus {
  Success = "SUCCESS",
  TokenExpired = "TOKEN_EXPIRED",     // 410 Gone / NotRegistered
  RateLimited = "RATE_LIMITED",       // 429 Too Many Requests
  InvalidPayload = "INVALID_PAYLOAD", // 400 Bad JSON
  NetworkError = "NETWORK_ERROR",
}

export interface DeviceNotification {
  deviceToken: string;
  title: string;
  body: string;
  payloadJson?: string;
}

export interface DeliveryResult {
  deviceToken: string;
  status: DeliveryStatus;
  errorMessage?: string;
}

export interface IPushProviderAdapter {
  sendBatch(batch: DeviceNotification[]): Promise<DeliveryResult[]>;
}

// Асинхронний обмежувач темпу (Token Bucket)
export class AsyncTokenBucket {
  private tokens: number;
  private lastRefill: number;

  constructor(
    private readonly ratePerSecond: number,
    private readonly capacity: number
  ) {
    this.tokens = capacity;
    this.lastRefill = Date.now();
  }

  async acquire(count = 1): Promise<void> {
    while (true) {
      this.refill();
      if (this.tokens >= count) {
        this.tokens -= count;
        return;
      }
      const waitMs = Math.ceil(((count - this.tokens) / this.ratePerSecond) * 1000);
      await new Promise((resolve) => setTimeout(resolve, Math.max(waitMs, 10)));
    }
  }

  private refill(): void {
    const now = Date.now();
    const elapsedSeconds = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsedSeconds * this.ratePerSecond);
    this.lastRefill = now;
  }
}

// Мок-адаптер з імітацією відповідей APNs / FCM
export class MockPushAdapter implements IPushProviderAdapter {
  async sendBatch(batch: DeviceNotification[]): Promise<DeliveryResult[]> {
    return batch.map((item) => {
      if (item.deviceToken.startsWith("invalid_")) {
        return {
          deviceToken: item.deviceToken,
          status: DeliveryStatus.TokenExpired,
          errorMessage: "410 Unregistered device token",
        };
      }
      if (item.deviceToken.startsWith("bad_")) {
        return {
          deviceToken: item.deviceToken,
          status: DeliveryStatus.InvalidPayload,
          errorMessage: "400 Malformed JSON structure",
        };
      }
      return {
        deviceToken: item.deviceToken,
        status: DeliveryStatus.Success,
      };
    });
  }
}

export class NotificationDispatcher extends EventEmitter {
  private readonly rateLimiter: AsyncTokenBucket;
  private readonly expiredTokensFeedback: string[] = [];
  private readonly deadLetterQueue: DeviceNotification[] = [];

  constructor(
    private readonly adapter: IPushProviderAdapter,
    maxRps: number,
    private readonly batchSize = 500
  ) {
    super();
    this.rateLimiter = new AsyncTokenBucket(maxRps, maxRps * 2);
  }

  async dispatchFanout(tokens: string[], title: string, body: string): Promise<void> {
    if (tokens.length === 0) return;

    // 1. Розбиття на батчі (Chunking)
    for (let i = 0; i < tokens.length; i += this.batchSize) {
      const chunkTokens = tokens.slice(i, i + this.batchSize);
      const batch: DeviceNotification[] = chunkTokens.map((token) => ({
        deviceToken: token,
        title,
        body,
      }));

      // 2. Контроль темпу
      await this.rateLimiter.acquire(batch.length);

      // 3. Відправка та обробка статусів
      const results = await this.adapter.sendBatch(batch);
      this.handleResults(results, batch);
    }
  }

  private handleResults(results: DeliveryResult[], originalBatch: DeviceNotification[]): void {
    const batchMap = new Map(originalBatch.map((item) => [item.deviceToken, item]));

    for (const res of results) {
      switch (res.status) {
        case DeliveryStatus.Success:
          break;
        case DeliveryStatus.TokenExpired:
          this.expiredTokensFeedback.push(res.deviceToken);
          this.emit("tokenExpired", res.deviceToken);
          break;
        case DeliveryStatus.InvalidPayload:
        case DeliveryStatus.RateLimited:
        case DeliveryStatus.NetworkError:
          const original = batchMap.get(res.deviceToken);
          if (original) {
            this.deadLetterQueue.push(original);
            this.emit("dlqItem", original, res.errorMessage);
          }
          break;
      }
    }
  }

  drainExpiredTokens(): string[] {
    return this.expiredTokensFeedback.splice(0, this.expiredTokensFeedback.length);
  }

  drainDeadLetterQueue(): DeviceNotification[] {
    return this.deadLetterQueue.splice(0, this.deadLetterQueue.length);
  }
}
```
:::

## Оптимізація виділення пам'яті (Zero-Allocation у гарячому шляху)

При обробці мільйонів сповіщень щосекунди стандартні виклики `new` та `malloc` створюють суттєву фрагментацію купи та накладні витрати на синхронізацію алокатора ядра.

Для досягнення максимальної пропускної здатності в C++ застосовують такі техніки:
- **Поліморфні ресурси пам'яті (PMR):** використання `std::pmr::monotonic_buffer_resource` для виділення масивів сповіщень у межах одного батча з наступним миттєвим скиданням покажчика вершини арени без викликів `free()`.
- **Безкопіювальні зрізи (Zero-Copy Views):** використання `std::span` та `std::string_view` для передачі фрагментів JSON-шаблонів та масивів токенів без дублювання рядків у пам'яті.
- **Попереднє резервування (Pre-allocation):** вектори результатів та списки нотифікацій викликають `.reserve(batch_size)` до початку циклу, що усуває реалокації та копіювання буферів.

## Анатомія протокольних взаємодій із провайдерами

Щоб зрозуміти, чому диспетчер організовано саме так, розглянемо специфіку роботи мережевих шлюзів.

### 1. Мультиплексування Apple APNs поверх HTTP/2
Протокол Apple Push Notification service вимагає встановлення постійного TLS-з'єднання з автентифікацією через JWT або mTLS-сертифікат. Кожне сповіщення надсилається окремим HTTP/2 запитом `POST /3/device/{device_token}` всередині власного потоку (Stream ID).

Ключові параметри протоколу:
- Відкриття нового TCP/TLS-з'єднання на кожне повідомлення суворо заборонено: вартість TLS-рукостискання становить від 50 до 120 мілісекунд і призводить до блокування IP-адреси за підозрілу активність.
- Одне з'єднання підтримує до 1000–1500 одночасних мультиплексованих потоків. Диспетчер підтримує пул довгоживучих з'єднань, розподіляючи батчі повідомлень між активними сесіями.
- Відповідь APNs повертається асинхронно: статус `200 OK` підтверджує прийняття, а помилки повертаються в тілі JSON (наприклад, `{"reason":"BadDeviceToken"}` зі статусом `400` або `{"reason":"Unregistered"}` зі статусом `410`).

### 2. Пакети Google FCM (HTTP v1 Batch API)
Шлюз Firebase Cloud Messaging дозволяє відправляти до 500 повідомлень в одному складеному HTTP-запиті (multipart/mixed MIME payload).

Особливість обробки FCM полягає в тому, що HTTP-статус самого конверта майже завжди дорівнює `200 OK`, навіть якщо всі 500 токенів усередині пакета завершилися помилкою. Диспетчер зобов'язаний розібрати внутрішній масив відповідей і класифікувати кожен токен індивідуально.

## Інженерний розбір пасток та крайових випадків

Під час експлуатації диспетчера розсилки в умовах навантаження у сотні тисяч подій на хвилину виникають типові архітектурні пастки.

### 1. Ефект часткового збою батча (Partial Batch Failure)
У батч-протоколах поширена помилка — трактувати невдалу HTTP-відповідь шлюзу як відмову всього батча. Якщо провайдер повернув статус `200 OK`, але 3 токени з 500 виявилися невалідними, наївна перевідправка всього батча призведе до дублювання 497 сповіщень кінцевим користувачам.

**Рішення:** парсити індивідуальні індекси відповідей (Sub-responses). Тільки елементи зі статусами `429` (Rate Limited) або `503` (Service Unavailable) додаються в чергу на повтор (Retry Queue) із експоненційним джиттером; невалідні токени (`400/410`) негайно маршрутизуються у Feedback-канал.

### 2. Витік пам'яті у каналі зворотного зв'язку (Feedback Buffer Bloat)
Якщо розсилка генерує десятки тисяч невалідних токенів щохвилини, а сервіс очищення бази даних працює повільно або тимчасово недоступний, черга `expired_tokens_feedback_` у пам'яті диспетчера розростається і викликає аварійне завершення процесу через вичерпання оперативної пам'яті (Out-Of-Memory, OOM).

**Рішення:** використання строго обмеженого буфера (Bounded Buffer) із виштовхуванням старих записів у持久ну чергу (Kafka або RabbitMQ) або скиданням на диск (Spill-to-Disk) при досягненні ліміту розміру черги.

### 3. Каскадне блокування пулу потоків через повільні мережеві з'єднання
Якщо зовнішній шлюз APNs або FCM починає збільшувати затримку відповіді (Latency Spike від 50 мс до 2000 мс), синхронні воркери зависають в очікуванні сокетів. Вхідна черга повідомлень стрімко переповнюється.

**Рішення:** асинхронне неблокувальне введення-виведення на базі `epoll` / `io_uring` (у C++) або `Event Loop` (у TypeScript/Go), суворі таймаути на рівні з'єднань (Connection Timeout = 2 с, Read Timeout = 5 с) та автоматичний запобіжник (Circuit Breaker), який відсікає надсилання нових батчів при деградації шлюзу.

### 4. Гонитва станів під час поповнення Token Bucket
При паралельній роботі десятків воркерів наївна перевірка та списання токенів без атомарних операцій призводить до гонитви (Race Condition), коли ліміт провайдера перевищується у кілька разів за частки секунди.

**Рішення:** сувора синхронізація через `std::mutex` або використання неблокувальних атомарних змінних `std::atomic<double>` із циклом `compare_exchange_weak`.

### 5. Семантика підтвердження зміщення (Kafka Offset Commit)
Якщо воркер фіксує офсет повідомлення у топіку брокера до того, як батч успішно відправлено провайдеру (Auto-commit), аварійне падіння воркера призведе до втрати сповіщень. Якщо ж офсет фіксується після успішної доставки, падіння воркера під час запису офсету призведе до повторного зчитування і дублювання всієї розсилки.

**Рішення:** застосування ідемпотентних ідентифікаторів повідомлень на стороні мобільних клієнтів (Client-side Deduplication via Notification ID) у поєднанні з ручним синхронним фіксуванням офсетів (Manual Commit) після успішного підтвердження доставки батча.

### 6. Взаємодія з транзакційними SMTP-пулами
На відміну від HTTP/2 шлюзів мобільних push-повідомлень, протокол SMTP є текстовим та чутливим до затримок TCP-рукостискань і командних діалогів (`HELO`, `MAIL FROM`, `RCPT TO`, `DATA`).

Для розсилки електронної пошти диспетчер повинен реалізовувати:
- **Пайплайнінг команд (ESMTP PIPELINING):** надсилання всього блоку команд без очікування проміжної відповіді сервера на кожний рядок.
- **Пул підігрітих з'єднань (Keep-Alive Connection Pool):** утримання відкритих TCP-сесій до поштових релеїв (Postfix, Amazon SES, SendGrid), що зменшує накладні витрати на встановлення TLS у 10–15 разів.
- **Контроль репутації IP та Warm-up:** плавне нарощування інтенсивності розсилки з нових IP-адрес (наприклад, не більше 1 000 листів у перший день з подвоєнням щодня), щоб уникнути потрапляння до спам-фільтрів (Spamhaus, Barracuda).

## Розбір виробничого інциденту: каскадний шторм оновлення токенів

Розглянемо реальний інцидент із практики експлуатації мобільного додатку з 20 мільйонами користувачів.

### Перебіг збою:
1. Під час релізу нової версії мобільного додатку о 14:00 було оновлено SDK Firebase Messaging. Через дефект у логіці оновлення додаток почав генерувати новий push-токен при кожному холодному запуску.
2. Протягом двох годин активні користувачі згенерували понад 8 мільйонів нових токенів, які записалися в базу даних як додаткові пристрої без деактивації старих.
3. О 18:00 під час відправки маркетингового пуша диспетчер сформував розсилку на 28 мільйонів записів замість очікуваних 20 мільйонів.
4. Шлюз FCM почав масово повертати помилки `410 Gone` (Unregistered) на 8 мільйонів застарілих токенів.
5. Сервіс зворотного зв'язку (Feedback Consumer) не витримав лавиноподібного навантаження у 50 000 операцій запису в секунду, переповнив внутрішній буфер пам'яті й аварійно завершився з помилкою OOM.
6. Воркери розсилки, втративши можливість скидати невалідні токени, почали блокуватися на черзі зворотного зв'язку, що призвело до повної зупинки конвеєра розсилки.

### Заходи з ліквідації та архітектурні виправлення:
- Було впроваджено асинхронний буфер зворотного зв'язку на базі топіка Kafka з лімітом дискового простору, що повністю усунуло залежність воркерів від доступності сервісу очищення бази даних.
- Базу даних переведено на модель «один активний токен на комбінацію `(user_id, device_fingerprint)`», де запис нового токена автоматично позначає старий як неактивний у тій самій транзакції.
- Впроваджено автоматичний Circuit Breaker на рівні Feedback Service: якщо частка помилок 410 у розсилці перевищує 25%, конвеєр тимчасово знижує темп відправки вдвічі для захисту сховища сесій.
- Налаштовано пільговий період (Grace Period) тривалістю 7 діб: токени не видаляються фізично з диска, а переводяться у статус «тимчасово неактивний», що дозволяє уникнути втрати сесій при випадкових помилках шлюзів.
- Додано автоматичний лічильник невдалих спроб доставки: після 3 послідовних помилок із кодом 410 токен позначається як остаточно мертвий і виключається з вибірки генератора батчів.

## Стратегія тестування диспетчера

Для перевірки стійкості конвеєра розсилки застосовують три рівні тестування:
1. **Модульні тести (Unit Tests):** верифікація математики Token Bucket, перевірка коректності обчислення доступних токенів при мілісекундних зміщеннях часу, тестування розбиття масивів різної довжини на батчі (крайові випадки: порожній масив, розмір масиву менший за батч, розмір масиву кратний батчу).
2. **Інтеграційні тести з Mock HTTP/2 сервером:** запуск локального тестового сервера, який імітує поведінку APNs та FCM. Сервер генерує випадкові помилки 429, 410, 503 та обриви з'єднання, перевіряючи коректність наповнення черг зворотного зв'язку (Feedback Buffer) та карантину (DLQ).
3. **Навантажувальні стрес-тести (Chaos & Load Testing):** подача штучного потоку завдань на рівні 50 000 RPS із раптовим введенням штучної мережевої затримки (Network Latency Spike) у 2000 мс. Тест перевіряє, чи не призводить затримка до витоку пам'яті (OOM) і чи коректно спрацьовує механізм Backpressure у Kafka-консюмерах.

## Спостережність та моніторинг конвеєра розсилки

Диспетчер розсилки повинен експортувати стандартний набір метрик у форматі Prometheus:
- `fanout_dispatched_total{provider, status}` — лічильник відправлених повідомлень за статусами (`success`, `expired`, `rate_limited`, `failed`);
- `fanout_batch_size_bucket` — гістограма розподілу розмірів батчів;
- `fanout_provider_latency_seconds_bucket{provider}` — гістограма часу відгуку зовнішніх мережевих шлюзів;
- `fanout_rate_limiter_wait_seconds_total` — сумарний час, проведений воркерами в очікуванні вільних токенів пропускної здатності;
- `fanout_dlq_messages_total` — кількість повідомлень, скинутих у Dead Letter Queue.

Комплексний моніторинг цих показників дозволяє вчасно виявити деградацію зовнішніх шлюзів, відкоригувати розміри батчів та запобігти виникненню заторів у чергах завдань.
