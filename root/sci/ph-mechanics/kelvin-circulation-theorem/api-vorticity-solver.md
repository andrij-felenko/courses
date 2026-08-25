# 📋 Інтерфейс соловера вихровості та збереження циркуляції

Публічний програмістський інтерфейс (API) бібліотеки `vorticity_solver` призначений для чисельного розв'язання двовимірних рівнянь гідродінаміки нестисливої рідини у формулюванні «вихір — функція течії» (англ. *vorticity-streamfunction formulation*). Інтерфейс надає структури конфігурації сітки, граничних умов, функції інтегрування по часу та діагностичні методи для відстеження циркуляції за теоремою Кельвіна.

Бібліотека забезпечує точне дотримання законів збереження на дискретному рівні завдяки використанню симетричних різничних операторів для ротора та дивергенції, що зводить схематичну в'язкість до мінімуму. Всі масиви полів зберігаються в неперервних блоках пам'яті за порядком `row-major`, що оптимізує використання кєш-пам'яті процесора при паралельних обчисленнях.

## Математичне підґрунтя формулювання вихір — функція течії

Двовимірні рівняння Нав'є — Стокса для нестисливої рідини у формулюванні через компоненти швидкості `(u, v)` та тиск `p` вимагають розв'язання рівняння неперервності `∇ · u = 0` разом із рівняннями переносу імпульсу. У формулюванні через скалярну завихреність `ω = ∂v/∂x - ∂u/∂y` та функцію течії `Ψ` тиск повністю виключається з системи рівнянь, що значно підвищує обчислювальну стійкість.

Зв'язок між вектором швидкості та скалярною функцією течії `Ψ` визначається як:

```
u = ∂Ψ / ∂y,   v = - ∂Ψ / ∂x
```

При такому визначенні рівняння неперервності `∂u/∂x + ∂v/∂y = ∂²Ψ/∂x∂y - ∂²Ψ/∂y∂x = 0` виконується тотожно для будь-якої двічі диференційовної функції `Ψ`. Скалярна завихреність `ω` пов'язана з функцією течії рівнянням Пуассона:

```
∇²Ψ = ∂²Ψ/∂x² + ∂²Ψ/∂y² = - ω
```

Рівняння переносу завихреності у двовимірній нестисливій рідині набуває вигляду:

```
∂ω/∂t + u · ∂ω/∂x + v · ∂ω/∂y = ν · (∂²ω/∂x² + ∂²ω/∂y²)
```

У разі ідеальної нев'язкої рідини (`ν = 0`) праве значення дорівнює нулю, і завихреність переноситься як адвективний скаляр. Згідно з теоремою Кельвіна, інтеграл завихреності по довільній рідкій області `S(t)` залишається суворо постійним у часі: `Γ = ∬[S(t)] ω dA = const`.

## Структури даних та типи

### `solver_config_t` — Параметри обчислювальної сітки та середовища

| Поле | Тип | Опис | Зазони / Замовчування |
| :--- | :--- | :--- | :--- |
| `nx` | `size_t` | Кількість вузлів сітки по осі X | `nx >= 16`, за замовчуванням `128` |
| `ny` | `size_t` | Кількість вузлів сітки по осі Y | `ny >= 16`, за замовчуванням `128` |
| `dx` | `double` | Крок обчислювальної сітки по осі X (м) | `dx > 0.0`, за замовчуванням `0.01` |
| `dy` | `double` | Крок обчислювальної сітки по осі Y (м) | `dy > 0.0`, за замовчуванням `0.01` |
| `dt` | `double` | Крок інтегрування по часу (с) | Обмежений умовою КФЛ `dt <= dx / u_max` |
| `viscosity` | `double` | Кінематична в'язкість `ν` (м²/с) | `ν >= 0.0` (`0.0` для ідеальної рідини) |
| `bc_type` | `boundary_cond_t` | Тип граничних умов | `PERIODIC`, `NO_SLIP`, `SLIP_WALL` |

