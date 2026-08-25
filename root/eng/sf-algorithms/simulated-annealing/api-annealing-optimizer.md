# 📋 Інтерфейс та архітектура оптимізатора відпалу

Високопродуктивний рушій імітації відпалу вимагає чіткого архітектурного розмежування алгоритмічного ядра (цикл зміни температури, критерій Метрополіса, стохастичний вибір) від проблемно-орієнтованої логіки (представлення стану, генерація сусідніх конфігурацій та обчислення різниці вартості `ΔE`).

Недбале проектування інтерфейсу, у якому стан копіюється на кожній ітерації через динамічну пам'ять (`malloc` або конструктори копіювання `std::vector`), призводить до катастрофічної деградації швидкодії у 10–100 разів. Оскільки внутрішній цикл оптимізатора виконує від `10⁶` до `10⁸` ітерацій на секунду, архітектурний контракт мусить гарантувати нульове виділення пам'яті в купі (`zero-heap-allocation`) під час активного пошуку та підтримувати максимальну локальність даних у кеш-пам'яті L1/L2.

Нижче наведено модульний контракт інтерфейсу для мов C та сучасного C++20, розрахований на високонавантажені обчислювальні задачі.

## 1. Архітектурні компоненти та життєвий цикл оптимізатора

Уніфікований рушій базується на шести функціональних абстракціях:

1. **Стан (`State`)**: Компактна структура даних, що описує конфігурацію задачі. Стан передається як непрозорий вказівник або узагальнений тип. Пам'ять для поточного стану (`s_curr`) та найкращого рекорду (`s_best`) виділяється одноразово до запуску циклу.
2. **Окільний оператор (`Move / Proposal`)**: Опис елементарної мутації стану (наприклад, перестановка двох індексів, інверсія відрізка, перемикання біта). Структура мутації повинна містити мінімально достатню інформацію для швидкого застосування або відкату.
3. **Оцінювач вартості (`Evaluator`)**:
   - Повний розрахунок `evaluate_full(state)`: використовується одноразово на старті оптимізації та періодично (раз на `10⁴–10⁵` ітерацій) для запобігання накопиченню похибок округлення чисел з плаваючою комою. Часова складність — `O(N)`.
   - Інкрементний розрахунок `evaluate_delta(state, move)`: швидкий розрахунок різниці `ΔE = E(state') - E(state)` без виконання самої мутації стану. Часова складність — `O(1)` або `O(log N)`.
4. **Застосування та відкат (`Apply / Rollback`)**: Якщо мутація приймається за критерієм Метрополіса, вона модифікує стан на місці (`in-place`). Якщо мутація відхиляється, стан залишається незайманим, що виключає зайві операції запису в пам'ять.
5. **Температурний розклад (`CoolingSchedule`)**: Політика зміни температури, яка інкапсулює закон спадання `T_{k+1} = f(T_k, k)` та умови ранньої зупинки (наприклад, перевищення ліміту епох без покращення рекорду).
6. **Телеметрія та спостереження (`Observer`)**: Зворотний виклик (callback), що надає статистику для моніторингу: поточну температуру, коефіцієнт прийнятих переходів (acceptance rate), частку погіршень та поточний рекорд.

## 2. Запобігання накопиченню чисельної похибки

При тривалій роботі з інкрементним додаванням `current_energy += delta_e` у форматі `double` через скінченну точність мантиси (IEEE 754) виникає накопичення похибок округлення (catastrophic cancellation). За `10⁷` ітерацій накопичена похибка може сягати кількох одиниць енергії, спотворюючи критерій прийняття Метрополіса.

Архітектурний контракт вирішує це шляхом **періодичної ресинхронізації**: наприкінці кожної епохи або через кожні `K` ітерацій викликається `evaluate_full(s_curr)` для відновлення точного значення енергії.

## 3. Інтерфейсний контракт бібліотеки

