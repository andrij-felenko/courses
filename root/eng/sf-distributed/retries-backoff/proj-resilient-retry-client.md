# ⚙️ Стійкий клієнт повторних спроб: експоненційний відступ, джитер і токенний бюджет

У розподілених системах наївний цикл `for (int i = 0; i < 3; ++i)` для повторення мережевих викликів є джерелом масштабних системних аварій. Коли клієнтська бібліотека повторює запити без урахування характеру помилки, вона марнує ресурси на повторення завідомо безнадійних операцій (наприклад, помилок автентифікації 401 Unauthorized або синтаксичних помилок валідації 400 Bad Request). Якщо повтори відбуваються без внесення випадкового шуму (джитера), тисячі паралельних екземплярів сервісу утворюють резонансні хвилі синхронізованого навантаження. Нарешті, за відсутності глобального бюджету повторів усередині процесу, клієнти здатні лавиноподібно помножити потік запитів саме в той момент, коли бекенд намагається відновитися після збою, перетворюючи короткочасну деградацію на тривалий колапс інфраструктури.

Стійкий клієнт повторних спроб (Resilient Retry Client) вирішує цю задачу комплексно. Він ізолює прикладний код від складнощів мережевого транспорту, об'єднуючи чотири незалежні інженерні контури:
1. **Класифікатор помилок (Error Classifier):** семантичний розбір кодів відповідей HTTP та gRPC з розподілом на тимчасові (Transient), які має сенс повторювати, та постійні (Permanent), які вимагають негайної передачі помилки нагору.
2. **Генератор затримки Full Jitter:** математично оптимізоване розсіювання запитів у часі, що ліквідує синхронізацію клієнтів і забезпечує мінімальну середню затримку.
3. **Токенний бюджет повторів (Token Bucket Retry Budget):** адаптивне динамічне обмеження частки повторного трафіку відносно потоку успішних операцій на рівні екземпляра програми.
4. **Контролер контекстних дедлайнів (Deadline & Monotonic Time Keeper):** наскрізна перевірка часового бюджету операції, що запобігає виконанню безглуздих мережевих спроб, коли клієнт або вищий сервіс уже не чекає на відповідь.

```
Вхідний виклик ──> [Дедлайн вичерпано?] ──(Так)──> Відмова (504 Timeout)
                          │ (Ні)
                          ▼
                 [Виконання HTTP/RPC]
                          │
            ┌─────────────┴─────────────┐
      (200 OK)                     (Помилка)
            │                           │
            ▼                           ▼
[Поповнити бюджет: +0.1]    [Класифікатор помилок]
            │               ┌───────────┴───────────┐
            ▼         (Постійна: 4xx)       (Тимчасова: 503/429/Drop)
     Успішний фінал         │                       │
                            ▼                       ▼
                     Негайна відмова        [Є токени в бюджеті?]
                                            ┌───────┴───────┐
                                          (Так)            (Ні: Бюджет вичерпано)
                                            │               │
                                            ▼               ▼
                                   [Full Jitter відступ]  Fast-Fail (Вичерпано)
                                            │
                                            ▼
                                   [Списати 1.0 токен] ──> Повтор запиту
```

## Архітектурний дизайн та інваріанти компонентів

Проектування стійкого клієнта базується на суворому дотриманні наступних фундаментальних інваріантів:

### 1. Монотонний вимір часу без дрейфу годинника
Для всіх часових розрахунків — обчислення тривалості відступу, перевірки дедлайнів, вимірювання часу обходу мережі (RTT) — використовується виключно монотонний системний таймер (`std::chrono::steady_clock` у C++ або `CLOCK_MONOTONIC` у POSIX C). 

Астрономічний годинник реального часу (`CLOCK_REALTIME` або `std::chrono::system_clock`) підпорядковується демонам синхронізації часу NTP/PTP, які можуть у будь-який момент плавно або стрибкоподібно скоригувати час назад (наприклад, під час компенсації високосної секунди або виправлення часового зсуву сервера). Якщо розрахунок дедлайну або паузи відступу спирається на годинник реального часу, стрибок часу назад на дві секунди призведе до того, що клієнт заморозить виконання робочого потоку на дві додаткові секунди. Стрибок часу вперед, навпаки, змусить клієнт помилково вважати, що дедлайн миттєво закінчився, і передчасно обірвати повністю здорову операцію. Монотонний таймер гарантує строгу монотонність плину часу без зворотних стрибків.