Поле `viscosity` задає коефіцієнт в'язкої дифузії. Якщо значення дорівнює нулю (`0.0`), солевер працює у режимі ідеальної нев'язкої рідини і зберігає циркуляцію Кельвіна. Якщо значення додатне (`ν > 0`), вмикається в'язка дифузія за допомогою явного чи неявного схематичного оператора Лапласа.

Поле `bc_type` задає фізичні умови на межах обчислювального домену:
- `BC_PERIODIC`: періодичні граничні умови вздовж обох осей, ідеально підходять для моделювання однорідної турбулентності.
- `BC_SLIP_WALL`: непроникна стінка без ковзання (`v_n = 0`, `∂v_t/∂n = 0`), завихреність на межі дорівнює нулю.
- `BC_NO_SLIP`: тверда стінка з умовами прилипання (`u = 0`, `v = 0`), стінка слугує джерелом генерації завихреності.

### `circulation_stats_t` — Результат обчислення діагностики циркуляції

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| `circulation` | `double` | Значення замкненого контурного інтеграла `Γ = ∮ u · dr` (м²/с) |
| `vorticity_integral` | `double` | Значення поверхневого інтеграла вихровості `∬ ω · dA` (м²/с) |
| `stokes_error` | `double` | Абсолютна різниця `|Γ - ∬ ω · dA|` (оцінка точної теореми Стокса) |
| `baroclinic_generation` | `double` | Швидкість генерування циркуляції бароклінним моментом `dΓ/dt` (м²/с²) |
| `viscous_dissipation` | `double` | Швидкість в'язкої дисипації циркуляції (м²/с²) |

Структура дає змогу оцінювати як замкнений контурний інтеграл вздовж вказаного полігона, так і поверхневий інтеграл вихровості всередині нього. Абсолютна різниця між ними `stokes_error` слугує мережевим тестом дискретної точності схеми.

### `solver_error_t` — Коди повернення та помилки

| Заголовок / Код | Значення | Опис помилки |
| :--- | :--- | :--- |
| `SOLVER_SUCCESS` | `0` | Операція виконана успішно |
| `SOLVER_ERR_INVALID_PARAM` | `-1` | Передано некоректний параметр конфігурації (наприклад, `dx <= 0`) |
| `SOLVER_ERR_NO_MEMORY` | `-2` | Не вдалося виділити пам'ять під буфери сітки |
| `SOLVER_ERR_CFL_VIOLATION` | `-3` | Крок часу `dt` порушує умову стійкості Куранта — Фрідріхса — Леві |
| `SOLVER_ERR_POISSON_CONVERGENCE`| `-4` | Соловер Пуассона для функції течії не збігся за задану кількість ітерацій |

Функції бібліотеки повертають від'ємні значення у разі виникнення помилок виконання, що дозволяє легко інтегрувати перевірки у системи обробки помилок.

---

## Заголовки C та C++ програмного інтерфейсу

