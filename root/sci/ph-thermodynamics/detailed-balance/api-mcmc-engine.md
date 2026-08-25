# 📋 Інтерфейс бібліотеки MCMC-симуляції та аудиту балансу

Опис програмного інтерфейсу (API) C/C++ бібліотеки `libmcmc_engine`, призначеної для проведення симуляцій Марковських ланцюгів Монте-Карло, розрахунку стаціонарних розподілів та автоматичного аудиту виконання принципу детального балансу. Цей документ містить повний контракт специфікацій типів даних, конфігураційних структур, сигнатур функцій, кодів помилок, правил володіння пам'яттю, потокобезпечності та налаштувань чисельних допусків.

## 1. Загальний огляд архітектури та сценарії використання

Бібліотека `libmcmc_engine` реалізує універсальний генератор дискретних та неперервних марковських ланцюгів за алгоритмом Метрополіса-Гастінгса. Головне призначення бібліотеки — надати фізикам, обчислювальним хімікам та інженерам інструмент проведення стохастичного моделювання з вбудованим математичним контролем виникнення нефізичних циркулюючих струмів (порушення детального балансу).

Основою архітектури є непрозорий контекстний об'єкт `mcmc_engine_t`. Оскільки об'єкт є непрозорим вказівником (opaque pointer), внутрішній стан симулятора — включаючи масиви лічильників відвідань, генератори псевдовипадкових чисел та поточний стан ланцюга — повністю прихований від зовнішнього коду, що гарантує цілісність даних та відсутність несанкціонованих модифікацій.

Робота з бібліотекою передбачає п'ять послідовних кроків у життєвому циклі програми:
1. Конфігурація параметрів симуляції (температура, кількість дискретних станів, термалізація, кількість кроків вибірки) у структурі `mcmc_config_t`.
2. Створення контексту двигуна шляхом виклику функції `mcmc_engine_create()`, яка виділяє потрібну пам'ять та ініціалізує статистичні лічильники.
3. Задання потенціального профілю енергетичних станів викликом `mcmc_engine_set_energies()`.
4. Виконання стохастичної симуляції, термалізації та збору даних викликом `mcmc_engine_run()`.
5. Збір підсумкової статистики й проведення чисельного аудиту реберного балансу викликом `mcmc_engine_verify_balance()`.

## 2. Коди повернення та система обробки помилок

Усі функції бібліотеки повертають цілочисельний код статусу `mcmc_status_t`. Якщо операція завершилася успішно, функція повертає `MCMC_SUCCESS`. Будь-яке ненульове значення вказує на конкретну помилку у вхідних даних або стані обчислень.

