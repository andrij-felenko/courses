# ⚙️ Реалізація адаптивного контролера допуску на основі градієнта затримки

Статичні ліміти кількості одночасних запитів ламаються при першій зміні умов: якщо внутрішня база даних сповільнилася на 20%, фіксований ліміт у 100 з'єднань миттєво перетворюється на гігантську чергу очікування. Замість статичного конфігурування надійні системи застосовують алгоритми динамічного пошуку пропускної здатності, які безперервно підлаштовують допустимий паралелізм під поточну затримку системи.

Тут розроблено повнофункціональний контролер допуску, який реалізує алгоритм класу Vegas/Gradient, контролює активний паралелізм за допомогою атомарних операцій без блокувань, перевіряє час життя завдань у черзі та підтримує багаторівневе скидання навантаження за пріоритетами.

## 1. Постановка задачі та алгоритмічна модель

Розподілений сервіс обробляє неоднорідний потік запитів. Коли внутрішні залежності (сховища даних, сторонні API) сповільнюються, час обробки кожного виклику зростає. Якщо тримати кількість одночасно виконуваних запитів незмінною, внутрішні черги завдань роздуваються, а затримка перевищує клієнтські таймаути.

Контролер допуску має розв'язувати такі задачі:
1. **Облік активних завдань:** Атомарно відстежувати кількість запитів, які перебувають у процесі виконання (`in_flight`);
2. **Оцінка базової швидкості:** Вимірювати мінімальну затримку (`min_rtt`) у ненавантаженому стані як фізичну базову межу продуктивності сервісу;
3. **Згладжування поточної затримки:** Обчислювати експоненційне ковзне середнє (`smoothed_rtt`) для останніх завершених запитів;
4. **Адаптація ліміту за градієнтом:** Розраховувати відношення `gradient = min_rtt / smoothed_rtt` та оновлювати допустимий ліміт паралелізму за формулою:
   ```
   limit_new = limit_curr · gradient + headroom
   ```
   де `headroom` (запас зондування) дозволяє плавно збільшувати ліміт, коли з'являється вільний ресурс;
5. **Скидання за пріоритетами:** При наближенні до ліміту відсікати низькопріоритетні та фонові запити, резервуючи ємність для критичних операцій;
6. **Контроль часу в черзі (Sojourn Time Gate):** Миттєво відхиляти запити, чий дедлайн уже сплив під час очікування в черзі.

## 2. Архітектура та життєвий цикл запиту

Контролер допуску взаємодіє з сервісом через патерн видачі дозволів (Permit). Кожен запит перед початком виконання зобов'язаний отримати токен допуску. Якщо токен видано, запит виконує бізнес-логіку; після завершення токен автоматично повертається контролеру разом із виміряною тривалістю операції.

```
[Вхідний запит] 
       │
       ▼
try_admit(priority, deadline)
  ├── 1. Перевірка дедлайну: (now >= deadline) ──► [ВІДХИЛЕНО: TIMEOUT]
  ├── 2. Перевірка пріоритету: (in_flight >= 0.8·limit) ──► [ВІДХИЛЕНО: SHED]
  └── 3. Атомарний CAS: (in_flight < limit)
       │
       ├─► [УСПІХ: Видано Permit] ──► Виконання бізнес-логіки
       │                                     │
       │                                     ▼
       │                               Деструктор ~Permit()
       │                                     │
       │                                     ▼
       │                               release(duration)
       │                                     │
       │                                     ▼
       │                               Оновлення min_rtt, smoothed_rtt та ліміту
       │
       └─► [ВІДХИЛЕНО: OVERLOAD] ──► Повернення 503 Service Unavailable (0 CPU)
```

## 3. Реалізація мовами C та C++

У реалізації на мові C застосовано стандартні засоби POSIX (`pthread_mutex_t`, `clock_gettime`) та атомарні типи C11 (`stdatomic.h`). Реалізація на C++20 використовує ідіоматичний підхід RAII: об'єкт `Permit` захоплює слот у конструкторі та гарантовано повертає його в деструкторі, унеможливлюючи витоки ресурсів при виникненні винятків.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <time.h>
#include <math.h>
#include <pthread.h>

