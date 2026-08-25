# 📋 Інтерфейс та API бібліотеки чисельного розв'язувача рівняння Матьє

У цій довідковій вставці описано програмний інтерфейс (API), структури даних, параметри конфігурації, коди помилок та специфікацію функцій бібліотеки чисельного аналізу рівняння Матьє `libmathieu`. Довідник призначений для розробників та дослідників, які інтегрують обчислення коефіцієнтів стійкості, функцій Матьє та показників Флоке у фізичні симуляції (пастки іонів, параметричні маятники, акустичні мембрани, мікроелектромеханічні резонатори MEMS та високочастотні електронні системи).

Бібліотека надає C-сумісний інтерфейс розширюваного ABI (Application Binary Interface) з гарантією зворотної бінарної сумісності та ідіоматичну C++20 обгортку у просторі імен `mathieu::solver`.

## Архітектурний огляд та специфікація ABI

Дизайн бібліотеки `libmathieu` побудовано за принципом відсутності прихованого глобального стану (англ. *stateless architecture*). Усі обчислювальні функції є строго детермінованими чистими функціями, чий результат визначається виключно вхідними параметрами та структурою конфігурації `MathieuConfig`. Це гарантує повну безпеку викликів у багатопотокових середовищах без використання блокувань або м'ютексів.

Для забезпечення високої обчислювальної ефективності розрахунок поодиноких точок простору параметрів `(q, a)` здійснюється виключно у стеку виконання без жодного виділення пам'яті у динамічній купі (англ. *zero heap allocation*). Динамічна пам'ять виділяється лише при генерації двовимірних прямокутних сіток стійкості `MathieuGrid` за допомогою функцій `mathieu_grid_allocate` та звільняється викликом `mathieu_grid_free`.

Таке розділення пам'яті дозволяє безпечно інтегрувати бібліотеку у фізичні двигуни реального часу (наприклад, для розрахунку поведінки іонів у квантовому симуляторі чи вібрацій конструкцій) без ризику фрагментації пам'яті або затримок, пов'язаних із роботою складальника сміття.

## Структури даних та основні типи

Основними елементами управління обчислювальним процесом у бібліотеці є переліки режимів `MathieuMethod`, кодів повернення `MathieuStatus` та станів стійкості `MathieuStabilityState`. 

Конфігураційна структура `MathieuConfig` задає чисельні допуски та ліміти:
* `method` вибирає один з трьох алгоритмів: класичний RK4 з фіксованим кроком, адаптивний метод Дормана — Принса RK45 або спектральний метод ланцюгових дробів Інса.
* `period_steps` визначає кількість сіткових інтервалів на півперіоді `π` (за замовчуванням `1000`).
* `abs_tolerance` та `rel_tolerance` встановлюють межі абсолютної та відносної похибки для адаптивних методів розрахунку.
* `max_iterations` обмежує кількість ітерацій при обчисленні нескінченних ланцюгових дробів.

Результат аналізу фазової точки `MathieuPointResult` містить не лише підсумковий прапорець стійкості `state`, але й повну матрицю монодромії `monodromy[2][2]`, її слід `trace`, а також вираховані характеристики Флоке `floquet_exponent` (для нестійких режимів) та `floquet_nu` (для квазіперіодичних стійких режимів).

Порівняльне визначення структур даних у C ABI та C++20 обгортці:

:::tabs
```c
/* C ABI переліки та структури даних бібліотеки libmathieu */
typedef enum {
    MATHIEU_SUCCESS               =  0,  /* Успішне виконання */
    MATHIEU_ERR_INVALID_PARAM     = -1,  /* Некоректні вхідні параметри */
    MATHIEU_ERR_NO_CONVERGENCE    = -2,  /* Ланцюговий дріб не збігся */
    MATHIEU_ERR_OUT_OF_MEMORY     = -3,  /* Помилка виділення пам'яті */
    MATHIEU_ERR_DIVERGENCE        = -4   /* Чисельна нестійкість розв'язку */
} MathieuStatus;

typedef enum {
    MATHIEU_METHOD_RK4            = 0,  /* Метод Рунге — Кутти 4-го порядку */
    MATHIEU_METHOD_DORMAND_PRINCE = 1,  /* Метод Дормана — Принса RK45 */
    MATHIEU_METHOD_CONT_FRACTIONS = 2   /* Метод ланцюгових дробів Інса */
} MathieuMethod;

typedef enum {
    MATHIEU_STATE_STABLE          = 0,  /* Область стійкості (|Tr(M)| < 2) */
    MATHIEU_STATE_UNSTABLE        = 1,  /* Область параметричного резонансу */
    MATHIEU_STATE_BOUNDARY        = 2   /* Точна межа стійкості */
} MathieuStabilityState;

typedef struct {
    MathieuMethod method;       /* Вибраний алгоритм обчислення */
    int period_steps;           /* Кількість кроків на період pi */
    double abs_tolerance;       /* Абсолютна точність */
    double rel_tolerance;       /* Відносна точність */
    int max_iterations;         /* Максимальна кількість ітерацій */
} MathieuConfig;

typedef struct {
    double a;                   /* Спектральний параметр a */
    double q;                   /* Параметр модуляції q */
    double monodromy[2][2];     /* Матриця монодромії M = Φ(pi) */
    double trace;               /* Слід Tr(M) */
    double floquet_exponent;    /* Дійсний показник Флоке mu */
    double floquet_nu;          /* Уявний показник nu */
    MathieuStabilityState state;/* Статус стійкості */
} MathieuPointResult;

typedef struct {
    double q_min, q_max;        /* Діапазон параметра q */
    double a_min, a_max;        /* Діапазон параметра a */
    size_t q_res, a_res;        /* Роздільна здатність */
    MathieuStabilityState* grid;/* Динамічний масив сітки */
} MathieuGrid;
```
```cpp
// C++20 Типи даних та структури конфігурації
#include <array>
#include <vector>
#include <cstddef>

namespace mathieu::solver {

enum class Status : int {
    Success = 0,
    InvalidParam = -1,
    NoConvergence = -2,
    OutOfMemory = -3,
    Divergence = -4
};

enum class Method {
    RK4 = 0,
    DormandPrince = 1,
    ContinuedFractions = 2
};

enum class StabilityState {
    Stable = 0,
    Unstable = 1,
    Boundary = 2
};

struct Config {
    Method method{Method::RK4};
    int period_steps{1000};
    double abs_tolerance{1e-9};
    double rel_tolerance{1e-8};
    int max_iterations{500};
};

struct PointResult {
    double a{0.0};
    double q{0.0};
    std::array<std::array<double, 2>, 2> monodromy{};
    double trace{0.0};
    double floquet_exponent{0.0};
    double floquet_nu{0.0};
    StabilityState state{StabilityState::Stable};
};

struct Grid {
    double q_min{0.0}, q_max{1.0};
    double a_min{0.0}, a_max{1.0};
    std::size_t q_res{100}, a_res{100};
    std::vector<StabilityState> data{};
};

} // namespace mathieu::solver
```
:::

## Специфікація функцій та пробіг сигнатур API

Кожна функція у C API повертає статус `MathieuStatus`, а обчислені значення передаються через вихідні вказівники `result`, `a_out` чи `grid_out`.

1. **`mathieu_config_default`:** Заповнює конфігурацію дефолтними параметрами, які є оптимальними для більшості фізичних задач.
2. **`mathieu_analyze_point`:** Головна функція аналізу. Здійснює інтегрування двох базових станів на періоді `π`, розраховує матрицю монодромії та вираховує півслід `Tr(M)/2`.
3. **`mathieu_eigenvalue_a` та `mathieu_eigenvalue_b`:** Використовують нескінченні ланцюгові дроби для знаходження точних спектральних меж `a_n(q)` та `b_n(q)` без інтегрування у часі.
4. **`mathieu_grid_allocate`, `mathieu_grid_compute` та `mathieu_grid_free`:** Спеціалізоване триплетне сімейство функцій для створення двовимірних карт стійкості у прямокутній області `[q_min, q_max] × [a_min, a_max]`.
5. **`mathieu_floquet_exponent` та `mathieu_fourier_coefficients`:** Обчислюють спектральні характеристики розв'язку (показники Флоке та коефіцієнти ряду Фур'є).

