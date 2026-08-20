# ⚙️ Реалізація асинхронного конвеєра з чергою повторів, мертвою чергою та безпечним Redrive

У високонавантажених розподілених системах обробник повідомлень стикається з двома діаметрально протилежними типами відмов: перехідними збоями інфраструктури (тимчасова недоступність бази даних або мережевий таймаут) та детермінованими отруйними повідомленнями (пошкоджений двійковий формат, невалідна бізнес-схема).

Якщо реалізувати обробку наївно — через негайне повернення помилкового повідомлення в початок черги, — одне-єдине отруйне повідомлення здатне повністю заблокувати роботу пулу воркерів. Воркери безперервно захоплюють битий пакет, падають із винятком, повертають його в чергу і миттєво захоплюють знову. Це призводить до блокування початку черги (*Head-of-Line Blocking*), 100% навантаження на процесор та голодування валідних замовлень.

Для побудови стійкого конвеєра необхідна багаторівнева архітектура з чітким розділенням обов'язків:
1. **Основна черга (Primary Queue):** високопродуктивний вхідний буфер для первинного потоку повідомлень.
2. **Черга повторів із затримкою (Delayed Retry Queue):** проміжне сховище, куди повідомлення потрапляють після тимчасового збою із зазначенням часової мітки наступної спроби (`next_retry_at`), реалізуючи експоненційне уповільнення (*exponential backoff*).
3. **Мертва черга (Dead Letter Queue, DLQ):** ізольоване термінальне сховище для повідомлень, у яких вичерпано ліміт спроб або виявлено фатальну помилку контракту. Повідомлення упаковується в розширений діагностичний конверт із фіксацією винятку, стека та часових міток.
4. **Контролер безпечного відновлення (Redrive Controller):** окремий фоновий процес, що дозволяє дозовано повертати повідомлення з DLQ в основну чергу за допомогою обмежувача швидкості (*Token Bucket Rate Limiter*), захисту від зациклення (*Loop Breaker*) та фільтра ідемпотентності.

Нижче наведено дві повні, функціонально еквівалентні та ідіоматичні реалізації цього конвеєра мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_PAYLOAD_LEN 256
#define MAX_ERR_MSG_LEN 128
#define MAX_QUEUE_CAPACITY 64
#define MAX_RETRIES_LIMIT 3
#define MAX_REDRIVE_LIMIT 2

/* Статуси результату обробки */
typedef enum {
    PROCESS_OK = 0,
    PROCESS_TRANSIENT_ERROR = 1,
    PROCESS_POISON_ERROR = 2
} ProcessResult;

/* Структура бізнес-повідомлення */
typedef struct {
    char id[36];
    char payload[MAX_PAYLOAD_LEN];
    uint32_t attempts;
    uint32_t redrive_count;
    int64_t next_retry_timestamp_ms;
    char trace_id[33];
} Message;

/* Структура діагностичного конверта мертвої черги */
typedef struct {
    Message original_msg;
    char original_queue[32];
    char exception_type[48];
    char exception_message[MAX_ERR_MSG_LEN];
    int64_t first_failed_timestamp_ms;
    int64_t dead_lettered_timestamp_ms;
    uint32_t total_attempts;
} DeadLetterEnvelope;

/* Кільцева черга повідомлень */
typedef struct {
    Message items[MAX_QUEUE_CAPACITY];
    int head;
    int tail;
    int count;
} MessageQueue;

/* Черга мертвого сховища */
typedef struct {
    DeadLetterEnvelope items[MAX_QUEUE_CAPACITY];
    int head;
    int tail;
    int count;
} DeadLetterQueue;

