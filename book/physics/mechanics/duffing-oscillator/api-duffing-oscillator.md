# 📋 Інтерфейс та програмний контракт обчислювального двигуна осцилятора Дуффінга

Цей документ визначає публічний програмний інтерфейс (API), структури даних, коди помилок, інваріанти виконання та інженерний контракт бібліотечного двигуна `libduffing` для чисельного розв'язання рівняння Дуффінга, проведення аналізу біфуркацій та генерації стробоскопічних перерізів Пуанкаре.

Бібліотека розроблена для застосування у високопродуктивних обчислювальних симуляторах, системах реального часу та модулях цифрової обробки сигналів МЕМС-сенсорів.

---

### Архітектура програмного контракту та рівні абстракції

Програмний інтерфейс `libduffing` розділено на два рівні абстракції:
1. **Низькорівневий C99 ABI інтерфейс:** Призначений для максимальної продуктивності, прямої інтеграції у вбудовані системи (embedded), драйвери та FFI-зв'язування з іншими мовами програмування (Python, Rust, Julia, C#). Використовує непрозорий вказівник `duffing_solver_t` для гарантії інкапсуляції стану.
2. **Високорівневий C++20 RAII інтерфейс:** Забезпечує строго строгу типобезпеку, відсутність витоків ресурсів завдяки семантиці переміщення (Move Semantics), роботу із сучасними контейнерами `std::vector` та шаблонами обробки помилок без винятків через `std::expected`.

---

### Публічні заголовки інтерфейсів (C99 ABI та C++20 RAII)

