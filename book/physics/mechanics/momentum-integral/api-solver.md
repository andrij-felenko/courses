# 📋 Інтерфейс програмного модуля розв'язувача рівняння імпульсу

Цей довідник описує специфікацію публічного інтерфейсу програмного модуля `libmomentum`, призначеного для обчислення характеристик ламінарного та турбулентного примежового шару інтегральними методами Кармана, Твейтса та Хеда.

Модуль надає уніфіковані структури даних, функції конфігурації, процедури обчислення та обробку помилок як для чистого середовища C (C99+), так і для ідіоматичного C++ (C++17/C++20).

## 1. Архітектурні принципи та призначення модуля

Програмний бібліотечний модуль `libmomentum` спроектовано як високопродуктивний, безпотоково-безпечний (reentrant/thread-safe) розв'язувач рівняння імпульсу примежового шару. Основним завданням модуля є приймання геометричної сітки `x` та розподілу потенційної швидкості `U_e(x)`, чисельне розв'язання рівнянь імпульсу і формування повного набору аеродинамічних характеристик (товщин `θ` та `δ*`, коефіцієнтів `H` і `C_f`, напруження тертя `τ_w` та координати відриву `x_sep`).

Архітектура модуля розділена на два рівні:
1. **Низькорівневе C ABI (`momentum_solver.h`)**: Забезпечує пряму сумісність із мовою C99, гарантує стабільний бінарний інтерфейс (ABI) без спотворення імен функцій (*name mangling*) та дозволяє легку інтеграцію з мовами високого рівня (Python через `ctypes` або `cffi`, Rust через `bindgen`, Julia, Fortran).
2. **Високорівнева C++ Обгортка (`momentum_solver.hpp`)**: Використовує можливості стандарту C++17 (`std::span`, `std::expected`, `std::string_view`, RAII, семантику переміщення), усуваючи ризики витоків пам'яті та сирих вказівників.

## 2. Перелік режимів розрахунку та статусів

Розв'язувач підтримує декілька режимів моделювання примежового шару:

| Режим (`bl_solver_mode_t`) | Опис фізичної моделі | Обчислювальна складність |
| :--- | :--- | :--- |
| `BL_MODE_THWAITES_LAMINAR` | Ламінарний однопараметричний метод Твейтса (квадратурна формула) | `O(N)` часова складність |
| `BL_MODE_POHLHAUSEN_LAMINAR` | Метод Полгаузена з поліномом 4-го степеня та диференціальним кроком | `O(N)` часова складність |
| `BL_MODE_HEAD_TURBULENT` | Турбулентний метод затягування Хеда (система двох ODE) | `O(N)` з кроком Рунге — Кутти |
| `BL_MODE_COUPLED_TRANSITION` | Комбінований розрахунок з автопереходом за критерієм Мішеля або `e^N` | `O(N)` з автоматичним переключенням |

### Коди статусу та помилок (`bl_status_t`)

Для детальної діагностики результатів виконання функції повертають строгі коди помилок:

| Код статусу | Числове значення | Фізична та програмна причина виникнення |
| :--- | :--- | :--- |
| `BL_SUCCESS` | `0` | Розрахунок виконано успішно по всій довжині сітки |
| `BL_ERROR_NULL_POINTER` | `-1` | Передано нульовий вказівник `NULL` у критичний параметр функції |
| `BL_ERROR_INVALID_GRID` | `-2` | Сітка по координаті `x` не є строго монотонною або кількість точок `N < 2` |
| `BL_ERROR_INVALID_VISCOSITY`| `-3` | Значення в'язкості `nu <= 0` або густини `rho <= 0` є нефізичними |
| `BL_ERROR_SEPARATION` | `-4` | Виявлено ламінарний відрив (`λ_T ≤ -0.09`), і конфігурація вимагала зупинки |
| `BL_ERROR_CONVERGENCE` | `-5` | Чисельний розв'язок не досяг збіжності за виділену кількість ітерацій |

## 3. Детальний опис структур даних

### Структура `bl_fluid_properties_t`
Визначає фізичні властивості робочого середовища:
- `density` (`ρ`): Густина флюїду в кг/м³. Для нормального повітря при стандартних умовах `1.225` кг/м³, для прісної води `998.2` кг/м³.
- `kinematic_viscosity` (`ν`): Кінематична в'язкість `ν = μ / ρ` у м²/с. Для повітря `1.5e-5` м²/с, для води `1.0e-6` м²/с.
- `reynolds_critical` (`Re_crit`): Безрозмірне критичне число Рейнольдса, при досягненні якого моделюється ламінарно-турбулентний перехід (значення за замовчуванням `5.0e5`).