### 2. Потокобезпечний токенний кошик без блокування гарячого шляху
Токенний кошик бюджету повторів є спільним ресурсом для сотень паралельних потоків обробки запитів. При успішному завершенні виклику (код 200 OK) потік поповнює баланс на фіксовану дробову частку (наприклад, `+0.1` токена). При необхідності виконання повторної спроби потік намагається списати повний токен (`-1.0`).

Якщо баланс кошика менший за одиницю, це означає, що частка помилок у системі перевищила допустимий 10-відсотковий поріг, і клієнт переходить у режим миттєвої відмови (Fast-Fail). Замість виконання чергової спроби виклик негайно завершується помилкою, захищаючи віддалений сервіс від лавинного перевантаження. Для мінімізації накладних витрат стан кошика синхронізується за допомогою швидких м'ютексів або атомарних операцій, що не створюють простоїв на гарячому шляху корисного трафіку.

### 3. Наскрізна передача ключів ідемпотентності
Мережевий тайм-аут є принципово невизначеним станом (Indeterminate State): клієнт не знає, чи запит загубився дорогою до сервера, чи сервер упав під час обробки, чи сервер успішно виконав транзакцію, але пакет із відповіддю було скинуто комутатором на зворотному шляху.

Повторення мутуючого запиту (створення платежу, списання коштів, зміна балансу) без механізму ідемпотентності неминуче призведе до дублювання операцій у базі даних. Стійкий клієнт генерує унікальний криптографічний ідентифікатор транзакції `Idempotency-Key` (UUIDv4 або SHA-256 хеш від параметрів запиту) на рівні бізнес-логіки перед першою спробою. Цей самий ключ передається в HTTP-заголовках або gRPC-метаданих усіх наступних фізичних повторів цієї логічної операції, дозволяючи серверу розпізнати дублікати та повернути збережений результат без повторного виконання бізнес-дії.

## Семантика кодів помилок: HTTP та gRPC

Ефективність повторних спроб цілком залежить від точності семантичного розбору відповідей. Неправильна класифікація або вбиває бекенд зайвими повторами, або передчасно обриває виклики, які могли б завершитися успішно після короткої паузи.

### Порівняльна матриця класифікації статусів

| Протокол HTTP | Статус gRPC | Семантична категорія | Поведінка клієнта | Обґрунтування механізму |
| :--- | :--- | :--- | :--- | :--- |
| **200 OK / 201 Created** | `OK (0)` | Успіх (Success) | Поповнення бюджету (`+0.1`) | Транзакція завершена, запис у кошик токенів |
| **400 Bad Request** | `INVALID_ARGUMENT (3)` | Постійна (Permanent) | Негайна відмова (Fail-Fast) | Синтаксична або валідаційна помилка в тілі |
| **401 / 403 Forbidden** | `UNAUTHENTICATED (16)` | Постійна (Permanent) | Негайна відмова | Відсутність або недійсність токена доступу |
| **404 Not Found** | `NOT_FOUND (5)` | Постійна (Permanent) | Негайна відмова | Ресурс не існує в системі |
| **409 Conflict** | `ALREADY_EXISTS (6)` | Постійна / Спеціальна | Залежить від бізнес-логіки | Конфлікт версій (Optimistic Lock); потрібен reload |
| **422 Unprocessable** | `FAILED_PRECONDITION (9)` | Постійна (Permanent) | Негайна відмова | Бізнес-інваріант порушено (наприклад, нема коштів) |
| **429 Too Many Req** | `RESOURCE_EXHAUSTED (8)` | Тимчасова (Transient) | Повтор з `Retry-After` | Сервер обмежив швидкість; чекати вказівки сервера |
| **502 Bad Gateway** | `UNAVAILABLE (14)` | Тимчасова (Transient) | Повтор з Full Jitter | Проміжний проксі не зміг з'єднатися з інстансом |
| **503 Service Unavail** | `UNAVAILABLE (14)` | Тимчасова (Transient) | Повтор з Full Jitter | Вузол перезавантажується або черга переповнена |
| **504 Gateway Timeout** | `DEADLINE_EXCEEDED (4)` | Тимчасова (Transient) | Повтор (тільки ідемпотентні) | Шлюз не дочекався відповіді від бекенда |
| **TCP RST / ECONNRESET**| Помилка сокета | Тимчасова (Transient) | Повтор з новим з'єднанням | Сервер скинув сокет (падіння процесу або failover) |

## Повна реалізація стійкого клієнта на C++20 та C

