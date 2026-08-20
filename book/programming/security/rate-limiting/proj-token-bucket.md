# ⚙️ Високопродуктивна реалізація Token Bucket та GCRA на C та C++

Ця практична вставка містить готові до використання у промислових системах багатопотокові реалізації алгоритмів обмеження швидкості Token Bucket, Leaky Bucket та GCRA на мовах C та C++. Вона розбирає техніку «лінивого поповнення» (lazy refill), що усуває потребу у фонових таймерах, реалізацію без блокувань (lock-free) на базі атомарних операцій CAS, заміну чисел із плаваючою комою на фіксовану цілочисельну арифметику, а також захист від переповнення при роботі з наносекундними монотонними годинниками.

---

## 1. Концепція «лінивого поповнення» (Lazy Refill)

Наївна реалізація Token Bucket часто створює окремий фоновий потік чи періодичний таймер, який щосекунди або щомілісекунди інкрементує лічильник токенів. Для системи з сотнями тисяч підключених клієнтів це призводить до катастрофічного накладного навантаження: мільйони операцій запису в пам'ять щомиті навіть для абсолютно пасивних з'єднань, що марно споживає ресурси процесора та руйнує кеш-лінії L1/L2.

Промисловий підхід полягає у **лінивому математичному поповненні** безпосередньо в момент обробки вхідного запиту:
1. Для кожного клієнта зберігаються лише два поля: поточний залишок токенів `tokens` та часова мітка останнього звернення `last_refill_time`.
2. Коли надходить новий запит, обчислюється фізичний час, що минув від попереднього візиту: `Δt = t_now - last_refill_time`.
3. До балансу додаються токени, які мали б надійти за цей інтервал: `tokens = min(capacity, tokens + Δt · refill_rate)`.
4. Часова мітка оновлюється `last_refill_time = t_now`, і якщо `tokens ≥ 1.0`, запит пропускається, а баланс декрементується.

Такий підхід має нульову вартість для неактивних сесій (O(0) фонової роботи) та виконується за сталий час O(1) під час звернення.

---

## 2. Реалізація Token Bucket з м'ютексом

Нижче наведено потокобезпечну реалізацію Token Bucket із мікросекундною точністю. М'ютекс гарантує ізоляцію стану між паралельними робочими потоками сервера.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>

typedef struct {
    double capacity;         /* Максимальна місткість (токени) */
    double tokens;           /* Поточний залишок токенів */
    double refill_rate;      /* Токенів на секунду */
    uint64_t last_refill_ns; /* Час останнього поповнення (наносекунди) */
    pthread_mutex_t lock;    /* М'ютекс захисту стану */
} token_bucket_t;

/* Отримання монотонного часу в наносекундах */
static uint64_t get_monotonic_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

void token_bucket_init(token_bucket_t *tb, double capacity, double refill_rate) {
    tb->capacity = capacity;
    tb->tokens = capacity;
    tb->refill_rate = refill_rate;
    tb->last_refill_ns = get_monotonic_ns();
    pthread_mutex_init(&tb->lock, NULL);
}

void token_bucket_destroy(token_bucket_t *tb) {
    pthread_mutex_destroy(&tb->lock);
}

bool token_bucket_try_consume(token_bucket_t *tb, double tokens_to_consume) {
    pthread_mutex_lock(&tb->lock);

    uint64_t now_ns = get_monotonic_ns();
    uint64_t elapsed_ns = now_ns - tb->last_refill_ns;
    tb->last_refill_ns = now_ns;

    /* Поповнення токенів за минулий інтервал часу */
    double delta_sec = (double)elapsed_ns / 1000000000.0;
    tb->tokens += delta_sec * tb->refill_rate;
    if (tb->tokens > tb->capacity) {
        tb->tokens = tb->capacity;
    }

    bool allowed = false;
    if (tb->tokens >= tokens_to_consume) {
        tb->tokens -= tokens_to_consume;
        allowed = true;
    }

    pthread_mutex_unlock(&tb->lock);
    return allowed;
}
```
```cpp
#include <chrono>
#include <mutex>
#include <algorithm>
#include <cstdint>