Порівняння сигнатур функцій у C ABI та C++ класи `MathieuSolver`:

:::tabs
```c
/* C ABI Сигнатури функцій бібліотеки libmathieu */

/* Управління конфігурацією */
MathieuConfig mathieu_config_default(void);

/* Обчислення монодромії та аналіз точки (q, a) */
MathieuStatus mathieu_analyze_point(
    double a, double q,
    const MathieuConfig* config,
    MathieuPointResult* result
);

MathieuStatus mathieu_compute_monodromy(
    double a, double q, double z_period,
    const MathieuConfig* config,
    double monodromy_out[2][2]
);

/* Обчислення власних значень a_n(q) та b_n(q) */
MathieuStatus mathieu_eigenvalue_a(
    int order_n, double q,
    const MathieuConfig* config,
    double* a_out
);

MathieuStatus mathieu_eigenvalue_b(
    int order_n, double q,
    const MathieuConfig* config,
    double* b_out
);

/* Управління сіткою стійкості */
MathieuStatus mathieu_grid_allocate(
    size_t a_res, size_t q_res,
    MathieuGrid** grid_out
);

MathieuStatus mathieu_grid_compute(
    double q_min, double q_max,
    double a_min, double a_max,
    const MathieuConfig* config,
    MathieuGrid* grid
);

void mathieu_grid_free(MathieuGrid* grid);

/* Спектральні показники та коефіцієнти Фур'є */
MathieuStatus mathieu_floquet_exponent(
    double a, double q,
    const MathieuConfig* config,
    double* mu_out, double* nu_out
);

MathieuStatus mathieu_fourier_coefficients(
    int order_n, double q,
    double* coeffs_out, size_t max_coeffs
);
```
```cpp
// C++20 Інтерфейс класу MathieuSolver у просторі імен mathieu::solver
#include <vector>
#include <array>
#include <expected>

namespace mathieu::solver {

class MathieuSolver {
public:
    explicit MathieuSolver(Config config = {}) : config_(config) {}

    // Обчислення аналізу точки
    [[nodiscard]] PointResult analyze_point(double a, double q) const;

    // Обчислення власних значень a_n(q) та b_n(q)
    [[nodiscard]] double eigenvalue_a(int order_n, double q) const;
    [[nodiscard]] double eigenvalue_b(int order_n, double q) const;

    // Побудова двовимірної сітки стійкості
    [[nodiscard]] Grid compute_grid(
        double q_min, double q_max, std::size_t q_res,
        double a_min, double a_max, std::size_t a_res
    ) const;

    // Показники Флоке та коефіцієнти Фур'є
    [[nodiscard]] std::pair<double, double> floquet_exponents(double a, double q) const;
    [[nodiscard]] std::vector<double> fourier_coefficients(int order_n, double q) const;

private:
    Config config_;
};

} // namespace mathieu::solver
```
:::

## Валідація параметрів, крайові випадки та обробка помилок

Під час виклику обчислювальних функцій бібліотека `libmathieu` проводить сувору перевірку вхідних аргументів (англ. *precondition assertion*):