Нижче наведено самодостатній production-код клієнта, що демонструє роботу класифікатора, генератора Full Jitter, токенного бюджету повторів та перевірку контекстних дедлайнів на C++20 та C.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <random>
#include <atomic>
#include <mutex>
#include <optional>
#include <expected>
#include <functional>
#include <format>
#include <cmath>

namespace net {

using namespace std::chrono_literals;

// Структура відповіді транспортного рівня
struct Response {
    int status_code{200};
    std::string body;
    std::chrono::milliseconds latency{0};
};

// Семантична класифікація результату виклику
enum class ErrorKind {
    Transient,  // Тимчасовий збій (503, 429, 504, скидання TCP, timeout сокета)
    Permanent   // Фатальна помилка (400, 401, 403, 404, 422)
};

struct RequestError {
    ErrorKind kind;
    int status_code;
    std::string message;
};

// Повна конфігурація політики стійкості
struct RetryPolicy {
    int max_attempts{4};                         // Максимум 4 спроби (1 первинна + 3 повтори)
    std::chrono::milliseconds base_backoff{100ms}; // Початковий інтервал відступу t0
    std::chrono::milliseconds max_backoff{3000ms}; // Верхня межа зрізання інтервалу t_max
    double backoff_multiplier{2.0};              // Експоненційний множник b
    double budget_deposit_per_success{0.10};     // Поповнення бюджету (+0.1 за успіх -> 10% квота)
    double budget_withdraw_per_retry{1.00};      // Списання за кожну повторну спробу
    double max_budget_tokens{100.0};             // Максимальна ємність токенного кошика
};

// Потокобезпечний токенний кошик бюджету повторних спроб
class TokenBucketRetryBudget {
public:
    explicit TokenBucketRetryBudget(double max_tokens = 100.0, double initial_tokens = 20.0)
        : max_tokens_(max_tokens), tokens_(initial_tokens) {}

    // Поповнення кошика при отриманні успішної відповіді 2xx
    void record_success(double deposit = 0.10) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        tokens_ = std::min(max_tokens_, tokens_ + deposit);
    }

    // Спроба списання токена перед виконанням повтору (Fast-Fail перевірка)
    bool try_withdraw_retry(double cost = 1.00) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        if (tokens_ >= cost) {
            tokens_ -= cost;
            return true;
        }
        return false; // Токени закінчилися: лавинне блокування повторів
    }

    double current_balance() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return tokens_;
    }

private:
    mutable std::mutex mutex_;
    double max_tokens_;
    double tokens_;
};

// Калькулятор затримки за алгоритмом Full Jitter
class BackoffCalculator {
public:
    explicit BackoffCalculator(const RetryPolicy& policy)
        : policy_(policy), rng_(std::random_device{}()) {}

    std::chrono::milliseconds calculate(int retry_index) {
        // Детерміністична експоненційна стеля: v(i) = min(t_max, t0 * b^i)
        double factor = std::pow(policy_.backoff_multiplier, retry_index);
        double max_ms = policy_.base_backoff.count() * factor;
        double ceiling_ms = std::min(static_cast<double>(policy_.max_backoff.count()), max_ms);

        // Full Jitter: рівномірний випадковий вибір на інтервалі [0, ceiling_ms]
        std::uniform_real_distribution<double> dist(0.0, ceiling_ms);
        std::lock_guard<std::mutex> lock(rng_mutex_);
        return std::chrono::milliseconds(static_cast<long long>(dist(rng_)));
    }

private:
    RetryPolicy policy_;
    std::mutex rng_mutex_;
    std::mt19937 rng_;
};

// Класифікатор кодів помилок протоколу HTTP
class HttpErrorClassifier {
public:
    static ErrorKind classify(int status_code) noexcept {
        switch (status_code) {
            case 408: // Request Timeout (клієнтський сокет відвалився)
            case 429: // Too Many Requests (сервер сигналізує про обмеження швидкості)
            case 502: // Bad Gateway (проміжний проксі втратив зв'язок)
            case 503: // Service Unavailable (бекенд перевантажений або перезавантажується)
            case 504: // Gateway Timeout (вихідний шлюз не дочекався бекенда)
                return ErrorKind::Transient;
            default:
                if (status_code >= 400 && status_code < 500) {
                    // Клієнтські помилки (400, 401, 403, 404, 422) ніколи не лікуються повтором
                    return ErrorKind::Permanent;
                }
                if (status_code >= 500) {
                    // Інші серверні помилки (наприклад, 500 Internal Server Error) вважаємо тимчасовими
                    return ErrorKind::Transient;
                }
                return ErrorKind::Permanent;
        }
    }
};