:::tabs
```c
#ifndef SIMULATED_ANNEALING_H
#define SIMULATED_ANNEALING_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Швидкий генератор псевдовипадкових чисел xoshiro256** */
typedef struct {
    uint64_t s[4];
} sa_rng_t;

void sa_rng_seed(sa_rng_t* rng, uint64_t seed);
uint64_t sa_rng_next64(sa_rng_t* rng);
double sa_rng_uniform(sa_rng_t* rng); /* Повертає значення у діапазоні [0.0, 1.0) */

/* Типи температурних розкладів */
typedef enum {
    SA_COOLING_GEOMETRIC,   /* T_{k+1} = alpha * T_k */
    SA_COOLING_LINEAR,      /* T_{k+1} = max(T_min, T_k - beta) */
    SA_COOLING_LOGARITHMIC  /* T_k = T_0 / ln(1 + k) */
} sa_cooling_type_t;

/* Параметри конфігурації оптимізатора */
typedef struct {
    double initial_temp;     /* T_0: початкова температура */
    double min_temp;         /* T_min: температура зупинки */
    double cooling_rate;     /* alpha (0.80..0.99) для GEOMETRIC або beta для LINEAR */
    size_t steps_per_epoch;  /* Кількість кроків на кожному ізотермічному рівні */
    size_t max_epochs;       /* Максимальна кількість епох охолодження */
    size_t max_stagnation;   /* Ліміт епох без оновлення глобального рекорду */
    size_t resync_interval;  /* Інтервал повної ресинхронізації енергії (ітерацій) */
    sa_cooling_type_t type;  /* Обраний температурний розклад */
} sa_params_t;

/* Статистика та метрики виконання */
typedef struct {
    uint64_t total_proposals;
    uint64_t accepted_improvements;
    uint64_t accepted_deteriorations;
    uint64_t rejected_moves;
    double best_energy;
    double final_temp;
    size_t epochs_run;
} sa_stats_t;

/* Контракт проблемно-орієнтованої моделі */
typedef struct sa_problem {
    void* context; /* Користувацькі дані задачі (матриці ваг, координати тощо) */
    
    /* Повний розрахунок вартості початкового стану O(N) */
    double (*evaluate_full)(const void* state, void* context);
    
    /* Генерація випадкової мутації з околу N(state) */
    void (*propose_move)(const void* state, void* move_out, sa_rng_t* rng, void* context);
    
    /* Інкрементний розрахунок різниці енергії: ΔE = E(state') - E(state) за O(1) */
    double (*evaluate_delta)(const void* state, const void* move, void* context);
    
    /* Застосування прийнятої мутації до стану на місці */
    void (*apply_move)(void* state, const void* move, void* context);
    
    /* Копіювання стану для збереження глобального рекорду */
    void (*copy_state)(void* dst, const void* src, void* context);
    
    /* Опціональний зворотний виклик для телеметрії (може бути NULL) */
    void (*on_epoch_end)(size_t epoch, double temp, double best_energy, 
                         double acceptance_rate, void* context);
} sa_problem_t;

/* Головна функція запуску оптимізатора */
bool sa_optimize(const sa_problem_t* problem,
                 void* state_io,
                 size_t state_size,
                 size_t move_size,
                 const sa_params_t* params,
                 uint64_t random_seed,
                 sa_stats_t* stats_out);

#ifdef __cplusplus
}
#endif

#endif /* SIMULATED_ANNEALING_H */
```
```cpp
#pragma once

#include <concepts>
#include <cstddef>
#include <cstdint>
#include <random>
#include <span>
#include <functional>
#include <algorithm>
#include <cmath>

namespace sa {

/* Концепт C++20 для визначення задачі відпалу */
template <typename Problem, typename State, typename Move>
concept AnnealingProblem = requires(Problem p, State& s, const State& cs, const Move& m, std::mt19937_64& rng) {
    { p.evaluate_full(cs) } -> std::convertible_to<double>;
    { p.propose_move(cs, rng) } -> std::same_as<Move>;
    { p.evaluate_delta(cs, m) } -> std::convertible_to<double>;
    { p.apply_move(s, m) } -> std::same_as<void>;
};

enum class CoolingType {
    Geometric,
    Linear,
    Logarithmic
};

struct Params {
    double initial_temp = 1000.0;
    double min_temp = 1e-4;
    double cooling_rate = 0.95;
    std::size_t steps_per_epoch = 1000;
    std::size_t max_epochs = 5000;
    std::size_t max_stagnation = 200;
    std::size_t resync_interval = 10000;
    CoolingType cooling_type = CoolingType::Geometric;
};

struct Stats {
    std::uint64_t total_proposals = 0;
    std::uint64_t accepted_improvements = 0;
    std::uint64_t accepted_deteriorations = 0;
    std::uint64_t rejected_moves = 0;
    double best_energy = 0.0;
    double final_temp = 0.0;
    std::size_t epochs_run = 0;

    [[nodiscard]] double acceptance_rate() const noexcept {
        if (total_proposals == 0) return 0.0;
        return static_cast<double>(accepted_improvements + accepted_deteriorations) / 
               static_cast<double>(total_proposals);
    }
};

/* Шаблонний оптимізатор з нульовим оверхедом поліморфізму */
template <typename State, typename Move, AnnealingProblem<State, Move> Problem>
class Optimizer {
public:
    using ObserverCallback = std::function<void(std::size_t epoch, double temp, double best_energy, double accept_rate)>;

    explicit Optimizer(Problem problem, Params params = {})
        : problem_(std::move(problem)), params_(params) {}

    Stats run(State& initial_state, std::uint64_t seed = 42, ObserverCallback observer = nullptr) {
        std::mt19937_64 rng(seed);
        std::uniform_real_distribution<double> uniform_dist(0.0, 1.0);

        State current_state = initial_state;
        State best_state = initial_state;

        double current_energy = problem_.evaluate_full(current_state);
        double best_energy = current_energy;

        double temp = params_.initial_temp;
        Stats stats{};
        stats.best_energy = best_energy;

        std::size_t stagnation_counter = 0;
        std::size_t steps_since_resync = 0;

        for (std::size_t epoch = 0; epoch < params_.max_epochs && temp > params_.min_temp; ++epoch) {
            std::uint64_t epoch_proposals = 0;
            std::uint64_t epoch_accepted = 0;

            for (std::size_t step = 0; step < params_.steps_per_epoch; ++step) {
                Move move = problem_.propose_move(current_state, rng);
                double delta_e = problem_.evaluate_delta(current_state, move);

                ++stats.total_proposals;
                ++epoch_proposals;
                ++steps_since_resync;

                bool accept = false;
                if (delta_e <= 0.0) {
                    accept = true;
                    ++stats.accepted_improvements;
                } else {
                    double acceptance_prob = std::exp(-delta_e / temp);
                    if (uniform_dist(rng) < acceptance_prob) {
                        accept = true;
                        ++stats.accepted_deteriorations;
                    } else {
                        ++stats.rejected_moves;
                    }
                }

                if (accept) {
                    problem_.apply_move(current_state, move);
                    current_energy += delta_e;
                    ++epoch_accepted;

                    if (steps_since_resync >= params_.resync_interval) {
                        current_energy = problem_.evaluate_full(current_state);
                        steps_since_resync = 0;
                    }

                    if (current_energy < best_energy) {
                        best_energy = current_energy;
                        best_state = current_state;
                        stagnation_counter = 0;
                    }
                }
            }

            stats.best_energy = best_energy;
            stats.final_temp = temp;
            stats.epochs_run = epoch + 1;

            if (observer) {
                double epoch_rate = epoch_proposals > 0 
                    ? static_cast<double>(epoch_accepted) / static_cast<double>(epoch_proposals) 
                    : 0.0;
                observer(epoch, temp, best_energy, epoch_rate);
            }

            // Оновлення температури за обраним законом
            switch (params_.cooling_type) {
                case CoolingType::Geometric:
                    temp *= params_.cooling_rate;
                    break;
                case CoolingType::Linear:
                    temp = std::max(params_.min_temp, temp - params_.cooling_rate);
                    break;
                case CoolingType::Logarithmic:
                    temp = params_.initial_temp / std::log(2.0 + static_cast<double>(epoch));
                    break;
            }

            ++stagnation_counter;
            if (stagnation_counter >= params_.max_stagnation) {
                break; // Дострокова зупинка при замерзанні
            }
        }

        initial_state = std::move(best_state);
        return stats;
    }

private:
    Problem problem_;
    Params params_;
};

} // namespace sa
```
:::