typedef enum {
    PRIO_LOW    = 0,
    PRIO_NORMAL = 1,
    PRIO_HIGH   = 2
} RequestPriority;

typedef struct {
    atomic_int in_flight;
    atomic_int limit;
    int min_limit;
    int max_limit;
    
    double min_rtt_ms;
    double smoothed_rtt_ms;
    double smoothing_factor;
    double headroom;
    
    pthread_mutex_t metrics_lock;
} AdmissionController;

void admission_init(AdmissionController* ac, int min_limit, int max_limit) {
    atomic_init(&ac->in_flight, 0);
    atomic_init(&ac->limit, min_limit);
    ac->min_limit = min_limit;
    ac->max_limit = max_limit;
    ac->min_rtt_ms = 0.0;
    ac->smoothed_rtt_ms = 0.0;
    ac->smoothing_factor = 0.1;
    ac->headroom = 1.0;
    pthread_mutex_init(&ac->metrics_lock, NULL);
}

void admission_destroy(AdmissionController* ac) {
    pthread_mutex_destroy(&ac->metrics_lock);
}

int64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + (ts.tv_nsec / 1000000);
}

bool admission_try_acquire(AdmissionController* ac, RequestPriority prio, int64_t deadline_ms) {
    int64_t now = current_time_ms();
    
    /* 1. Перевірка дедлайну: якщо запит уже прострочений у черзі, відхиляємо */
    if (deadline_ms > 0 && now >= deadline_ms) {
        return false;
    }
    
    int cur_limit = atomic_load_explicit(&ac->limit, memory_order_relaxed);
    int current_in_flight = atomic_load_explicit(&ac->in_flight, memory_order_relaxed);
    
    /* 2. Пріоритетне скидання: низький пріоритет відсікається при 80% ліміту */
    if (prio == PRIO_LOW && current_in_flight >= (int)(cur_limit * 0.8)) {
        return false;
    }
    if (prio == PRIO_NORMAL && current_in_flight >= (int)(cur_limit * 0.95)) {
        return false;
    }
    
    /* 3. Атомарне захоплення слота за допомогою CAS-циклу */
    while (current_in_flight < cur_limit) {
        if (atomic_compare_exchange_weak_explicit(&ac->in_flight, 
                                                  &current_in_flight, 
                                                  current_in_flight + 1,
                                                  memory_order_acquire,
                                                  memory_order_relaxed)) {
            return true;
        }
    }
    
    return false;
}

void admission_release(AdmissionController* ac, double duration_ms) {
    atomic_fetch_sub_explicit(&ac->in_flight, 1, memory_order_release);
    
    pthread_mutex_lock(&ac->metrics_lock);
    
    /* Оновлення мінімального базового часу відгуку */
    if (ac->min_rtt_ms <= 0.0 || duration_ms < ac->min_rtt_ms) {
        ac->min_rtt_ms = duration_ms;
    }
    
    /* Експоненційне згладжування поточної затримки (EWMA) */
    if (ac->smoothed_rtt_ms <= 0.0) {
        ac->smoothed_rtt_ms = duration_ms;
    } else {
        ac->smoothed_rtt_ms = (1.0 - ac->smoothing_factor) * ac->smoothed_rtt_ms 
                            + ac->smoothing_factor * duration_ms;
    }
    
    /* Розрахунок градієнта та оновлення ліміту */
    if (ac->min_rtt_ms > 0.0 && ac->smoothed_rtt_ms > 0.0) {
        double gradient = ac->min_rtt_ms / ac->smoothed_rtt_ms;
        if (gradient > 1.0) gradient = 1.0;
        
        int cur_limit = atomic_load_explicit(&ac->limit, memory_order_relaxed);
        double new_limit = (double)cur_limit * gradient + ac->headroom;
        
        int target = (int)round(new_limit);
        if (target < ac->min_limit) target = ac->min_limit;
        if (target > ac->max_limit) target = ac->max_limit;
        
        atomic_store_explicit(&ac->limit, target, memory_order_relaxed);
    }
    
    pthread_mutex_unlock(&ac->metrics_lock);
}
```
```cpp
#include <iostream>
#include <atomic>
#include <chrono>
#include <mutex>
#include <algorithm>
#include <cmath>
#include <optional>