// Контекст запиту з монотонним дедлайном та ключем ідемпотентності
struct RequestContext {
    std::string idempotency_key;
    std::chrono::steady_clock::time_point deadline;

    bool is_expired() const noexcept {
        return std::chrono::steady_clock::now() >= deadline;
    }

    std::chrono::milliseconds time_remaining() const noexcept {
        auto now = std::chrono::steady_clock::now();
        if (now >= deadline) return 0ms;
        return std::chrono::duration_cast<std::chrono::milliseconds>(deadline - now);
    }
};

// Головний стійкий клієнт
class ResilientClient {
public:
    explicit ResilientClient(RetryPolicy policy = RetryPolicy{})
        : policy_(policy),
          budget_(policy.max_budget_tokens, 15.0),
          backoff_(policy) {}

    using TransportFn = std::function<std::expected<Response, int>(const std::string& url, 
                                                                  const std::string& key)>;

    // Виконання стійкого виклику із захистом від штормів
    std::expected<Response, RequestError> execute(const std::string& url,
                                                  RequestContext ctx,
                                                  TransportFn transport) {
        for (int attempt = 0; attempt < policy_.max_attempts; ++attempt) {
            // Крок 1: Перевірка глобального дедлайну транзакції
            if (ctx.is_expired()) {
                return std::unexpected(RequestError{
                    ErrorKind::Permanent,
                    504,
                    "Глобальний дедлайн транзакції вичерпано до відправки запиту"
                });
            }

            // Крок 2: Якщо це повторна спроба (attempt > 0) — перевіряємо бюджет і робимо паузу
            if (attempt > 0) {
                // Перевірка наявності токенів у токенному кошику
                if (!budget_.try_withdraw_retry(policy_.budget_withdraw_per_retry)) {
                    return std::unexpected(RequestError{
                        ErrorKind::Transient,
                        429,
                        "Бюджет повторів вичерпано (Retry Budget Exhausted, Fast-Fail захист)"
                    });
                }

                // Розрахунок паузи за алгоритмом Full Jitter
                auto backoff_duration = backoff_.calculate(attempt - 1);

                // Перевірка: чи не перевищує обчислений відступ залишок дедлайну
                if (backoff_duration >= ctx.time_remaining()) {
                    return std::unexpected(RequestError{
                        ErrorKind::Permanent,
                        504,
                        "Залишок дедлайну менший за розраховану тривалість відступу"
                    });
                }

                // Очікування розрахованої затримки
                std::this_thread::sleep_for(backoff_duration);
            }

            // Крок 3: Виконання фізичного виклику через мережевий транспорт
            auto result = transport(url, ctx.idempotency_key);

            if (result.has_value()) {
                const auto& resp = result.value();
                if (resp.status_code >= 200 && resp.status_code < 300) {
                    // Успіх: поповнюємо бюджет повторів новими токенами
                    budget_.record_success(policy_.budget_deposit_per_success);
                    return resp;
                }

                // Аналіз коду помилки класифікатором
                auto kind = HttpErrorClassifier::classify(resp.status_code);
                if (kind == ErrorKind::Permanent) {
                    return std::unexpected(RequestError{
                        ErrorKind::Permanent,
                        resp.status_code,
                        std::format("Постійна помилка HTTP {}, повтори скасовано", resp.status_code)
                    });
                }

                // Тимчасова помилка бекенда (503, 429) — переходимо до наступної ітерації циклу
                std::cout << std::format("  [Спроба {}] Тимчасова помилка HTTP {} -> планування повтору\n",
                                         attempt + 1, resp.status_code);
            } else {
                // Мережевий збій транспорту (скидання з'єднання TCP RST, timeout)
                int net_err = result.error();
                std::cout << std::format("  [Спроба {}] Мережевий збій сокета errno={} -> планування повтору\n",
                                         attempt + 1, net_err);
            }
        }

        return std::unexpected(RequestError{
            ErrorKind::Transient,
            503,
            "Вичерпано максимальний ліміт спроб (Max Retries Exceeded)"
        });
    }

    double get_budget_balance() const noexcept {
        return budget_.current_balance();
    }

private:
    RetryPolicy policy_;
    TokenBucketRetryBudget budget_;
    BackoffCalculator backoff_;
};

} // namespace net

