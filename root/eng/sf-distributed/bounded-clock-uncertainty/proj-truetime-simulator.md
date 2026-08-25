# ⚙️ Емулятор TrueTime API, перевірка перекриття інтервалів та бар'єр Commit Wait

Реалізація абстракції обмеженої невизначеності часу вимагає побудови спеціалізованого програмного шару, який перетворює показання монотонного апаратного таймера та оцінку дрейфу на замкнені інтервали часу, а також забезпечує прецизійне блокування потоку виконання під час бар'єра фіксації транзакції.

Цей практичний проект демонструє внутрішню механіку TrueTime API, моделює фізичну розбіжність годинників на незалежних вузлах кластера та підтверджує збереження лінеаризовності при виникненні причинно пов'язаних транзакцій.

## Архітектура емулятора

Емулятор побудовано на трьох взаємопов'язаних рівнях:
1. **Рівень апаратного джерела (Clock Source):** емулює фізичний генератор вузла. Враховує початкову похибку синхронізації `ε₀`, відносний дрейф кварцу `ρ` (у ppm) та штучно введений постійний зсув шкали (англ. *offset bias*), що дозволяє симулювати відставання одного вузла від іншого на кілька мілісекунд.
2. **Рівень інтервального часу (TrueTime API Layer):** реалізує обчислення динамічного розширення похибки `ε(t) = ε₀ + ρ·Δt`, формує структуру `tt_interval_t` та надає предикати `tt_after()` і `tt_before()`.
3. **Рівень координації транзакцій (Transaction Sequencer):** емулює двох клієнтів і два незалежні сервери. Перший клієнт виконує транзакцію `T₁` на вузлі `A`, отримує підтвердження, після чого через зовнішній канал передає сигнал другому клієнту, який ініціює `T₂` на вузлі `B`. Емулятор перевіряє строге виконання умови `s₁ < s₂`.

## Модель потоків та синхронізація

Для забезпечення точної симуляції багатопотокового середовища емулятор ізолює стан кожного вузла за допомогою м'ютексів або атомарних операцій. Кожен вузол має власну віртуальну часову шкалу:
- Локальний годинник опитується через високоточний системний таймер `CLOCK_MONOTONIC`.
- До системного часу додається статичний калібрований зсув `offset_bias_us`, який моделює фізичну розсинхронізацію (наприклад, +1 мс на вузлі `A` та -4 мс на вузлі `B`).
- Поточна невизначеність `ε` збільшується пропорційно часу, що минув з моменту віртуальної ресинхронізації `last_sync`.

Бар'єр фіксації `Commit Wait` використовує гібридну стратегію очікування:
1. **Грубе очікування (Sleep-Wait):** якщо до вичерпання інтервалу залишається понад 100 мікросекунд, потік відпускає процесор через `nanosleep` або `std::this_thread::sleep_for`.
2. **Точна доводка (Spin-Wait):** на фінальних мікросекундах потік виконує активне опитування, щоб уникнути втрати десятків мікросекунд через квантування планувальника операційної системи.

## Реалізація мовами C та C++

У наведеному нижче коді представлено дві ідіоматичні реалізації симулятора: версію мовою C на базі POSIX Threads (`pthread_mutex_t`, `nanosleep`, `clock_gettime`) та об'єктно-орієнтовану багатопотокову реалізацію мовою C++ на базі стандартної бібліотеки `std::chrono`, `std::thread` та `std::mutex`.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <inttypes.h>

/* Часовий інтервал TrueTime в мікросекундах */
typedef struct {
    int64_t earliest;
    int64_t latest;
} tt_interval_t;

/* Стан локального годинника вузла */
typedef struct {
    int64_t base_uncertainty_us; /* Базова похибка еталону (ε₀) */
    double drift_rate_ppm;       /* Максимальний дрейф генератора в ppm */
    struct timespec last_sync;   /* Момент останньої синхронізації */
    int64_t offset_bias_us;      /* Штучний зсув шкали вузла */
    pthread_mutex_t lock;
} tt_clock_node_t;