enum class RequestPriority {
    Low    = 0,
    Normal = 1,
    High   = 2
};

class AdaptiveAdmissionController {
public:
    struct Config {
        int min_limit = 10;
        int max_limit = 500;
        double smoothing_factor = 0.1;
        double headroom = 1.0;
    };

    explicit AdaptiveAdmissionController(Config config)
        : config_(config),
          limit_(config.min_limit),
          in_flight_(0),
          min_rtt_(std::chrono::duration<double, std::milli>::zero()),
          smoothed_rtt_(std::chrono::duration<double, std::milli>::zero()) {}

    class Permit {
    public:
        Permit(AdaptiveAdmissionController& parent, std::chrono::steady_clock::time_point start)
            : parent_(&parent), start_time_(start) {}
        
        ~Permit() {
            if (parent_) {
                auto duration = std::chrono::duration<double, std::milli>(
                    std::chrono::steady_clock::now() - start_time_
                );
                parent_->release(duration.count());
            }
        }
        
        Permit(const Permit&) = delete;
        Permit& operator=(const Permit&) = delete;
        
        Permit(Permit&& other) noexcept 
            : parent_(other.parent_), start_time_(other.start_time_) {
            other.parent_ = nullptr;
        }

        Permit& operator=(Permit&& other) noexcept {
            if (this != &other) {
                if (parent_) {
                    auto duration = std::chrono::duration<double, std::milli>(
                        std::chrono::steady_clock::now() - start_time_
                    );
                    parent_->release(duration.count());
                }
                parent_ = other.parent_;
                start_time_ = other.start_time_;
                other.parent_ = nullptr;
            }
            return *this;
        }

    private:
        AdaptiveAdmissionController* parent_;
        std::chrono::steady_clock::time_point start_time_;
    };

    [[nodiscard]] std::optional<Permit> try_acquire(
        RequestPriority prio, 
        std::optional<std::chrono::steady_clock::time_point> deadline = std::nullopt) 
    {
        const auto now = std::chrono::steady_clock::now();
        
        // 1. Перевірка дедлайну
        if (deadline && now >= *deadline) {
            return std::nullopt;
        }

        const int cur_limit = limit_.load(std::memory_order_relaxed);
        int cur_in_flight = in_flight_.load(std::memory_order_relaxed);

        // 2. Пріоритетне скидання навантаження
        if (prio == RequestPriority::Low && cur_in_flight >= static_cast<int>(cur_limit * 0.80)) {
            return std::nullopt;
        }
        if (prio == RequestPriority::Normal && cur_in_flight >= static_cast<int>(cur_limit * 0.95)) {
            return std::nullopt;
        }

        // 3. Атомарне захоплення слота (Lock-free CAS)
        while (cur_in_flight < cur_limit) {
            if (in_flight_.compare_exchange_weak(cur_in_flight, cur_in_flight + 1,
                                                 std::memory_order_acquire,
                                                 std::memory_order_relaxed)) {
                return Permit(*this, now);
            }
        }

        return std::nullopt;
    }

    [[nodiscard]] int current_limit() const noexcept {
        return limit_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] int active_in_flight() const noexcept {
        return in_flight_.load(std::memory_order_relaxed);
    }

private:
    void release(double duration_ms) {
        in_flight_.fetch_sub(1, std::memory_order_release);

        std::lock_guard<std::mutex> lock(metrics_mutex_);

        // Оновлення мінімального базового часу відгуку
        if (min_rtt_.count() <= 0.0 || duration_ms < min_rtt_.count()) {
            min_rtt_ = std::chrono::duration<double, std::milli>(duration_ms);
        }

        // Експоненційне згладжування затримки (EWMA)
        if (smoothed_rtt_.count() <= 0.0) {
            smoothed_rtt_ = std::chrono::duration<double, std::milli>(duration_ms);
        } else {
            smoothed_rtt_ = std::chrono::duration<double, std::milli>(
                (1.0 - config_.smoothing_factor) * smoothed_rtt_.count() +
                config_.smoothing_factor * duration_ms
            );
        }

        // Розрахунок градієнта та оновлення ліміту
        if (min_rtt_.count() > 0.0 && smoothed_rtt_.count() > 0.0) {
            double gradient = min_rtt_.count() / smoothed_rtt_.count();
            gradient = std::min(gradient, 1.0);

            const int cur_limit = limit_.load(std::memory_order_relaxed);
            const double new_limit = static_cast<double>(cur_limit) * gradient + config_.headroom;

            int target = static_cast<int>(std::round(new_limit));
            target = std::clamp(target, config_.min_limit, config_.max_limit);

            limit_.store(target, std::memory_order_relaxed);
        }
    }

