# 📋 Інтерфейс та API бібліотеки кругового відображення

На цій сторінці описано публічний програмний інтерфейс (API) та C/C++ бібліотеку `libcirclemap`, призначену для аналізу синус-кругового відображення Арнольда, розрахунку чисел обертання, ідентифікації режиму фазового захоплення, обчислення похідних драбини диявола та автоматичного пошуку меж язиків Арнольда у просторі параметрів.

Бібліотека розроблена за принципами високої обчислювальної ефективності, сумісності з C11 (ANSI C) та сучасними стандартизованими обгортками C++20.

## Архітектурний огляд та угоди про виклики

Бібліотека надає дворинний інтерфейс:
1. **Низькорівневе C-API:** Забезпечує пряму сумісність з іншими мовами програмування (Python, Rust, Julia, Fortran, C#) через двійковий інтерфейс ABI (англ. *Application Binary Interface*). Усі C-функції мають префікс `circle_map_`, використовують системні угоди про виклики `cdecl` та повертають цілочисельні коди помилок.
2. **Високорівневий C++20 API:** Пропонує об'єктно-орієнтовану обгортку у просторі імен `physics::nonlinear::api`, використовує строгу типізацію `std::span`, `std::optional`, `std::expected` (C++23) або винятки `std::invalid_argument`, заснований на принципах RAII для автоматичного управління пам'яттю та ресурсами.

### Потокобезпечність, повторна входжуваність та відсутність побічних ефектів

Усі обчислювальні функції бібліотеки є чисто функціональними (англ. *pure functions*), не використовують глобальний стан, статичні змінні чи модифіковані контексти. Вони є повністю повторно входжуваними (англ. *reentrant*) та потокобезпечними (англ. *thread-safe*). Розподіл завдань між кількома потоками виконання за допомогою OpenMP чи `std::jthread` не вимагає синхронізації м'ютексами.

Жодна функція обчислювального ядра не виділяє динамічну пам'ять на купі (англ. *heap*) під час розрахунку траєкторії, що гарантує відсутність затримок виділення пам'яті (англ. *zero allocation overhead*) та дозволяє використовувати бібліотеку в системах жорсткого реального часу (англ. *hard real-time systems*).

### Управління пам'яттю та володіння ресурсами

У низькорівневому C-API виділення пам'яті під двовимірні масиви сканування покладається на сторону виклику (англ. *caller-allocated buffers*). Передача вказівників на попередньо виділені масиви виключає приховані виділення пам'яті всередині бібліотеки та спрощує інтеграцію з буферами Python NumPy або C# Fixed Arrays.

У C++20 API використовуються контейнери `std::vector`, які автоматично керують життєвим циклом пам'яті на основі принципу RAII (англ. *Resource Acquisition Is Initialization*).

## Структури даних та типи типів

Нижче наведено основні конфігураційні структури, що передаються у функції API.

### Конфігурація одиночної траєкторії (`circle_map_config_t` / `CircleMapConfig`)

Структура описує параметри нелінійного відображення та налаштування чисельного інтегрування для одного експерименту:

* Поле `omega` (`double`): Безрозмірна відносна частота власного руху `Ω ∈ [0, 1]`. Значення обрізається до дробової частини `Ω - floor(Ω)`.
* Поле `k` (`double`): Амплітуда зовнішнього нелінійного зв'язку `K ≥ 0`. При `K ≤ 1` відображення є диффеоморфізмом колом, а при `K > 1` стає некоректним і допускає детермінований хаос.
* Поле `transient_steps` (`size_t`): Кількість початкових ітерацій для відкидання перехідного процесу (типово `10000`).
* Поле `measure_steps` (`size_t`): Кількість вимірювальних кроків для обчислення середнього зсуву фази (типово `50000`).
* Поле `initial_x` (`double`): Початкова фаза системи `x₀ ∈ [0, 1)`.

### Конфігурація сканування сітки (`circle_map_grid_params_t` / `GridScanParams`)

Структура задає межі прямокутної області в просторі параметрів `(Ω, K)` для сканування:

* Поле `omega_min`, `omega_max` (`double`): Нижжня та верхня межі діапазону сканування частоти `Ω`.
* Поле `k_min`, `k_max` (`double`): Нижжня та верхня межі діапазону сканування амплітуди нелінійності `K`.
* Поле `resolution_omega` (`size_t`): Кількість дискретних точок вздовж осі `Ω`.
* Поле `resolution_k` (`size_t`): Кількість дискретних точок вздовж осі `K`.

### Результат розрахунку траєкторії (`circle_map_result_t` / `SimulationResult`)

Структура містить повні результати аналізу обчисленої траєкторії:

* Поле `rotation_number` (`double`): Розраховане чисельне значення числа обертання `W`.
* Поле `numerator` (`int`): Чисельник найближчого раціонального дробу `p`.
* Поле `denominator` (`int`): Знаменник найближчого раціонального дробу `q`.
* Поле `is_locked` (`bool`): Прапорець фазового захоплення (істина, якщо `|W - p/q| ≤ tol`).
* Поле `lyapunov_exponent` (`double`): Старший показник Ляпунова `λ` для діагностики детермінованого хаосу.

## Коди повернення та детальна специфікація помилок

Усі низькорівневі C-функції повертають цілочисельний статус виконання типу `circle_map_status_t`:

* `CIRCLE_MAP_SUCCESS (0)`: Операція виконана успішно без помилок.
* `CIRCLE_MAP_ERROR_NULL_POINTER (-1)`: У функцію передано нульовий вказівник `NULL` замість дійсного масиву чи конфігурації.
* `CIRCLE_MAP_ERROR_INVALID_PARAM (-2)`: Один з параметрів виходить за допустимі межі (наприклад `measure_steps == 0`, `resolution_omega == 0` або `k < 0`).
* `CIRCLE_MAP_ERROR_CONVERGENCE (-3)`: Чисельний алгоритм бісекції або Ньютона — Рафсона не збігся за заданий ліміт ітерацій (типово 100 кроків бісекції).
* `CIRCLE_MAP_ERROR_OUT_OF_MEMORY (-4)`: Не вдалося виділити буфер пам'яті необхідного розміру (використовується лише у C++ контейнерних методів).

У C++20 API для передачі помилок без використання повільних винятків застосовується стандартний тип `std::expected<T, ApiErrorCode>`, що дозволяє обробляти помилки з нульовими накладними витратами часу виконання.

## Прогрес-колбеки та зворотні виклики

При моделюванні сіток високої роздільної здатності тривалість сканування може ставити кілька хвилин. Для відстеження прогресу виконання бібліотека надає механізм зворотних викликів (англ. *progress callbacks*).

Якщо функція-колбек повертає значення `false`, обчислювальний процес сканування негайно переривається з кодом повернення `CIRCLE_MAP_ERROR_CONVERGENCE`, а вже обчислені точки залишаються збереженими у вихідному масиві. Це дозволяє користувачу реалізувати кнопку скасування (англ. *Cancel*) у графічному інтерфейсі.

:::tabs
```c
#include <stddef.h>
#include <stdbool.h>

/**
 * @brief Сигнатура зворотного виклику прогресу виконання C-API.
 * @param completed_tasks Кількість завершених точок.
 * @param total_tasks Загальна кількість точок сітки.
 * @param user_data Користувацький вказівник контексту.
 * @return true продовжує обчислення, false перериває процес.
 */
typedef bool (*circle_map_progress_cb_t)(
    size_t completed_tasks,
    size_t total_tasks,
    void *user_data
);
```
```cpp
#include <functional>
#include <cstddef>

namespace physics::nonlinear::api {

/**
 * @brief Псевдонім C++20 для зворотного виклику прогресу.
 */
using ProgressCallback = std::function<bool(std::size_t completed, std::size_t total)>;

} // namespace physics::nonlinear::api
```
:::

## Серіалізація та чекпоінти станцій обчислень

Для збереження стану тривалих обчислень та можливості відновлення розрахунків після збою бібліотека надає функції серіалізатора стану.

Серіалізований буфер містить поточне значення фази `x[n]`, накопичений цілочисельний лічильник обертів `turns`, параметри відображення `Ω`, `K` та поточний номер кроку `current_step`.

:::tabs
```c
#include <stddef.h>
#include <stdint.h>

typedef struct {
    double current_x;
    int64_t total_turns;
    double omega;
    double k;
    size_t current_step;
} circle_map_state_t;

/**
 * @brief Зберігає поточний стан траєкторії у структуру стану.
 */
circle_map_status_t circle_map_save_state(
    double x, int64_t turns, double omega, double k, size_t step,
    circle_map_state_t *out_state
);
```
```cpp
#include <cstdint>
#include <cstddef>

namespace physics::nonlinear::api {

struct SimulationState {
    double current_x{0.0};
    std::int64_t total_turns{0};
    double omega{0.0};
    double k{0.0};
    std::size_t current_step{0};
};

class StateSerializer {
public:
    [[nodiscard]] static SimulationState capture(
        double x, std::int64_t turns, double omega, double k, std::size_t step) noexcept 
    {
        return SimulationState{x, turns, omega, k, step};
    }
};

} // namespace physics::nonlinear::api
```
:::

## Управління пулом обчислювальних потоків (Thread Pool API)

Для оптимізованої роботи у багатозадачних середовищах бібліотека підтримує створення та керування власністю пулу робочих потоків.

Функції керування пулом дозволяють фіксувати потоки за конкретними процесорними ядрами (англ. *CPU thread affinity*) для усунення перемикання контекстів кешу.

:::tabs
```c
typedef struct circle_map_thread_pool circle_map_thread_pool_t;

/**
 * @brief Створює новий пул обчислювальних потоків.
 */
circle_map_thread_pool_t* circle_map_thread_pool_create(size_t num_threads);

/**
 * @brief Знищує пул потоків та вивільняє ресурси.
 */
void circle_map_thread_pool_destroy(circle_map_thread_pool_t *pool);
```
```cpp
#include <memory>
#include <thread>
#include <vector>

namespace physics::nonlinear::api {

class ThreadPool {
public:
    explicit ThreadPool(std::size_t thread_count = std::thread::hardware_concurrency());
    ~ThreadPool();

    ThreadPool(const ThreadPool&) = delete;
    ThreadPool& operator=(const ThreadPool&) = delete;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace physics::nonlinear::api
```
:::

## Табличне прискорення тригонометрії (LUT Optimization API)

Для надання можливості надшвидкого розрахунку при моделюванні на ресурсно-обмежених мікроконтролерах (англ. *embedded microcontrollers*) бібліотека підтримує табличну оптимізацію обчислення синуса (англ. *Lookup Table / LUT*).

Попередньо розрахована таблиця синусів розміром `LUT_SIZE` (наприклад 4096 точок) з лінійною інтерполяцією підвищує швидкість обчислення кроку відображення у 3–5 разів порівняно зі стандартним викликом `sin()`.

:::tabs
```c
typedef struct {
    size_t table_size;
    const double *lut_values;
} circle_map_lut_config_t;

/**
 * @brief Ініціалізує та повертає конфігурацію LUT для прискорення.
 */
circle_map_status_t circle_map_init_lut(
    size_t table_size,
    circle_map_lut_config_t *out_lut
);
```
```cpp
#include <vector>
#include <cstddef>

namespace physics::nonlinear::api {

class LookupTable {
public:
    explicit LookupTable(std::size_t size = 4096);
    [[nodiscard]] double fast_sin(double phase) const noexcept;

private:
    std::vector<double> table_;
};

} // namespace physics::nonlinear::api
```
:::

## Адаптивне подрібнення сітки (Adaptive Grid Refinement API)

Для економії обчислювального часу при зйомці детальних фрактальних меж язиків Арнольда застосовується алгоритм адаптивного квадродерева (англ. *Quadtree Grid Refinement*).

Якщо різниця чисел обертання `|W_a - W_b|` між сусідніми вузлами сітки перевищує заданий поріг `delta_threshold`, комірка автоматично ділиться на чотири підкомірки.

:::tabs
```c
typedef struct {
    double delta_threshold;
    size_t max_depth;
} circle_map_adaptive_config_t;

/**
 * @brief Виконує адаптивне подрібнення сітки параметрів.
 */
circle_map_status_t circle_map_scan_grid_adaptive(
    const circle_map_config_t *base_cfg,
    const circle_map_adaptive_config_t *adapt_cfg,
    double omega_min, double omega_max,
    double k_min, double k_max
);
```
```cpp
namespace physics::nonlinear::api {

struct AdaptiveConfig {
    double delta_threshold{1e-3};
    std::size_t max_depth{5};
};

class AdaptiveGridScanner {
public:
    [[nodiscard]] static std::expected<void, ApiErrorCode> scan_adaptive(
        const CircleMapConfig& base_config,
        const AdaptiveConfig& adapt_config,
        const GridBounds& bounds) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль аналізу квазіперіодичності та золотого перетину (Golden Ratio API)

Для дослідження критичного переходу від торичного квазіперіодичного руху до хаосу при золотому перетині `Ω_golden = (√5 - 1) / 2 ≈ 0.6180339887` надається спеціалізована функція обчислення сходинок дробу Фібоначчі.

:::tabs
```c
typedef struct {
    double golden_ratio_w;
    double critical_k;
    double lyapunov_at_critical;
} circle_map_golden_result_t;

/**
 * @brief Аналізує критичну універсальність при золотому перетині.
 */
circle_map_status_t circle_map_analyze_golden_ratio(
    size_t steps,
    circle_map_golden_result_t *out_result
);
```
```cpp
namespace physics::nonlinear::api {

struct GoldenRatioMetrics {
    double golden_w{0.618033988749895};
    double critical_k{1.0};
    double lyapunov{0.0};
};

class GoldenRatioAnalyzer {
public:
    [[nodiscard]] static std::expected<GoldenRatioMetrics, ApiErrorCode> analyze(
        std::size_t steps = 100000) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль графічного прискорення GPGPU (CUDA / OpenCL Accelerator API)

Для проведення масивних комп'ютерних експериментів із роздільною здатністю понад `10000 × 10000` точок сітки бібліотека інтегрує інтерфейс делегування обчислень на графічні процесори (GPGPU).

:::tabs
```c
typedef struct {
    int device_id;
    size_t threads_per_block;
} circle_map_gpu_config_t;

/**
 * @brief Виконує сканування сітки на прискорювачі GPU.
 */
circle_map_status_t circle_map_scan_grid_gpu(
    const circle_map_config_t *base_cfg,
    const circle_map_gpu_config_t *gpu_cfg,
    double omega_min, double omega_max, size_t res_omega,
    double k_min, double k_max, size_t res_k,
    double *out_w_matrix
);
```
```cpp
namespace physics::nonlinear::api {

struct GpuConfig {
    int device_id{0};
    std::size_t threads_per_block{256};
};

class GpuGridScanner {
public:
    [[nodiscard]] static std::expected<std::vector<double>, ApiErrorCode> scan_gpu(
        const CircleMapConfig& base_config,
        const GpuConfig& gpu_config,
        const GridBounds& bounds) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль аналізу біфуркацій подвоєння періоду (Period-Doubling Bifurcation API)

При значеннях параметра зв'язку `K > 1` відображення Арнольда втрачає обратність та зазнає каскаду біфуркацій подвоєння періоду.

Функції цього модуля дозволяють обчислювати точки послідовних біфуркацій та розраховувати універсальну константу Фейгенбаума `δ ≈ 4.6692016`.

:::tabs
```c
typedef struct {
    double k_bifurcation;
    int period;
    double feigenbaum_delta;
} circle_map_bifurcation_point_t;

/**
 * @brief Знаходить точку наступної біфуркації подвоєння періоду.
 */
circle_map_status_t circle_map_find_bifurcation(
    double k_start,
    int current_period,
    circle_map_bifurcation_point_t *out_bif
);
```
```cpp
namespace physics::nonlinear::api {

struct BifurcationPoint {
    double k_bifurcation{0.0};
    int period{1};
    double feigenbaum_delta{4.6692016};
};

class BifurcationAnalyzer {
public:
    [[nodiscard]] static std::expected<BifurcationPoint, ApiErrorCode> find_next_bifurcation(
        double k_start, int current_period) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль перевірки системної точності та лімітів (Capability & Precision API)

Для забезпечення коректної роботи на різних апаратних платформах надаються методи інспекції системних можливостей (англ. *system capabilities*).

:::tabs
```c
typedef struct {
    bool has_avx2_support;
    bool has_fp16_support;
    size_t simd_vector_width;
} circle_map_capabilities_t;

/**
 * @brief Отримує апаратні характеристики процесора.
 */
circle_map_status_t circle_map_get_capabilities(
    circle_map_capabilities_t *out_caps
);
```
```cpp
namespace physics::nonlinear::api {

struct SystemCapabilities {
    bool has_avx2{false};
    bool has_fp16{false};
    std::size_t simd_width{4};
};

class CapabilityInspector {
public:
    [[nodiscard]] static SystemCapabilities inspect() noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль генерації палітри колірного відображення (Palette Color Mapping API)

Для перетворення матриць чисел обертання у повноколірні RGB-зображення карти Арнольда надається модуль палітри:

:::tabs
```c
typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} circle_map_color_rgb_t;

/**
 * @brief Перетворює число обертання W у RGB колір за вибраною палітрою.
 */
circle_map_color_rgb_t circle_map_rotation_to_rgb(double w, bool is_locked);
```
```cpp
#include <cstdint>

namespace physics::nonlinear::api {

struct RGBColor {
    std::uint8_t r{0};
    std::uint8_t g{0};
    std::uint8_t b{0};
};

class ColorMapper {
public:
    [[nodiscard]] static constexpr RGBColor map_rotation(double w, bool is_locked) noexcept {
        if (is_locked) {
            return RGBColor{0, 128, 255};
        }
        const auto val = static_cast<std::uint8_t>(w * 255.0);
        return RGBColor{val, val, val};
    }
};

} // namespace physics::nonlinear::api
```
:::

## Модуль зв'язаних кругових відображень (Coupled Maps Array API)

Для дослідження синхронізації в ансамблях з `N` нелінійних осциляторів надається розширена функція моделювання решітки зв'язаних відображень (англ. *Coupled Map Lattices / CML*):

```
x_i[n+1] = x_i[n] + Ω_i - (K / (2·π)) · sin(2·π·x_i[n]) + (g / 2) · (sin(2·π·(x_{i+1} - x_i)) + sin(2·π·(x_{i-1} - x_i)))
```

де `g` — коефіцієнт міжосциляторного зв'язку (англ. *inter-oscillator coupling strength*).

:::tabs
```c
typedef struct {
    size_t num_oscillators;
    const double *omegas;
    double k_global;
    double coupling_g;
} circle_map_coupled_config_t;

/**
 * @brief Обчислює вектор чисел обертання для ансамблю осциляторів.
 */
circle_map_status_t circle_map_solve_coupled(
    const circle_map_coupled_config_t *cfg,
    size_t steps,
    double *out_rotations
);
```
```cpp
namespace physics::nonlinear::api {

struct CoupledSystemConfig {
    std::vector<double> omegas;
    double k_global{0.5};
    double coupling_strength{0.1};
    std::size_t steps{10000};
};

class CoupledCircleMapSolver {
public:
    [[nodiscard]] static std::expected<std::vector<double>, ApiErrorCode> solve_ensemble(
        const CoupledSystemConfig& config) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль профілювання продуктивності та тестування (Profiling & Benchmark API)

Для оцінки швидконодії та точності обчислень бібліотека містить вбудовані утиліти профілювання часу виконання та перевірки накреслених метрик.

:::tabs
```c
typedef struct {
    double execution_time_seconds;
    double iterations_per_second;
    size_t cache_misses_est;
} circle_map_perf_metrics_t;

/**
 * @brief Вимірює час виконання та продуктивність ядра.
 */
circle_map_status_t circle_map_benchmark(
    const circle_map_config_t *cfg,
    circle_map_perf_metrics_t *out_metrics
);
```
```cpp
namespace physics::nonlinear::api {

struct PerformanceMetrics {
    double execution_time_seconds{0.0};
    double iterations_per_second{0.0};
    std::size_t cache_misses_est{0};
};

class Profiler {
public:
    [[nodiscard]] static PerformanceMetrics benchmark_solver(
        const CircleMapConfig& config) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль розподіленого сканування MPI (MPI Distributed API)

Для розрахунку надвисокороздільних карт (наприклад `10000 × 10000` точок) на обчислювальних кластерах та суперкомп'ютерах надається модуль розподілених обчислень на основі стандарту MPI (англ. *Message Passing Interface*).

Головний процес (англ. *master rank 0*) розбиває прямокутну сітку `(Ω, K)` на горизонтальні смуги і розсилає їх робочим вузлам (англ. *worker ranks*). Підсумкові матриці збираються викликом `MPI_Gatherv`.

:::tabs
```c
/**
 * @brief Виконує розподілене сканування сітки за допомогою MPI.
 */
circle_map_status_t circle_map_scan_grid_mpi(
    const circle_map_config_t *base_cfg,
    double omega_min, double omega_max, size_t res_omega,
    double k_min, double k_max, size_t res_k,
    double *out_w_matrix
);
```
```cpp
namespace physics::nonlinear::api {

class MpiGridScanner {
public:
    [[nodiscard]] static std::expected<std::vector<double>, ApiErrorCode> scan_distributed(
        const CircleMapConfig& base_config,
        const GridBounds& bounds) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль тестування фазового шуму (Phase Noise API)

Для моделювання реальних фізичних та генераторних систем під дією теплових та джиттерних завад додається виклик стохастичного відображення:

```
x[n+1] = x[n] + Ω - (K / (2·π)) · sin(2·π·x[n]) + ξ[n]
```

де `ξ[n]` — білий гауссівський шум з нульовим математичним сподіванням та середньоквадратичним відхиленням `σ_noise`.

:::tabs
```c
typedef struct {
    double noise_sigma;
    uint64_t random_seed;
} circle_map_noise_config_t;

/**
 * @brief Розраховує траєкторію за наявності гауссівського фазового шуму.
 */
circle_map_status_t circle_map_solve_noisy(
    const circle_map_config_t *cfg,
    const circle_map_noise_config_t *noise_cfg,
    circle_map_result_t *out_result
);
```
```cpp
#include <cstdint>

namespace physics::nonlinear::api {

struct NoiseConfig {
    double noise_sigma{0.001};
    std::uint64_t random_seed{42};
};

class NoisyCircleMapSolver {
public:
    NoisyCircleMapSolver(CircleMapConfig base_config, NoiseConfig noise_config)
        : base_config_{base_config}, noise_config_{noise_config} {}

    [[nodiscard]] std::expected<SimulationResult, ApiErrorCode> solve() const noexcept;

private:
    CircleMapConfig base_config_;
    NoiseConfig noise_config_;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль аналізу ізоліній та ізоклін числа обертання (Isocline API)

Бібліотека надає спеціалізовані функції для чисельного побудування ізоліній постійного числа обертання `W(Ω, K) = W_target` у просторі параметрів.

Алгоритм відстеження ізокліни (англ. *isocline continuation*) застосовує адаптивний крок по `K` та шукає відповідне значення `Ω` методом Ньютона на кожному зрізі.

:::tabs
```c
typedef struct {
    double target_w;
    double k_start;
    double k_end;
    size_t steps_k;
} circle_map_isocline_config_t;

/**
 * @brief Розраховує вектор точок ізолінії W = const.
 */
circle_map_status_t circle_map_trace_isocline(
    const circle_map_isocline_config_t *cfg,
    double *out_omega_array,
    double *out_k_array
);
```
```cpp
namespace physics::nonlinear::api {

struct IsoclineConfig {
    double target_w{0.5};
    double k_start{0.0};
    double k_end{1.0};
    std::size_t steps_k{100};
};

struct IsoclinePoint {
    double omega{0.0};
    double k{0.0};
};

class IsoclineTracer {
public:
    [[nodiscard]] static std::expected<std::vector<IsoclinePoint>, ApiErrorCode> trace(
        const IsoclineConfig& config) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Модуль спектрального аналізу фазових траєкторій (FFT Spectral API)

Для розрізнення багатоперіодичних орбіт та квазіперіодичних режимів з невимірними частотами бібліотека інтегрує модуль дискретного перетворення Фур'є (FFT) над фазовою послідовністю `e^(2·π·i·x[n])`.

Спектральні піки відповідають раціональним гармонікам числа обертання `W`, а суцільний шумовий спектр сигналізує про виникнення детермінованого хаосу при `K > 1`.

:::tabs
```c
typedef struct {
    size_t fft_size;
    double *real_spectrum;
    double *imag_spectrum;
    double dominant_frequency;
} circle_map_spectrum_t;

/**
 * @brief Обчислює спектр потужності фазової послідовності.
 */
circle_map_status_t circle_map_compute_spectrum(
    const circle_map_config_t *cfg,
    size_t fft_size,
    circle_map_spectrum_t *out_spectrum
);
```
```cpp
namespace physics::nonlinear::api {

struct FourierSpectrum {
    std::vector<double> frequencies;
    std::vector<double> magnitudes;
    double dominant_frequency{0.0};
};

class SpectrumAnalyzer {
public:
    [[nodiscard]] static std::expected<FourierSpectrum, ApiErrorCode> analyze(
        const CircleMapConfig& config, std::size_t fft_size = 1024) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Експорт результатів у бінарні файли формату HDF5

Для наукових розрахунків великого масштабу бібліотека підтримує прямий вивід двовимірних масивів у формат HDF5 (англ. *Hierarchical Data Format v5*).

Цей формат підтримує прозоре стиснення масивів алгоритмами zlib/szip та збереження метаданих експерименту у вигляді HDF5-атрибутів.

:::tabs
```c
/**
 * @brief Зберігає двовимірну матрицю чисел обертання у файл HDF5.
 */
circle_map_status_t circle_map_export_hdf5(
    const char *filepath,
    const double *w_matrix,
    size_t res_omega,
    size_t res_k
);
```
```cpp
#include <string_view>
#include <span>

namespace physics::nonlinear::api {

class Hdf5Exporter {
public:
    [[nodiscard]] static std::expected<void, ApiErrorCode> save(
        std::string_view filepath,
        std::span<const double> w_matrix,
        std::size_t res_omega,
        std::size_t res_k) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Опис функцій C-API та C++20 API

У цьому розділі наведено точний сигнатурний контракт C-API та ідіоматичний C++20 API.

### 1. Функція обчислення траєкторії `circle_map_solve`

**Призначення:** Моделює траєкторію відображення для заданих параметрів, розраховує число обертання та показник Ляпунова.

:::tabs
```c
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    CIRCLE_MAP_SUCCESS = 0,
    CIRCLE_MAP_ERROR_NULL_POINTER = -1,
    CIRCLE_MAP_ERROR_INVALID_PARAM = -2,
    CIRCLE_MAP_ERROR_CONVERGENCE = -3,
    CIRCLE_MAP_ERROR_OUT_OF_MEMORY = -4
} circle_map_status_t;

typedef struct {
    double omega;
    double k;
    size_t transient_steps;
    size_t measure_steps;
    double initial_x;
} circle_map_config_t;

typedef struct {
    double rotation_number;
    int numerator;
    int denominator;
    bool is_locked;
    double lyapunov_exponent;
} circle_map_result_t;

/**
 * @brief Обчислює число обертання та режим захоплення фази.
 * @param[in] cfg Вказівник на конфігурацію параметрів.
 * @param[in] max_q Максимальний розглядний знаменник резонансу.
 * @param[in] tol Допустиме відхилення для фіксації фазового захоплення.
 * @param[out] out_result Вказівник на структуру для запису результатів.
 * @return Код статусу виконання circle_map_status_t.
 */
circle_map_status_t circle_map_solve(
    const circle_map_config_t *cfg,
    int max_q,
    double tol,
    circle_map_result_t *out_result
);
```
```cpp
#include <optional>
#include <expected>
#include <numbers>
#include <span>
#include <string_view>
#include <vector>

namespace physics::nonlinear::api {

enum class ApiErrorCode {
    NullPointer,
    InvalidParameter,
    ConvergenceFailure,
    OutOfMemory
};

struct CircleMapConfig {
    double omega{0.0};
    double k{0.0};
    std::size_t transient_steps{10000};
    std::size_t measure_steps{50000};
    double initial_x{0.0};
};

struct ResonanceInfo {
    int numerator{0};
    int denominator{1};
    double error{0.0};
};

struct SimulationResult {
    double rotation_number{0.0};
    std::optional<ResonanceInfo> resonance{};
    double lyapunov_exponent{0.0};
};

class CircleMapSolver {
public:
    explicit constexpr CircleMapSolver(CircleMapConfig config) noexcept
        : config_{config} {}

    [[nodiscard]] std::expected<SimulationResult, ApiErrorCode> solve(
        int max_denominator = 16,
        double tolerance = 1e-4) const noexcept;

private:
    CircleMapConfig config_;
};

} // namespace physics::nonlinear::api
```
:::

### 2. Функція сканування двовимірної сітки `circle_map_scan_grid`

**Призначення:** Багатопотокова обробка масиву параметрів у прямокутній сітці з поверненням буфера чисел обертання та масиву прапорців фазового захоплення.

**Параметри:**
* `grid_params`: Межі діапазонів сканування та роздільна здатність.
* `base_cfg`: Базові налаштування кількості ітерацій.
* `out_w_matrix`: Попередньо виділений масив розміром `resolution_omega × resolution_k` для чисел обертання.
* `out_locked_matrix`: Попередньо виділений масив прапорців захоплення.

**Керування пам'яттю:** Виділення та звільнення пам'яті під вихідні масиви покладається на клієнтський код. Бібліотека не зберігає вказівники на виділені буфери.

:::tabs
```c
/**
 * @brief Сканує двовимірну сітку параметрів (Omega, K).
 * @param[in] base_cfg Кількість ітерацій та початкові умови.
 * @param[in] omega_min Нижнє значення Omega.
 * @param[in] omega_max Верхнє значення Omega.
 * @param[in] res_omega Роздільна здатність по осі Omega.
 * @param[in] k_min Нижнє значення K.
 * @param[in] k_max Верхнє значення K.
 * @param[in] res_k Роздільна здатність по осі K.
 * @param[out] out_w_matrix Вихідний масив чисел обертання (розмір res_w * res_k).
 * @param[out] out_locked_matrix Вихідний масив статусу захоплення (розмір res_w * res_k).
 * @return Код статусу виконання circle_map_status_t.
 */
circle_map_status_t circle_map_scan_grid(
    const circle_map_config_t *base_cfg,
    double omega_min, double omega_max, size_t res_omega,
    double k_min, double k_max, size_t res_k,
    double *out_w_matrix,
    bool *out_locked_matrix
);
```
```cpp
namespace physics::nonlinear::api {

struct GridBounds {
    double omega_min{0.0};
    double omega_max{1.0};
    std::size_t res_omega{100};
    double k_min{0.0};
    double k_max{1.0};
    std::size_t res_k{100};
};

class GridScanner {
public:
    explicit GridScanner(CircleMapConfig base_config)
        : base_config_{base_config} {}

    [[nodiscard]] std::expected<std::vector<SimulationResult>, ApiErrorCode> scan(
        const GridBounds& bounds) const;

private:
    CircleMapConfig base_config_;
};

} // namespace physics::nonlinear::api
```
:::

### 3. Функція виявлення точних меж язика `circle_map_find_tongue_boundaries`

**Призначення:** Пошук лівої `Ω_left` та правої `Ω_right` меж язика Арнольда для заданого раціонального резонансу `p/q` при зафіксованій амплітуді `K` методом ділення навпіл (бісекції).

**Параметри:**
* `k_val`: Фіксоване значення параметра нелінійності `K`.
* `p`, `q`: Чисельник та знаменник цільового резонансу.
* `bisection_tol`: Допустима похибка визначення межі по `Ω` (типово `10⁻⁶`).
* `out_omega_left`: Вказівник для запису лівої межі `Ω_left`.
* `out_omega_right`: Вказівник для запису правої межі `Ω_right`.

:::tabs
```c
/**
 * @brief Знаходить ліву та праву межі язика Арнольда p/q при заданому K.
 * @param[in] k_val Амплітуда нелінійного зв'язку K.
 * @param[in] p Чисельник резонансу.
 * @param[in] q Знаменник резонансу.
 * @param[in] bisection_tol Точність пошуку межі.
 * @param[out] out_omega_left Ліва межа язика Omega_left.
 * @param[out] out_omega_right Права межа язика Omega_right.
 * @return Код статусу виконання circle_map_status_t.
 */
circle_map_status_t circle_map_find_tongue_boundaries(
    double k_val,
    int p,
    int q,
    double bisection_tol,
    double *out_omega_left,
    double *out_omega_right
);
```
```cpp
namespace physics::nonlinear::api {

struct TongueBoundaries {
    double omega_left{0.0};
    double omega_right{0.0};
    double width{0.0};
};

class TongueBoundaryFinder {
public:
    [[nodiscard]] static std::expected<TongueBoundaries, ApiErrorCode> find_boundaries(
        double k_val, int p, int q, double tolerance = 1e-6) noexcept;
};

} // namespace physics::nonlinear::api
```
:::

## Специфікація двійкового інтерфейсу (ABI) та зв'язування

Для підтримки повної сумісності двійкового коду (ABI) між різними компіляторами (GCC, Clang, MSVC) бібліотека задовольняє наступним вимогам:

1. **Компонування C-символів:** Усі заголовочні файли обгорнуті блоком `extern "C"`, що запобігає спотворенню імен функцій (англ. *name mangling*) у C++.
2. **Вирівнювання структур:** Структури C-API мають явне вирівнювання по 8 байт, відповідаючи стандартній упаковці типів плаваючої крапки `double` та `size_t`.
3. **Версіонування ABI:** Заголовочний файл містить константи версії `CIRCLE_MAP_VERSION_MAJOR`, `CIRCLE_MAP_VERSION_MINOR` та `CIRCLE_MAP_VERSION_PATCH`.

:::tabs
```c
#ifdef __cplusplus
extern "C" {
#endif

#define CIRCLE_MAP_VERSION_MAJOR 1
#define CIRCLE_MAP_VERSION_MINOR 0
#define CIRCLE_MAP_VERSION_PATCH 0

/**
 * @brief Повертає текстовий рядок з повною версією бібліотеки.
 */
const char* circle_map_get_version_string(void);

#ifdef __cplusplus
}
#endif
```
```cpp
#include <string_view>

namespace physics::nonlinear::api {

struct LibraryVersion {
    int major{1};
    int minor{0};
    int patch{0};

    [[nodiscard]] static constexpr std::string_view string() noexcept {
        return "1.0.0";
    }
};

} // namespace physics::nonlinear::api
```
:::

## Інтеграція з іншими мовами програмування

Завдяки наявності чистого C-API бібліотека легко підключається до високорівневих мов програмування без необхідності написання складних C-розширень.

### Інтеграція з Python (ctypes)

Приклад створення Python-обгортки над системною динамічною бібліотекою `libcirclemap.so` / `circlemap.dll`:

```python
import ctypes

class CircleMapConfig(ctypes.Structure):
    _fields_ = [
        ("omega", ctypes.c_double),
        ("k", ctypes.c_double),
        ("transient_steps", ctypes.c_size_t),
        ("measure_steps", ctypes.c_size_t),
        ("initial_x", ctypes.c_double)
    ]

class CircleMapResult(ctypes.Structure):
    _fields_ = [
        ("rotation_number", ctypes.c_double),
        ("numerator", ctypes.c_int),
        ("denominator", ctypes.c_int),
        ("is_locked", ctypes.c_bool),
        ("lyapunov_exponent", ctypes.c_double)
    ]

# Завантаження бібліотеки
lib = ctypes.CDLL("./libcirclemap.so")
lib.circle_map_solve.argtypes = [
    ctypes.POINTER(CircleMapConfig),
    ctypes.c_int,
    ctypes.c_double,
    ctypes.POINTER(CircleMapResult)
]
lib.circle_map_solve.restype = ctypes.c_int
```

## Повний приклад використання C-API та C++20 API

Нижче наведено завершені приклади програм, які ініціалізують конфігураційні структури, викликають функції розрахунку траєкторії та обробляють повернені результати або коди помилок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Припускаємо наявність заголовочного файла C-API */
#include "circle_map.h"

int main(void) {
    circle_map_config_t cfg = {
        .omega = 0.5,
        .k = 0.7,
        .transient_steps = 10000,
        .measure_steps = 50000,
        .initial_x = 0.2
    };

    circle_map_result_t result;
    circle_map_status_t status = circle_map_solve(&cfg, 16, 1e-4, &result);

    if (status != CIRCLE_MAP_SUCCESS) {
        fprintf(stderr, "Помилка обчислення: код %d\n", status);
        return EXIT_FAILURE;
    }

    printf("=== Результати обчислення через C-API ===\n");
    printf("Число обертання W: %.6f\n", result.rotation_number);
    printf("Показник Ляпунова lambda: %.6f\n", result.lyapunov_exponent);

    if (result.is_locked) {
        printf("Статус: Захоплення фази на резонансі %d/%d\n", result.numerator, result.denominator);
    } else {
        printf("Статус: Квазіперіодичний режим\n");
    }

    /* Пошук меж язика 1/2 при K = 0.7 */
    double w_left = 0.0, w_right = 0.0;
    status = circle_map_find_tongue_boundaries(0.7, 1, 2, 1e-6, &w_left, &w_right);
    if (status == CIRCLE_MAP_SUCCESS) {
        printf("Межі язика 1/2 при K=0.7: Omega in [%.6f, %.6f], ширина = %.6f\n",
               w_left, w_right, w_right - w_left);
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <vector>

// Припускаємо наявність заголовочного файла C++ API
#include "circle_map.hpp"

int main() {
    using namespace physics::nonlinear::api;

    const CircleMapConfig config{
        .omega = 0.5,
        .k = 0.7,
        .transient_steps = 10000,
        .measure_steps = 50000,
        .initial_x = 0.2
    };

    const CircleMapSolver solver{config};
    const auto outcome = solver.solve(16, 1e-4);

    if (!outcome) {
        std::cerr << "Помилка обчислення C++ API!\n";
        return 1;
    }

    const auto& res = outcome.value();
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "=== Результати обчислення через C++20 API ===\n";
    std::cout << "Число обертання W: " << res.rotation_number << "\n";
    std::cout << "Показник Ляпунова lambda: " << res.lyapunov_exponent << "\n";

    if (res.resonance) {
        std::cout << "Статус: Захоплення фази на резонансі "
                  << res.resonance->numerator << "/" << res.resonance->denominator
                  << " (абсолютна похибка: " << res.resonance->error << ")\n";
    } else {
        std::cout << "Статус: Квазіперіодичний режим\n";
    }

    const auto bounds_outcome = TongueBoundaryFinder::find_boundaries(0.7, 1, 2, 1e-6);
    if (bounds_outcome) {
        const auto& b = bounds_outcome.value();
        std::cout << "Межі язика 1/2 при K=0.7: Omega in ["
                  << b.omega_left << ", " << b.omega_right
                  << "], ширина = " << b.width << "\n";
    }

    return 0;
}
```
:::

## Рекомендації з інтеграції та сумісності

При включенні бібліотеки `libcirclemap` у сторонні обчислювальні проекти дотримуйтесь наступних практичних правил:

1. **Компіляція:** Для досягнення максимальної швидкості використовуйте прапори оптимізації `-O3 -ffast-math -march=native`.
2. **Низька похибка плаваючої крапки:** Якщо вимагається точність вище `10⁻⁸` для знаменників `q > 100`, замініть тип `double` на `long double` або підключіть версію бібліотеки з підтримкою квадро-точності (англ. *quad precision `__float128`*).
3. **Прив'язки до Python (Ctypes / Pybind11):** Завдяки чистому двійковому C-API бібліотека легко підключається до Python без компенсації продуктивності за допомогою модуля `ctypes` або бібліотеки `pybind11`.
4. **Контроль витоків пам'яті:** Усі ресурси, виділені функціями створення пулів потоків чи спектрального аналізу, мають явно звільнятися відповідними парними функціями знищення.
5. **Обробка помилок в ініціалізаторах:** Завжди перевіряйте повернутий статус `circle_map_status_t` перед використанням вихідних буферів, оскільки передача нульових вказівників спричиняє негайне переривання з кодом помилки.
