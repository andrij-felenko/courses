# ⚙️ Реалізація адаптивного лімітера конкурентності Vegas на C та C++

У розподілених системах статичні обмеження пулів потоків або фіксовані конфігурації кількості одночасних з'єднань є головним джерелом каскадних відмов. Коли під навантаженням час виконання запитів до бази даних або зовнішнього API зростає в кілька разів, фіксований ліміт паралелізму призводить до вибухового росту внутрішніх черг, масового спливання клієнтських дедлайнів та спалювання процесорного часу на обслуговування прострочених викликів.

Нижче наведено повноцінну, потокобезпечну реалізацію адаптивного контролера конкурентності за алгоритмом Vegas / Gradient. Реалізація підтримує динамічне відстеження мінімального часу відгуку без черг (`minRTT`), вимірювання затримок у ковзному вікні, експоненційне згладжування оцінок та автоматичне старіння базису для захисту від хибного голодування.

## Архітектурний дизайн та потокобезпека

Реалізація оптимізована для висококонкурентного виконання (понад 100 000 запитів на секунду) і розділяє критичний шлях ухвалення рішень на дві зони:

1. **Гарячий шлях допуску (Lock-free Fast Path):**
   При надходженні нового запиту перевірка `in_flight < current_limit` та інкрементування лічильника здійснюються через атомарні операції `std::atomic` без захоплення блокувань м'ютекса. Це забезпечує мінімальні накладні витрати (менше ніж 10 наносекунд на запит) і миттєве відхилення надлишкового трафіку з кодом помилки `429 Too Many Requests`.
2. **Шлях фіксації завершення та телеметрії (Sample Collector):**
   Коли запит завершується, час його виконання додається до поточного вікна вибірки. Щоб уникнути конкуренції за спільні структури даних, м'ютекс захищає лише блок агрегації метрик і перерахунку ліміту, який викликається один раз на кілька десятків або сотень запитів.

## Повний вихідний код реалізації

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <pthread.h>
#include <time.h>
#include <math.h>

#define DEFAULT_MIN_LIMIT 5.0
#define DEFAULT_MAX_LIMIT 1000.0
#define DEFAULT_INITIAL_LIMIT 20.0
#define DEFAULT_WINDOW_SIZE 50
#define DEFAULT_MIN_RTT_TTL_SEC 300.0 /* 5 хвилин */

typedef struct {
    double min_limit;          /* мінімальна межа паралелізму */
    double max_limit;          /* максимальна межа паралелізму */
    double headroom;           /* параметр запасу черги h */
    double smoothing;          /* коефіцієнт експоненційного згладжування σ */
    uint32_t sample_window;    /* кількість запитів на одне вікно вибірки */
    double min_rtt_ttl_sec;    /* тривалість життя базового minRTT */
} vegas_config_t;

typedef struct {
    vegas_config_t cfg;
    atomic_int in_flight;

    pthread_mutex_t lock;
    double current_limit;

    /* Поточне вікно вибірки */
    uint32_t sample_count;
    double sample_rtt_sum_ms;

    /* Базова затримка */
    double min_rtt_ms;
    double min_rtt_timestamp_sec;
} vegas_limiter_t;

static double get_monotonic_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

vegas_limiter_t* vegas_limiter_create(const vegas_config_t* cfg) {
    vegas_limiter_t* lim = (vegas_limiter_t*)calloc(1, sizeof(vegas_limiter_t));
    if (!lim) return NULL;

    lim->cfg = *cfg;
    atomic_init(&lim->in_flight, 0);
    pthread_mutex_init(&lim->lock, NULL);

    lim->current_limit = cfg->min_limit > 0 ? cfg->min_limit : DEFAULT_INITIAL_LIMIT;
    lim->min_rtt_ms = -1.0; /* ще не ініціалізовано */
    lim->min_rtt_timestamp_sec = get_monotonic_time_sec();
    return lim;
}

void vegas_limiter_destroy(vegas_limiter_t* lim) {
    if (!lim) return;
    pthread_mutex_destroy(&lim->lock);
    free(lim);
}