1. **Перевірка невід'ємності кроків та частот:** Якщо `period_steps <= 0` або `max_iterations <= 0`, функція повертає код `MATHIEU_ERR_INVALID_PARAM` без виконання інтегрування.
2. **Обробка переповнення та нестійкості (Overflow Protection):** При інтегруванні нестійких режимів у глибині язиків нестійкості (коли `μ · π > 700`) фазова змінна `y(π)` може перевищити максимальне значення з плаваючою крапкою `IEEE 754` (`10³⁰⁸`). У цьому випадку інтегратор зупиняє розрахунок, фіксує статус `MATHIEU_STATE_UNSTABLE` та повертає код `MATHIEU_ERR_DIVERGENCE`, запобігаючи генерації нечислових значень `NaN` чи `Inf`.
3. **Крайові значення ланцюгового дробу:** Якщо метод Інса не досягає відносної точності `abs_tolerance` за задану кількість ітерацій `max_iterations` (що можливе при `q > 50`), функція повертає код `MATHIEU_ERR_NO_CONVERGENCE`.

---

## Інтеграція у проєкти та збирання через CMake

Для підключення бібліотеки `libmathieu` до C та C++ проєктів використовується стандартний сценарій CMake:

```cmake
find_package(MathieuSolver CONFIG REQUIRED)
target_link_libraries(my_physics_sim PRIVATE MathieuSolver::mathieu_solver)
```

Матричний розрахунок сітки підтримує паралельні обчислення через OpenMP або POSIX threads, що дозволяє швидко генерувати карти стійкості для графічних інтерфейсів симулятора у реальному часі.

---

## Приклад використання API C++ у проєктах пасток іонів чи вібростендів

Нижче наведено фрагмент коду, який перевіряє стійкість робочої точки квадрупольної пастки Поля для іонів берилію:

```cpp
#include <iostream>
#include <mathieu/solver.hpp>

int main() {
    using namespace mathieu::solver;

    // Створення розв'язувача з підвищеною точністю RK4 (2000 кроків за період)
    Config config;
    config.period_steps = 2000;
    MathieuSolver solver(config);

    // Робочі параметри пастки Поля: a = 0.237, q = 0.706
    double a_paul = 0.237;
    double q_paul = 0.706;

    PointResult res = solver.analyze_point(a_paul, q_paul);

    std::cout << "Аналіз робочої точки іонної пастки Поля:\n";
    std::cout << "Слід монодромії Tr(M): " << res.trace << "\n";
    
    if (res.state == StabilityState::Stable) {
        std::cout << "Статус: СТІЙКИЙ РЕЖИМ (Іон утримується в пастці)\n";
        std::cout << "Частота мікроколивань nu: " << res.floquet_nu << "\n";
    } else {
        std::cout << "Статус: НЕСТІЙКИЙ РЕЖИМ (Іон вилітає на електроди!)\n";
        std::cout << "Показник вильоту (μ): " << res.floquet_exponent << "\n";
    }

    return 0;
}
```

---

## Гарантії потокобезпечності, обробка помилок та ABI

1. **Потокобезпечність (Thread-Safety):** Усі обчислювальні функції `mathieu_analyze_point`, `mathieu_eigenvalue_a` та `mathieu_eigenvalue_b` є чисто функціональними (pure functions), не використовують глобального чи статичного mutable-стану й можуть безпечно викликатися паралельно з багатьох потоків (`OpenMP`, `std::jthread`, `pthread`).
2. **Обробка виняткових ситуацій:** C-інтерфейс бібліотеки ніколи не викидає винятків (exceptions-safe C ABI). Усі помилки передаються через повернення статусного коду `MathieuStatus`. В обгортці C++ виклики повертають `std::expected` або викидають `std::runtime_error` у випадку передачі невалідних параметрів, таких як від'ємні розмірності сітки чи незбіжні ланцюгові дроби.
3. **Пам'ять:** Обчислення поодиноких точок не виконує жодних динамічних виділень пам'яті у купі (`heap-allocation-free`), працюючи виключно у стеку.
4. **Гарантії зворотної сумісності ABI:** Структури даних мають фіксований розмір та вирівнювання за стандартами C99/C11, що дозволяє підключати динамічні бібліотеки `.so` / `.dll` у середовищах Python (через `ctypes` або `cffi`), Julia, Rust та C# / .NET без додаткових трансляторів.
