# 📋 Специфікація параметрів теплофізичних властивостей та розв'язувача

Цей документ визначає стандартизований програмний інтерфейс (API), виклики, контракти даних, структуру пам'яті та довідкові таблиці матеріальних констант для програмних модулів обчислення стаціонарних та нестаціонарних температурних полів у суцільних середовищах.

Інтерфейс розроблено для забезпечення сумісності між модулями теплового розрахунку в симуляторах електроніки, САПР та автоматизованих системах керування охолодженням. Документ описує структури даних для завдання теплофізичних властивостей матеріалів, конфігурації граничних умов, налаштування чисельної сітки, а також сигнатури функцій обчислення теплових потоків і перевірки критерію стійкості.

### 1. Фізичні одиниці, константи та переліки (Enums & Constants)

Програмний інтерфейс оперує суворо одиницями вимірювання Міжнародної системи одиниць SI:
- Термодинамічна температура `T`: кельвіни [К] або градуси Цельсія [°C] (у виразах випромінювання обов'язковий перерахунок у кельвіни `T_K = T_C + 273.15`);
- Густина теплового потоку `q`: вати на квадратний метр [Вт/м²];
- Коефіцієнт теплопровідності `k`: вати на метр-кельвін [Вт/(м·К)];
- Питома теплоємність `c_p`: джоулі на кілограм-кельвін [Дж/(кг·К)];
- Коефіцієнт конвективної тепловіддачі `h`: вати на квадратний метр-кельвін [Вт/(м²·К)].

Нижче наведено визначення базових констант та типізованих переліків для мови C:

:::tabs
```c
// Фізичні константи
#define THERMAL_STEFAN_BOLTZMANN 5.670374419e-8 // Стала Стефана-Больцмана σ [Вт/(м²·К⁴)]
#define THERMAL_ABSOLUTE_ZERO_C  -273.15        // Абсолютний нуль [°C]

// Типи граничних умов
typedef enum {
    THERMAL_BC_DIRICHLET = 0, // 1-й рід: Задана фіксована температура T_surface [°C]
    THERMAL_BC_NEUMANN   = 1, // 2-й рід: Заданий тепловий потік q_surface [Вт/м²]
    THERMAL_BC_ROBIN     = 2, // 3-й рід: Конвекція h * (T_surface - T_ambient)
    THERMAL_BC_RADIATION = 3  // 4-й рід: Випромінювання ε * σ * (T_s⁴ - T_amb⁴)
} thermal_bc_type_t;

// Статуси виконання функцій розв'язувача
typedef enum {
    THERMAL_SUCCESS             =  0, // Обчислення завершено успішно
    THERMAL_ERROR_NULL_POINTER  = -1, // Передано нульовий вказівник на структуру
    THERMAL_ERROR_INVALID_PARAM = -2, // Передано некоректний фізичний параметр (k <= 0, dx <= 0)
    THERMAL_ERROR_CFL_VIOLATION = -3, // Часовий крок dt перевищує межу стійкості CFL
    THERMAL_ERROR_NO_CONVERGE   = -4  // Стаціонарний розв'язок не досяг допуску за max_iter
} thermal_status_t;
```
```cpp
#include <cstdint>

namespace thermal {

// Фізичні константи
constexpr double STEFAN_BOLTZMANN = 5.670374419e-8; // σ [Вт/(м²·К⁴)]
constexpr double ABSOLUTE_ZERO_C  = -273.15;        // Абсолютний нуль [°C]

// Типи граничних умов
enum class BoundaryType : std::uint8_t {
    Dirichlet = 0, // 1-й рід: Задана температура T_surface [°C]
    Neumann   = 1, // 2-й рід: Заданий потік q_surface [Вт/м²]
    Robin     = 2, // 3-й рід: Конвекція h * (T_surface - T_ambient)
    Radiation = 3  // 4-й рід: Випромінювання ε * σ * (T_s⁴ - T_amb⁴)
};

// Статуси виконання функцій розв'язувача
enum class SolverStatus : std::int32_t {
    Success          =  0,
    NullPointer      = -1,
    InvalidParameter = -2,
    CflViolation     = -3,
    NoConvergence    = -4
};

} // namespace thermal
```
:::

Для програмних комплексів мовою C++ переліки реалізовано у вигляді строго типізованих `enum class` у просторі імен `thermal`.

### 2. Детальний опис структур даних та параметрів

Опис матеріалу та конфігурація розрахункової області задаються структурованими типами даних. Всі числові значення використовують тип плаваючої крапки подвійної точності `double` (IEEE 754 64-bit) для мінімізації накопичення помилок округлення під час тривалих нестаціонарних розрахунків.

#### Властивості матеріалу (`thermal_material_t` / `MaterialProperties`)
- `conductivity` (`k`): коефіцієнт теплопровідності суцільного матеріалу [Вт/(м·К)]. Мусить бути суворо додатним значенням (`k > 0`). Для ізотропних матеріалів теплопровідність однакова в усіх напрямках. Для анізотропних матеріалів (наприклад, склотекстоліт FR-4 або орієнтований графіт) значення `k` у площині шарів `k_xy` та перпендикулярно до них `k_z` відрізняються в рази.
- `density` (`ρ`): маса одиниці об'єму матеріалу [кг/м³] (`ρ > 0`). Визначено при кімнатній температурі.
- `specific_heat` (`c_p`): кількість енергії, необхідна для нагрівання 1 кг речовини на 1 кельвін при постійному тиску [Дж/(кг·К)] (`c_p > 0`). Добуток `ρ · c_p` дає об'ємну теплоємність матеріалу [Дж/(м³·К)], яка визначає інерційну здатність зберігати тепло.
- `emissivity` (`ε`): безрозмірний коефіцієнт ступеня чорноти поверхні в діапазоні від `0.0` (ідеальний відбивач/дзеркало) до `1.0` (абсолютно чорне тіло). Описує ефективність інфрачервоного випромінювання поверхні за законом Стефана-Больцмана.

#### Граничні умови (`thermal_bc_t` / `BoundaryCondition`)
- `type`: тип граничної умови. Визначає математичну формулу розрахунку потоку тепла на граничному вузлі сітки.
- `value`: скалярне значення. Для умови Діріхле (`THERMAL_BC_DIRICHLET`) це фіксована температура поверхні `T_surface` [°C]. Для умови Неймана (`THERMAL_BC_NEUMANN`) це густина зовнішнього теплового потоку `q_surface` [Вт/м²] (додатне значення означає приплив тепла в тіло, від'ємне — відплив).
- `h_coeff`: коефіцієнт конвективної тепловіддачі `h` [Вт/(м²·К)]. Використовується лише для граничної умови 3-го роду (`THERMAL_BC_ROBIN`).
- `t_ambient`: температура навколишнього середовища `T_ambient` [°C]. Використовується для розрахунку конвекції та випромінювання на межі.

#### Налаштування розв'язувача (`thermal_solver_config_t` / `SolverConfig`)
- `grid_x`, `grid_y`: кількість дискретних вузлів чисельної сітки вздовж осей X та Y відповідно. Мінімальне припустиме значення — 3 вузли.
- `dx`, `dy`: просторові кроки сітки [м]. Приймаються рівномірними для всієї області розрахунку.
- `dt`: дискретний крок за часом [с]. Для явних розв'язувачів підлягає обов'язковій перевірці на відповідність критерію стійкості Куранта–Фрідріхса–Леві (CFL): `dt ≤ 0.5 · dx² / α`.
- `max_time`: загальний фізичний час симуляції [с] для нестаціонарних задач.
- `tolerance`: норма різниці температур між послідовними ітераціями `max|T^(n+1) - T^n|` для зупинки стаціонарного розв'язувача.
- `is_transient`: прапорець режиму обчислення: `true` вимагає розрахунку часової динаміки `T(x,y,t)`, `false` вимагає пошуку стаціонарного розподілу `T(x,y)` за умови `∂T/∂t = 0`.

:::tabs
```c
#include <stddef.h>
#include <stdbool.h>

// Властивості суцільного матеріалу
typedef struct {
    double conductivity;    // k: Коефіцієнт теплопровідності [Вт/(м·К)] (k > 0)
    double density;         // ρ: Густина матеріалу [кг/м³] (ρ > 0)
    double specific_heat;   // c_p: Питома теплоємність [Дж/(кг·К)] (c_p > 0)
    double emissivity;      // ε: Ступінь чорноти поверхні (0.0 <= ε <= 1.0)
} thermal_material_t;

// Параметри граничної умови для однієї грані
typedef struct {
    thermal_bc_type_t type; // Тип граничної умови (Dirichlet, Neumann, Robin, Radiation)
    double value;           // T_surface [°C] для 1-го роду або q_surface [Вт/м²] для 2-го роду
    double h_coeff;         // Коефіцієнт конвекції h [Вт/(м²·К)] (для Robin)
    double t_ambient;       // Температура довкілля T_amb [°C] (для Robin і Radiation)
} thermal_bc_t;

// Налаштування чисельної сітки та параметрів розв'язувача
typedef struct {
    size_t grid_x;          // Кількість вузлів сітки вздовж осі X
    size_t grid_y;          // Кількість вузлів сітки вздовж осі Y
    double dx;              // Просторовий крок дискретизації dx [м]
    double dy;              // Просторовий крок дискретизації dy [м]
    double dt;              // Часовий крок дискретизації dt [с]
    double max_time;        // Загальний фізичний час симуляції [с]
    double tolerance;       // Допуск сбіжності стаціонарного стану
    bool is_transient;      // прапорець: true = нестаціонарний, false = стаціонарний
} thermal_solver_config_t;
```
```cpp
#include <cstddef>
#include <cstdint>

namespace thermal {

enum class BoundaryType : std::uint8_t {
    Dirichlet = 0, // Задана температура T_surface [°C]
    Neumann   = 1, // Заданий потік q_surface [Вт/м²]
    Robin     = 2, // Конвекція h * (T_s - T_amb)
    Radiation = 3  // Випромінювання ε * σ * (T_s⁴ - T_amb⁴)
};

enum class SolverStatus : std::int32_t {
    Success          =  0,
    NullPointer      = -1,
    InvalidParameter = -2,
    CflViolation     = -3,
    NoConvergence    = -4
};

struct MaterialProperties {
    double conductivity{385.0};    // k [Вт/(м·К)] (значення за замовчуванням для міді)
    double density{8960.0};        // ρ [кг/м³]
    double specific_heat{385.0};   // c_p [Дж/(кг·К)]
    double emissivity{0.05};       // ε (полірована мідна поверхня)

    // Обчислити коефіцієнт температуропровідності α = k / (ρ * c_p)
    [[nodiscard]] constexpr double diffusivity() const noexcept {
        return conductivity / (density * specific_heat);
    }
};

struct BoundaryCondition {
    BoundaryType type{BoundaryType::Dirichlet};
    double value{20.0};            // T [°C] або q [Вт/м²]
    double h_coeff{10.0};          // h [Вт/(м²·К)]
    double t_ambient{20.0};        // T_ambient [°C]
};

struct SolverConfig {
    std::size_t grid_x{100};
    std::size_t grid_y{100};
    double dx{0.001};              // 1 мм
    double dy{0.001};              // 1 мм
    double dt{0.0001};             // 0.1 мс
    double max_time{1.0};          // 1 секунда
    double tolerance{1e-6};
    bool is_transient{true};
};

} // namespace thermal
```
:::

### 3. Организація пам'яті сітки та доступ до даних

Розподіл температур на двовимірній сітці розміром `grid_x × grid_y` зберігається у суцільному одноразово виділеному блоці оперативної пам'яті розміром `grid_x * grid_y * sizeof(double)` байт.

Використовується канонічний порядок розташування елементів у пам'яті за рядками (*row-major order*), прийнятий у мовах C та C++:
```
індекс у масиві = y * grid_x + x
```
де `x` змінюється від `0` до `grid_x - 1` (внутрішній швидкий цикл), а `y` змінюється від `0` до `grid_y - 1` (зовнішній повільний цикл).

Така організація забезпечує сувору послідовність вибірки даних із кеш-пам'яті процесора (Cache Line Prefetching) при просторовій обробці сітки, що підвищує продуктивність у 4–8 разів порівняно з масивами вказівників на вказівники (`double**`).

Для забезпечення SIMD-векторизації (Advanced Vector Extensions, AVX-512 або ARM NEON) пам'ять для масиву температур має бути вирівняна за межею 64 байти за допомогою системних функцій `posix_memalign` або `_mm_malloc`.

### 4. Специфікація функціонального контракту (Function Signatures)

Обчислювальний модуль надає набір допоміжних та основних процедур. Усі функції мовою C приймають вказівники на вихідні дані та повертають код статусу `thermal_status_t`.

:::tabs
```c
#ifdef __cplusplus
extern "C" {
#endif

// Обчислити температуропровідність α = k / (ρ * c_p) [м²/с]
double thermal_calc_diffusivity(const thermal_material_t* mat);

// Обчислити максимально припустимий часовий крок dt_max [с] за умовою CFL:
// dt_max = 0.5 * min(dx², dy²) / α
double thermal_get_max_stable_dt(const thermal_material_t* mat, double dx, double dy);

// Обчислити конвективний тепловий потік за законом Ньютона: q = h * (T_s - T_amb)
double thermal_calc_convective_flux(double h_coeff, double t_surface, double t_ambient);

// Обчислити радіаційний тепловий потік за законом Стефана-Больцмана:
// q = ε * σ * ((T_s + 273.15)⁴ - (T_amb + 273.15)⁴)
double thermal_calc_radiative_flux(double emissivity, double t_surface, double t_ambient);

// Запустити двовимірний розв'язувач рівняння теплопровідності
thermal_status_t thermal_solve_2d(
    const thermal_solver_config_t* config,
    const thermal_material_t* material,
    const thermal_bc_t boundary_conditions[4], // Граничні умови: [Північ, Південь, Схід, Захід]
    double* grid_output                          // Вихідний масив розміром grid_x * grid_y
);

#ifdef __cplusplus
}
#endif
```
```cpp
#include <span>
#include <array>
#include <expected>
#include <vector>

namespace thermal {

class ThermalSolver {
public:
    ThermalSolver(SolverConfig config, MaterialProperties material);

    // Встановити граничні умови для 4 граней розрахункової області
    void set_boundary_conditions(const std::array<BoundaryCondition, 4>& bcs) noexcept;

    // Обчислити максимальний припустимий часовий крок за критерієм CFL
    [[nodiscard]] double max_stable_dt() const noexcept;

    // Запустити обчислення (повертає void або помилку SolverStatus)
    [[nodiscard]] std::expected<void, SolverStatus> run();

    // Отримати доступ до результатів розрахунку розподілу температури
    [[nodiscard]] std::span<const double> temperature_grid() const noexcept;

private:
    SolverConfig config_;
    MaterialProperties material_;
    std::array<BoundaryCondition, 4> bcs_;
    std::vector<double> grid_;
};

} // namespace thermal
```
:::

### 5. Повний приклад використання API розв'язувача

Приклад нижче демонструє послідовність викликів для розрахунку двовимірного температурного поля в алюмінієвій пластині розміром 10 × 10 см:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    // 1. Задати властивості алюмінію 6061-T6
    thermal_material_t mat = {
        .conductivity = 167.0,  // k [Вт/(м·К)]
        .density = 2700.0,      // ρ [кг/м³]
        .specific_heat = 896.0, // c_p [Дж/(кг·К)]
        .emissivity = 0.85      // ε (анодований)
    };

    // 2. Задати геометрію та сітку
    thermal_solver_config_t cfg = {
        .grid_x = 50,
        .grid_y = 50,
        .dx = 0.002,            // 2 мм
        .dy = 0.002,            // 2 мм
        .dt = 0.001,            // 1 мс
        .max_time = 5.0,        // 5 секунд
        .tolerance = 1e-5,
        .is_transient = true
    };

    // 3. Задати граничні умови на 4 гранях [Північ, Південь, Схід, Захід]
    thermal_bc_t bcs[4] = {
        {.type = THERMAL_BC_DIRICHLET, .value = 100.0}, // Північ: 100 °C
        {.type = THERMAL_BC_DIRICHLET, .value = 20.0},  // Південь: 20 °C
        {.type = THERMAL_BC_ROBIN, .h_coeff = 25.0, .t_ambient = 20.0}, // Схід: конвекція
        {.type = THERMAL_BC_ROBIN, .h_coeff = 25.0, .t_ambient = 20.0}  // Захід: конвекція
    };

    // 4. Перевірити стійкість
    double max_dt = thermal_get_max_stable_dt(&mat, cfg.dx, cfg.dy);
    if (cfg.dt > max_dt) {
        printf("Крок dt = %.5f завеликий! dt_max = %.5f с\n", cfg.dt, max_dt);
        cfg.dt = max_dt * 0.9; // Зменшити крок із запасом
    }

    // 5. Виділити пам'ять під вихідну сітку
    double* grid = (double*)malloc(cfg.grid_x * cfg.grid_y * sizeof(double));
    if (!grid) return 1;

    // 6. Запустити симуляцію
    thermal_status_t status = thermal_solve_2d(&cfg, &mat, bcs, grid);
    if (status == THERMAL_SUCCESS) {
        printf("Розрахунок успішно завершено. Температура в центрі: %.2f °C\n",
               grid[(cfg.grid_y / 2) * cfg.grid_x + (cfg.grid_x / 2)]);
    } else {
        printf("Помилка розв'язувача: код %d\n", status);
    }

    free(grid);
    return 0;
}
```
```cpp
#include <iostream>

int main() {
    using namespace thermal;

    try {
        SolverConfig cfg{
            .grid_x = 50,
            .grid_y = 50,
            .dx = 0.002,
            .dy = 0.002,
            .dt = 0.001,
            .max_time = 5.0,
            .tolerance = 1e-5,
            .is_transient = true
        };

        MaterialProperties mat{
            .conductivity = 167.0,
            .density = 2700.0,
            .specific_heat = 896.0,
            .emissivity = 0.85
        };

        ThermalSolver solver(cfg, mat);

        std::array<BoundaryCondition, 4> bcs{
            BoundaryCondition{BoundaryType::Dirichlet, 100.0},
            BoundaryCondition{BoundaryType::Dirichlet, 20.0},
            BoundaryCondition{BoundaryType::Robin, 0.0, 25.0, 20.0},
            BoundaryCondition{BoundaryType::Robin, 0.0, 25.0, 20.0}
        };

        solver.set_boundary_conditions(bcs);

        auto result = solver.run();
        if (result.has_value()) {
            const auto grid = solver.temperature_grid();
            const auto center_idx = (cfg.grid_y / 2) * cfg.grid_x + (cfg.grid_x / 2);
            std::cout << "Розрахунок завершено. Т_центр = " << grid[center_idx] << " °C\n";
        } else {
            std::cerr << "Помилка розв'язувача, код: " << static_cast<int>(result.error()) << '\n';
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

### 6. Нормативна таблиця теплофізичних властивостей матеріалів

У таблиці наведено довідкові значення коефіцієнтів теплопровідності, густини, питомої теплоємності, температуропровідності та ступеня чорноти для стандартних конструкційних матеріалів електроніки при температурі 20 °C (293 К):

| Матеріал | Теплопровідність `k` [Вт/(м·К)] | Густина `ρ` [кг/м³] | Питома теплоємність `c_p` [Дж/(кг·К)] | Температуропровідність `α` [м²/с] | Ступінь чорноти `ε` (поверхня) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Алмаз (монокристал)** | 2000.0 | 3520 | 518 | 1.10 × 10⁻³ | 0.70 |
| **Мідь (C11000)** | 385.0 | 8960 | 385 | 1.12 × 10⁻⁴ | 0.03 (полірована) / 0.78 (окислена) |
| **Алюміній (6061-T6)** | 167.0 | 2700 | 896 | 6.90 × 10⁻⁵ | 0.05 (полірований) / 0.85 (анодований) |
| **Кремній (Si, монокристал)**| 148.0 | 2330 | 712 | 8.92 × 10⁻⁵ | 0.60 |
| **Припій SAC305 (Sn-Ag-Cu)** | 58.0 | 7370 | 232 | 3.39 × 10⁻⁵ | 0.15 |
| **Сталь нержавіюча (AISI 304)**| 16.2 | 8000 | 500 | 4.05 × 10⁻⁶ | 0.17 (полірована) / 0.80 (окислена) |
| **Склотекстоліт FR-4 (PCB)** | 0.25 (паралельно) / 0.81 (перпендикулярно) | 1850 | 1100 | 1.23 × 10⁻⁷ | 0.90 (паяльна маска) |
| **Термопаста (стандарт)** | 1.5 – 8.5 | 2300 | 800 | 8.15 × 10⁻⁸ | 0.92 |
| **Повітря (1 атм, 20 °C)** | 0.026 | 1.204 | 1005 | 2.15 × 10⁻⁵ | не застосовується (газ) |
| **Вода (рідка, 20 °C)** | 0.598 | 998 | 4182 | 1.43 × 10⁻⁷ | 0.96 |

### 7. Порядок діагностики та обробки помилок

Під час виклику функцій обчислювального модуля виконується покрокова діагностика вхідних даних:
1. **Перевірка нульових вказівників**: якщо будь-який із обов'язкових аргументів (`config`, `material`, `grid_output`) має значення `NULL`, функція негайно повертає код `THERMAL_ERROR_NULL_POINTER`.
2. **Валідація фізичних параметрів**: перевіряється дотримання умов `k > 0`, `ρ > 0`, `c_p > 0`, `dx > 0` та `dy > 0`. При виявленні від'ємних або нульових значень обчислення переривається з кодом `THERMAL_ERROR_INVALID_PARAM`.
3. **Автоматичний контроль стійкості CFL**: перед початком часового циклу розв'язувач розраховує критичний крок `dt_max = 0.5 * min(dx², dy²) / α`. Якщо значення `dt` у конфігурації перевищує `dt_max`, функція повертає код `THERMAL_ERROR_CFL_VIOLATION`. Це запобігає виконанню завідомо нестійкого розрахунку та генерації недійсних числових значень `NaN`.
4. **Контроль збіжності стаціонарного стану**: якщо за максимальну кількість ітерацій норма зміни температурного поля не досягла величини `tolerance`, функція повертає код `THERMAL_ERROR_NO_CONVERGE`. Це сигналізує про наявність некоректних або взаємно суперечливих граничних умов (наприклад, задано повну теплоізоляцію на всіх межах при наявності внутрішніх джерел тепла).
