# 📋 Інтерфейс та структура даних симулятора електростатики

Ця вставка містить повну розширену специфікацію програмного інтерфейсу (API) та структур даних бібліотеки чисельного симулювання електростатичних полів `libelectrostatics`. Документація описує структури даних для опису тривимірних розрахункових сіток, розподілу зарядів, діелектричних властивостей середовища, граничних умов та результатів інтегрування потоку Гаусса мовами C та C++.

## 1. Архітектурні принципи та дизайн API

Бібліотека `libelectrostatics` спроектована за принципом чіткого відокремлення даних від обчислювального ядра. Програмний інтерфейс надає два зв'язаних рівні доступності:

1. **C API (ANSI C99 / C11)**: ABI-сумісний процедурний інтерфейс із явним управлінням ресурсами за допомогою функцій `create`/`destroy` та передачею вказівників на нерозкриті структури (opaque handles). C API гарантує сумісність із будь-якими мовами програмування (Python CFFI, Rust, Fortran, C#).
2. **C++ API (C++20)**: Об'єктно-орієнтована обгортка високого рівня на базі семантики переміщення (Move Semantics), RAII-контейнерів `std::vector`, переглядів `std::span`, безпечної обробки помилок через `std::expected` та типів повернення `std::optional`.

### Ключові принципи проектування:
- **Нульові приховані виділення пам'яті у внутрішніх циклах**: Усі обчислювальні буфери (потенціал, густина заряду, компоненти поля) виділяються єдиним блоком під час ініціалізації сітки.
- **Векторна сумісність пам'яті**: Поля зберігаються у суцільних вирівняних масивах (`alignas(64)`), що допускає векторну оптимізацію SIMD (AVX-512).
- **Потокобезпека**: Стан обчислювального двигуна є незалежним для кожного примірника. Одночасний читальний доступ до обчисленого поля з кількох потоків є строго потокобезпечним.

## 2. Політика управління пам'яттю та володіння ресурсами

Управління оперативною пам'яттю в симуляторі побудовано за суворими правилами володіння (Ownership Semantics), що виключає витоки пам'яті (Memory Leaks) та подвійне звільнення (Double Free):

1. **Модель володіння в C API**:
   - Об'єкт сітки створюється викликом `sim_create_grid`, який виділяє єдиний нерозривний блок динамічної пам'яті у купі (Heap). Всі внутрішні масиви потенціалу `V`, густини заряду `ρ`, компонент поля `Ex, Ey, Ez` та діелектричних проникностей `ε_r` знаходяться у власності екземпляра сітки `grid_handle`.
   - Користувач бібліотеки володіє непрозорим вказівником `void *grid_handle` і зобов'язаний передати його у функцію `sim_destroy_grid` після завершення обчислень.
   - Вказівники на буфери, що повертаються функцією `sim_get_field_pointers`, є лише читальними переглядами (Read-Only Views). Користувачу заборонено викликати `free()` для цих вказівників.

2. **Модель володіння в C++20 API**:
   - Клас `ElectrostaticEngine` керує пам'яттю за концепцією RAII (Resource Acquisition Is Initialization). Усі масиви зберігаються у контейнерах `std::vector<double>`, які автоматично звільняють пам'ять при виході об'єкта з області видимості.
   - Для уникнення випадкового глибокого копіювання масивів обсягом у сотні мегабайт конструктор копіювання та оператор присвоєння копіюванням строго видалені (`= delete`).
   - Підтримується семантика переміщення (`= default` move constructor / assignment), що дозволяє передавати обчислювальні екземпляри між функціями та потоками без накладних витрат.

## 3. Коди помилок та статусів розрахунку

Усі процедури C API повертають перелічуваний тип статусу `sim_status_t`, що дозволяє відстежувати помилки пам'яті, некоректні параметри та збіжність ітерацій.

:::tabs
```c
// C API Status Codes
typedef enum {
    SIM_SUCCESS = 0,                   // Успішне виконання операції
    SIM_ERROR_INVALID_ARGUMENT = -1,   // Некоректні вхідні параметри (NULL pointer, від'ємний крок)
    SIM_ERROR_OUT_OF_MEMORY = -2,      // Помилка виділення динамічної пам'яті
    SIM_ERROR_DIVERGENCE = -3,         // Ітераційний процес SOR розбігся (нестійкість)
    SIM_ERROR_MAX_ITERATIONS = -4,     // Досягнуто ліміту ітерацій без збіжності за допуском tol
    SIM_ERROR_BOUNDARY_INVALID = -5    // Некоректна конфігурація граничних умов
} sim_status_t;
```
```cpp
// C++20 Strongly Typed Errors
namespace physics::electrodynamics {

enum class SimError {
    InvalidArgument,
    OutOfMemory,
    Divergence,
    MaxIterationsReached,
    InvalidBoundary
};

} // namespace physics::electrodynamics
```
:::

## 4. Основні структури даних (C та C++)

### А. Структури конфігурації сітки та граничних умов

Граничні умови визначають поведінку електростатичного поля на зовнішніх межах розрахункового об'єму та поверхнях вкладених провідників. Бібліотека підтримує три фундаментальні класи граничних умов:
- **Діріхле (Dirichlet)**: Задається фіксований потенціал `V = V_bound` (наприклад, заземлені корпуси, підключені до джерела живлення електроди).
- **Неймана (Neumann)**: Задається нормальна похідна потенціалу `∂V/∂n = g` (для ізольованих граней або площин симетрії, де `∂V/∂n = 0`).
- **Робіна (Robin / Mixed)**: Задається лінійна комбінація потенціалу та його нормальної похідної `α·V + β·(∂V/∂n) = u_0` (застосовується для наближення нескінченно віддалених границь).

:::tabs
```c
// C API Grid Configuration & Boundary Conditions
typedef enum {
    BOUNDARY_DIRICHLET = 0, // Фіксований потенціал V = V_bound
    BOUNDARY_NEUMANN = 1,   // Фіксована нормальна похідна dV/dn = 0 (ізольована грань)
    BOUNDARY_ROBIN = 2      // Змішана гранична умова Robin
} boundary_type_t;

typedef struct {
    boundary_type_t type;
    double potential_volts; // Значення потенціалу для умов Діріхле
    double normal_derivative; // Значення нормальної похідної dV/dn
} boundary_condition_t;

typedef struct {
    size_t nx;              // Кількість вузлів по осі X
    size_t ny;              // Кількість вузлів по осі Y
    size_t nz;              // Кількість вузлів по осі Z
    double dx;              // Крок сітки по осі X (м)
    double dy;              // Крок сітки по осі Y (м)
    double dz;              // Крок сітки по осі Z (м)
    boundary_condition_t boundary_x_min;
    boundary_condition_t boundary_x_max;
    boundary_condition_t boundary_y_min;
    boundary_condition_t boundary_y_max;
    boundary_condition_t boundary_z_min;
    boundary_condition_t boundary_z_max;
} grid_config_t;
```
```cpp
// C++20 Grid Specifications
namespace physics::electrodynamics {

enum class BoundaryType {
    Dirichlet,
    Neumann,
    Robin
};

struct BoundaryCondition {
    BoundaryType type{BoundaryType::Dirichlet};
    double potential_volts{0.0};
    double normal_derivative{0.0};
};

struct GridConfig {
    size_t nx{32};
    size_t ny{32};
    size_t nz{32};
    double dx{0.01};
    double dy{0.01};
    double dz{0.01};
    BoundaryCondition boundary_x_min{};
    BoundaryCondition boundary_x_max{};
    BoundaryCondition boundary_y_min{};
    BoundaryCondition boundary_y_max{};
    BoundaryCondition boundary_z_min{};
    BoundaryCondition boundary_z_max{};
};

} // namespace physics::electrodynamics
```
:::

### Б. Результати верифікації закону Гаусса

Для передачі результатів перевірки закону Гаусса `∮ E · dA = Q / ε₀` через дискретну гауссову поверхню використовується структура `gauss_verification_result_t`.

:::tabs
```c
// C API Gauss Verification Result Struct
typedef struct {
    double integrated_flux;       // Чисельний потік вектора напруженості ∮ E · dA (В·м)
    double enclosed_charge;       // Повний заряд усередині поверхні Q_enclosed (Кл)
    double theoretical_flux;      // Теоретичний потік Q / eps0 (В·м)
    double absolute_error;        // Абсолютна різниця |Flux - Q/eps0|
    double relative_error_percent;// Відносна похибка у відсотках (%)
    size_t surface_cell_count;    // Кількість граней сітки, що утворюють гауссову поверхню
} gauss_verification_result_t;
```
```cpp
// C++20 Gauss Verification Result Struct
namespace physics::electrodynamics {

struct GaussVerificationResult {
    double integrated_flux{0.0};
    double enclosed_charge{0.0};
    double theoretical_flux{0.0};
    double absolute_error{0.0};
    double relative_error_percent{0.0};
    size_t surface_cell_count{0};
};

} // namespace physics::electrodynamics
```
:::

## 5. Детальна специфікація функцій C API (`libelectrostatics.h`)

Нижче наведено повні контракти функцій C API із зазначенням вхідних параметрів, пост-умов та вимог до потокобезпеки.

### 5.1 `sim_create_grid`
Виділяє пам’ять під тривимірну сітку й оновлює структури конфігурації.
- **Вхідні параметри**:
  - `config` (`const grid_config_t*`): Вказівник на структуру конфігурації сітки. `nx, ny, nz` повинні бути більші за 2, а `dx, dy, dz` строго додатними.
- **Вихідні параметри**:
  - `out_grid_handle` (`void**`): Непрозорий вказівник handle на створений об'єкт сітки.
- **Передумови**: `config != NULL`, `out_grid_handle != NULL`.
- **Постумови**: У разі успіху виділяється пам'ять під суцільні масиви `V`, `ρ`, `Ex`, `Ey`, `Ez` та повертається `SIM_SUCCESS`.
- **Часова складність**: `O(Nx · Ny · Nz)`.
- **Потокобезпека**: Функція реінтерабельна.

### 5.2 `sim_destroy_grid`
Очищує всі виділені буфери та деалокує об'єкт сітки.
- **Синтаксис**:
  ```c
  void sim_destroy_grid(void *grid_handle);
  ```
- **Параметри**: `grid_handle` (`void*`): Вказівник, отриманий від `sim_create_grid`. Якщо передано `NULL`, функція виконує безпечне негайне повернення без дій.

### 5.3 `sim_set_charge_density`
Задає об'ємну густину вільних електричних зарядів `ρ(i, j, k)` в окремій комірці.
- **Синтаксис**:
  ```c
  sim_status_t sim_set_charge_density(void *grid_handle, size_t i, size_t j, size_t k, double rho_coulombs_per_m3);
  ```
- **Параметри**:
  - `grid_handle`: Дійсний вказівник на сітку.
  - `i, j, k`: Дискретні індекси вузла сітки (`0 ≤ i < Nx`, `0 ≤ j < Ny`, `0 ≤ k < Nz`).
  - `rho_coulombs_per_m3`: Густина заряду в кулонах на кубічний метр (Кл/м³).
- **Помилки**: Повертає `SIM_ERROR_INVALID_ARGUMENT`, якщо індекси виходять за межі розрахункового об'єму.

### 5.4 `sim_set_relative_permittivity`
Встановлює локальну відносну діелектричну проникність `ε_r` середовища в комірці `(i, j, k)`.
- **Синтаксис**:
  ```c
  sim_status_t sim_set_relative_permittivity(void *grid_handle, size_t i, size_t j, size_t k, double epsilon_r);
  ```
- **Примітки**: За замовчуванням усім коміркам присвоюється `ε_r = 1.0` (вакуум). При розрахунку на межі діелектриків використовується гармонійне усереднення провідностей `2·ε1·ε2 / (ε1 + ε2)`.

### 5.5 `sim_solve_poisson_sor`
Запускає ітераційний розв’язувач Пуассона методом послідовної верхньої релаксації.
- **Синтаксис**:
  ```c
  sim_status_t sim_solve_poisson_sor(void *grid_handle, double tolerance, size_t max_iterations, double relaxation_omega, size_t *out_iterations_performed);
  ```
- **Параметри**:
  - `tolerance`: Максимально припустима зміна потенціалу між ітераціями `max|V^{t+1} - V^t|`. Рекомендоване значення `1e-5 .. 1e-7`.
  - `max_iterations`: Гранична кількість ітерацій.
  - `relaxation_omega`: Параметр релаксації `1.0 < ω < 2.0`. При `ω ≥ 2.0` повертається `SIM_ERROR_DIVERGENCE`.
  - `out_iterations_performed`: Приймає кількість реально виконаних ітерацій.

### 5.6 `sim_compute_electric_field`
Розраховує векторний простір напруженості електричного поля `E = -∇V` по всьому об'єму сітки.
- **Синтаксис**:
  ```c
  sim_status_t sim_compute_electric_field(void *grid_handle);
  ```
- **Деталі**: Автоматично викликається після закінчення `sim_solve_poisson_sor`. Використовує центральні різниці другого порядку точності.

### 5.7 `sim_verify_gauss_law`
Виконує чисельне інтегрування потоку поля `∮ E · dA` через прямокутний гауссовий кубоїд та обчислює похибку відносно внутрішнього заряду `Q / ε₀`.
- **Синтаксис**:
  ```c
  sim_status_t sim_verify_gauss_law(void *grid_handle, size_t i_min, size_t i_max, size_t j_min, size_t j_max, size_t k_min, size_t k_max, gauss_verification_result_t *out_result);
  ```

### 5.8 `sim_get_field_pointers`
Отримує прямолінійні вказівники на суцільні внутрішні масиви пам’яті для прямого обчислення або візуалізації.
- **Синтаксис**:
  ```c
  sim_status_t sim_get_field_pointers(void *grid_handle, const double **out_v, const double **out_ex, const double **out_ey, const double **out_ez);
  ```

## 6. Послідовність викликів API (Typical Call Sequence)

Типовий життєвий цикл роботи з бібліотекою `libelectrostatics` складається з п'яти послідовних кроків:

1. **Конфігурація та ініціалізація**:
   Створення конфігураційної структури `grid_config_t` (або `GridConfig`), встановлення розмірів сітки `(Nx, Ny, Nz)` та типів граничних умов. Ініціалізація сітки викликом `sim_create_grid` (або конструктора `ElectrostaticEngine`).
2. **Задання фізичних джерел та середовища**:
   Виклики `sim_set_charge_density` для розміщення об'ємних зарядів `ρ(r)` та `sim_set_relative_permittivity` для об'єктів з різною діелектричною проникністю `ε_r`.
3. **Розв'язання рівняння Пуассона**:
   Виклик `sim_solve_poisson_sor` (або `engine.solvePoisson`), який запускає ітераційний розрахунок потенціалу `V` до досягнення критерію збіжності `tolerance`.
4. **Обчислення поля та верифікація Гаусса**:
   Автоматичний або явний виклик `sim_compute_electric_field` для розрахунку компонент `(Ex, Ey, Ez)`. Виклик `sim_verify_gauss_law` для контролю виконання закону Гаусса на вибраній замкненій поверхні.
5. **Деалокація ресурсів**:
   Виклик `sim_destroy_grid` у C API або автоматичне деструктування об'єкта `ElectrostaticEngine` у C++ API.

## 7. Специфікація класу C++ API (`ElectrostaticEngine.hpp`)

C++20 версія пропонує об'єктно-орієнтований клас `ElectrostaticEngine` з безпечною обробкою ресурсів через RAII та підтримкою семантики переміщення.

:::tabs
```c
// Приклад використання C API
#include <stdio.h>
#include "libelectrostatics.h"

int run_c_simulation(void) {
    grid_config_t cfg = {
        .nx = 50, .ny = 50, .nz = 50,
        .dx = 0.02, .dy = 0.02, .dz = 0.02,
        .boundary_x_min = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_x_max = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_y_min = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_y_max = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_z_min = {BOUNDARY_DIRICHLET, 0.0, 0.0},
        .boundary_z_max = {BOUNDARY_DIRICHLET, 0.0, 0.0}
    };

    void *grid = NULL;
    if (sim_create_grid(&cfg, &grid) != SIM_SUCCESS) {
        printf("Failed to allocate grid!\n");
        return -1;
    }

    // Задаємо заряд у центрі
    sim_set_charge_density(grid, 25, 25, 25, 1.0e-6);

    size_t iters = 0;
    sim_status_t status = sim_solve_poisson_sor(grid, 1e-5, 1000, 1.6, &iters);
    if (status == SIM_SUCCESS) {
        printf("Poisson solved in %zu iterations.\n", iters);

        gauss_verification_result_t gres;
        sim_verify_gauss_law(grid, 15, 35, 15, 35, 15, 35, &gres);
        printf("Gauss Relative Error: %.2f%%\n", gres.relative_error_percent);
    }

    sim_destroy_grid(grid);
    return 0;
}
```
```cpp
// Приклад використання C++20 API
#include <iostream>
#include <expected>
#include <span>
#include <vector>

namespace physics::electrodynamics {

class ElectrostaticEngine {
public:
    explicit ElectrostaticEngine(const GridConfig& config);
    ~ElectrostaticEngine() = default;

    ElectrostaticEngine(const ElectrostaticEngine&) = delete;
    ElectrostaticEngine& operator=(const ElectrostaticEngine&) = delete;
    ElectrostaticEngine(ElectrostaticEngine&&) noexcept = default;
    ElectrostaticEngine& operator=(ElectrostaticEngine&&) noexcept = default;

    [[nodiscard]] SimError setChargeDensity(size_t i, size_t j, size_t k, double rho);
    [[nodiscard]] SimError setRelativePermittivity(size_t i, size_t j, size_t k, double eps_r);
    [[nodiscard]] std::expected<size_t, SimError> solvePoisson(double tol = 1e-5, size_t max_iter = 1000, double omega = 1.6);
    [[nodiscard]] std::expected<GaussVerificationResult, SimError> verifyGaussLaw(size_t i1, size_t i2, size_t j1, size_t j2, size_t k1, size_t k2) const;

    [[nodiscard]] std::span<const double> getPotentialBuffer() const noexcept;
    [[nodiscard]] std::span<const double> getElectricFieldX() const noexcept;
    [[nodiscard]] std::span<const double> getElectricFieldY() const noexcept;
    [[nodiscard]] std::span<const double> getElectricFieldZ() const noexcept;

private:
    GridConfig config_;
    std::vector<double> potential_;
    std::vector<double> charge_density_;
    std::vector<double> permittivity_;
    std::vector<double> ex_;
    std::vector<double> ey_;
    std::vector<double> ez_;
};

} // namespace physics::electrodynamics
```
:::

## 8. Модель багатопотоковості та паралельних обчислень

Бібліотека підтримує два рівні паралелізації для високопродуктивних обчислень:

1. **Паралелізм на рівні потоків OpenMP (Shared Memory)**:
   Ітераційне ядро `sim_solve_poisson_sor` підтримує прапорець компіляції `#pragma omp parallel for` у поєднанні з червоно-чорним розфарбуванням вузлів (Red-Black Ordering). Це забезпечує лінійне прискорення розрахунку пропорційно кількості фізичних ядер процесора.
2. **Гарантії потокобезпеки (Thread Safety Guarantees)**:
   - **Конкурентне читання**: Будь-яка кількість потоків може одночасно викликати читальні методи (`verifyGaussLaw`, `getPotentialBuffer`, `sim_verify_gauss_law`) для того самого екземпляра сітки без застосування блокувань.
   - **Запис та модифікація**: Зміна потенціалу або виклик розв'язувача є ексклюзивною операцією, яка вимагає зовнішньої синхронізації (наприклад, через `std::mutex`).

## 9. Порівняльний аналіз продуктивності та безпеки пам'яті

1. **Просторова складність**: Пам'ять під 3D-сітку розраховується як `6 × 8 × Nx × Ny × Nz` байт (масиви `V`, `ρ`, `Ex`, `Ey`, `Ez`, `ε_r` типу `double` та масив граничних умов). Для сітки `100³` це становить близько 48 МБ RAM, що вільно вміщається в кеш L3 сучасних процесів.
2. **Часова складність**: Одна ітерація SOR вимагає `7` математичних операцій з плаваючою комою (FLOP) на вузол. Для сітки `100³` (1 мільйон вузлів) 400 ітерацій вимагають близько 2.8 ГФЛОП обчислень, що на сучасному процесорі виконується за 0.05-0.15 секунди.
3. **Обробка граничних випадків**: Всі функції C/C++ API здійснюють сувору перевірку виходу за межі масиву (Boundary Check), повертаючи статус `SIM_ERROR_INVALID_ARGUMENT` або `SimError::InvalidArgument`, що унеможливлює виникнення вразливостей типу Buffer Overflow або Undefined Behavior.