| Код статусу | Опис помилки | Дія розробника при виникненні |
|---|---|---|
| `MCMC_SUCCESS = 0` | Операція виконана успішно | Продовжити виконання програми |
| `MCMC_ERROR_INVALID_PARAM = -1` | Передано некоректний аргумент (NULL вказівник, від'ємна температура, count == 0) | Перевірити коректність вхідних даних перед викликом |
| `MCMC_ERROR_OUT_OF_MEMORY = -2` | Помилка виділення динамічної пам'яті в системі | Звільнити неіспользувані ресурси пам'яті |
| `MCMC_ERROR_NOT_CONVERGED = -3` | Ланцюг не досяг стаціонарного стану за відведений час | Збільшити кількість кроків термалізації `burn_in_steps` |
| `MCMC_ERROR_BALANCE_VIOLATED = -4` | Максимальний потік дисбалансу перевищує встановлений допуск | Перевірити симетрію пропозицій кандидатів `q(i → j)` |

Детальна розшифровка кодів помилок:
- `MCMC_ERROR_INVALID_PARAM` виникає тоді, коли у функцію передано вказівник NULL, якщо задана температура `temperature <= 0.0`, якщо кількість станів `num_states < 2`, або якщо кількість кроків є нульовою.
- `MCMC_ERROR_OUT_OF_MEMORY` повертається при виклику `mcmc_engine_create()`, якщо операційна система не може виділити потрібний обсяг оперативності пам'яті для матриць розміром `N × N`.
- `MCMC_ERROR_NOT_CONVERGED` сигналізує про те, що розраховані дисперсії середніх значень не стабілізувалися, що свідчить про застрягання ланцюга у глибокому метастабільному мінімумі.
- `MCMC_ERROR_BALANCE_VIOLATED` генерується функцією `mcmc_engine_verify_balance()`, якщо обчислений максимальний потік дисбалансу `max_imbalance_flux` перевищує встановлений поріг `balance_tolerance`.

## 3. Специфікація заголовочних файлів C та C++

Нижче наведено строгі оголошення типів даних та сигнатур функцій для заголовочного файла C та обгортки C++.

:::tabs
```c
#ifndef MCMC_ENGINE_H
#define MCMC_ENGINE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    MCMC_SUCCESS = 0,
    MCMC_ERROR_INVALID_PARAM = -1,
    MCMC_ERROR_OUT_OF_MEMORY = -2,
    MCMC_ERROR_NOT_CONVERGED = -3,
    MCMC_ERROR_BALANCE_VIOLATED = -4
} mcmc_status_t;

// Налаштування симулятора
typedef struct {
    size_t num_states;         // Кількість дискретних станів системи (> 1)
    double temperature;        // Термодинамічна температура (T > 0.0)
    size_t burn_in_steps;      // Кількість кроків релаксації перед збором статистики
    size_t sampling_steps;     // Кількість кроків збору даних
    unsigned int random_seed;  // Базове зерно генератора псевдовипадкових чисел
    double balance_tolerance;  // Пороговий допуск дисбалансу |J_ij| (наприклад 1e-4)
} mcmc_config_t;

// Результати аудиту детального балансу
typedef struct {
    double max_imbalance_flux; // Максимальне значення |P(i)*W(i->j) - P(j)*W(j->i)|
    size_t worst_edge_from;    // Індекс стану i найгіршого ребра
    size_t worst_edge_to;      // Індекс стану j найгіршого ребра
    double entropy_prod_rate;  // Оцінка швидкості генерації ентропії (dS/dt)
    bool is_balanced;          // Прапорець виконання умови детального балансу
} mcmc_balance_report_t;

// Непрозорий тип контексту двигуна
typedef struct mcmc_engine_s mcmc_engine_t;

// Створення та знищення контексту
mcmc_status_t mcmc_engine_create(const mcmc_config_t *config, mcmc_engine_t **engine_out);
mcmc_status_t mcmc_engine_destroy(mcmc_engine_t *engine);

// Встановлення енергій станів
mcmc_status_t mcmc_engine_set_energies(mcmc_engine_t *engine, const double *energies, size_t count);

// Виконання симуляції
mcmc_status_t mcmc_engine_run(mcmc_engine_t *engine);

// Збір результатів та перевірка балансу
mcmc_status_t mcmc_engine_get_probabilities(const mcmc_engine_t *engine, double *prob_out, size_t count);
mcmc_status_t mcmc_engine_verify_balance(const mcmc_engine_t *engine, mcmc_balance_report_t *report_out);

#ifdef __cplusplus
}
#endif

#endif // MCMC_ENGINE_H
```
```cpp
#ifndef MCMC_ENGINE_HPP
#define MCMC_ENGINE_HPP

#include <vector>
#include <memory>
#include <expected>
#include <string>
#include <span>

namespace mcmc {

enum class ErrorCode {
    InvalidParam,
    OutOfMemory,
    NotConverged,
    BalanceViolated
};

struct Config {
    std::size_t num_states{0};
    double temperature{1.0};
    std::size_t burn_in_steps{100'000};
    std::size_t sampling_steps{1'000'000};
    unsigned int random_seed{42};
    double balance_tolerance{1e-4};
};

struct BalanceReport {
    double max_imbalance_flux{0.0};
    std::size_t worst_edge_from{0};
    std::size_t worst_edge_to{0};
    double entropy_production_rate{0.0};
    bool is_balanced{false};
};

class Engine {
public:
    static std::expected<std::unique_ptr<Engine>, ErrorCode> create(const Config& config);
    
    ~Engine();
    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;
    Engine(Engine&&) noexcept;
    Engine& operator=(Engine&&) noexcept;

    ErrorCode set_energies(std::span<const double> energies);
    ErrorCode run();
    
    [[nodiscard]] std::span<const double> get_probabilities() const noexcept;
    [[nodiscard]] BalanceReport verify_balance() const;

private:
    explicit Engine(const Config& config);
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace mcmc

#endif // MCMC_ENGINE_HPP
```
:::

## 4. Детальний опис сигнатур функцій та контракти

### `mcmc_engine_create`
Створює новий контекст симулятора, виділяє пам'ять для внутрішніх матриць переходів та ініціалізує генератор псевдовипадкових чисел.
- **Аргументи:**
  - `config`: Постійний вказівник на структуру конфігурації `mcmc_config_t`.
  - `engine_out`: Вказівник на змінну-вказівник `mcmc_engine_t*`, куди буде записано адресу створеного контексту.
- **Передумови:** `config != NULL`, `config->num_states > 1`, `config->temperature > 0.0`.
- **Повертає:** `MCMC_SUCCESS` при успішному виділенні пам'яті та ініціалізації.
- **Примітка щодо пам'яті:** Пам'ять виділяється за допомогою `calloc()`, що гарантує нульове початкове значення для всіх внутрішніх лічильників відвідань та переходів.

### `mcmc_engine_set_energies`
Задає масив потенціальних енергій `E_i` для кожного із `N` станів.
- **Аргументи:**
  - `engine`: Дійсний вказівник на контекст двигуна.
  - `energies`: Масив дійсних чисел типу `double` розмірністю `count`.
  - `count`: Кількість елементів масиву (повинна збігатися з `config.num_states`).
- **Передумови:** `engine != NULL`, `energies != NULL`, `count == num_states`.
- **Повертає:** `MCMC_SUCCESS` або `MCMC_ERROR_INVALID_PARAM` у разі невідповідності розмірностей.

### `mcmc_engine_run`
Запускає основний цикл Монте-Карло симуляції. Процес обчислень складається з двох послідовних фаз:
1. **Фаза термалізації (Burn-in):** Симуляція здійснює `burn_in_steps` кроків Метрополіса без фіксації даних. Це необхідно для того, щоб марковський ланцюг заснував стаціонарний стан і позбувся залежності від початкової конфігурації.
2. **Фаза вибірки (Sampling):** Симуляція здійснює `sampling_steps` кроків із фіксацією кількості відвідань кожного стану та підрахунком кількості переходів між кожною парою станів.
- **Повертає:** `MCMC_SUCCESS` при успішному завершенні симуляції.

### `mcmc_engine_verify_balance`
Обчислює емпіричні перехідні ймовірності `W(i → j) = N(i → j) / N_visits(i)` та аналізує матрицю реберних потоків ймовірності `J_{ij} = |P(i) · W(i → j) - P(j) · W(j → i)|`.
- **Опис полів звіту `mcmc_balance_report_t`:**
  - `max_imbalance_flux`: Найбільше значення реберного дисбалансу серед усіх попарних комбінацій станів.
  - `worst_edge_from` / `worst_edge_to`: Індекси станів ребра, на якому зафіксовано максимальний потік дисбалансу.
  - `entropy_prod_rate`: Чисельна оцінка інтенсивності генерації ентропії `dS/dt`.
  - `is_balanced`: `true`, якщо `max_imbalance_flux <= config.balance_tolerance`.

## 5. Приклад практичного використання інтерфейсу

У наведених нижче прикладах показано повний цикл роботи з бібліотекою мовами C та C++.

:::tabs
```c
#include "mcmc_engine.h"
#include <stdio.h>

int main(void) {
    mcmc_config_t cfg = {
        .num_states = 4,
        .temperature = 1.0,
        .burn_in_steps = 50000,
        .sampling_steps = 2000000,
        .random_seed = 12345,
        .balance_tolerance = 1e-4
    };

    mcmc_engine_t *engine = NULL;
    if (mcmc_engine_create(&cfg, &engine) != MCMC_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації MCMC двигуна\n");
        return 1;
    }

    double energies[4] = {0.0, 1.5, 3.0, 0.5};
    mcmc_engine_set_energies(engine, energies, 4);

    if (mcmc_engine_run(engine) == MCMC_SUCCESS) {
        mcmc_balance_report_t report;
        mcmc_engine_verify_balance(engine, &report);

        printf("Максимальний дисбаланс потоків: %.8f\n", report.max_imbalance_flux);
        printf("Оцінка генерації ентропії dS/dt: %.8f\n", report.entropy_prod_rate);
        printf("Детальний баланс підтверджено: %s\n", report.is_balanced ? "ТАК" : "НІ");
    }

    mcmc_engine_destroy(engine);
    return 0;
}
```
```cpp
#include "mcmc_engine.hpp"
#include <iostream>

int main() {
    mcmc::Config cfg{
        .num_states = 4,
        .temperature = 1.0,
        .burn_in_steps = 50'000,
        .sampling_steps = 2'000'000,
        .random_seed = 12345,
        .balance_tolerance = 1e-4
    };

    auto engine_res = mcmc::Engine::create(cfg);
    if (!engine_res) {
        std::cerr << "Помилка створення MCMC двигуна\n";
        return 1;
    }

    auto engine = std::move(*engine_res);
    const std::vector<double> energies = {0.0, 1.5, 3.0, 0.5};
    engine->set_energies(energies);

    if (engine->run() == mcmc::ErrorCode::InvalidParam) {
        return 1;
    }

    auto report = engine->verify_balance();
    std::cout << "Максимальний дисбаланс C++: " << report.max_imbalance_flux << "\n";
    std::cout << "Оцінка генерації ентропії dS/dt: " << report.entropy_production_rate << "\n";
    std::cout << "Детальний баланс підтверджено: " << (report.is_balanced ? "ТАК" : "НІ") << "\n";

    return 0;
}
```
:::

## 6. Правила управління пам'яттю, потокобезпечність та продуктивність

1. **Управління пам'яттю (Memory Ownership):** Контекст `mcmc_engine_t` створюється динамічно у купі (heap). Викликач зобов'язаний звільнити пам'ять викликом `mcmc_engine_destroy()`. Спроба повторного виклику `mcmc_engine_destroy()` для одного й того самого вказівника призводить до неописаної поведінки. У C++ версії використовується шаблон RAII `std::unique_ptr` із власною функцією вилучення, що повністю виключає витоки пам'яті при виникненні винятків.
2. **Передача та копіювання даних:** Функція `mcmc_engine_set_energies()` копіює значення енергій у внутрішній буфер контексту. Викликач залишається власником переданого масиву і може безпечно видалити або модифікувати свій оригінальний масив одразу після завершення виклику.
3. **Багатопотоковість (Thread Safety):** Окремі екземпляри `mcmc_engine_t` є повністю незалежними і можуть паралельно оброблятися у різних потоках виконання (Thread-safe for distinct instances). Одночасне використання одного й того самого екземпляра з кількох потоків без зовнішньої синхронізації (наприклад м'ютекса `std::mutex`) заборонено.
4. **Продуктивність та масштабуваність:** Внутрішні масиви лічильників оптимізовані за вирівнюванням пам'яті для ефективного використання кеш-ліній процесора (L1/L2 cache efficiency). Для систем із великою кількістю станів `N > 10000` рекомендується використовувати розріджену матрицю переходів (sparse matrix format).