## 4. Інтеграційний приклад: Задача розбиття чисел (Number Partitioning)

Задача розбиття чисел полягає у поділі заданої множини чисел `A = {a_1, a_2, ..., a_n}` на дві неперетинні підмножини `S_1` та `S_2` так, щоб мінімізувати абсолютну різницю їхніх сум:

```
E(s) = |∑_{i ∈ S_1} a_i − ∑_{i ∈ S_2} a_i|
```

Задача є NP-повною. Стан подається як булевий масив `in_set1[i]`. Мутація полягає у випадковому перемиканні належності одного елемента (`flip`).

Різниця вартості розраховується за `O(1)` без повторного підсумовування всіх елементів множини:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    const int64_t* values;
    size_t count;
    int64_t total_sum;
} partition_context_t;

typedef struct {
    bool* in_set1;
} partition_state_t;

typedef struct {
    size_t flip_index;
} partition_move_t;

static double part_evaluate_full(const void* s, void* ctx) {
    const partition_state_t* state = (const partition_state_t*)s;
    const partition_context_t* context = (const partition_context_t*)ctx;
    int64_t sum1 = 0;
    for (size_t i = 0; i < context->count; ++i) {
        if (state->in_set1[i]) sum1 += context->values[i];
    }
    int64_t sum2 = context->total_sum - sum1;
    return (double)llabs(sum1 - sum2);
}