class TokenBucket {
public:
    TokenBucket(double capacity, double refill_rate_per_sec)
        : capacity_(capacity),
          tokens_(capacity),
          refill_rate_(refill_rate_per_sec),
          last_refill_tp_(std::chrono::steady_clock::now()) {}

    bool try_consume(double tokens_to_consume = 1.0) {
        std::lock_guard<std::mutex> lock(mutex_);

        auto now = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed = now - last_refill_tp_;
        last_refill_tp_ = now;

        // Поповнення токенів
        tokens_ = std::min(capacity_, tokens_ + elapsed.count() * refill_rate_);

        if (tokens_ >= tokens_to_consume) {
            tokens_ -= tokens_to_consume;
            return true;
        }

        return false;
    }

private:
    const double capacity_;
    const double refill_rate_;
    double tokens_;
    std::chrono::steady_clock::time_point last_refill_tp_;
    std::mutex mutex_;
};
```
:::

---

## 3. Високошвидкісний Lock-Free алгоритм GCRA на атомарних операціях

У високонавантажених зворотних проксі-серверах (reverse proxies) та мережевих шлюзах блокування на м'ютексах створюють відчутні затримки через конфлікти між ядрами процесора (англ. *mutex lock contention*). Оскільки алгоритм GCRA зводиться до збереження єдиної часової мітки `TAT` (Theoretical Arrival Time), його можна реалізувати без жодних блокувань за допомогою атомарного циклу `compare_exchange_weak` (CAS).

Семантика пам'яті:
- `atomic_load` із `memory_order_relaxed` виконує швидке читання поточного значення `TAT`.
- `atomic_compare_exchange_weak` із `memory_order_acq_rel` гарантує строгу синхронізацію: усі попередні операції запису стають видимими для інших ядер у момент успішного оновлення.
- Використання слабкої форми CAS (`compare_exchange_weak`) є значно продуктивнішим за сильну на архітектурах ARM та RISC-V завдяки зменшенню накладних витрат інструкцій LL/SC (Load-Link / Store-Conditional).

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <time.h>

typedef struct {
    uint64_t emission_interval_ns; /* T = 1 / rate (наносекунди) */
    uint64_t burst_tolerance_ns;    /* tau (наносекунди) */
    _Atomic uint64_t tat_ns;        /* Теоретичний час прибуття (атомарний) */
} gcra_limiter_t;

static uint64_t gcra_get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

void gcra_init(gcra_limiter_t *limiter, uint64_t rate_per_sec, uint64_t burst_capacity) {
    limiter->emission_interval_ns = 1000000000ULL / rate_per_sec;
    limiter->burst_tolerance_ns = (burst_capacity - 1) * limiter->emission_interval_ns;
    atomic_init(&limiter->tat_ns, 0);
}

bool gcra_try_acquire(gcra_limiter_t *limiter) {
    uint64_t now = gcra_get_time_ns();
    uint64_t current_tat = atomic_load_explicit(&limiter->tat_ns, memory_order_relaxed);

    while (1) {
        /* Якщо прибуття раніше, ніж TAT - burst_tolerance: відхилити */
        if (current_tat > now + limiter->burst_tolerance_ns) {
            return false;
        }

        /* Новий очікуваний час прибуття */
        uint64_t base = (now > current_tat) ? now : current_tat;
        uint64_t next_tat = base + limiter->emission_interval_ns;

        /* Атомарна спроба зафіксувати новий TAT */
        if (atomic_compare_exchange_weak_explicit(
                &limiter->tat_ns,
                &current_tat,
                next_tat,
                memory_order_acq_rel,
                memory_order_relaxed)) {
            return true;
        }
        /* При колізії цикл повторюється з оновленим current_tat */
    }
}
```
```cpp
#include <atomic>
#include <chrono>
#include <cstdint>
#include <algorithm>

class LockFreeGcraLimiter {
public:
    LockFreeGcraLimiter(uint64_t rate_per_sec, uint64_t burst_capacity)
        : emission_interval_ns_(1'000'000'000ULL / rate_per_sec),
          burst_tolerance_ns_((burst_capacity - 1) * emission_interval_ns_),
          tat_ns_(0) {}

    bool try_acquire() {
        uint64_t now = current_time_ns();
        uint64_t current_tat = tat_ns_.load(std::memory_order_relaxed);

        while (true) {
            // Перевірка, чи не перевищує запит допустимий ліміт сплеску
            if (current_tat > now + burst_tolerance_ns_) {
                return false;
            }

            uint64_t base = std::max(now, current_tat);
            uint64_t next_tat = base + emission_interval_ns_;

            if (tat_ns_.compare_exchange_weak(
                    current_tat,
                    next_tat,
                    std::memory_order_acq_rel,
                    std::memory_order_relaxed)) {
                return true;
            }
        }
    }

private:
    static uint64_t current_time_ns() {
        auto now = std::chrono::steady_clock::now().time_since_epoch();
        return std::chrono::duration_cast<std::chrono::nanoseconds>(now).count();
    }

    const uint64_t emission_interval_ns_;
    const uint64_t burst_tolerance_ns_;
    std::atomic<uint64_t> tat_ns_;
};
```
:::