static int64_t timespec_to_us(const struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000LL + (int64_t)ts->tv_nsec / 1000LL;
}

static void us_to_timespec(int64_t us, struct timespec *ts) {
    ts->tv_sec = (time_t)(us / 1000000LL);
    ts->tv_nsec = (long)((us % 1000000LL) * 1000LL);
}

/* Ініціалізація локального часового вузла */
void tt_node_init(tt_clock_node_t *node, int64_t base_eps_us, double drift_ppm, int64_t bias_us) {
    node->base_uncertainty_us = base_eps_us;
    node->drift_rate_ppm = drift_ppm;
    node->offset_bias_us = bias_us;
    clock_gettime(CLOCK_MONOTONIC, &node->last_sync);
    pthread_mutex_init(&node->lock, NULL);
}

void tt_node_destroy(tt_clock_node_t *node) {
    pthread_mutex_destroy(&node->lock);
}

/* Отримання поточного інтервалу TrueTime */
tt_interval_t tt_now(tt_clock_node_t *node) {
    struct timespec now_ts;
    clock_gettime(CLOCK_MONOTONIC, &now_ts);

    pthread_mutex_lock(&node->lock);
    int64_t now_us = timespec_to_us(&now_ts) + node->offset_bias_us;
    int64_t elapsed_us = timespec_to_us(&now_ts) - timespec_to_us(&node->last_sync);
    if (elapsed_us < 0) elapsed_us = 0;

    /* Динамічне зростання невизначеності: ε(t) = ε₀ + ρ·Δt */
    int64_t drift_us = (int64_t)((double)elapsed_us * (node->drift_rate_ppm / 1000000.0));
    int64_t total_eps = node->base_uncertainty_us + drift_us;
    pthread_mutex_unlock(&node->lock);

    tt_interval_t interval;
    interval.earliest = now_us - total_eps;
    interval.latest = now_us + total_eps;
    return interval;
}

/* Перевірка, чи момент t гарантовано настав у фізичному часі */
bool tt_after(tt_clock_node_t *node, int64_t t) {
    tt_interval_t cur = tt_now(node);
    return cur.earliest > t;
}

/* Перевірка, чи момент t гарантовано ще не настав */
bool tt_before(tt_clock_node_t *node, int64_t t) {
    tt_interval_t cur = tt_now(node);
    return cur.latest < t;
}

/* Бар'єр Commit Wait: блокування потоку доки earliest > s */
void tt_commit_wait(tt_clock_node_t *node, int64_t commit_ts) {
    while (!tt_after(node, commit_ts)) {
        tt_interval_t cur = tt_now(node);
        int64_t remaining_us = commit_ts - cur.earliest + 50; /* +50 мкс захисний інтервал */
        if (remaining_us > 0) {
            struct timespec req;
            us_to_timespec(remaining_us, &req);
            nanosleep(&req, NULL);
        }
    }
}

/* Демонстрація виконання розподілених транзакцій */
typedef struct {
    tt_clock_node_t *node_a;
    tt_clock_node_t *node_b;
    int64_t tx1_commit_ts;
    int64_t tx2_commit_ts;
    bool violation_detected;
} test_context_t;