static void part_propose_move(const void* s, void* move_out, sa_rng_t* rng, void* ctx) {
    (void)s;
    const partition_context_t* context = (const partition_context_t*)ctx;
    partition_move_t* move = (partition_move_t*)move_out;
    move->flip_index = (size_t)(sa_rng_next64(rng) % context->count);
}

static double part_evaluate_delta(const void* s, const void* m, void* ctx) {
    const partition_state_t* state = (const partition_state_t*)s;
    const partition_move_t* move = (const partition_move_t*)m;
    const partition_context_t* context = (const partition_context_t*)ctx;

    int64_t val = context->values[move->flip_index];
    int64_t current_sum1 = 0;
    for (size_t i = 0; i < context->count; ++i) {
        if (state->in_set1[i]) current_sum1 += context->values[i];
    }
    int64_t current_sum2 = context->total_sum - current_sum1;
    double current_diff = (double)llabs(current_sum1 - current_sum2);

    int64_t next_sum1 = state->in_set1[move->flip_index] ? (current_sum1 - val) : (current_sum1 + val);
    int64_t next_sum2 = context->total_sum - next_sum1;
    double next_diff = (double)llabs(next_sum1 - next_sum2);

    return next_diff - current_diff;
}

static void part_apply_move(void* s, const void* m, void* ctx) {
    (void)ctx;
    partition_state_t* state = (partition_state_t*)s;
    const partition_move_t* move = (const partition_move_t*)m;
    state->in_set1[move->flip_index] = !state->in_set1[move->flip_index];
}
```
```cpp
#include <vector>
#include <numeric>
#include <cmath>
#include <iostream>

struct PartitionProblem {
    std::vector<std::int64_t> values;
    std::int64_t total_sum = 0;

    explicit PartitionProblem(std::vector<std::int64_t> vals)
        : values(std::move(vals)),
          total_sum(std::accumulate(values.begin(), values.end(), std::int64_t{0})) {}

    struct State {
        std::vector<bool> in_set1;
        std::int64_t sum1 = 0;
    };

    struct Move {
        std::size_t index = 0;
    };

    [[nodiscard]] double evaluate_full(const State& s) const noexcept {
        std::int64_t sum2 = total_sum - s.sum1;
        return static_cast<double>(std::abs(s.sum1 - sum2));
    }

    [[nodiscard]] Move propose_move(const State& /*s*/, std::mt19937_64& rng) const noexcept {
        std::uniform_int_distribution<std::size_t> dist(0, values.size() - 1);
        return Move{dist(rng)};
    }