:::tabs
```c
#ifndef VORTICITY_SOLVER_H
#define VORTICITY_SOLVER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BC_PERIODIC = 0,
    BC_SLIP_WALL = 1,
    BC_NO_SLIP = 2
} boundary_cond_t;

typedef enum {
    SOLVER_SUCCESS = 0,
    SOLVER_ERR_INVALID_PARAM = -1,
    SOLVER_ERR_NO_MEMORY = -2,
    SOLVER_ERR_CFL_VIOLATION = -3,
    SOLVER_ERR_POISSON_CONVERGENCE = -4
} solver_error_t;

typedef struct {
    size_t nx;
    size_t ny;
    double dx;
    double dy;
    double dt;
    double viscosity;
    boundary_cond_t bc_type;
} solver_config_t;

typedef struct {
    double circulation;
    double vorticity_integral;
    double stokes_error;
    double baroclinic_generation;
    double viscous_dissipation;
} circulation_stats_t;

typedef struct {
    double x;
    double y;
} point2d_t;

typedef struct vorticity_solver_s vorticity_solver_t;

/* Створення та знищення об'єкта соловера */
solver_error_t vorticity_solver_create(const solver_config_t* config, vorticity_solver_t** out_solver);
void vorticity_solver_destroy(vorticity_solver_t* solver);

/* Ініціалізація початкового поля вихровості */
solver_error_t vorticity_solver_set_vorticity(vorticity_solver_t* solver, const double* omega_field);

/* Крок інтегрування по часу */
solver_error_t vorticity_solver_step(vorticity_solver_t* solver);

/* Отримання поточного фізичного часу */
double vorticity_solver_get_time(const vorticity_solver_t* solver);

/* Отримання вказівників на поля швидкостей та вихровості (readonly) */
const double* vorticity_solver_get_omega(const vorticity_solver_t* solver);
const double* vorticity_solver_get_velocity_u(const vorticity_solver_t* solver);
const double* vorticity_solver_get_velocity_v(const vorticity_solver_t* solver);

/* Обчислення циркуляції Кельвіна вздовж довільного замкненого полігонального контуру */
solver_error_t vorticity_solver_compute_circulation(
    const vorticity_solver_t* solver,
    const point2d_t* contour_points,
    size_t num_points,
    circulation_stats_t* out_stats
);

#ifdef __cplusplus
}
#endif

#endif /* VORTICITY_SOLVER_H */
```

```cpp
#ifndef VORTICITY_SOLVER_HPP
#define VORTICITY_SOLVER_HPP

#include <vector>
#include <span>
#include <memory>
#include <system_error>
#include <cstddef>

namespace fluid {

enum class BoundaryCondition {
    Periodic,
    SlipWall,
    NoSlip
};

enum class SolverErrc {
    Success = 0,
    InvalidParameter = 1,
    OutOfMemory = 2,
    CflViolation = 3,
    PoissonConvergenceFailure = 4
};

std::error_code make_error_code(SolverErrc e);

struct SolverConfig {
    std::size_t nx{128};
    std::size_t ny{128};
    double dx{0.01};
    double dy{0.01};
    double dt{0.001};
    double viscosity{0.0};
    BoundaryCondition bc_type{BoundaryCondition::Periodic};
};

struct CirculationStats {
    double circulation{0.0};
    double vorticity_integral{0.0};
    double stokes_error{0.0};
    double baroclinic_generation{0.0};
    double viscous_dissipation{0.0};
};

struct Point2D {
    double x{0.0};
    double y{0.0};
};

class VorticitySolver {
public:
    explicit VorticitySolver(const SolverConfig& config);
    ~VorticitySolver();

    VorticitySolver(const VorticitySolver&) = delete;
    VorticitySolver& operator=(const VorticitySolver&) = delete;

    VorticitySolver(VorticitySolver&&) noexcept;
    VorticitySolver& operator=(VorticitySolver&&) noexcept;

    void set_vorticity(std::span<const double> omega_field);
    void step();

    [[nodiscard]] double get_time() const noexcept;
    [[nodiscard]] std::span<const double> get_omega() const noexcept;
    [[nodiscard]] std::span<const double> get_velocity_u() const noexcept;
    [[nodiscard]] std::span<const double> get_velocity_v() const noexcept;

    [[nodiscard]] CirculationStats compute_circulation(std::span<const Point2D> contour) const;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace fluid

namespace std {
    template <>
    struct is_error_code_enum<fluid::SolverErrc> : true_type {};
}

#endif // VORTICITY_SOLVER_HPP
```
:::

---

## Детальний опис функцій та специфікація викликів

### `vorticity_solver_create` / `VorticitySolver::VorticitySolver`

Функція відповідає за виділення динамічної пам'яті та ініціалізацію внутрішнього стану соловера. При виклику виділяються двовимірні масиви для поля вихровості `ω(x, y)`, функції течії `Ψ(x, y)` та компонент швидкості `u(x, y)`, `v(x, y)`. Перевіряються параметри сітки на позитивність та розраховується обмеження на крок часу за умовою стійкості Куранта — Фрідріхса — Леві (CFL):

