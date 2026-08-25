# ⚙️ Реалізація демпфера навантаження: кільцевий буфер з бекпреше, токен-бакет споживача та відсікання за таймаутом

Практична реалізація патерну вирівнювання навантаження чергою вимагає узгодження трьох критичних компонентів у багатопотоковому середовищі:
1. **Обмежений потокобезпечний буфер (Bounded Queue):** приймає задачі від мережевих потоків прийому без блокування продюсера, контролює максимальну ємність та сигналізує про переповнення.
2. **Токен-бакет лімітер на боці споживачів (Consumer Rate Limiter):** суворо обмежує сумарну кількість транзакцій на секунду, які пул воркерів має право відправити до бази даних.
3. **Фільтр застарілих задач (TTL Deadlock Filter):** перевіряє часові дедлайни задач перед виконанням, відсікаючи ті, що втратили актуальність під час очікування в черзі.

Коли вхідний мережевий потік генерує тисячі паралельних з'єднань, пряме виділення пам'яті під необмежені черги швидко призводить до фрагментації купи (*heap fragmentation*) та аварійного падіння процесу через вичерпання RAM. Тому промисловий демпфер завжди будується як кільцевий буфер фіксованої місткості з попередньо виділеною неперервною ділянкою пам'яті.

## Програмна архітектура демпфера

Система складається з диспетчера черги, пулу робочих потоків (*worker threads*) та механізму регулювання темпу на основі алгоритму маркерного кошика (*Token Bucket*).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAX_QUEUE_CAPACITY 1024
#define MAX_PAYLOAD_LEN    256

/* Статуси операції постановки в чергу */
typedef enum {
    LEVELER_SUCCESS = 0,
    LEVELER_QUEUE_FULL = 1,
    LEVELER_SHUTDOWN = 2
} LevelerStatus;

/* Структура завдання */
typedef struct {
    uint64_t task_id;
    char     payload[MAX_PAYLOAD_LEN];
    uint64_t enqueue_time_ms;
    uint64_t deadline_ms; /* Абсолютний дедлайн у мілісекундах */
} Task;

/* Допоміжна функція отримання монотонного часу в мілісекундах */
static uint64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

/* Маркерний кошик для регулювання темпу споживання (Token Bucket) */
typedef struct {
    pthread_mutex_t lock;
    double          tokens;
    double          capacity;
    double          fill_rate_per_sec;
    uint64_t        last_refill_ms;
} TokenBucket;

static void token_bucket_init(TokenBucket *tb, double rate_rps, double capacity) {
    pthread_mutex_init(&tb->lock, NULL);
    tb->tokens = capacity;
    tb->capacity = capacity;
    tb->fill_rate_per_sec = rate_rps;
    tb->last_refill_ms = current_time_ms();
}

static void token_bucket_destroy(TokenBucket *tb) {
    pthread_mutex_destroy(&tb->lock);
}

/* Спроба взяти токен з очікуванням */
static void token_bucket_consume(TokenBucket *tb) {
    while (1) {
        pthread_mutex_lock(&tb->lock);
        uint64_t now = current_time_ms();
        double elapsed_sec = (double)(now - tb->last_refill_ms) / 1000.0;
        tb->tokens += elapsed_sec * tb->fill_rate_per_sec;
        if (tb->tokens > tb->capacity) {
            tb->tokens = tb->capacity;
        }
        tb->last_refill_ms = now;

        if (tb->tokens >= 1.0) {
            tb->tokens -= 1.0;
            pthread_mutex_unlock(&tb->lock);
            return;
        }

        /* Розрахунок часу очікування до появи наступного токена */
        double needed = 1.0 - tb->tokens;
        useconds_t wait_us = (useconds_t)((needed / tb->fill_rate_per_sec) * 1000000.0);
        pthread_mutex_unlock(&tb->lock);

        if (wait_us < 1000) wait_us = 1000;
        usleep(wait_us);
    }
}

/* Обмежений кільцевий буфер черги з демпфуванням */
typedef struct {
    Task            ring[MAX_QUEUE_CAPACITY];
    size_t          head;
    size_t          tail;
    size_t          count;
    size_t          max_capacity;
    bool            shutdown;

    pthread_mutex_t lock;
    pthread_cond_t  not_empty;

    TokenBucket     rate_limiter;

    /* Метрики */
    uint64_t        tasks_processed;
    uint64_t        tasks_rejected;
    uint64_t        tasks_expired;
} QueueLoadLeveler;