    [[nodiscard]] double evaluate_delta(const State& s, const Move& m) const noexcept {
        std::int64_t val = values[m.index];
        std::int64_t next_sum1 = s.in_set1[m.index] ? (s.sum1 - val) : (s.sum1 + val);
        std::int64_t next_sum2 = total_sum - next_sum1;
        
        double current_energy = static_cast<double>(std::abs(s.sum1 - (total_sum - s.sum1)));
        double next_energy = static_cast<double>(std::abs(next_sum1 - next_sum2));
        return next_energy - current_energy;
    }

    void apply_move(State& s, const Move& m) const noexcept {
        std::int64_t val = values[m.index];
        if (s.in_set1[m.index]) {
            s.sum1 -= val;
            s.in_set1[m.index] = false;
        } else {
            s.sum1 += val;
            s.in_set1[m.index] = true;
        }
    }
};
```
:::

## 5. Обробка крайових випадків та перевірка коректності

Під час інтеграції користувацької задачі з рушієм відпалу необхідно контролювати такі крайові стани:

1. **Недопустимі та заборонені конфігурації**: Якщо мутація порушує жорсткі обмеження задачі (наприклад, перевищення місткості рюкзака), функція `evaluate_delta` повинна повертати штрафне значення `+INFINITY` або дуже велику додатну константу. Це гарантує, що ймовірність прийняття `exp(-∞ / T) = 0`, і алгоритм автоматично відхилить такий перехід.
2. **Нескінченні енергії та ділення на нуль**: При наближенні температури до нуля дріб `ΔE / T` може призвести до переповнення типу `double` (повертаючи `HUGE_VAL`). У реалізації оптимізатора перевірка `if (delta_e <= 0.0)` обов'язково стоїть першою, а для додатних `delta_e` при наднизьких `T` результат експоненти коректно прямує до `0.0`.
3. **Захист від нульової дисперсії**: Якщо всі сусідні стани мають однакову енергію (`ΔE = 0`), система виконує чисте випадкове блукання (плато). Алгоритм не повинен інтерпретувати це як успішне покращення глобального рекорду, а лічильник стагнації мусить коректно нарощуватися.

## 6. Багатопотоковість та паралельний відпал (Parallel Annealing)

Оскільки алгоритм імітації відпалу спирається на послідовний ланцюг Маркова (де кожний наступний стан залежить від результату попереднього прийняття), наївна паралелізація одного ланцюга призводить до конфліктів синхронізації пам'яті. 

У високопродуктивних системах застосовують дві перевірені паралельні моделі:

1. **Мультистартовий паралелізм (Independent Multi-Restart)**:
   Запуск `M` незалежних оптимізаторів на різних ядрах процесора. Кожен потік ініціалізується власним генератором випадкових чисел з унікальним зерном (`seed + thread_id`). Потоки працюють повністю ізольовано без блокувань та атоміків. Після завершення обчислень головний потік обирає глобально найкращий стан серед усіх `M` результатів. Ця схема має лінійну масштабованість `O(M)` і суттєво підвищує ймовірність знаходження глобального мінімуму на складних багатоекстремальних рельєфах.

## 7. Профілювання та апаратні лічильники продуктивності

Для досягнення максимальної пропускної здатності оптимізатора рекомендується аналізувати виконання за допомогою апаратних лічильників процесора (`perf`, VTune або Instruments):

1. **Частка промахів кешу L1D (L1 Data Cache Miss Rate)**: Мусить бути меншою за 0.5%. Якщо промахи зростають, це вказує на надмірний розмір структури стану або нелокальний доступ до пам'яті під час розрахунку `ΔE`.
2. **Промахи передбачення переходів (Branch Mispredictions)**: Перевірка критерію Метрополіса `if (r < exp(-ΔE / T))` є принципово стохастичною. На середніх температурах (де ймовірність прийняття близька до 50%) апаратний передбачувач переходів процесора дає до 30–40% промахів. Для критичних за часом ділянок застосовують безгалузеву арифметику (predication / CMOV) або папелайн із генерацією масиву випадкових рішень.
3. **Інструкцій за такт (IPC — Instructions Per Cycle)**: Оптимізований внутрішній цикл без трансцендентних викликів `exp` та без динамічного виділення пам'яті досягає показника IPC ≥ 2.5 на сучасних архітектурах x86-64 та ARM64.