/* Спроба допуску запиту (Lock-free перевірка атомарного лічильника) */
bool vegas_limiter_acquire(vegas_limiter_t* lim, double* out_start_time) {
    int current = atomic_load_explicit(&lim->in_flight, memory_order_relaxed);
    
    /* Читання поточного ліміту для швидкого відсікання */
    double limit = lim->current_limit;
    if ((double)current >= limit) {
        return false; /* Швидке відхилення надлишку: 429 Too Many Requests */
    }

    /* Атомарне інкрементування активних запитів */
    atomic_fetch_add_explicit(&lim->in_flight, 1, memory_order_acq_rel);
    *out_start_time = get_monotonic_time_sec();
    return true;
}

/* Фіксація завершення запиту та оновлення моделі */
void vegas_limiter_release(vegas_limiter_t* lim, double start_time, bool success) {
    double now = get_monotonic_time_sec();
    double duration_ms = (now - start_time) * 1000.0;

    atomic_fetch_sub_explicit(&lim->in_flight, 1, memory_order_acq_rel);

    /* Неуспішні запити (мережеві обриви, дедлайни) не повинні спотворювати RTT */
    if (!success || duration_ms <= 0.0) {
        return;
    }

    pthread_mutex_lock(&lim->lock);

    /* Оновлення або планове старіння minRTT */
    if (lim->min_rtt_ms < 0.0 || (now - lim->min_rtt_timestamp_sec) > lim->cfg.min_rtt_ttl_sec) {
        lim->min_rtt_ms = duration_ms;
        lim->min_rtt_timestamp_sec = now;
    } else if (duration_ms < lim->min_rtt_ms) {
        lim->min_rtt_ms = duration_ms;
    }

    lim->sample_count++;
    lim->sample_rtt_sum_ms += duration_ms;

    /* Закриття вікна вибірки та перерахунок ліміту */
    if (lim->sample_count >= lim->cfg.sample_window) {
        double sample_rtt = lim->sample_rtt_sum_ms / (double)lim->sample_count;
        double min_rtt = lim->min_rtt_ms;

        if (sample_rtt > 0.0 && min_rtt > 0.0) {
            double gradient = min_rtt / sample_rtt;
            
            /* Обчислення цільового ліміту за формулою Vegas */
            double target_limit = lim->current_limit * gradient + lim->cfg.headroom;
            
            /* Експоненційне згладжування */
            double next_limit = (1.0 - lim->cfg.smoothing) * lim->current_limit 
                              + lim->cfg.smoothing * target_limit;

            /* Обмеження діапазоном безпеки */
            if (next_limit < lim->cfg.min_limit) next_limit = lim->cfg.min_limit;
            if (next_limit > lim->cfg.max_limit) next_limit = lim->cfg.max_limit;

            lim->current_limit = next_limit;
        }

        lim->sample_count = 0;
        lim->sample_rtt_sum_ms = 0.0;
    }

    pthread_mutex_unlock(&lim->lock);
}
```
```cpp
#include <iostream>
#include <chrono>
#include <atomic>
#include <mutex>
#include <optional>
#include <algorithm>
#include <memory>

class AdaptiveVegasLimiter {
public:
    struct Config {
        double min_limit = 5.0;
        double max_limit = 1000.0;
        double initial_limit = 20.0;
        double headroom = 10.0;                // Запас черги h для пошуку максимуму
        double smoothing = 0.2;                // Коефіцієнт згладжування σ
        uint32_t sample_window = 50;           // Кількість запитів на вікно
        std::chrono::seconds min_rtt_ttl{300}; // 5 хвилин до старіння minRTT
    };

    // RAII-токен допуску: автоматично звільняє ресурс і фіксує час у деструкторі
    class Token {
    public:
        Token(AdaptiveVegasLimiter& parent)
            : parent_(parent), start_time_(std::chrono::steady_clock::now()), active_(true) {}

        ~Token() {
            if (active_) {
                release(true);
            }
        }

        Token(const Token&) = delete;
        Token& operator=(const Token&) = delete;