:::tabs
```c
/* duffing_engine.h — Публічний заголовок C-бібліотеки libduffing */
#ifndef DUFFING_ENGINE_H
#define DUFFING_ENGINE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Статуси виконання та коди помилок */
typedef enum {
    DUFFING_SUCCESS               =  0,
    DUFFING_ERROR_INVALID_PARAM   = -1,
    DUFFING_ERROR_NULL_POINTER    = -2,
    DUFFING_ERROR_NUMERICAL_DIVERGE = -3,
    DUFFING_ERROR_ALLOCATION_FAIL = -4
} duffing_status_t;

/* Конфігурація параметрів механічної системи */
typedef struct {
    double alpha;  /* лінійна жорсткість (позитивна для 1-ямного, негативна для 2-ямного) */
    double beta;   /* кубічна нелінійність (β != 0) */
    double delta;  /* коефіцієнт згасання (δ >= 0) */
    double gamma;  /* амплітуда зовнішнього збудження (γ >= 0) */
    double omega;  /* частота зовнішньої сили (ω > 0) */
} duffing_config_t;

/* Вектор фазового стану системи */
typedef struct {
    double x;      /* координата зміщення */
    double v;      /* швидкість */
    double t;      /* поточний час */
} duffing_state_t;

/* Непрозорий вказівник на обчислювальний контекст розв'язувача */
typedef struct duffing_solver duffing_solver_t;

/* Створення та ініціалізація екземпляра розв'язувача */
duffing_status_t duffing_solver_create(
    const duffing_config_t* config,
    duffing_state_t initial_state,
    double step_size,
    duffing_solver_t** out_solver
);

/* Виконання одного кроку інтегрування (RK4) */
duffing_status_t duffing_solver_step(duffing_solver_t* solver);

/* Пропуск перехідного процесу протягом вказаної кількості періодів */
duffing_status_t duffing_solver_run_transient(
    duffing_solver_t* solver,
    size_t num_periods
);

/* Заповнення масиву точками перерізу Пуанкаре (одна точка на кожен період) */
duffing_status_t duffing_solver_sample_poincare(
    duffing_solver_t* solver,
    duffing_state_t* out_points,
    size_t num_points,
    size_t steps_per_period
);

/* Зчитування поточного стану розв'язувача */
duffing_status_t duffing_solver_get_state(
    const duffing_solver_t* solver,
    duffing_state_t* out_state
);

/* Звільнення ресурсів розв'язувача */
void duffing_solver_destroy(duffing_solver_t* solver);

#ifdef __cplusplus
}
#endif

#endif /* DUFFING_ENGINE_H */
```
```cpp
// DuffingEngine.hpp — Об'єктно-орієнтована C++20 обгортка
#ifndef DUFFING_ENGINE_HPP
#define DUFFING_ENGINE_HPP

#include "duffing_engine.h"
#include <vector>
#include <span>
#include <expected>
#include <string>
#include <memory>

namespace duffing {

enum class ErrorCode {
    InvalidParam,
    NullPointer,
    NumericalDivergence,
    AllocationFailure
};

struct Config : public duffing_config_t {};
struct State  : public duffing_state_t {};

class Solver {
public:
    // RAII Створення: повертає std::expected з екземпляром розв'язувача або помилкою
    static std::expected<Solver, ErrorCode> create(
        const Config& config,
        State initialState,
        double stepSize) 
    {
        duffing_solver_t* rawSolver = nullptr;
        duffing_status_t st = duffing_solver_create(&config, initialState, stepSize, &rawSolver);
        if (st != DUFFING_SUCCESS) {
            return std::unexpected(mapStatus(st));
        }
        return Solver(rawSolver);
    }

    ~Solver() {
        if (handle_) {
            duffing_solver_destroy(handle_);
        }
    }

    Solver(const Solver&) = delete;
    Solver& operator=(const Solver&) = delete;

    Solver(Solver&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }

    Solver& operator=(Solver&& other) noexcept {
        if (this != &other) {
            if (handle_) duffing_solver_destroy(handle_);
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }

    // Виконання кроку
    std::expected<void, ErrorCode> step() noexcept {
        duffing_status_t st = duffing_solver_step(handle_);
        if (st != DUFFING_SUCCESS) return std::unexpected(mapStatus(st));
        return {};
    }

    // Відбір точок для перерізу Пуанкаре в std::vector
    std::expected<std::vector<State>, ErrorCode> generatePoincare(
        std::size_t numPoints,
        std::size_t stepsPerPeriod) 
    {
        std::vector<State> buffer(numPoints);
        duffing_status_t st = duffing_solver_sample_poincare(
            handle_,
            buffer.data(),
            numPoints,
            stepsPerPeriod
        );
        if (st != DUFFING_SUCCESS) {
            return std::unexpected(mapStatus(st));
        }
        return buffer;
    }

    [[nodiscard]] State getState() const noexcept {
        State s{};
        duffing_solver_get_state(handle_, &s);
        return s;
    }

private:
    explicit Solver(duffing_solver_t* handle) noexcept : handle_(handle) {}

    static ErrorCode mapStatus(duffing_status_t st) noexcept {
        switch (st) {
            case DUFFING_ERROR_INVALID_PARAM:     return ErrorCode::InvalidParam;
            case DUFFING_ERROR_NULL_POINTER:      return ErrorCode::NullPointer;
            case DUFFING_ERROR_NUMERICAL_DIVERGE: return ErrorCode::NumericalDivergence;
            default:                              return ErrorCode::AllocationFailure;
        }
    }

    duffing_solver_t* handle_{ nullptr };
};

} // namespace duffing

#endif // DUFFING_ENGINE_HPP
```
:::

---

### Детальний опис функціональних викликів C-API та C++ API

#### 1. `duffing_solver_create` та `duffing::Solver::create`
Призначені для виділення оперативної пам'яті під контекст розв'язувача, валідації параметрів механічної системи та ініціалізації початкового стану.
- **Аргументи:**
  - `config`: Вказівник на заповнену структуру `duffing_config_t`.
  - `initial_state`: Початкові значення координати, швидкості та часу.
  - `step_size`: Крок інтегрування `h` (повинен бути строго додатним і задовольняти умову стійкості).
  - `out_solver`: Вказівник на змінну вказівника, у яку буде записана адреса створеного об'єкта.