void leveler_init(QueueLoadLeveler *ql, size_t capacity, double max_rate_rps) {
    memset(ql, 0, sizeof(*ql));
    ql->max_capacity = (capacity > MAX_QUEUE_CAPACITY) ? MAX_QUEUE_CAPACITY : capacity;
    pthread_mutex_init(&ql->lock, NULL);
    pthread_cond_init(&ql->not_empty, NULL);
    token_bucket_init(&ql->rate_limiter, max_rate_rps, max_rate_rps * 0.2); /* Бурст 20% */
}

void leveler_destroy(QueueLoadLeveler *ql) {
    pthread_mutex_destroy(&ql->lock);
    pthread_cond_destroy(&ql->not_empty);
    token_bucket_destroy(&ql->rate_limiter);
}

/* Неблокуюча постановка задачі у чергу (Ingress) */
LevelerStatus leveler_enqueue(QueueLoadLeveler *ql, const char *payload, uint64_t timeout_ms) {
    pthread_mutex_lock(&ql->lock);

    if (ql->shutdown) {
        pthread_mutex_unlock(&ql->lock);
        return LEVELER_SHUTDOWN;
    }

    /* Якщо буфер переповнений — негайний бекпреше (Load Shedding) */
    if (ql->count >= ql->max_capacity) {
        ql->tasks_rejected++;
        pthread_mutex_unlock(&ql->lock);
        return LEVELER_QUEUE_FULL;
    }

    uint64_t now = current_time_ms();
    Task *t = &ql->ring[ql->tail];
    t->task_id = ql->tasks_processed + ql->count + 1;
    strncpy(t->payload, payload, MAX_PAYLOAD_LEN - 1);
    t->payload[MAX_PAYLOAD_LEN - 1] = '\0';
    t->enqueue_time_ms = now;
    t->deadline_ms = now + timeout_ms;

    ql->tail = (ql->tail + 1) % ql->max_capacity;
    ql->count++;

    pthread_cond_signal(&ql->not_empty);
    pthread_mutex_unlock(&ql->lock);

    return LEVELER_SUCCESS;
}

/* Вичитування задачі воркером з контролем темпу та дедлайну */
bool leveler_dequeue(QueueLoadLeveler *ql, Task *out_task) {
    while (1) {
        pthread_mutex_lock(&ql->lock);

        while (ql->count == 0 && !ql->shutdown) {
            pthread_cond_wait(&ql->not_empty, &ql->lock);
        }

        if (ql->count == 0 && ql->shutdown) {
            pthread_mutex_unlock(&ql->lock);
            return false;
        }

        /* Забираємо задачу з черги */
        *out_task = ql->ring[ql->head];
        ql->head = (ql->head + 1) % ql->max_capacity;
        ql->count--;

        pthread_mutex_unlock(&ql->lock);

        /* Перевірка дедлайну (чи не застаріла задача в черзі) */
        uint64_t now = current_time_ms();
        if (now > out_task->deadline_ms) {
            pthread_mutex_lock(&ql->lock);
            ql->tasks_expired++;
            pthread_mutex_unlock(&ql->lock);
            continue; /* Пропускаємо протерміновану задачу */
        }

        /* Застосування токен-бакета: воркер затримується до дозволеного темпу */
        token_bucket_consume(&ql->rate_limiter);

        pthread_mutex_lock(&ql->lock);
        ql->tasks_processed++;
        pthread_mutex_unlock(&ql->lock);

        return true;
    }
}