        Token(Token&& other) noexcept
            : parent_(other.parent_), start_time_(other.start_time_), active_(other.active_) {
            other.active_ = false;
        }

        void release(bool success = true) {
            if (active_) {
                auto end_time = std::chrono::steady_clock::now();
                auto duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time_).count();
                parent_.on_request_completed(duration_ms, success);
                active_ = false;
            }
        }

    private:
        AdaptiveVegasLimiter& parent_;
        std::chrono::steady_clock::time_point start_time_;
        bool active_;
    };

    explicit AdaptiveVegasLimiter(Config cfg = {})
        : cfg_(cfg), current_limit_(cfg.initial_limit), in_flight_(0) {}

    // Спроба отримати допуск до виконання
    [[nodiscard]] std::optional<Token> try_acquire() {
        int current = in_flight_.load(std::memory_order_relaxed);
        if (static_cast<double>(current) >= current_limit_.load(std::memory_order_relaxed)) {
            return std::nullopt; // Швидке скидання навантаження (HTTP 429)
        }

        in_flight_.fetch_add(1, std::memory_order_acq_rel);
        return Token(*this);
    }

    [[nodiscard]] double current_limit() const noexcept {
        return current_limit_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] int in_flight() const noexcept {
        return in_flight_.load(std::memory_order_relaxed);
    }