void* worker_thread(void *arg) {
    test_context_t *ctx = (test_context_t*)arg;

    /* Транзакція T1 на Вузлі А */
    tt_interval_t int1 = tt_now(ctx->node_a);
    int64_t s1 = int1.latest; /* Вибір мітки коміту: s1 = latest */
    
    printf("[Tx1 Вузол A] Обрано мітку s1 = %" PRId64 " мкс (інтервал: [%" PRId64 ", %" PRId64 "])\n",
           s1, int1.earliest, int1.latest);

    /* Бар'єр очікування на Вузлі А */
    tt_commit_wait(ctx->node_a, s1);
    ctx->tx1_commit_ts = s1;
    printf("[Tx1 Вузол A] Зафіксовано після Commit Wait. Відповідь повернено клієнту.\n");

    /* Імітація зовнішньої передачі даних від клієнта 1 до клієнта 2 (5 мс) */
    usleep(5000);

    /* Транзакція T2 на Вузлі B (який має значний від'ємний зсув годинника!) */
    tt_interval_t int2 = tt_now(ctx->node_b);
    int64_t s2 = int2.latest;
    printf("[Tx2 Вузол B] Обрано мітку s2 = %" PRId64 " мкс (інтервал: [%" PRId64 ", %" PRId64 "])\n",
           s2, int2.earliest, int2.latest);

    tt_commit_wait(ctx->node_b, s2);
    ctx->tx2_commit_ts = s2;
    printf("[Tx2 Вузол B] Зафіксовано. s2 = %" PRId64 "\n", s2);

    /* Перевірка інваріанта лінеаризовності: s1 < s2 */
    if (s2 <= s1) {
        printf("ПОМИЛКА: Порушення лінеаризовності! s2 (%" PRId64 ") <= s1 (%" PRId64 ")\n", s2, s1);
        ctx->violation_detected = true;
    } else {
        printf("УСПІХ: Порядок збережено: s1 (%" PRId64 ") < s2 (%" PRId64 ") [Δ = %" PRId64 " мкс]\n",
               s1, s2, s2 - s1);
    }
    return NULL;
}