### Структура `bl_solver_config_t`
Визначає налаштування алгоритму розв'язання:
- `mode`: Обраний алгоритмічний режим розрахунку з переліку `bl_solver_mode_t`.
- `enable_separation_stop`: Булевий прапорець (1 або 0). Якщо встановлено в `1`, чисельне інтегрування негайно зупиняється при виявленні точки відриву (`λ_T ≤ -0.09`), а координата фіксується в полі `x_separation`. Якщо встановлено в `0`, розрахунок продовжується до кінця сітки з фіксацією граничних значень.
- `initial_theta`: Початкова товщина втрати імпульсу `θ(0)` в метрах на передній кромці. Якщо дорівнює `0.0`, товщина розраховується автоматично за аналітичними формулами точки гальмування.

### Структура `bl_point_result_t`
Містить вихідні фізичні параметри примежового шару для кожної точки сітки `x`:
- `x`: Поздовжня координата точки на поверхні, м.
- `U_e`: Зовнішня швидкість потенційного потоку в цій точці, м/с.
- `dUe_dx`: Похідна (градієнт) зовнішньої швидкості за координатою `x`, 1/с.
- `theta` (`θ`): Розрахована товщина втрати імпульсу, м.
- `delta_star` (`δ*`): Розрахована товщина зміщення `δ* = H · θ`, м.
- `H`: Безрозмірний коефіцієнт форми профілю швидкості.
- `C_f`: Місцевий коефіцієнт поверхневого тертя `τ_w / (0.5 · ρ · U_e²)`.
- `tau_w`: Напруження тертя на стінці в Паскалях (`Па = Н/м²`).
- `is_separated`: Прапорець, який приймає значення `1`, якщо в цій точці виявлено відрив течії.
- `is_turbulent`: Прапорець, який приймає значення `1`, якщо режим течії в цій точці є турбулентним.

### Структура `bl_solution_mesh_t`
Зберігає повний результуючий масив обчислених точок та загальні інтегральні характеристики течії:
- `points`: Динамічний масив обчислених точок типу `bl_point_result_t` розміром `count`.
- `count`: Кількість точок у розрахованій сітці.
- `x_separation`: Координата `x` точки відриву примежового шару (в метрах). Якщо відрив не стався по всій довжині поверхні, містить значення `-1.0`.
- `total_friction_drag`: Сумарна сила поверхневого тертя, проінтегрована вздовж всієї поверхні на один метр розмаху (у Ньютонах на метр, Н/м).

## 4. Заголовочні файли інтерфейсу

Нижче наведено повністю документовані заголовочні файли мовами C та C++.