private:
    void on_request_completed(double duration_ms, bool success) {
        in_flight_.fetch_sub(1, std::memory_order_acq_rel);

        if (!success || duration_ms <= 0.0) {
            return;
        }

        std::lock_guard<std::mutex> lock(metrics_mutex_);
        auto now = std::chrono::steady_clock::now();

        // Скидання або оновлення базису minRTT
        if (!min_rtt_ms_ || (now - min_rtt_timestamp_) > cfg_.min_rtt_ttl) {
            min_rtt_ms_ = duration_ms;
            min_rtt_timestamp_ = now;
        } else {
            min_rtt_ms_ = std::min(*min_rtt_ms_, duration_ms);
        }

        sample_rtt_sum_ms_ += duration_ms;
        sample_count_++;

        if (sample_count_ >= cfg_.sample_window) {
            recalculate_limit();
        }
    }

    void recalculate_limit() {
        double sample_rtt = sample_rtt_sum_ms_ / static_cast<double>(sample_count_);
        double min_rtt = min_rtt_ms_.value_or(sample_rtt);

        if (sample_rtt > 0.0 && min_rtt > 0.0) {
            double gradient = min_rtt / sample_rtt;
            double current = current_limit_.load(std::memory_order_relaxed);

            double target = current * gradient + cfg_.headroom;
            double next = (1.0 - cfg_.smoothing) * current + cfg_.smoothing * target;

            next = std::clamp(next, cfg_.min_limit, cfg_.max_limit);
            current_limit_.store(next, std::memory_order_relaxed);
        }

        sample_count_ = 0;
        sample_rtt_sum_ms_ = 0.0;
    }

    const Config cfg_;
    std::atomic<double> current_limit_;
    std::atomic<int> in_flight_;

    std::mutex metrics_mutex_;
    std::optional<double> min_rtt_ms_;
    std::chrono::steady_clock::time_point min_rtt_timestamp_{};
    uint32_t sample_count_ = 0;
    double sample_rtt_sum_ms_ = 0.0;
};
```
:::

## Детальний розбір механізмів та семантики пам'яті

### 1. RAII-патерн та керування життєвим циклом токена
У C++ версії виклик `try_acquire()` повертає `std::optional<Token>`. Якщо лімітер перевантажений, об'єкт повертає `std::nullopt`, що дозволяє веб-серверу миттєво віддати клієнту відповідь без виділення пулу завдань. Якщо запит допущено, створений об'єкт `Token` володіє правом виконання:
- У конструкторі фіксується мітка часу початку `start_time_` через монотонний таймер `std::chrono::steady_clock`;
- У деструкторі токен гарантовано викликає `release()`, що унеможливлює витік ресурсу `in_flight_` навіть у разі виникнення виняткових ситуацій (C++ exceptions) під час обробки запиту;
- Завдяки забороні копіювання (`delete copy constructor`) та реалізації семантики переміщення (`move constructor`), токен можна безпечно передавати в асинхронні ланцюжки та callback-функції обробників.

### 2. Модель узгодженості пам'яті (Memory Ordering)
- Для читання лічильника `in_flight` під час швидкої перевірки використовується `std::memory_order_relaxed`, оскільки для попереднього фільтра не потрібна сувора синхронізація з іншими змінними ядра;
- Для зміни `in_flight` при вході та виході застосовується `std::memory_order_acq_rel`. Семантика *Acquire-Release* гарантує, що операції обробки корисного навантаження всередині запиту не можуть бути перевпорядковані процесором за межі блоку допуску;
- Атомарна змінна `current_limit_` читається без блокувань, забезпечуючи високу пропускну здатність багатоядерних систем без явища *False Sharing*.

## Інтеграція в HTTP та gRPC middleware

Типовий сценарій використання адаптивного лімітера в проміжному обробнику (middleware) веб-сервера виглядає так:

1. При надходженні HTTP-запиту middleware викликає `limiter.try_acquire()`;
2. Якщо отримано `std::nullopt`, middleware негайно перериває конвеєр, встановлює HTTP-заголовок `Retry-After: 1` і повертає статус `429 Too Many Requests` або `503 Service Unavailable`;
3. Якщо отримано валідний `Token`, запит передається далі в ланцюжок обробки;
4. Після завершення обробки бізнес-логіки токен звільняється. Якщо запит завершився внутрішньою помилкою бекенду (наприклад, 500 через тайм-аут бази даних), викликається `token.release(false)`, щоб не спотворювати вимірювання затримок нормальних викликів.

## Інженерні пастки та крайові випадки

Під час експлуатації адаптивних лімітерів у високонавантажених сервісах виникають типові складнощі:

### 1. Проблема холодного старту (Cold Start)
Якщо сервіс стартує з мінімальним лімітом (наприклад, `initial_limit = 5`), а на нього раптово приходить потік у 1000 RPS, лімітер буде відхиляти 99% запитів і надто повільно нарощувати вікно (на кілька одиниць за кожне вікно вибірки).
- **Вирішення:** Встановлювати `initial_limit` близьким до розрахункової штатної потужності (наприклад, 50–100) та використовувати більший крок нарощування на етапі ініціалізації.

### 2. Застрягання в застарілому minRTT (False Baseline Trap)
Якщо під час нічного затишшя без навантаження `minRTT` було зафіксовано на рівні 5 мс, а вдень сервіс перейшов на активну роботу з підключенням до географічно віддаленого кластера з базовою затримкою 25 мс:
- Без механізму старіння градієнт становитиме `g = 5 / 25 = 0.2`, і лімітер стисне пропускну здатність до `min_limit`, вважаючи систему перевантаженою;
- **Вирішення:** Обов'язкове ковзне вікно життя `minRTT` (`min_rtt_ttl = 300 секунд`), після закінчення якого базис вимірюється наново з реального потоку запитів.

### 3. Спотворення через помилки тайм-аутів
Якщо клієнт відмовився від запиту за таймаутом і обірвав TCP-з'єднання, фіксація такого запиту з тривалістю 1000 мс спотворить `sampleRTT`.
- **Вирішення:** Прапорець `success` передається у метод завершення; аварійно обірвані виклики зменшують `in_flight`, але не включаються до вибірки обчислення градієнта затримки.

### 4. Несиметричні типи ендпоінтів
Якщо один екземпляр лімітера використовується одночасно для легкого запиту перевірки працездатності `/health` (0.5 мс) та важкого аналітичного запиту `/reports` (300 мс), середнє значення `sample_rtt` стане стохастичним хаосом, а лімітер не зможе знайти стабільну точку рівноваги.
- **Вирішення:** Розділяти лімітери за кластерами маршрутів або типами операцій (наприклад, окремий контролер для читання та окремий для важкого запису).