void leveler_stop(QueueLoadLeveler *ql) {
    pthread_mutex_lock(&ql->lock);
    ql->shutdown = true;
    pthread_cond_broadcast(&ql->not_empty);
    pthread_mutex_unlock(&ql->lock);
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <atomic>
#include <expected>

namespace resilience {

using namespace std::chrono_literals;

enum class LevelerError {
    QueueFull,
    SystemShutdown
};

struct Task {
    uint64_t id{0};
    std::string payload;
    std::chrono::steady_clock::time_point enqueue_time;
    std::chrono::steady_clock::time_point deadline;
};

// Потокобезпечний маркерний кошик (Token Bucket)
class TokenBucket {
public:
    TokenBucket(double rate_rps, double capacity)
        : rate_per_sec_(rate_rps), capacity_(capacity), tokens_(capacity),
          last_refill_(std::chrono::steady_clock::now()) {}

    void consume() {
        while (true) {
            std::unique_lock lock(mutex_);
            auto now = std::chrono::steady_clock::now();
            std::chrono::duration<double> elapsed = now - last_refill_;
            tokens_ = std::min(capacity_, tokens_ + elapsed.count() * rate_per_sec_);
            last_refill_ = now;

            if (tokens_ >= 1.0) {
                tokens_ -= 1.0;
                return;
            }

            double missing = 1.0 - tokens_;
            auto wait_duration = std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::duration<double>(missing / rate_per_sec_)
            );
            lock.unlock();

            std::this_thread::sleep_for(std::max(wait_duration, 500us));
        }
    }

private:
    std::mutex mutex_;
    const double rate_per_sec_;
    const double capacity_;
    double tokens_;
    std::chrono::steady_clock::time_point last_refill_;
};

// Демпфер навантаження чергою
class QueueLoadLeveler {
public:
    QueueLoadLeveler(size_t max_capacity, double max_rps)
        : max_capacity_(max_capacity), rate_limiter_(max_rps, max_rps * 0.2) {}

    ~QueueLoadLeveler() {
        stop();
    }

    // Асинхронна постановка задачі з миттєвим бекпреше при переповненні
    std::expected<uint64_t, LevelerError> enqueue(std::string payload, std::chrono::milliseconds ttl) {
        std::unique_lock lock(mutex_);

        if (shutdown_) {
            return std::unexpected(LevelerError::SystemShutdown);
        }

        if (queue_.size() >= max_capacity_) {
            rejected_count_.fetch_add(1, std::memory_order_relaxed);
            return std::unexpected(LevelerError::QueueFull);
        }

        auto now = std::chrono::steady_clock::now();
        uint64_t task_id = next_task_id_++;
        queue_.push(Task{
            .id = task_id,
            .payload = std::move(payload),
            .enqueue_time = now,
            .deadline = now + ttl
        });

        cv_not_empty_.notify_one();
        return task_id;
    }

    // Отримання задачі пулом воркерів з урахуванням дедлайну та ліміту темпу
    std::optional<Task> dequeue() {
        while (true) {
            std::unique_lock lock(mutex_);
            cv_not_empty_.wait(lock, [this] {
                return !queue_.empty() || shutdown_;
            });

            if (queue_.empty() && shutdown_) {
                return std::nullopt;
            }

            Task task = std::move(queue_.front());
            queue_.pop();
            lock.unlock();

            // Перевірка дедлайну задачі
            if (std::chrono::steady_clock::now() > task.deadline) {
                expired_count_.fetch_add(1, std::memory_order_relaxed);
                continue; // Задача застаріла під час очікування в черзі
            }

            // Обмеження темпу звернень до захищеного бекенду
            rate_limiter_.consume();
            processed_count_.fetch_add(1, std::memory_order_relaxed);

            return task;
        }
    }

    void stop() {
        std::unique_lock lock(mutex_);
        shutdown_ = true;
        cv_not_empty_.notify_all();
    }

    size_t depth() const {
        std::unique_lock lock(mutex_);
        return queue_.size();
    }

    uint64_t processed() const { return processed_count_.load(std::memory_order_relaxed); }
    uint64_t rejected()  const { return rejected_count_.load(std::memory_order_relaxed); }
    uint64_t expired()   const { return expired_count_.load(std::memory_order_relaxed); }

private:
    const size_t max_capacity_;
    TokenBucket rate_limiter_;

    mutable std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    std::queue<Task> queue_;
    bool shutdown_{false};
    uint64_t next_task_id_{1};

    std::atomic<uint64_t> processed_count_{0};
    std::atomic<uint64_t> rejected_count_{0};
    std::atomic<uint64_t> expired_count_{0};
};

} // namespace resilience
```
:::

## Покроковий життєвий цикл задачі та поведінка під час сплеску

Щоб зрозуміти, як програма гарантує захист бекенду, простежимо шлях повідомлення на кожному кроці виконання:

1. **Фаза прийому (Enqueue):** Мережевий потік шлюзу отримує запит від клієнта і викликає `enqueue()`. Ця операція є критичною секцією мінімальної тривалості: вона захоплює м'ютекс лише на час перевірки лічильника `count` та копіювання дескриптора задачі в масив. Операція виконується за сталий час `O(1)` і займає менше мікросекунди. Якщо буфер заповнений, шлюз негайно повертає код помилки `LEVELER_QUEUE_FULL`, що транслюється у відповідь `HTTP 429 Too Many Requests`.
2. **Фаза очікування (Buffering):** Задача перебуває в кільцевому буфері. У цей період продюсер не утримує жодних мережевих з'єднань з базою даних, а операційна пам'ять системи захищена від неконтрольованого зростання.
3. **Фаза валідації актуальності (TTL Check):** Коли вільний воркер вилучає задачу з черги (`dequeue()`), він порівнює поточний монотонний час `clock_gettime(CLOCK_MONOTONIC)` з полем `deadline_ms`. Якщо під час пікового навантаження задача пролежала в черзі довше допустимого таймауту, вона негайно утилізується без здійснення важких звернень до бази даних.
4. **Фаза обмеження швидкості (Token Bucket Pacing):** Перед відправкою валідного запиту до бекенду потік воркера викликає `token_bucket_consume()`. Якщо ліміт 400 RPS вичерпано, воркер блокується на мікросекундній паузі, пропускаючи вперед лише дозволену кількість запитів за секунду.

## Розбір критичних інженерних пасток реалізації

При побудові демпфера навантаження в реальних високонавантажених сервісах виникають характерні проблеми низькорівневої синхронізації та розподілу ресурсів процесора:

### 1. Конкуренція за м'ютекс черги та хибне розділення кеш-ліній (False Sharing)

У базовій реалізації операції `enqueue` та `dequeue` використовують єдиний спільний м'ютекс. Коли десятки мережевих потоків намагаються одночасно виконати запис у чергу при 10 000 RPS, час очікування захоплення м'ютексу (*lock contention*) починає перевищувати корисний час виконання операції. 

Крім того, покажчики `head` та `tail` кільцевого буфера, якщо вони розташовані в сусідніх комірках пам'яті, потрапляють в одну й ту саму 64-байтну кеш-лінію процесора (*Cache Line*). Коли потік продюсера модифікує `tail`, кеш-лінія інвалідується в кеші L1/L2 ядра споживача, викликаючи так зване «тремтіння кешу» (*Cache Line Bouncing* за протоколом MESI).

Для усунення цього ефекту в промислових архітектурах застосовують вирівнювання покажчиків на межу кеш-лінії (`alignas(64)` у C++ або макроси вирівнювання в C) та використовують шардування черги на `N` незалежних підчерг (*Queue Sharding*) за хешем від ідентифікатора клієнта.

### 2. Точність таймерів та гранулярність сну в Token Bucket

Виклик системних функцій засинання (`usleep` у C або `std::this_thread::sleep_for` у C++) на операційних системах сімейства Linux та Windows має обмежену апаратну точність. Стандартний квант системного таймера ядра зазвичай становить від 1 до 4 мілісекунд (залежно від конфігурації `CONFIG_HZ` у ядрі Linux).

Якщо лімітер налаштований на високу частоту (наприклад, 4000 RPS, де інтервал між окремими токенами становить 0.25 мс), пряме засинання на кожному токені призведе до значного падіння реальної пропускної здатності, оскільки планувальник ОС не здатен прокидати потік частіше ніж раз на мілісекунду.

З цієї причини в промислових реалізаціях маркерний кошик підтримує роботу пачками (*token batching*): воркери захоплюють токени групами по 10–50 штук за одну операцію синхронізації, а поповнення кошика розраховується за реально минулим часом без потреби у високочастотних таймерних перериваннях.

### 3. Аварійний шторм дедлайнів (Deadline Cascades)

Якщо вхідний сплеск перевищив ємність черги і триває довше, ніж середній `TTL` задач, черга наповнюється протермінованими повідомленнями. Воркер, вичитуючи чергу, витрачає процесорні цикли на їхню відбраковку.

Якщо перевірку дедлайну робити після взяття токена в `TokenBucket`, воркер спалить цінний ліміт звернення до бази даних на задачу, яка взагалі не потребує виконання. Тому перевірка дедлайну в наведеному коді винесена **строго перед** викликом `rate_limiter.consume()`. Це гарантує, що жоден токен пропускної здатності захищеного бекенду не буде витрачений на мертву роботу.

### 4. Коректне завершення роботи (Graceful Shutdown)

Під час планового оновлення сервісу неприпустимо аварійно переривати потоки воркерів, оскільки повідомлення, що перебувають у процесі запису до бази даних, можуть залишити систему в неузгодженому стані.

Метод `stop()` (або `leveler_stop` у C) встановлює атомарний прапорець `shutdown = true` та надсилає групове сповіщення всім сплячим воркерам через виклик `pthread_cond_broadcast` (`cv_not_empty_.notify_all()`). Воркери прокидаються, послідовно вичитують залишок задач, що накопичилися в буфері, і лише після повного спорожнення черги коректно завершують своє виконання.