---

## 4. Реалізація черги Leaky Bucket для Traffic Shaping

Якщо інженерна задача вимагає не просто відхиляти запити, а вирівнювати їхній потік перед зверненням до повільної сторонньої системи (наприклад, банківського шлюзу з лімітом 10 транзакцій на секунду), використовується черга Leaky Bucket із кільцевим буфером.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

typedef struct {
    int id;
    void *payload;
} request_item_t;

typedef struct {
    request_item_t *buffer;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} leaky_queue_t;

void leaky_queue_init(leaky_queue_t *q, size_t capacity) {
    q->buffer = (request_item_t *)malloc(sizeof(request_item_t) * capacity);
    q->capacity = capacity;
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

bool leaky_queue_push(leaky_queue_t *q, request_item_t item) {
    pthread_mutex_lock(&q->lock);
    if (q->count >= q->capacity) {
        pthread_mutex_unlock(&q->lock);
        return false; /* Переповнення: скидання запиту */
    }
    q->buffer[q->tail] = item;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

request_item_t leaky_queue_pop_rate_limited(leaky_queue_t *q, uint32_t interval_us) {
    pthread_mutex_lock(&q->lock);
    while (q->count == 0) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }
    request_item_t item = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);

    /* Шейпінг: примусова затримка між обробкою елементів */
    usleep(interval_us);
    return item;
}

void leaky_queue_destroy(leaky_queue_t *q) {
    free(q->buffer);
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);
}
```
```cpp
#include <queue>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
#include <optional>

template <typename T>
class LeakyBucketQueue {
public:
    explicit LeakyBucketQueue(size_t capacity, std::chrono::microseconds leak_interval)
        : capacity_(capacity), leak_interval_(leak_interval), stopped_(false) {}

    bool try_push(T item) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.size() >= capacity_) {
            return false; // Черга переповнена
        }
        queue_.push(std::move(item));
        cv_not_empty_.notify_one();
        return true;
    }

    std::optional<T> pop_shaped() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_empty_.wait(lock, [this]() { return !queue_.empty() || stopped_; });

        if (stopped_ && queue_.empty()) {
            return std::nullopt;
        }

        T item = std::move(queue_.front());
        queue_.pop();
        lock.unlock();

        // Шейпінг: фіксований темп видачі завдань
        std::this_thread::sleep_for(leak_interval_);
        return item;
    }

    void stop() {
        std::lock_guard<std::mutex> lock(mutex_);
        stopped_ = true;
        cv_not_empty_.notify_all();
    }