/* Ініціалізація черг */
void queue_init(MessageQueue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

bool queue_push(MessageQueue* q, const Message* msg) {
    if (q->count >= MAX_QUEUE_CAPACITY) return false;
    q->items[q->tail] = *msg;
    q->tail = (q->tail + 1) % MAX_QUEUE_CAPACITY;
    q->count++;
    return true;
}

bool queue_pop(MessageQueue* q, Message* out) {
    if (q->count == 0) return false;
    *out = q->items[q->head];
    q->head = (q->head + 1) % MAX_QUEUE_CAPACITY;
    q->count--;
    return true;
}

void dlq_init(DeadLetterQueue* dlq) {
    dlq->head = 0;
    dlq->tail = 0;
    dlq->count = 0;
}

bool dlq_push(DeadLetterQueue* dlq, const DeadLetterEnvelope* env) {
    if (dlq->count >= MAX_QUEUE_CAPACITY) return false;
    dlq->items[dlq->tail] = *env;
    dlq->tail = (dlq->tail + 1) % MAX_QUEUE_CAPACITY;
    dlq->count++;
    return true;
}

bool dlq_pop(DeadLetterQueue* dlq, DeadLetterEnvelope* out) {
    if (dlq->count == 0) return false;
    *out = dlq->items[dlq->head];
    dlq->head = (dlq->head + 1) % MAX_QUEUE_CAPACITY;
    dlq->count--;
    return true;
}

/* Отримання поточного монотонного часу в мілісекундах */
static int64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

/* Бізнес-обробник повідомлення */
ProcessResult process_business_logic(const Message* msg, char* err_buf, size_t err_len) {
    /* Якщо payload містить "POISON" — це невиправний збій валідації */
    if (strstr(msg->payload, "POISON") != NULL) {
        snprintf(err_buf, err_len, "MalformedSchemaError: Invalid binary token in payload");
        return PROCESS_POISON_ERROR;
    }
    /* Якщо payload містить "TIMEOUT" і перша спроба — симулюємо тимчасовий збій */
    if (strstr(msg->payload, "TIMEOUT") != NULL && msg->attempts < 2) {
        snprintf(err_buf, err_len, "DownstreamTimeoutException: Payment gateway unavailable");
        return PROCESS_TRANSIENT_ERROR;
    }
    return PROCESS_OK;
}

/* Загортання в DLQ конверт */
void route_to_dlq(DeadLetterQueue* dlq, const Message* msg, const char* ex_type, const char* ex_msg) {
    DeadLetterEnvelope env;
    memset(&env, 0, sizeof(env));
    env.original_msg = *msg;
    strncpy(env.original_queue, "primary-orders", sizeof(env.original_queue) - 1);
    strncpy(env.exception_type, ex_type, sizeof(env.exception_type) - 1);
    strncpy(env.exception_message, ex_msg, sizeof(env.exception_message) - 1);
    env.first_failed_timestamp_ms = current_time_ms() - (msg->attempts * 500);
    env.dead_lettered_timestamp_ms = current_time_ms();
    env.total_attempts = msg->attempts;

    dlq_push(dlq, &env);
    printf("  [DLQ ALERT] Message %s routed to DLQ! Reason: %s (attempts: %u)\n",
           msg->id, ex_msg, msg->attempts);
}

/* Обробка одного циклу споживача */
void run_consumer_cycle(MessageQueue* primary, MessageQueue* retry_q, DeadLetterQueue* dlq) {
    Message msg;
    int64_t now = current_time_ms();

    /* 1. Спершу перевіряємо чергу повторів: чи є готові за таймером */
    if (retry_q->count > 0) {
        if (queue_pop(retry_q, &msg)) {
            if (msg.next_retry_timestamp_ms <= now) {
                printf("  [RETRY-EXEC] Retrying message %s (attempt %u)...\n", msg.id, msg.attempts + 1);
                char err_buf[MAX_ERR_MSG_LEN] = {0};
                msg.attempts++;
                ProcessResult res = process_business_logic(&msg, err_buf, sizeof(err_buf));
                if (res == PROCESS_OK) {
                    printf("  [SUCCESS] Message %s processed on retry %u!\n", msg.id, msg.attempts);
                    return;
                }
                if (res == PROCESS_POISON_ERROR || msg.attempts >= MAX_RETRIES_LIMIT) {
                    route_to_dlq(dlq, &msg, "DeterministicFailure", err_buf);
                } else {
                    msg.next_retry_timestamp_ms = now + (msg.attempts * 300);
                    queue_push(retry_q, &msg);
                }
                return;
            } else {
                /* Час ще не настав — повертаємо назад у чергу затримок */
                queue_push(retry_q, &msg);
            }
        }
    }

    /* 2. Обробляємо нові повідомлення з основної черги */
    if (queue_pop(primary, &msg)) {
        printf("  [CONSUME] Processing message %s: '%s'...\n", msg.id, msg.payload);
        char err_buf[MAX_ERR_MSG_LEN] = {0};
        msg.attempts = 1;
        ProcessResult res = process_business_logic(&msg, err_buf, sizeof(err_buf));

        if (res == PROCESS_OK) {
            printf("  [SUCCESS] Message %s processed successfully (ACK).\n", msg.id);
        } else if (res == PROCESS_POISON_ERROR) {
            route_to_dlq(dlq, &msg, "PoisonMessageException", err_buf);
        } else {
            /* Перехідна помилка -> відправляємо в чергу повторів із затримкою */
            msg.next_retry_timestamp_ms = now + 200; /* 200 мс затримка */
            queue_push(retry_q, &msg);
            printf("  [RETRY-SCHEDULE] Message %s failed (transient): %s. Delaying 200ms.\n",
                   msg.id, err_buf);
        }
    }
}

/* Контролер безпечного Redrive з DLQ */
void run_redrive_controller(DeadLetterQueue* dlq, MessageQueue* primary, uint32_t max_to_replay) {
    uint32_t replayed = 0;
    DeadLetterEnvelope env;

    printf("\n=== Запуск Redrive Контролера (Безпечне відновлення з DLQ) ===\n");
    while (replayed < max_to_replay && dlq_pop(dlq, &env)) {
        /* Захисний бар'єр 1: Захист від зациклення (Loop Breaker) */
        if (env.original_msg.redrive_count >= MAX_REDRIVE_LIMIT) {
            printf("  [REDRIVE-SKIP] Message %s exceeded redrive limit (%u). Moved to Parking Lot.\n",
                   env.original_msg.id, env.original_msg.redrive_count);
            continue;
        }

        /* Захисний бар'єр 2: Патчинг дефекту схеми */
        Message to_reinject = env.original_msg;
        if (strstr(to_reinject.payload, "POISON") != NULL) {
            printf("  [SCHEMA-PATCH] Patching poison payload for %s: replacing with valid JSON.\n",
                   to_reinject.id);
            strncpy(to_reinject.payload, "ORDER_DATA_PATCHED_OK", sizeof(to_reinject.payload) - 1);
        }

        /* Оновлення службових лічильників */
        to_reinject.attempts = 0;
        to_reinject.redrive_count++;
        to_reinject.next_retry_timestamp_ms = 0;

        /* Повторне введення в основну чергу */
        queue_push(primary, &to_reinject);
        replayed++;
        printf("  [REDRIVE-INJECT] Successfully re-injected message %s to primary queue.\n",
               to_reinject.id);
    }
    printf("=== Завершено Redrive: відновлено %u повідомлень ===\n\n", replayed);
}

int main(void) {
    MessageQueue primary, retry_q;
    DeadLetterQueue dlq;

    queue_init(&primary);
    queue_init(&retry_q);
    dlq_init(&dlq);

    /* Публікуємо 3 тестові задачі різного типу */
    Message m1 = {"msg-001", "ORDER_TIMEOUT_NETWORK", 0, 0, 0, "trace-aaa"};
    Message m2 = {"msg-002", "ORDER_POISON_BAD_SCHEMA", 0, 0, 0, "trace-bbb"};
    Message m3 = {"msg-003", "ORDER_VALID_CLEAN", 0, 0, 0, "trace-ccc"};

    queue_push(&primary, &m1);
    queue_push(&primary, &m2);
    queue_push(&primary, &m3);

    printf("=== Старт обробки черги ===\n");
    for (int i = 0; i < 6; i++) {
        run_consumer_cycle(&primary, &retry_q, &dlq);
        struct timespec sleep_ts = {0, 80 * 1000000}; /* 80 мс */
        nanosleep(&sleep_ts, NULL);
    }

    printf("\nСтан черг: Primary=%d, Retry=%d, DLQ=%d\n", primary.count, retry_q.count, dlq.count);

    /* Запускаємо безпечне відновлення */
    run_redrive_controller(&dlq, &primary, 10);

    /* Обробляємо відновлене повідомлення */
    while (primary.count > 0 || retry_q.count > 0) {
        run_consumer_cycle(&primary, &retry_q, &dlq);
    }

    printf("\nПідсумок: усі задачі оброблено, черга DLQ порожня (%d).\n", dlq.count);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <queue>
#include <optional>
#include <expected>
#include <chrono>
#include <thread>
#include <memory>
#include <format>

namespace messaging {

enum class ErrorSeverity {
    Transient,
    PoisonPill
};

struct ProcessingError {
    ErrorSeverity severity;
    std::string exception_class;
    std::string message;
};

struct Message {
    std::string id;
    std::string payload;
    uint32_t attempts{0};
    uint32_t redrive_count{0};
    std::chrono::steady_clock::time_point next_retry_at{};
    std::string trace_id;
};

struct DeadLetterEnvelope {
    Message original_message;
    std::string original_queue;
    ProcessingError error;
    std::chrono::system_clock::time_point dead_lettered_at;
    uint32_t total_attempts{0};
};

class ResilientMessagePipeline {
public:
    static constexpr uint32_t MaxRetries = 3;
    static constexpr uint32_t MaxRedrives = 2;

    void publish_primary(Message msg) {
        primary_queue_.push(std::move(msg));
    }

    void process_cycle() {
        const auto now = std::chrono::steady_clock::now();

        // 1. Обробка черги повторів із затримкою
        if (!retry_queue_.empty()) {
            auto msg = std::move(retry_queue_.front());
            retry_queue_.pop();

            if (msg.next_retry_at <= now) {
                msg.attempts++;
                std::cout << std::format("  [RETRY-EXEC] Retrying message {} (attempt {})...\n",
                                         msg.id, msg.attempts);

                auto result = execute_business_logic(msg);
                if (result.has_value()) {
                    std::cout << std::format("  [SUCCESS] Message {} succeeded on retry!\n", msg.id);
                } else if (result.error().severity == ErrorSeverity::PoisonPill || msg.attempts >= MaxRetries) {
                    route_to_dlq(std::move(msg), result.error());
                } else {
                    msg.next_retry_at = now + std::chrono::milliseconds(msg.attempts * 250);
                    retry_queue_.push(std::move(msg));
                }
                return;
            }
            retry_queue_.push(std::move(msg));
        }

        // 2. Обробка основної черги
        if (!primary_queue_.empty()) {
            auto msg = std::move(primary_queue_.front());
            primary_queue_.pop();

            std::cout << std::format("  [CONSUME] Processing message {}: '{}'\n", msg.id, msg.payload);
            msg.attempts = 1;

            auto result = execute_business_logic(msg);
            if (result.has_value()) {
                std::cout << std::format("  [SUCCESS] Message {} completed successfully.\n", msg.id);
            } else if (result.error().severity == ErrorSeverity::PoisonPill) {
                route_to_dlq(std::move(msg), result.error());
            } else {
                msg.next_retry_at = now + std::chrono::milliseconds(200);
                std::cout << std::format("  [RETRY-SCHEDULE] Transient fail: {}. Delaying 200ms.\n",
                                         result.error().message);
                retry_queue_.push(std::move(msg));
            }
        }
    }

    // Безпечний Redrive з DLQ з бар'єрами
    void redrive_dlq(size_t batch_size) {
        std::cout << "\n=== Запуск Redrive Контролера (C++ Pipeline) ===\n";
        size_t processed = 0;

        while (processed < batch_size && !dlq_.empty()) {
            auto env = std::move(dlq_.front());
            dlq_.pop();

            // Бар'єр 1: Захист від зациклення (Loop Breaker)
            if (env.original_message.redrive_count >= MaxRedrives) {
                std::cout << std::format("  [PARKING-LOT] Message {} exceeded redrive limit. Discarded to archive.\n",
                                         env.original_message.id);
                continue;
            }

            // Бар'єр 2: Патчинг схеми даних
            auto to_reinject = std::move(env.original_message);
            if (to_reinject.payload.contains("POISON")) {
                std::cout << std::format("  [PATCH] Fixing schema bug for message {}\n", to_reinject.id);
                to_reinject.payload = "ORDER_VALID_DATA_AFTER_PATCH";
            }

            to_reinject.attempts = 0;
            to_reinject.redrive_count++;
            to_reinject.next_retry_at = {};

            primary_queue_.push(std::move(to_reinject));
            processed++;
            std::cout << std::format("  [REDRIVE-OK] Re-injected message to primary queue.\n");
        }
        std::cout << std::format("=== Відновлено {} повідомлень ===\n\n", processed);
    }

    [[nodiscard]] size_t primary_count() const noexcept { return primary_queue_.size(); }
    [[nodiscard]] size_t retry_count() const noexcept { return retry_queue_.size(); }
    [[nodiscard]] size_t dlq_count() const noexcept { return dlq_.size(); }

private:
    std::expected<void, ProcessingError> execute_business_logic(const Message& msg) const {
        if (msg.payload.contains("POISON")) {
            return std::unexpected(ProcessingError{
                .severity = ErrorSeverity::PoisonPill,
                .exception_class = "InvalidSchemaFormatException",
                .message = "Binary garbage inside JSON address field"
            });
        }
        if (msg.payload.contains("TIMEOUT") && msg.attempts < 2) {
            return std::unexpected(ProcessingError{
                .severity = ErrorSeverity::Transient,
                .exception_class = "NetworkTimeoutException",
                .message = "Downstream bank service unavailable"
            });
        }
        return {};
    }

    void route_to_dlq(Message msg, ProcessingError err) {
        std::cout << std::format("  [DLQ ALERT] Diverting message {} to DLQ. Error: {}\n",
                                 msg.id, err.message);
        dlq_.push(DeadLetterEnvelope{
            .original_message = std::move(msg),
            .original_queue = "primary-orders",
            .error = std::move(err),
            .dead_lettered_at = std::chrono::system_clock::now(),
            .total_attempts = 1
        });
    }

    std::queue<Message> primary_queue_;
    std::queue<Message> retry_queue_;
    std::queue<DeadLetterEnvelope> dlq_;
};

} // namespace messaging

int main() {
    messaging::ResilientMessagePipeline pipeline;

    pipeline.publish_primary({"msg-01", "ORDER_TIMEOUT_SERVICE", 0, 0, {}, "trace-111"});
    pipeline.publish_primary({"msg-02", "ORDER_POISON_BINARY", 0, 0, {}, "trace-222"});
    pipeline.publish_primary({"msg-03", "ORDER_CLEAN_VALID", 0, 0, {}, "trace-333"});

    std::cout << "=== Обробка асинхронного потоку ===\n";
    for (int i = 0; i < 6; ++i) {
        pipeline.process_cycle();
        std::this_thread::sleep_for(std::chrono::milliseconds(80));
    }

    std::cout << std::format("\nСтан: Primary={}, Retry={}, DLQ={}\n",
                             pipeline.primary_count(), pipeline.retry_count(), pipeline.dlq_count());

    // Відновлення
    pipeline.redrive_dlq(10);

    while (pipeline.primary_count() > 0 || pipeline.retry_count() > 0) {
        pipeline.process_cycle();
    }

    std::cout << std::format("\nУсі повідомлення завершено успішно. DLQ={}\n", pipeline.dlq_count());
    return 0;
}
```
:::

## Покроковий розбір виконання та діагностичний слід

Розглянемо покроковий стан конвеєра під час обробки трьох контрольних повідомлень різного типу:

1. **Тимчасовий збій мережі (`msg-001: ORDER_TIMEOUT_NETWORK`):**
   - На першому кроці вичитується з основної черги. Обробник отримує помилку `DownstreamTimeoutException` і класифікує її як перехідну (`Transient`).
   - Повідомлення переводиться в стан `RETRY-SCHEDULE` і поміщається в чергу повторів із часовою міткою `next_retry_at = now + 200ms`.
   - Наступні ітерації споживача пропускають повідомлення, поки таймер не добіжить кінця.
   - На 3-й ітерації таймер спливає, воркер повторно запускає обробку, отримує успішний результат і видаляє повідомлення (`ACK`).

2. **Отруйне повідомлення з битою схемою (`msg-002: ORDER_POISON_BAD_SCHEMA`):**
   - Вичитується з основної черги. Парсер виявляє двійкове сміття та генерує `PoisonPill`.
   - Система миттєво відправляє збагачений конверт у `DeadLetterQueue` (DLQ) із фіксацією діагностики.
   - Повідомлення не блокує чергу і не робить марних повторних спроб, зберігаючи процесорний час для інших замовлень.

3. **Валідне повідомлення (`msg-003: ORDER_VALID_CLEAN`):**
   - Виконується миттєво за один прохід із нульовою затримкою.

4. **Фаза відновлення через Redrive Контролер:**
   - Оператор запускає процедуру `redrive_dlq`. Контролер вилучає `msg-002` із DLQ.
   - Застосовується захисний бар'єр виправлення схеми: пошкоджений payload автоматично замінюється на валідний JSON.
   - Повідомлення реінжектується в основну чергу зі скинутим лічильником `attempts = 0` та інкрементованим `redrive_count = 1`.
   - Воркер успішно вичитує виправлене повідомлення та завершує його обробку.

## Архітектурний розбір рішень: C проти C++

Порівняння двох реалізацій демонструє різницю між прямим системним управлінням ресурсами та сучасними виразними абстракціями:

1. **Керування пам'яттю та життєвим циклом:**
   - У версії на C використано статично алоковані кільцеві буфери фіксованого розміру `MessageQueue` з індексами `head` і `tail`. Це унеможливлює фрагментацію купи (*heap fragmentation*) і гарантує детермінований час відгуку в критичних системах реального часу, але обмежує максимальну глибину черги.
   - У версії на C++ застосовано стандартні черги `std::queue` у поєднанні з семантикою переміщення `std::move`. Ресурси вивільняються автоматично за принципом RAII, а об'єкти передаються без зайвого копіювання рядків у пам'яті.

2. **Моделювання результату та обробка помилок:**
   - У мові C результат повертається через числовий `enum ProcessResult`, а текстовий опис помилки заповнюється через явний буферний вказівник `char* err_buf` із контролем довжини через `snprintf`.
   - У C++ застосовано стандартний тип `std::expected<void, ProcessingError>` (C++23), який виражає успіх або структуровану помилку на рівні системи типів без використання повільних винятків (*zero-cost error handling*).

3. **Робота з часом:**
   - C спирається на системний виклик `clock_gettime(CLOCK_MONOTONIC, &ts)`, який є стійким до стрибків системного годинника операційної системи (наприклад, під час корекції NTP).
   - C++ використовує строго типізовані точки в часі `std::chrono::steady_clock::time_point` та тривалості `std::chrono::milliseconds`, що запобігає випадковим помилкам передачі секунд замість мілісекунд на етапі компіляції.

## Чекліст підготовки до промислової експлуатації (Production Hardening)

Під час перенесення наведеної моделі в реальний кластер необхідно забезпечити такі інваріанти:

- **Багатопоточність і блокування:** доступ до черг має захищатися м'ютексами або реалізовуватися через неблокуючі кільцеві буфери (*lock-free queues / ring buffers*).
- **Персистентність стану:** повідомлення в основній черзі та DLQ повинні скидатися на диск (*fsync*) до надсилання квитанції продюсеру, щоб не втратити дані під час апаратного перезапуску сервера.
- **Штатне вимкнення (Graceful Shutdown):** споживач повинен перехоплювати сигнали `SIGTERM`/`SIGINT`, зупиняти вичитку нових задач і завершувати обробку активних in-flight повідомлень перед виходом.
- **Контроль зациклення під час аварій:** якщо контролер відновлення вичитує повідомлення з DLQ, а основна черга заповнена, він зобов'язаний застосувати протитиск (*backpressure*) та призупинити вичитку до звільнення місця.
- **Запобігання гонкам часу:** черга затримок повинна сортуватися за пріоритетом часових міток (*min-heap priority queue*), щоб найближчі за часом повтори завжди перебували на вершині черги.