- **Повертане значення:** `DUFFING_SUCCESS` або відповідний код помилки при невалідних параметрах.
- **Послідовність виконання (Lifecycle Trace):**
  1. Перевірка вказівників `config` та `out_solver` на `NULL`.
  2. Перевірка параметрів: `config->omega > 0`, `config->delta >= 0`, `config->beta != 0`, `step_size > 0`.
  3. Виділення пам'яті за допомогою `malloc(sizeof(duffing_solver_t))`.
  4. Запис початкового стану та підрахунок похідних для першого кроку.

#### 2. `duffing_solver_step` та `duffing::Solver::step`
Виконує один чисельний крок інтегрування методом Рунге-Кутти 4-го порядку.
- **Модифікація стану:** Оновлює координату `x`, швидкість `v` та додає крок `h` до поточного часу `t`.
- **Перевірка стійкості:** Якщо в результаті обчислення `x` або `v` стають нескінченними або `NaN`, функція перериває виконання та повертає `DUFFING_ERROR_NUMERICAL_DIVERGE`.

#### 3. `duffing_solver_sample_poincare` та `duffing::Solver::generatePoincare`
Автоматизує процес фіксації точок перерізу Пуанкаре. Функція виконує внутрішній цикл інтегрування і зберігає стан системи рівно один раз на кожні `steps_per_period` кроків.
- **Безпека пам'яті:** У C-версії буфер `out_points` мусить бути попередньо виділений викликаючою стороною й мати розмір не менше `num_points * sizeof(duffing_state_t)`. У C++ версії вектор `std::vector<State>` створюється та повертається автоматично через семантику переміщення.
- **Простеження викликів:** Для кожної з `num_points` точок виконується внутрішній цикл із `steps_per_period` ітерацій виклику `duffing_solver_step`.

---

### Консольний інтерфейс утиліти (CLI CONTRACT)

Утиліта командного рядка `duffing_cli` надає можливість швидкого обчислення траєкторій та збереження точок перерізу Пуанкаре у текстові файли:

```shell
duffing_cli --alpha -1.0 --beta 1.0 --delta 0.2 --gamma 0.3 --omega 1.2 --pts 5000 --out poincare.dat
```

#### Параметри CLI:
- `--alpha <float>`: Лінійна жорсткість (за замовчуванням: `-1.0`).
- `--beta <float>`: Кубічна нелінійність (за замовчуванням: `1.0`).
- `--delta <float>`: Коефіцієнт згасання (за замовчуванням: `0.2`).
- `--gamma <float>`: Амплітуда зовнішнього збудження (за замовчуванням: `0.3`).
- `--omega <float>`: Частота зовнішньої сили (за замовчуванням: `1.2`).
- `--pts <int>`: Кількість точок Пуанкаре для генерації (за замовчуванням: `2000`).
- `--transient <int>`: Кількість періодів перехідного режиму для відкидання (за замовчуванням: `200`).
- `--out <filepath>`: Шлях до вихідного текстового файлу.

---

### Організація оперативної пам'яті, кеш-локальність та SIMD-векторизація

Обчислювальний двигун `libduffing` оптимізовано для виконання на сучасних процесорних архітектурах із багаторівневою кеш-пам'яттю (L1/L2/L3):

1. **Вирівнювання структур у пам'яті (Memory Alignment):**
   Структура `duffing_state_t` вирівняна за межею 64 бітів (8 байтів), що збігається з розміром числа подвійної точності `double`. При збереженні точок у масив `out_points` вони розміщуються в пам'яті суцільним блоком (Contiguous Memory Array). Це дозволяє процесору завантажувати дані в L1-кеш лінійками по 64 байти (кеш-лінія містить 8 чисел `double`), мінімізуючи промахи кешу (Cache Misses).