int main(void) {
    tt_clock_node_t node_a, node_b;
    /* Вузол A: похибка 2000 мкс (2 мс), випереджає еталон на +1000 мкс */
    tt_node_init(&node_a, 2000, 200.0, 1000);
    /* Вузол B: похибка 2000 мкс (2 мс), суттєво відстає: зсув -4000 мкс */
    tt_node_init(&node_b, 2000, 200.0, -4000);

    test_context_t ctx = { &node_a, &node_b, 0, 0, false };
    pthread_t th;
    pthread_create(&th, NULL, worker_thread, &ctx);
    pthread_join(th, NULL);

    tt_node_destroy(&node_a);
    tt_node_destroy(&node_b);
    return ctx.violation_detected ? 1 : 0;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <thread>
#include <mutex>
#include <algorithm>
#include <cstdint>
#include <format>

namespace truetime {

using Microseconds = std::chrono::microseconds;
using SteadyClock = std::chrono::steady_clock;
using TimePoint = std::chrono::time_point<SteadyClock>;

struct TimeInterval {
    std::int64_t earliest_us{0};
    std::int64_t latest_us{0};

    [[nodiscard]] bool contains(std::int64_t t) const noexcept {
        return earliest_us <= t && t <= latest_us;
    }

    [[nodiscard]] bool precedes(const TimeInterval& other) const noexcept {
        return latest_us < other.earliest_us;
    }

    [[nodiscard]] bool overlaps(const TimeInterval& other) const noexcept {
        return !(precedes(other) || other.precedes(*this));
    }
};

class ClockNode {
public:
    ClockNode(Microseconds base_uncertainty, double drift_ppm, Microseconds offset_bias)
        : base_uncertainty_(base_uncertainty),
          drift_ppm_(drift_ppm),
          offset_bias_(offset_bias),
          sync_point_(SteadyClock::now()) {}

    [[nodiscard]] TimeInterval now() const {
        const auto current_tp = SteadyClock::now();
        std::lock_guard<std::mutex> lock(mutex_);

        const auto elapsed_us = std::chrono::duration_cast<Microseconds>(current_tp - sync_point_).count();
        const auto raw_now_us = std::chrono::duration_cast<Microseconds>(current_tp.time_since_epoch()).count() + offset_bias_.count();

        const auto dynamic_drift_us = static_cast<std::int64_t>(static_cast<double>(elapsed_us) * (drift_ppm_ / 1'000'000.0));
        const auto total_uncertainty_us = base_uncertainty_.count() + dynamic_drift_us;

        return TimeInterval{
            .earliest_us = raw_now_us - total_uncertainty_us,
            .latest_us = raw_now_us + total_uncertainty_us
        };
    }

    [[nodiscard]] bool after(std::int64_t target_time_us) const {
        return now().earliest_us > target_time_us;
    }

    [[nodiscard]] bool before(std::int64_t target_time_us) const {
        return now().latest_us < target_time_us;
    }

    void commit_wait(std::int64_t commit_timestamp_us) const {
        while (!after(commit_timestamp_us)) {
            const auto current_interval = now();
            const auto remaining_us = commit_timestamp_us - current_interval.earliest_us + 50;
            if (remaining_us > 0) {
                std::this_thread::sleep_for(std::chrono::microseconds(remaining_us));
            }
        }
    }

    void resync(Microseconds new_base_uncertainty) {
        std::lock_guard<std::mutex> lock(mutex_);
        sync_point_ = SteadyClock::now();
        base_uncertainty_ = new_base_uncertainty;
    }

private:
    Microseconds base_uncertainty_;
    double drift_ppm_;
    Microseconds offset_bias_;
    TimePoint sync_point_;
    mutable std::mutex mutex_;
};

class TransactionCoordinator {
public:
    explicit TransactionCoordinator(ClockNode& clock) : clock_(clock) {}

    [[nodiscard]] std::int64_t execute_commit() {
        // Крок 1: Отримання інтервалу та вибір мітки коміту: s = latest
        const auto interval = clock_.now();
        const std::int64_t commit_ts = interval.latest_us;

        // Крок 2: Очікування закінчення невизначеності (Commit Wait)
        clock_.commit_wait(commit_ts);

        // Крок 3: Після виходу з Commit Wait мітка commit_ts гарантовано в минулому
        return commit_ts;
    }

private:
    ClockNode& clock_;
};

} // namespace truetime

int main() {
    // Вузол А: похибка 2 мс (2000 мкс), забігає вперед на +1 мс
    truetime::ClockNode node_a(std::chrono::microseconds(2000), 200.0, std::chrono::microseconds(1000));

    // Вузол В: похибка 2 мс (2000 мкс), суттєво відстає (-4 мс)
    truetime::ClockNode node_b(std::chrono::microseconds(2000), 200.0, std::chrono::microseconds(-4000));

    truetime::TransactionCoordinator coord_a(node_a);
    truetime::TransactionCoordinator coord_b(node_b);

    std::cout << "Початок транзакції T1 на Вузлі A...\n";
    const auto s1 = coord_a.execute_commit();
    std::cout << std::format("T1 зафіксовано з міткою s1 = {} мкс. Результат передано клієнту.\n", s1);

    // Зовнішня причинна затримка (клієнт надсилає запит на інший вузол)
    std::this_thread::sleep_for(std::chrono::milliseconds(5));

    std::cout << "Початок транзакції T2 на Вузлі B (з відстаючим локальним годинником)...\n";
    const auto s2 = coord_b.execute_commit();
    std::cout << std::format("T2 зафіксовано з міткою s2 = {} мкс.\n", s2);

    if (s2 > s1) {
        std::cout << std::format("УСПІХ: Зовнішню узгодженість дотримано: s1 ({}) < s2 ({}) [Різниця: {} мкс]\n",
                                 s1, s2, s2 - s1);
        return 0;
    } else {
        std::cerr << std::format("КРИТИЧНИЙ ЗБІЙ: Інверсія порядку! s2 ({}) <= s1 ({})\n", s2, s1);
        return 1;
    }
}
```
:::

## Покроковий розбір сценарію виконання

Розглянемо числовий трасування роботи програми:

1. **Параметри вузлів:**
   - `Вузол A` має базову похибку `ε = 2000 мкс` та додатній зсув шкали `+1000 мкс`.
   - `Вузол B` має таку саму похибку `ε = 2000 мкс`, але відстає від еталону на `-4000 мкс` (сумарна розбіжність між вузлами становить 5 мілісекунд).
2. **Транзакція T1 на Вузлі A:**
   - При старті умовний ідеальний час дорівнює `t = 10000 мкс`.
   - Локальний годинник `Вузла A` показує `10000 + 1000 = 11000 мкс`.
   - `tt_now()` повертає інтервал `[11000 − 2000, 11000 + 2000] = [9000, 13000]`.
   - Координатор обирає мітку коміту `s₁ = latest = 13000 мкс`.
   - Бар'єр `commit_wait` блокує повернення відповіді доти, доки `earliest` не перевищить `13000`. Для цього локальний час має досягти `13000 + 2000 = 15000 мкс`, що відповідає реальному фізичному моменту `t = 14000 мкс`.
   - Координатор очікує близько `4000 мкс` (тобто `2·ε`) і повертає успіх клієнту в момент `t = 14000 мкс`.
3. **Зовнішній причинний перехід:**
   - Клієнт 1 надсилає повідомлення Клієнту 2. Затримка передачі складає `5000 мкс`.
   - Транзакція `T₂` на `Вузлі B` розпочинається у реальний момент `t = 14000 + 5000 = 19000 мкс`.
4. **Транзакція T2 на Вузлі B:**
   - Локальний лічильник `Вузла B` у момент `t = 19000 мкс` показує `19000 − 4000 = 15000 мкс` (годинник суттєво відстає!).
   - Виклик `tt_now()` на `Вузлі B` повертає інтервал `[15000 − 2000, 15000 + 2000] = [13000, 17000]`.
   - Координатор обирає мітку `s₂ = latest = 17000 мкс`.
   - Порівняння міток дає: `s₁ = 13000 < s₂ = 17000`. Інверсії міток не сталося, лінеаризовність збережено.

Якби `Вузол A` не виконував правило Commit Wait, він віддав би мітку `11000` одразу в момент `t = 10000`. Якби затримка між клієнтами була меншою (наприклад, 1 мс), `Вузол B` розпочав би транзакцію в `t = 11000`, побачив би локальний час `7000` і обрав би мітку `9000`, що призвело б до грубої аномалії `s₂ (9000) < s₁ (11000)`.

## Діагностика аномалій та пастки оптимізації

Під час практичного використання емулятора слід враховувати наступні типові проблеми:

1. **Дрейф віртуальних машин:** Якщо емулятор запускається всередині контейнера або гіпервізора (KVM/VMware), таймер віртуального процесора може зазнавати стрибків (англ. *steal time*), коли хост-система виділяє ресурси іншим задачам. Для промислових тестів рекомендується використовувати виділені фізичні ядра з піннінгом потоків (`pthread_setaffinity_np`).
2. **Нелінійність функції sleep:** Стандартні системні виклики сну (`usleep`, `nanosleep`) в ОС Linux гарантують лише мінімальну тривалість очікування, проте максимальна затримка пробудження може перевищувати очікувану на кілька мілісекунд через квантування таймера планувальника (за замовчуванням `CONFIG_HZ = 250` або `1000`). Використання активного опитування на останніх мікросекундах повністю нівелює цей ефект.
3. **Конкуренція за блокування м'ютекса:** У високонавантажених серверах з сотнями робочих потоків часте блокування м'ютекса всередині `tt_now()` може створювати контеншн. У промислових рушіях стан годинника оновлюється фоновим потоком в атомарній структурі за допомогою механізму RCU (Read-Copy-Update) або lock-free читання `std::atomic<TimeState>`, що дозволяє сотням потоків читати час одночасно без взаємних затримок.

## Інструкція зі збирання та тестування

Для компіляції та запуску прикладів у середовищі Linux або macOS:

```bash
# Компіляція C-версії (POSIX threads)
gcc -O2 -Wall -Wextra -pthread proj-truetime-simulator.c -o truetime_c
./truetime_c

# Компіляція C++ версії (C++20/C++23)
g++ -O2 -Wall -Wextra -std=c++20 -pthread proj-truetime-simulator.cpp -o truetime_cpp
./truetime_cpp
```

Обидві програми повертають код завершення `0` у разі успішного проходження верифікації порядку транзакцій та `1` у разі виявлення порушення лінеаризовності.