private:
    const size_t capacity_;
    const std::chrono::microseconds leak_interval_;
    std::queue<T> queue_;
    std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    bool stopped_;
};
```
:::

---

## 5. Покроковий розбір конкуренції потоків та стратегії відступу

Розглянемо випадок, коли 16 робочих потоків вебсервера одночасно отримують запити від одного й того самого ідентифікатора клієнта в одну й ту саму мікросекунду.

Послідовність подій у lock-free реалізації GCRA:
1. **Одночасне читання:** Усі 16 потоків одночасно зчитують однакове значення `current_tat = 1000000000` через `atomic_load_explicit`.
2. **Перевірка ліміту:** Кожен потік переконується, що `current_tat ≤ now + burst_tolerance_ns`.
3. **Обчислення цільового стану:** Кожен потік розраховує одне й те саме значення `next_tat = current_tat + emission_interval_ns = 1100000000`.
4. **Конкуренція за CAS:** Лише один випадковий потік першим виконає інструкцію `atomic_compare_exchange_weak`. Його операція повертає `true`, а комірка пам'яті `tat_ns` набуває значення `1100000000`.
5. **Повторна спроба решти потоків:** Решта 15 потоків отримують `false` від CAS. Слабкий CAS автоматично перезаписує локальну змінну `current_tat` свіжим значенням з пам'яті (`1100000000`).
6. **Ітерація:** Потоки заходять на друге коло циклу `while(1)`. Другий потік успішно збільшує `tat_ns` до `1200000000`, третій — до `1300000000`, і так далі.
7. **Спрацювання відсікання:** Якщо сумарний сплеск перевищує `burst_tolerance_ns`, черговий потік на кроці (2) побачить `current_tat > now + burst_tolerance_ns` і миттєво вийде з циклу, повернувши `false` без виконання запису в пам'ять.

Завдяки відсутності системних викликів блокування операційної системи (futex у Linux), цей алгоритм обробляє десятки мільйонів перевірок на секунду на одному ядрі процесора.

---

## 6. Пастки реалізації та крайові випадки

1. **Вибір годинника (Monotonic vs Realtime):**
   Використання системного астрономічного часу (`CLOCK_REALTIME` або `std::chrono::system_clock`) є критичною вразливістю. Якщо демон NTP здійснить стрибок часу назад (leap second або синхронізація з еталоном), різниця `now - last_refill` стане від'ємною або спричинить переповнення беззнакового типу, заблокувавши доступ клієнта на дні або роки. Слід використовувати **виключно монотонні таймери** (`CLOCK_MONOTONIC` у C, `std::chrono::steady_clock` у C++), значення яких монотонно зростають і не залежать від корекцій системного календаря.

2. **Переповнення при множенні (Integer Overflow):**
   При розрахунку часу в наносекундах `uint64_t` переповнюється лише через 584 роки безперервної роботи ОС. Проте вираз `(burst_capacity - 1) * emission_interval_ns` може спричинити переповнення під час ініціалізації, якщо користувач вказав екстремально малу швидкість (наприклад, 1 запит на тиждень). Слід перевіряти вхідні параметри на переповнення до збереження у структури.

3. **Цілочисельна арифметика проти чисел із плаваючою комою:**
   Хоча тип `double` є інтуїтивним для поповнення токенів, він має дві серйозні вади: операції з `double` не підтримуються нативними атомарними інструкціями CAS на більшості архітектур і можуть давати мікропохибки накопичення через специфіку округлення IEEE-754. У системах критичного рівня перевагу віддають цілочисельному GCRA або масштабованій цілочисельній фіксованій комі (Fixed Point), де 1 токен представляється як `1 000 000` дискретних одиниць.

4. **Очищення сплячих ключів у пам'яті:**
   Якщо лімітер створюється для кожної унікальної IP-адреси, у відкритому Інтернеті зловмисник зі сфальсифікованих адрес (IP Spoofing) може змусити сервер виділити мільйони структур, вичерпавши оперативну пам'ять (RAM Exhaustion). Промислові реалізації завжди обмежують розмір хеш-таблиці алгоритмом LRU (Least Recently Used) або встановлюють жорсткий час життя (TTL) для записів.