```
dt <= min(dx, dy) / u_max
```

Якщо `dt` перевищує гранично допустимий крок, у C-функції повертається код `SOLVER_ERR_CFL_VIOLATION`, а в C++ генерується виняток `std::system_error` з відповідним категоріальним кодом `SolverErrc::CflViolation`. Забезпечується ідіоматична обробка винятків C++ через паттерн RAII та Pimpl для приховування деталей реалізації.

---

### `vorticity_solver_step` / `VorticitySolver::step`

Виконує один крок по часу `t -> t + dt` шляхом послідовного розв'язання трьох етапів обчислювального циклу:

1. **Розв'язання рівняння Пуассона для функції течії**:
   ```
   ∇²Ψ = -ω
   ```
   У випадку періодичних граничних умов розв'язок виконується за допомогою швидкого перетворення Фур'є (FFT) за один алгоритмічний крок `O(N log N)`. Для непроникних твердих стінок застосовується багатосітковий соловер (Multigrid) із залишговою точністю `10⁻⁸`.

2. **Оновлення компонента швидкості на сітці**:
   ```
   u = ∂Ψ / ∂y,   v = - ∂Ψ / ∂x
   ```
   Компоненти швидкості розраховуються за допомогою симетричних різниць 4-го порядку точності, що зберігає дивергенцію швидкостей рівною нулю.

3. **Адвекція та в'язка дифузія завихреності**:
   ```
   ∂ω / ∂t + u · ∂ω/∂x + v · ∂ω/∂y = ν · (∂²ω/∂x² + ∂²ω/∂y²)
   ```
   Перенос завихреності виконується за схемою WENO5 (Weighted Essentially Non-Oscillatory scheme), що запобігає виникненню нефізичних осциляцій біля сильних градієнтів завихреності.

---

### `vorticity_solver_compute_circulation` / `VorticitySolver::compute_circulation`

Розраховує діагностичні показники теореми Кельвіна для заданого полігонального рідкого контуру `contour`.

- **Параметр `contour_points`**: Масив точок `(x, y)`, що задають замкнений багатокутник у фізичних координатах середовища.
- **Повертане значення `circulation`**: Обчислений контурний інтеграл `Γ = ∮ (u dx + v dy)` методом трапецій.
- **Повертане значення `vorticity_integral`**: Інтеграл `∬ ω dx dy` по внутрішній області полігона.
- **Оцінка `stokes_error`**: Абсолютна різниця `|Γ - ∬ ω dA|`. У бездисипативній чисельній схемі ця величина залишається на рівні машинного нуля (`~10⁻¹⁴`), що свідчить про точне дотримання дискретної теореми Стокса.

---

## Приклад використання API в реальному коді

Нижче наведено робочий фрагмент коду для створення соловера, ініціалізації вихрової плями Гаусса та перевірки збереження циркуляції за теоремою Кельвіна протягом 100 часових кроків.