2. **SIMD Векторизація (AVX2 / AVX-512):**
   При масовому моделюванні ансамблю з тисяч незалежних осциляторів Дуффінга (наприклад, для розрахунку сітки басейнів притягання чи біфуркаційних діаграм) обчислення виконуються у формі Structure-of-Arrays (SoA) замість Array-of-Structures (AoS). Це дозволяє векторним інструкціям AVX-512 обробляти 8 елементів `double` паралельно за один такт процесора.

3. **Стратегія обробки помилок та нестійкості:**
   При роботі з нелінійними системами завжди існує ризик чисельної розбіжності. При виявленні `NaN` або `INF` під час обчислення `k₁..k₄` інтегратор не негайно перериває процес аварійно, а повертає код `DUFFING_ERROR_NUMERICAL_DIVERGE`, залишаючи останній стабільний стан у структурі `out_state` для подальшого аналізу.

---

### Таблиця параметрів конфігурації та інженерних обмежень

Нижче наведено повні вимоги до діапазонів вхідних параметрів системи та кроку інтегрування:

| Параметр | Поле структури | Тип | Валідна область | Рекомендований діапазон | Опис фізичного значення |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Лінійна жорсткість** | `alpha` | `double` | `(-∞, +∞)` | `[-2.0, 2.0]` | Визначає основну частоту (`α > 0`) або сідловий бар'єр (`α < 0`). |
| **Кубічна жорсткість** | `beta` | `double` | `(-∞, +∞), β ≠ 0` | `[0.1, 5.0]` | Визначає характер жорсткості: `β > 0` (жорстка), `β < 0` (м'яка). |
| **Згасання** | `delta` | `double` | `[0.0, +∞)` | `[0.05, 0.5]` | Коефіцієнт в'язкого тертя та дисипації енергії. |
| **Амплітуда сили** | `gamma` | `double` | `[0.0, +∞)` | `[0.0, 1.5]` | Амплітуда зовнішнього гармонічного збудження. |
| **Частота сили** | `omega` | `double` | `(0.0, +∞)` | `[0.5, 3.0]` | Кутова частота зовнішньої збуджуючої сили. |
| **Крок часу** | `step_size` | `double` | `(0.0, 0.1 / ω]` | `(2π/ω) / 500` | Крок інтегрування `h` методу Рунге-Кутти RK4. |

---

### Коди відповідей та інваріанти виконання

#### Специфікація коду помилки `duffing_status_t`

1. `DUFFING_SUCCESS (0)`: Операція завершена успішно. Всі вхідні дані валідні, стан інтегратора залишається коректним.
2. `DUFFING_ERROR_INVALID_PARAM (-1)`: Передано недопустиме значення параметра (наприклад, `omega <= 0`, `step_size <= 0` або `beta == 0`).
3. `DUFFING_ERROR_NULL_POINTER (-2)`: Один із переданих вказівників на структури або масиви дорівнює `NULL`.
4. `DUFFING_ERROR_NUMERICAL_DIVERGE (-3)`: Чисельне рішення розійшлося (координата `|x| > 1e6` або переповнення `NaN`/`INF`). Зазвичай виникає при надто великому кроці `h` або від'ємній кубічній нелінійності.
5. `DUFFING_ERROR_ALLOCATION_FAIL (-4)`: Не вдалося виділити оперативну пам'ять у системному хепі.

#### Потокобезпечність та інваріанти виконання

- **Thread-Safety (Потокобезпечність):** Окремі екземпляри `duffing_solver_t` повністю ізольовані й можуть паралельно виконуватися в різних потоках без синхронізації (No Shared Global State). Виклики методів над одним і тим самим екземпляром з різних потоках вимагають зовнішнього мутекса.
- **Гарантії пам'яті:** Функції бібліотеки не створюють прихованих витоків пам'яті. Метод `duffing_solver_destroy` гарантовано вивільняє 100% ресурсів, виділених при `create`.