:::tabs
```c
#ifndef MOMENTUM_SOLVER_H
#define MOMENTUM_SOLVER_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BL_SUCCESS = 0,
    BL_ERROR_NULL_POINTER = -1,
    BL_ERROR_INVALID_GRID = -2,
    BL_ERROR_INVALID_VISCOSITY = -3,
    BL_ERROR_SEPARATION = -4,
    BL_ERROR_CONVERGENCE = -5
} bl_status_t;

typedef enum {
    BL_MODE_THWAITES_LAMINAR = 0,
    BL_MODE_POHLHAUSEN_LAMINAR = 1,
    BL_MODE_HEAD_TURBULENT = 2,
    BL_MODE_COUPLED_TRANSITION = 3
} bl_solver_mode_t;

typedef struct {
    double density;              /* Густина флюїду rho, [кг/м³] */
    double kinematic_viscosity;  /* Кінематична в'язкість nu, [м²/с] */
    double reynolds_critical;    /* Критичне число Рейнольдса переходу */
} bl_fluid_properties_t;

typedef struct {
    bl_solver_mode_t mode;       /* Алгоритм розв'язання */
    int enable_separation_stop;  /* Зупиняти розрахунок при відриві (1 - так, 0 - ні) */
    double initial_theta;        /* Початкова товщина втрати імпульсу, [м] */
} bl_solver_config_t;

typedef struct {
    double x;                    /* Поздовжня координата, [м] */
    double U_e;                  /* Зовнішня швидкість, [м/с] */
    double dUe_dx;               /* Градієнт швидкості, [1/с] */
    double theta;                /* Товщина втрати імпульсу, [м] */
    double delta_star;           /* Товщина зміщення, [м] */
    double H;                    /* Коефіцієнт форми (delta_star / theta) */
    double C_f;                  /* Коефіцієнт поверхневого тертя */
    double tau_w;                /* Напруження тертя на стінці, [Па] */
    int is_separated;            /* 1 якщо в цій точці спостерігається відрив */
    int is_turbulent;            /* 1 якщо режим течії турбулентний */
} bl_point_result_t;

typedef struct {
    bl_point_result_t *points;   /* Динамічний масив результатів */
    size_t count;                /* Кількість оброблених точок */
    double x_separation;         /* Координата відриву (якщо стався, інакше -1.0) */
    double total_friction_drag;  /* Сумарний опір тертя на один метр ширини, [Н/м] */
} bl_solution_mesh_t;

/**
 * @brief Ініціалізація конфігурації розв'язувача за замовчуванням
 */
bl_status_t bl_config_init_default(bl_solver_config_t *config);

/**
 * @brief Виконання розрахунку примежового шару уздовж заданої сітки
 * 
 * @param fluid Параметри середовища (густина, в'язкість)
 * @param config Налаштування розв'язувача
 * @param x_grid Масив координат точок x, [м]
 * @param U_e_grid Масив зовнішніх швидкостей, [м/с]
 * @param dUe_dx_grid Масив градієнтів швидкостей, [1/с]
 * @param n_points Кількість точок сітки
 * @param out_mesh Структура для запису вихідних результатів
 * @return bl_status_t Код завершення розрахунку
 */
bl_status_t bl_solve_boundary_layer(
    const bl_fluid_properties_t *fluid,
    const bl_solver_config_t *config,
    const double *x_grid,
    const double *U_e_grid,
    const double *dUe_dx_grid,
    size_t n_points,
    bl_solution_mesh_t *out_mesh
);

/**
 * @brief Звільнення пам'яті вихідної сітки результатів
 */
void bl_mesh_free(bl_solution_mesh_t *mesh);

/**
 * @brief Отримання текстового опису коду статусу
 */
const char* bl_status_to_string(bl_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* MOMENTUM_SOLVER_H */
```
```cpp
#ifndef MOMENTUM_SOLVER_HPP
#define MOMENTUM_SOLVER_HPP

#include <vector>
#include <span >
#include <string_view>
#include <expected>
#include <system_error>

namespace momentum {

enum class Status {
    Success = 0,
    NullPointer = -1,
    InvalidGrid = -2,
    InvalidViscosity = -3,
    SeparationDetected = -4,
    ConvergenceFailed = -5
};

enum class SolverMode {
    ThwaitesLaminar,
    PohlhausenLaminar,
    HeadTurbulent,
    CoupledTransition
};

struct FluidProperties {
    double density{1.225};                 // кг/м³ (повітря за замовчуванням)
    double kinematic_viscosity{1.5e-5};    // м²/с
    double reynolds_critical{5.0e5};
};

struct SolverConfig {
    SolverMode mode{SolverMode::ThwaitesLaminar};
    bool stop_on_separation{true};
    double initial_theta{1.0e-6};
};

struct PointInput {
    double x{0.0};
    double U_e{0.0};
    double dUe_dx{0.0};
};

struct PointResult {
    double x{0.0};
    double U_e{0.0};
    double dUe_dx{0.0};
    double theta{0.0};
    double delta_star{0.0};
    double H{2.59};
    double C_f{0.0};
    double tau_w{0.0};
    bool is_separated{false};
    bool is_turbulent{false};
};

struct SolutionSummary {
    std::vector<PointResult> points;
    double separation_x{-1.0};
    double total_friction_drag{0.0};
};

class BoundaryLayerSolver {
public:
    explicit BoundaryLayerSolver(FluidProperties fluid, SolverConfig config = {})
        : fluid_(fluid), config_(config) {}

    [[nodiscard]] std::expected<SolutionSummary, Status> solve(
        std::span<const PointInput> grid
    ) const;

    void set_config(const SolverConfig& config) { config_ = config; }
    [[nodiscard]] const SolverConfig& config() const noexcept { return config_; }
    [[nodiscard]] const FluidProperties& fluid() const noexcept { return fluid_; }

private:
    FluidProperties fluid_;
    SolverConfig config_;
};

[[nodiscard]] std::string_view to_string(Status status) noexcept;

} // namespace momentum

#endif // MOMENTUM_SOLVER_HPP
```
:::

## 5. Обробка помилок та правила валідації вхідних даних

При кожному виклику розв'язувача `bl_solve_boundary_layer` (або методу `solve` у C++) проводиться суворий контроль вхідних даних перед початком чисельних обчислень:

1. **Контроль вказівників**: Якщо будь-який із масивів `x_grid`, `U_e_grid`, `dUe_dx_grid` або результатний об'єкт є `NULL` (або порожнім `std::span`), розв'язувач негайно повертає код `BL_ERROR_NULL_POINTER` (`Status::NullPointer`).
2. **Валідація сітки**: Сітка точок `x` повинна мати щонайменше 2 точки (`n_points >= 2`) і бути строго монотонно зростаючою (`x[i] > x[i-1]`). Якщо виявлено немонотонність або від'ємний крок сітки `dx <= 0`, повертається код `BL_ERROR_INVALID_GRID`.
3. **Перевірка в'язкості та густини**: Фізичні параметри флюїду повинно бути строго додатними: `nu > 0.0` та `rho > 0.0`. В іншому випадку повертається код `BL_ERROR_INVALID_VISCOSITY`.
4. **Обробка відриву**: Якщо під час чисельного інтегрування виявлено `λ_T ≤ -0.09` і в конфігурації увімкнено прапорець `enable_separation_stop = 1`, обчислення припиняються, у полі `x_separation` фіксується координата точки відриву, а функція повертає код `BL_ERROR_SEPARATION`.

## 6. Потокова безпека, керування пам'яттю та векторне прискорення

### Потокова безпека (Thread-Safety)
Усі функції бібліотеки `libmomentum` є строго реінтерабельними та чисто функціональними. Вони не використовують глобальний стан, статичні змінні або приховані мутекси. Кілька паралельних потоків виконання (наприклад, у середовищі OpenMP або `std::async`) можуть одночасно викликати процедури розрахунку для різних аеродинамічних профілів без будь-якого блокування.

### Модель керування пам'яттю
- **У мові C**: Функція `bl_solve_boundary_layer` виділяє пам'ять під динамічний масив `points` всередині структури `bl_solution_mesh_t` за допомогою `malloc`. Користувач зобов'язаний звільнити цю пам'ять після закінчення роботи шляхом виклику функції `bl_mesh_free(out_mesh)`.
- **У мові C++**: Керування пам'яттю є повністю автоматичним за принципом RAII. Результуючий вектор `std::vector<PointResult>` звільняє виділену пам'ять у своєму деструкторі при виході з області видимості, що унеможливлює витоки пам'яті.

### Оптимізація вирівнювання пам'яті та SIMD
Двовимірні масиви результатів вирівнюються за межами 64 байт (Cache line size) для прискорення автоматичної векторної обробки SIMD-інструкціями (AVX-2 / AVX-512). При обробці великих аеродинамічних сіток з тисячами точок це зменшує затримки доступу до оперативної пам'яті.

## 7. Повний інтеграційний приклад мовою C++

Нижче наведено практичний приклад використання C++ API бібліотеки `libmomentum` для обчислення опору тертя плоскої пластини:

```cpp
#include "momentum_solver.hpp"
#include <iostream>
#include <vector>
#include <iomanip>

int main() {
    using namespace momentum;

    // 1. Задання фізичних властивостей середовища (повітря за нормальних умов)
    FluidProperties air{
        .density = 1.225,              // кг/м³
        .kinematic_viscosity = 1.5e-5  // м²/с
    };

    // 2. Налаштування конфігурації розв'язувача
    SolverConfig config{
        .mode = SolverMode::ThwaitesLaminar,
        .stop_on_separation = true
    };

    BoundaryLayerSolver solver(air, config);

    // 3. Формування дискретної сітки уздовж пластини довжиною L = 1.5 м
    constexpr std::size_t num_points = 150;
    constexpr double length = 1.5;
    constexpr double U_free = 15.0; // м/с

    std::vector<PointInput> grid;
    grid.reserve(num_points);

    for (std::size_t i = 0; i < num_points; ++i) {
        double x_val = 0.001 + (length - 0.001) * static_cast<double>(i) / (num_points - 1);
        grid.push_back(PointInput{
            .x = x_val,
            .U_e = U_free,
            .dUe_dx = 0.0 // для плоскої пластини градієнт дорівнює нулю
        });
    }

    // 4. Виконання чисельного розрахунку
    auto solution = solver.solve(grid);

    if (!solution) {
        std::cerr << "Помилка при виконанні розрахунку: " 
                  << to_string(solution.error()) << "\n";
        return 1;
    }

    // 5. Виведення підсумкових результатів
    const auto& results = solution->points;
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Успішно оброблено точок: " << results.size() << "\n";
    std::cout << "Точка x = " << results.back().x << " м:\n";
    std::cout << "  Товщина втрати імпульсу (theta): " << results.back().theta * 1000.0 << " мм\n";
    std::cout << "  Товщина зміщення (delta_star):   " << results.back().delta_star * 1000.0 << " мм\n";
    std::cout << "  Коефіцієнт формы H:               " << results.back().H << "\n";
    std::cout << "  Місцевий коефіцієнт тертя C_f:    " << results.back().C_f << "\n";
    std::cout << "  Повний опір тертя пластини:       " << solution->total_friction_drag << " Н/м\n";

    return 0;
}
```