:::tabs
```c
#include "vorticity_solver.h"
#include <stdio.h>
#include <math.h>
#include <stdlib.h>

int main(void) {
    solver_config_t config = {
        .nx = 128,
        .ny = 128,
        .dx = 0.01,
        .dy = 0.01,
        .dt = 0.001,
        .viscosity = 0.0, /* Ідеальна рідина: ν = 0 */
        .bc_type = BC_PERIODIC
    };

    vorticity_solver_t* solver = NULL;
    if (vorticity_solver_create(&config, &solver) != SOLVER_SUCCESS) {
        fprintf(stderr, "Помилка створення соловера\n");
        return 1;
    }

    /* Заповнення початкового поля вихровості (вихір Гаусса) */
    double* omega = (double*)malloc(sizeof(double) * config.nx * config.ny);
    for (size_t j = 0; j < config.ny; ++j) {
        for (size_t i = 0; i < config.nx; ++i) {
            double x = i * config.dx - 0.64;
            double y = j * config.dy - 0.64;
            omega[j * config.nx + i] = 10.0 * exp(-(x*x + y*y) / 0.02);
        }
    }
    vorticity_solver_set_vorticity(solver, omega);
    free(omega);

    /* Задаємо замкнений квадратний контур */
    point2d_t contour[4] = {
        {0.40, 0.40},
        {0.88, 0.40},
        {0.88, 0.88},
        {0.40, 0.88}
    };

    circulation_stats_t stats_init;
    vorticity_solver_compute_circulation(solver, contour, 4, &stats_init);
    printf("Початкова циркуляція Г0 = %.6f м2/с\n", stats_init.circulation);

    /* Моделювання 100 кроків */
    for (int step = 0; step < 100; ++step) {
        vorticity_solver_step(solver);
    }

    circulation_stats_t stats_final;
    vorticity_solver_compute_circulation(solver, contour, 4, &stats_final);
    printf("Кінцева циркуляція   Г1 = %.6f м2/с\n", stats_final.circulation);
    printf("Відносна зміна dГ/Г0    = %.2e\n", 
           fabs(stats_final.circulation - stats_init.circulation) / stats_init.circulation);

    vorticity_solver_destroy(solver);
    return 0;
}
```

```cpp
#include "vorticity_solver.hpp"
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

int main() {
    try {
        fluid::SolverConfig config{
            .nx = 128,
            .ny = 128,
            .dx = 0.01,
            .dy = 0.01,
            .dt = 0.001,
            .viscosity = 0.0,
            .bc_type = fluid::BoundaryCondition::Periodic
        };

        fluid::VorticitySolver solver(config);

        std::vector<double> omega(config.nx * config.ny);
        for (std::size_t j = 0; j < config.ny; ++j) {
            for (std::size_t i = 0; i < config.nx; ++i) {
                double x = i * config.dx - 0.64;
                double y = j * config.dy - 0.64;
                omega[j * config.nx + i] = 10.0 * std::exp(-(x * x + y * y) / 0.02);
            }
        }
        solver.set_vorticity(omega);

        const std::vector<fluid::Point2D> contour{
            {0.40, 0.40},
            {0.88, 0.40},
            {0.88, 0.88},
            {0.40, 0.88}
        };

        auto stats_init = solver.compute_circulation(contour);
        std::cout << std::fixed << std::setprecision(6);
        std::cout << "Початкова циркуляція Г0 = " << stats_init.circulation << " м2/с\n";

        for (int step = 0; step < 100; ++step) {
            solver.step();
        }

        auto stats_final = solver.compute_circulation(contour);
        std::cout << "Кінцева циркуляція   Г1 = " << stats_final.circulation << " м2/с\n";
        std::cout << "Відносна зміна dГ/Г0    = " << std::scientific << std::setprecision(2)
                  << std::abs(stats_final.circulation - stats_init.circulation) / stats_init.circulation
                  << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Правила потокобезпечності та управління ресурсами

1. **Управління пам'яттю**: Всі внутрішні динамічні буфери створюються при виклику конструктора або `vorticity_solver_create` і вивільняються при виклику деструктора або `vorticity_solver_destroy`. Екземпляри соловера є монопольними володарями власних буферів і не виконують прихованих алокацій під час обчислювального кроку `step()`.
2. **Багатопотоковість та паралелізм**: Інтерфейс є потокобезпечним за читанням: методи з позначкою `const` (наприклад, `get_omega()`, `compute_circulation()`) можуть викликатися паралельно з кількох потоків виконання без блокувань. Модифікуючі методи (`step()`, `set_vorticity()`) вимагають зовнішньої синхронізації при виклику з різних потоків.
3. **Обробка помилок у C та C++**: C++ версія не використовує коди помилок через поверчувані значення, а застосовує стандартний механізм `std::error_code` та винятки `std::system_error`. Це виключає можливість ігнорування помилок виділення пам'яті чи некоректних параметрів обчислювальної сітки.