    Config config_;
    std::atomic<int> limit_;
    std::atomic<int> in_flight_;
    
    std::mutex metrics_mutex_;
    std::chrono::duration<double, std::milli> min_rtt_;
    std::chrono::duration<double, std::milli> smoothed_rtt_;
};
```
:::

## 4. Аналіз моделі пам'яті та безпеки багатопоточності

У наведеній реалізації критичний шлях ухвалення рішення `try_acquire` спроектовано як повністю вільний від блокувань (Lock-Free).

Використання атомарного циклу `compare_exchange_weak` із семантикою `std::memory_order_acquire` гарантує, що операція збільшення лічильника `in_flight` синхронізується з операціями вивільнення слотів `std::memory_order_release` в інших потоках. Вибір слабкої форми порівняння зіставляння (Weak CAS) обумовлений тим, що на архітектурах ARM та PowerPC інструкція `compare_exchange_weak` генерує простішу послідовність асемблерних команд (LL/SC — Load-Linked / Store-Conditional). Спонтанні невдачі (Spurious Failures) автоматично обробляються зовнішнім циклом `while`, що забезпечує максимальну пропускну здатність процесорних кешів.

Оновлення метрик у методі `release` винесено під захист м'ютекса `metrics_mutex_`. Оскільки обчислення градієнта та згладжування затримки відбувається після фактичного завершення запиту, короткочасне блокування не сповільнює вхідні клієнтські потоки. Для систем із надвисоким навантаженням (понад 100 000 RPS) метрики агрегують у потоко-локальних буферах (Thread-Local Storage) та скидають у глобальний стан батчами один раз на кілька мілісекунд.

## 5. Практичні пастки та граничні випадки експлуатації

Під час впровадження адаптивного контролера допуску у високопродуктивні продакшен-середовища необхідно враховувати кілька неочевидних крайових випадків:

**1. Проблема «застрягання» мінімального RTT (`min_rtt` drift):**
Якщо під час холодного старту або нічного затишшя сервіс зафіксував аномально швидкий виклик (наприклад, 2 мс через 100% потрапляння в кеш), а вдень структура запитів змінилася на складнішу (середній час 20 мс), градієнт `2 / 20 = 0.1` стисне ліміт до мінімального значення `min_limit` і заблокує систему.
*Рішення:* Значення `min_rtt` не повинно бути вічним. Його скидають за таймером кожні 15–30 хвилин або обчислюють як ковзний мінімум у вікні останніх 1000 запитів.

**2. Холодний старт і надмірний `headroom`:**
Якщо сервіс тривалий час працює з мінімальним трафіком, параметр `headroom` щосекунди додаватиме одиницю до ліміту, поступово роздуваючи його до значення `max_limit`. Коли прийде раптовий шторм трафіку, контролер пропустить занадто багато запитів до того, як зворотний зв'язок зафіксує зростання затримки.
*Рішення:* Ліміт `max_limit` має жорстко відповідати фізичним обмеженням пулу з'єднань із базою даних або обсягу вільної пам'яті контейнера.

**3. Вплив фонових пауз збирача сміття (GC Stalls):**
У середовищах із керованими середовищами виконання (Java, Go, Node.js) короткочасна пауза GC на 50 мілісекунд призводить до різкого стрибка `smoothed_rtt`. Якщо коефіцієнт згладжування `smoothing_factor` вибрано занадто великим (наприклад, 0.5 замість 0.05–0.1), контролер різко стисне ліміт, відкинувши нормальні запити. Експоненційне згладжування фільтрує поодинокі викиди, реагуючи лише на стійку тенденцію зростання черг.