int main() {
    using namespace std::chrono_literals;

    net::ResilientClient client;
    net::RequestContext ctx{
        .idempotency_key = "req-uuid-9874-aefc",
        .deadline = std::chrono::steady_clock::now() + 5000ms
    };

    int call_counter = 0;

    // Емулятор віддаленого сервера з тимчасовим збоєм
    auto mock_transport = [&call_counter](const std::string& url, 
                                          const std::string& key) -> std::expected<net::Response, int> {
        ++call_counter;
        if (call_counter <= 2) {
            // Перші 2 виклики завершуються тимчасовим збоєм 503 Service Unavailable
            return net::Response{.status_code = 503, .body = "Service Overloaded"};
        }
        // Третій виклик завершується успішно
        return net::Response{.status_code = 200, .body = "{\"status\":\"order_created\"}"};
    };

    std::cout << "Запуск стійкого клієнта з експоненційним відступом та джитером:\n";
    auto outcome = client.execute("https://api.payments.internal/v1/charge", ctx, mock_transport);

    if (outcome.has_value()) {
        std::cout << "Успішна відповідь: " << outcome.value().body << "\n";
        std::cout << "Баланс бюджету повторів: " << client.get_budget_balance() << " токенів\n";
    } else {
        std::cout << "Запит провалено: " << outcome.error().message << "\n";
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <unistd.h>
#include <pthread.h>
#include <stdbool.h>

typedef enum {
    ERR_TRANSIENT,
    ERR_PERMANENT
} ErrorKind;

typedef struct {
    int status_code;
    char body[256];
} HttpResponse;

typedef struct {
    ErrorKind kind;
    int status_code;
    char message[256];
} RequestError;

typedef struct {
    int max_attempts;
    long base_backoff_ms;
    long max_backoff_ms;
    double multiplier;
    double deposit_per_success;
    double withdraw_per_retry;
    double max_tokens;
} RetryPolicy;

typedef struct {
    pthread_mutex_t lock;
    double tokens;
    double max_tokens;
} TokenBucket;

void token_bucket_init(TokenBucket* tb, double max_tokens, double initial) {
    pthread_mutex_init(&tb->lock, NULL);
    tb->max_tokens = max_tokens;
    tb->tokens = initial;
}

void token_bucket_record_success(TokenBucket* tb, double deposit) {
    pthread_mutex_lock(&tb->lock);
    tb->tokens += deposit;
    if (tb->tokens > tb->max_tokens) tb->tokens = tb->max_tokens;
    pthread_mutex_unlock(&tb->lock);
}

bool token_bucket_try_withdraw(TokenBucket* tb, double cost) {
    bool ok = false;
    pthread_mutex_lock(&tb->lock);
    if (tb->tokens >= cost) {
        tb->tokens -= cost;
        ok = true;
    }
    pthread_mutex_unlock(&tb->lock);
    return ok;
}

long calculate_full_jitter(const RetryPolicy* p, int attempt_index) {
    double factor = pow(p->multiplier, attempt_index);
    double max_ms = (double)p->base_backoff_ms * factor;
    if (max_ms > (double)p->max_backoff_ms) max_ms = (double)p->max_backoff_ms;
    
    double r = (double)rand() / (double)RAND_MAX;
    return (long)(r * max_ms);
}

ErrorKind classify_status(int status_code) {
    if (status_code == 408 || status_code == 429 || status_code == 502 || 
        status_code == 503 || status_code == 504) {
        return ERR_TRANSIENT;
    }
    if (status_code >= 400 && status_code < 500) {
        return ERR_PERMANENT;
    }
    if (status_code >= 500) {
        return ERR_TRANSIENT;
    }
    return ERR_PERMANENT;
}

// Монотонний годинник у мілісекундах без стрибків NTP
long get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

// Емуляція мережевого транспорту з тимчасовим збоєм
bool mock_transport(const char* url, const char* key, int* out_status, char* out_body) {
    static int attempt_count = 0;
    attempt_count++;
    if (attempt_count <= 2) {
        *out_status = 503;
        snprintf(out_body, 256, "Service Busy");
        return true;
    }
    *out_status = 200;
    snprintf(out_body, 256, "{\"status\":\"success\"}");
    return true;
}

int main(void) {
    srand((unsigned)time(NULL));
    
    RetryPolicy policy = {
        .max_attempts = 4,
        .base_backoff_ms = 100,
        .max_backoff_ms = 3000,
        .multiplier = 2.0,
        .deposit_per_success = 0.10,
        .withdraw_per_retry = 1.00,
        .max_tokens = 100.0
    };
    
    TokenBucket budget;
    token_bucket_init(&budget, policy.max_tokens, 15.0);
    
    long start_time = get_monotonic_ms();
    long deadline_ms = start_time + 5000; // 5 секунд загальний дедлайн
    
    int status = 0;
    char body[256] = {0};
    bool request_succeeded = false;
    
    for (int attempt = 0; attempt < policy.max_attempts; ++attempt) {
        long now = get_monotonic_ms();
        if (now >= deadline_ms) {
            printf("Дедлайн операції вичерпано!\n");
            break;
        }
        
        if (attempt > 0) {
            // Перевірка наявності токенів у бюджеті повторів
            if (!token_bucket_try_withdraw(&budget, policy.withdraw_per_retry)) {
                printf("Бюджет повторів вичерпано (Fast-Fail захист)!\n");
                break;
            }
            
            long backoff_ms = calculate_full_jitter(&policy, attempt - 1);
            if (now + backoff_ms >= deadline_ms) {
                printf("Розрахована затримка відступу виходить за межі дедлайну!\n");
                break;
            }
            
            usleep((useconds_t)(backoff_ms * 1000));
        }
        
        if (mock_transport("https://api.payments.internal/v1/charge", "req-key-123", &status, body)) {
            if (status >= 200 && status < 300) {
                token_bucket_record_success(&budget, policy.deposit_per_success);
                request_succeeded = true;
                break;
            }
            
            ErrorKind k = classify_status(status);
            if (k == ERR_PERMANENT) {
                printf("Постійна помилка HTTP %d, скасування повторів.\n", status);
                break;
            }
            printf("  [Спроба %d] Тимчасова помилка HTTP %d -> планування повтору\n", attempt + 1, status);
        }
    }
    
    if (request_succeeded) {
        printf("Успішно отримано відповідь: %s\n", body);
    } else {
        printf("Операція завершилася відмовою.\n");
    }
    
    pthread_mutex_destroy(&budget.lock);
    return 0;
}
```
:::

## Покроковий розбір механізму виконання виклику

Розглянемо послідовність дій під час виконання виклику методом `ResilientClient::execute()`:

1. **Ініціалізація та вхідний контроль:** Клієнт приймає цільовий URL, контекст запиту `RequestContext` із ключем ідемпотентності та дедлайном, а також функтор транспорту `TransportFn`. На початку кожної ітерації циклу метод `ctx.is_expired()` порівнює поточне значення монотонного годинника з точкою дедлайну. Якщо час уже вичерпано, виклик негайно завершується зі статусом помилки 504 Gateway Timeout, не виконуючи жодної мережевої операції.

2. **Контроль бюджету та очікування (для повторних спроб):** Якщо це не перший виклик (`attempt > 0`), клієнт звертається до екземпляра `TokenBucketRetryBudget`. Метод `try_withdraw_retry()` перевіряє наявність щонайменше 1.0 токена.
   * Якщо баланс кошика достатній, 1.0 токен списується, і калькулятор `BackoffCalculator::calculate()` генерує випадкову паузу за формулою Full Jitter на основі індексу спроби.
   * Якщо пауза вміщується у залишок дедлайну `ctx.time_remaining()`, потік засинає на розрахований час.
   * Якщо токенів недостатньо (наприклад, через масовий збій бекенда, коли частка помилок перевищила 10%), клієнт виконує швидку відмову (Fast-Fail), повертаючи помилку 429 Too Many Requests без посилання запиту в мережу.

3. **Виконання транспорту та класифікація результату:** Транспортний шар виконує фізичний HTTP/RPC виклик.
   * У разі успіху (код 200–299) метод `budget_.record_success(0.10)` поповнює баланс токенів, закріплюючи право на майбутні повтори, і повертає корисне навантаження клієнту.
   * У разі помилки HTTP статичний метод `HttpErrorClassifier::classify()` аналізує статус. Постійні помилки (400, 401, 403, 404, 422) негайно переривають цикл. Тимчасові помилки (503, 429, 504 або помилки сокета) дозволяють перейти до наступної ітерації циклу.

## Оптимізація паралелізму та кеш-ліній процесора (Lock-Free & False Sharing)

У високонавантажених сервісах (від 50 000 до 200 000 запитів/с на процес) стандартний `std::mutex` у токенному кошику може викликати деградацію продуктивності через конкуренцію за блокування (Lock Contention).

Для усунення вузького місця застосовують наступні оптимізації архітектури пам'яті:
1. **Вирівнювання на розмір кеш-лінії (`alignas(64)`):** Потоки різних ядер процесора модифікують локальні лічильники успіхів. Якщо лічильники розташовані поруч у пам'яті, виникає ефект хибного розділення (False Sharing), коли запис одного ядра призводить до інвалідації L1/L2 кешу іншого ядра. Вирівнювання структури на 64 байти ізолює лічильники в окремих кеш-лініях процесора.
2. **Атомарний кошик без блокувань (Lock-Free Atomic Bucket):** Баланс токенів зберігається як цілочисельний фіксований дріб в `std::atomic<int64_t>` (де 1 токен = 10 000 дискретних одиниць). Операція списання виконується через циклічний `compare_exchange_weak` із семантикою пам'яті `std::memory_order_relaxed` для успішного зчитування та `std::memory_order_acquire`/`release` для фіксації балансу.
3. **Батчинг поповнення (Batch Replenishment):** Замість того, щоб кожна успішна відповідь виконувала атомарний запис у спільний кошик, робочий потік накопичує 10 локальних успіхів і поповнює глобальний бюджет одним атомарним додаванням `+1.0`, скорочуючи кількість між'ядерних шинних транзакцій у 10 разів.

## Потокова передача тіла запиту (Streaming & Request Body Rewind)

Особливу складність становлять повторні спроби для запитів, які передають велике тіло (наприклад, завантаження файлу або передача багатомегабайтного JSON-пакета):
* Якщо клієнт використовує потокову передачу байтів (HTTP Chunked Transfer або gRPC Streaming), під час першої спроби внутрішній покажчик потоку читання зсувається до кінця буфера.
* Якщо сокет обривається після передачі половини даних, повторна відправка виклику наївним способом відправить порожнє тіло або викличе паніку розіменування недійсного покажчика.
* **Інваріант для стійких клієнтів:** клієнтський транспорт зобов'язаний або зберігати буферизовану копію тіла запиту в пам'яті/на диску з можливістю скидання покажчика читання на початок (`seek(0)` / `rewind()`), або вимагати від прикладного коду фабрики нових потоків читання перед кожною повторною спробою.

## Управління пулом з'єднань та відновлення сесій TLS

Повторні спроби на рівні L7 (HTTP/gRPC) тісно взаємодіють із рівнем L4 (TCP) та захищеним шаром L5/L6 (TLS):
* **Збереження з'єднань (HTTP Keep-Alive / TCP Connection Pooling):** Якщо помилка спричинена перевантаженням бекенда (HTTP 503), TCP-з'єднання залишається повністю здоровим. Виконання повторної спроби через той самий відкритий сокет утилізує існуюче TCP-вікно і не створює накладних витрат на нове тристороннє рукостискання (SYN/ACK).
* **Відновлення сесій TLS (TLS Session Resumption):** Якщо сокет розірвано сервером (TCP RST), нове підключення повинно використовувати квитки сесій TLS (TLS Session Tickets / PSK за стандартом TLS 1.3), що дозволяє завершити шифроване рукостискання за 1 RTT (або 0-RTT) замість повного криптографічного обміну ключами Діффі-Хеллмана на еліптичних кривих.
* **Очищення сокетів у стані TIME_WAIT:** Під час частих повторів із примусовим закриттям сокетів операційна система накопичує тисячі сокетів у стані `TIME_WAIT` (тривалістю 60 секунд). Це може призвести до вичерпання діапазону локальних ефемерних портів (Ephemeral Port Exhaustion). Використання пулу з'єднань та активація прапорця ядра Linux `tcp_tw_reuse` повністю усувають ризик вичерпання портів під час штормів повторів.

## Інтеграція спостережності та метрик (OpenTelemetry / Prometheus)

У промислових сервісах клієнт повторних спроб зобов'язаний експортувати детальні метрики для моніторингу стану системи та налаштування алертів:

1. **Лічильник спроб за результатами (`client_retries_total`):**
   * Мітки: `service_name`, `endpoint`, `attempt_number="1..4"`, `status_code="200|503|429|timeout"`.
   * Ця метрика показує ефективність кожного шару повторів: який відсоток тимчасових збоїв лікується першим повтором, а який вимагає другої чи третьої спроби.

2. **Гістограма тривалості відступу (`client_retry_backoff_seconds`):**
   * Бакети: `0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0` секунд.
   * Дозволяє перевірити коректність роботи алгоритму Full Jitter у реальному часі та переконатися у відсутності аномальних детерміністичних згущень.

3. **Калібрувальна шкала балансу токенів (`client_retry_budget_tokens`):**
   * Поточне значення кількості доступних токенів у `TokenBucketRetryBudget`.
   * Падіння балансу нижче 50% від максимальної ємності свідчить про початок масштабної деградації бекенда; падіння до 0 активує сповіщення черговому інженеру про початок лавинного блокування (Fast-Fail).

4. **Розподілений трейсинг (W3C Trace Context):**
   * Кожен фізичний HTTP-запит несе спільний заголовок `traceparent` (Trace ID), але кожна окрема повторна спроба отримує унікальний `Span ID` всередині батьківського спану клієнтської транзакції. Це дозволяє в інтерфейсі Jaeger або Grafana Tempo наочно бачити таймлайн усіх спроб, тривалість пауз відступу та точний момент повернення помилки.

## Зіставлення з інфраструктурними політиками Envoy та Linkerd

Якщо в системі розгорнуто сервісну сітку (Service Mesh), алгоритми клієнтського відступу конфігуруються декларативно на рівні площини управління:

* **Envoy xDS RouteConfiguration:**
  ```yaml
  retry_policy:
    retry_on: "5xx,connect-failure,refused-stream"
    num_retries: 3
    retry_back_off:
      base_interval: 0.1s
      max_interval: 3.0s
    retry_budget:
      budget_percent:
        value: 10.0
      min_retry_concurrency: 5
  ```
  Envoy реалізує точно такий самий алгоритм Full Jitter та токенний бюджет повторів (`budget_percent`), делегуючи захист від штормів сайдкар-проксі безпосередньо в мережевому шарі інфраструктури.

## Тестування та хаос-інжиніринг (Chaos & Fault Injection)

Тестування клієнтів стійкості є критичним етапом, оскільки недетерміністична природа джитера ускладнює написання традиційних юніт-тестів.

Для детерміністичного тестування застосовуються такі практики:
* **Ін'єкція генератора псевдовипадкових чисел:** генератор `std::mt19937` ініціалізується фіксованим фіктивним сід-числом (Seed), що дозволяє перевірити розрахунок точних значень пауз на кожній ітерації.
* **Віртуальний годинник (Mock Clock):** замість реального очікування `std::this_thread::sleep_for()` тестовий фреймворк передає віртуальний годинник, час на якому штучно прокручується вперед на величину відступу.
* **Емуляція мережевих збоїв (Chaos Testing):** за допомогою мок-транспорту симулюються сценарії:
  1. *Короткочасний збій:* перші дві спроби повертають 503, третя — 200 OK. Перевіряється поповнення бюджету наприкінці.
  2. *Постійний збій:* повернення 400 Bad Request на першій спробі. Перевіряється негайна зупинка без повторів і збереження токенів у бюджеті.
  3. *Вичерпання бюджету:* серія зі ста помилок підряд. Перевіряється перехід клієнта у стан Fast-Fail після вичерпання стартового запасу токенів.
  4. *Закінчення дедлайну:* початковий дедлайн 150 мс, перша спроба триває 100 мс, розрахований відступ — 80 мс. Перевіряється скасування повтору без виконання другого мережевого запиту.

## Аналіз критичних інженерних пасток

Під час експлуатації клієнтів повторних спроб у високонавантаженому середовищі виникають наступні типові помилки:

### 1. Повторення неідемпотентних мутуючих запитів після таймауту сокета
Якщо клієнт відправив запит POST `/api/v1/payments/charge` і не отримав відповіді протягом таймауту сокета `SO_RCVTIMEO`:
* Сервер міг успішно прийняти пакет, провести транзакцію в базі даних і списати кошти, але пакет з HTTP 200 OK загубився в мережі.
* Повторний виклик без заголовка `Idempotency-Key` спричинить подвійне списання грошей.
* **Інваріант:** повторні спроби для небезпечних методів (POST, non-idempotent PUT/PATCH) суворо заборонені, якщо протокол взаємодії не підтримує наскрізні ключі ідемпотентності на рівні сховища бекенда.

### 2. Скидання лічильника спроб при отриманні нового з'єднання з пулу
Якщо клієнтська бібліотека відкриває нове TCP-з'єднання з пулу після розриву попереднього сокета, лічильник спроб `attempt` не повинен скидатися до нуля. Спроби мають рахуватися на рівні логічної бізнес-операції, інакше клієнт генеруватиме нескінченний потік підключень до мертвого вузла.

### 3. Ігнорування заголовка сервера Retry-After
Якщо віддалений сервіс повертає код 429 Too Many Requests або 503 Service Unavailable із заголовком `Retry-After: 120` (затримка 120 секунд), клієнт зобов'язаний використати вказаний сервером інтервал, а не власний розрахунковий відступ у 200 мілісекунд. Ігнорування вказівки сервера нівелює механізми захисту бекенда від перевантаження.
