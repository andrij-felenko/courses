# 📋 Інтерфейс та контракт C/C++ бібліотеки розв'язувача вихорових систем

Цей документ визначає публічний програмний інтерфейс (API Contract), специфікацію структур даних, коди помилок та інженерні угоди C/C++ бібліотеки `libvortex_solver` для чисельного розрахунку динаміки вихорових ниток та точкових вихорів на основі закону Біо — Савара та теорем Гельмгольца.

Бібліотека призначена для використання в обчислювальній гідродинаміці (CFD), аерокосмічному моделюванні, розрахунках зносних вихорових слідів за крилами літаків та вітротурбінами.

## 1. Загальна архітектура, контракти пам'яті та потокобезпечність

Бібліотека `libvortex_solver` розроблена із дотриманням стандартів C11 та C++17. Вона надає суворо C-сумісний ABI (Application Binary Interface) для інтеграції у C/C++ проекти, а також підключення через FFI (Foreign Function Interface) до мов Python, Rust, Julia чи Go.

### 1.1 Контракт управління пам'яттю
- Усі об'єкти конфігурацій, масивів вихорів та результатів розрахунку, виділені функціями бібліотеки (`vortex_system_create_*`), залишаються під володінням обчислювального ядра до тих пір, поки користувач явно не звільнить їх відповідними процедурами `vortex_system_free()`.
- Виклик системної функції `free()` або `delete` безпосередньо на внутрішніх вказівниках повертає невизначену поведінку (Undefined Behavior).
- Усі внутрішні масиви координат вихорів вирівнюються у пам'яті за кордоном 64 байт (`alignas(64)`). Це забезпечує максимальну продуктивність AVX-512 та SIMD векторних інструкцій при обчисленні паралельних сум Біо — Савара складністю `O(N²)`.
- Усі процедури динамічного виділення пам'яті перевіряють результат виклику системного розподілювача і повертають код статусу `VORTEX_ERR_OUT_OF_MEMORY` у разі браку системних ресурсів.

### 1.2 Потокобезпечність та реентерабельність
- Усі процедури обчислення поля індукованих швидкостей є строго повторно входжуваними (reentrant).
- Обчислювальне ядро не використовує глобального або статичного стану.
- Паралельне обчислення швидкостей у різних потоках POSIX (pthread) або OpenMP для незалежних екземплярів вихорових систем виконується повністю без блокувань м'ютексами.

### 1.3 Обробка помилок та діагностика
Жодна функція C API не генерує винятків. Усі процедури повертають код статусу `vortex_status_t`. У C++ обгортці від'ємні коди статусів автоматично транслюються у винятки `std::runtime_error` або `std::invalid_argument`.

---

## 2. Коди статусів та специфікація типів даних (`:::tabs`)

Нижче наведено вичерпну специфікацію кодів статусів, переліків регуляризації ядра та конфігураційних структур мовами C та C++.

:::tabs
```c
typedef enum {
    VORTEX_SUCCESS                  =  0,  /* Операція виконана успішно */
    VORTEX_ERR_INVALID_PARAM        = -1,  /* Некоректний параметр (NULL, N <= 0, dt <= 0) */
    VORTEX_ERR_OUT_OF_MEMORY        = -2,  /* Помилка виділення пам'яті */
    VORTEX_ERR_CORE_SINGULARITY     = -3,  /* Відстань між вихорами < ε при вимкненій регуляризації */
    VORTEX_ERR_INTEGRATION_DIVERGED  = -4,  /* Чисельна незбіжність (координати прямують до NaN/Inf) */
    VORTEX_ERR_DIMENSION_MISMATCH   = -5   /* Несумісність виміру домену (очікувалося 2D замість 3D) */
} vortex_status_t;

typedef enum {
    VORTEX_CORE_SINGULAR   = 0,  /* Точковий вихор Біо — Савара без регуляризації (1/r) */
    VORTEX_CORE_KRASNY     = 1,  /* Ядро Красного: 1 / (r² + ε²) */
    VORTEX_CORE_LAMB_OSEEN = 2   /* Ядро Лемба — Осеєна з в'язкою дифузією ядра: 1 - exp(-r²/ε²) */
} vortex_core_type_t;

typedef enum {
    VORTEX_INTEGRATOR_EULER = 0,  /* Метод Ейлера 1-го порядку (лише для тестів) */
    VORTEX_INTEGRATOR_RK4   = 1   /* Метод Рунге — Кутти 4-го порядку */
} vortex_integrator_type_t;

typedef struct {
    double x;         /* Положення за віссю X [м] */
    double y;         /* Положення за віссю Y [м] */
    double z;         /* Положення за віссю Z [м] (0.0 для 2D) */
    double gamma;     /* Інтенсивність вихору (циркуляція Г) [м²/с] */
} vortex_point_t;

typedef struct {
    int num_vortices;                   /* Кількість вихорів у системі */
    double core_radius_eps;             /* Радіус ядра регуляризації ε [м] */
    vortex_core_type_t core_type;       /* Тип ядра регуляризації Біо — Савара */
    vortex_integrator_type_t integrator;/* Схема чисельного інтегрування */
    double dt;                          /* Крок інтегрування за часом [с] */
    int is_3d;                          /* Прапорець 3D системи (1 — 3D нитки, 0 — 2D точки) */
} vortex_solver_config_t;

typedef struct {
    double total_circulation;    /* Сумарна циркуляція ∑ Г_i */
    double center_of_vorticity_x;/* Центр вихореності X_com = ∑(Г_i * x_i) / ∑Г_i */
    double center_of_vorticity_y;/* Центр вихореності Y_com = ∑(Г_i * y_i) / ∑Г_i */
    double angular_momentum;     /* Момент імпульсу M = ∑ Г_i * (x_i² + y_i²) */
    double kinetic_energy;       /* Квазі-енергія взаємодії E = -1/(4π) ∑∑ Г_i Г_j ln(r_ij) */
} vortex_invariants_t;
```
```cpp
#include <cstdint>
#include <string_view>

namespace vortex {

enum class Status : int32_t {
    Success             =  0,
    InvalidParam        = -1,
    OutOfMemory         = -2,
    CoreSingularity     = -3,
    IntegrationDiverged = -4,
    DimensionMismatch   = -5
};

enum class CoreType : uint8_t {
    Singular  = 0,
    Krasny    = 1,
    LambOseen = 2
};

enum class IntegratorType : uint8_t {
    Euler = 0,
    RK4   = 1
};

struct Point {
    double x{0.0};
    double y{0.0};
    double z{0.0};
    double gamma{0.0};
};

struct Config {
    int32_t num_vortices{0};
    double core_radius_eps{0.01};
    CoreType core_type{CoreType::Krasny};
    IntegratorType integrator{IntegratorType::RK4};
    double dt{0.001};
    bool is_3d{false};
};

struct Invariants {
    double total_circulation{0.0};
    double center_of_vorticity_x{0.0};
    double center_of_vorticity_y{0.0};
    double angular_momentum{0.0};
    double kinetic_energy{0.0};
};

} // namespace vortex
```
:::

---

## 3. Детальна розшифровка кодів помилок `vortex_status_t`

Детальний аналіз можливих штатно та аварійно визначених ситуацій дозволяє розробникам будувати надійні гідродинамічні розв'язувачі:

1. `VORTEX_SUCCESS (0)`: Операція виконана успішно. Всі вихідні масиви містять коректні обчислені значення.
2. `VORTEX_ERR_INVALID_PARAM (-1)`: Передано некоректний вхідний аргумент. Виникає у таких випадках:
   - Вказівник на структуру конфігурації або масив вихорів дорівнює `NULL`.
   - Кількість вихорів `num_vortices <= 0`.
   - Крок інтегрування за часом `dt <= 0.0`.
   - Радіус регуляризаційного ядра `core_radius_eps < 0.0`.
   - Дії користувача: перевірити валідність вхідних параметрів перед викликом функції.
3. `VORTEX_ERR_OUT_OF_MEMORY (-2)`: Виникає при неможливості виділити динамічну пам'ять під вирівняні масиви координат вихорів або робочі буфери розв'язувача RK4. Дії користувача: зменшити кількість вихорів `num_vortices` або звільнити невикористані об'єкти за допомогою `vortex_system_free()`.
4. `VORTEX_ERR_CORE_SINGULARITY (-3)`: Повідомляє, що відстань між двома точковими вихорами стала меншою за `10⁻⁶` при вимкненій регуляризації ядра (`VORTEX_CORE_SINGULAR`). Нестійкість Біо — Савара дає надзвичайно велику швидкість, що загрожує чисельним збоєм. Дії користувача: увімкнути регуляризоване ядро Красного (`VORTEX_CORE_KRASNY`) або Лемба — Осеєна (`VORTEX_CORE_LAMB_OSEEN`).
5. `VORTEX_ERR_INTEGRATION_DIVERGED (-4)`: Чисельний розв'язок втратив стійкість, і координати вихорів набули чисельних значень `NaN` або `Inf`. Виникає при виборі занадто великого кроку часу `dt`, який порушує умову стійкості Куранта. Дії користувача: зменшити крок інтегрування `dt` у 2–5 разів.
6. `VORTEX_ERR_DIMENSION_MISMATCH (-5)`: Запитано 3D розрахунок індукованої швидкості для системи, ініціалізованої у двовимірному режимі (`is_3d = 0`). Дії користувача: встановити `is_3d = 1` при формуванні 3D ниток.

---

## 4. Сигнатури функцій C та C++ API (`:::tabs`)

Нижче наведено специфікацію всіх функцій C API та відповідний ідіоматичний C++20 інтерфейс класів.

:::tabs
```c
/**
 * @brief Створює новий екземпляр вихорової системи
 * 
 * @param config Позитивна конфігурація розв'язувача
 * @param init_points Початковий масив вихорових точок розміром config->num_vortices
 * @param system_handle[out] Вихідний вказівник на створений об'єкт
 * @return VORTEX_SUCCESS або код помилки
 */
vortex_status_t vortex_system_create(
    const vortex_solver_config_t *config,
    const vortex_point_t *init_points,
    void **system_handle
);

/**
 * @brief Виконує один крок часового інтегрування системи вихорів
 * 
 * @param system_handle Валідний об'єкт системи
 * @return VORTEX_SUCCESS або VORTEX_ERR_INTEGRATION_DIVERGED
 */
vortex_status_t vortex_system_step(void *system_handle);

/**
 * @brief Обчислює індуковану швидкість потоку у довільній точці простору (x, y, z)
 * 
 * @param system_handle Вказівник на систему
 * @param px Координата точки X
 * @param py Координата точки Y
 * @param pz Координата точки Z
 * @param vx[out] Індукована швидкість V_x
 * @param vy[out] Індукована швидкість V_y
 * @param vz[out] Індукована швидкість V_z
 * @return VORTEX_SUCCESS або VORTEX_ERR_INVALID_PARAM
 */
vortex_status_t vortex_compute_induced_velocity(
    const void *system_handle,
    double px, double py, double pz,
    double *vx, double *vy, double *vz
);

/**
 * @brief Обчислює поточні значення інваріантів руху (циркуляція, момент, енергія)
 * 
 * @param system_handle Вказівник на систему
 * @param invariants[out] Вихідна структура інваріантів
 * @return VORTEX_SUCCESS або VORTEX_ERR_INVALID_PARAM
 */
vortex_status_t vortex_system_get_invariants(
    const void *system_handle,
    vortex_invariants_t *invariants
);

/**
 * @brief Звільняє пам'ять вихорової системи
 * @param system_handle Вказівник на систему
 */
void vortex_system_free(void *system_handle);
```
```cpp
#include <vector>
#include <memory>
#include <span>
#include <expected>
#include "vortex_solver.h"

namespace vortex {

class Solver {
private:
    void* handle_{nullptr};

public:
    explicit Solver(void* handle) noexcept : handle_(handle) {}
    
    ~Solver() {
        if (handle_) {
            vortex_system_free(handle_);
        }
    }

    Solver(const Solver&) = delete;
    Solver& operator=(const Solver&) = delete;
    Solver(Solver&& rhs) noexcept : handle_(rhs.handle_) { rhs.handle_ = nullptr; }
    Solver& operator=(Solver&& rhs) noexcept {
        if (this != &rhs) {
            if (handle_) vortex_system_free(handle_);
            handle_ = rhs.handle_;
            rhs.handle_ = nullptr;
        }
        return *this;
    }

    static std::expected<Solver, Status> create(
        const Config& config, 
        std::span<const Point> init_points
    ) {
        if (init_points.size() != static_cast<size_t>(config.num_vortices)) {
            return std::unexpected(Status::InvalidParam);
        }
        void* h = nullptr;
        vortex_status_t st = vortex_system_create(
            reinterpret_cast<const vortex_solver_config_t*>(&config),
            reinterpret_cast<const vortex_point_t*>(init_points.data()),
            &h
        );
        if (st != VORTEX_SUCCESS) {
            return std::unexpected(static_cast<Status>(st));
        }
        return Solver(h);
    }

    Status step() {
        return static_cast<Status>(vortex_system_step(handle_));
    }

    [[nodiscard]] std::expected<Invariants, Status> invariants() const {
        Invariants inv{};
        vortex_status_t st = vortex_system_get_invariants(
            handle_, 
            reinterpret_cast<vortex_invariants_t*>(&inv)
        );
        if (st != VORTEX_SUCCESS) {
            return std::unexpected(static_cast<Status>(st));
        }
        return inv;
    }
};

} // namespace vortex
```
:::

---

## 5. Шість етапів обчислительного конвеєра `vortex_system_step`

Внутрішній обчислительний конвеєр виконання одного кроку інтегрування `vortex_system_step` складається з 6 послідовних етапів:

1. **Етап 1 (Валідація стану):** Перевіряється прапорець ініціалізації та відсутність `NaN/Inf` у координатах вихорів.
2. **Етап 2 (Обчислення K1):** За законом Біо — Савара з урахуванням регуляризаційного ядра `K_ε` обчислюються векторні швидкості усіх точок `V_1 = F(Y^n)`.
3. **Етап 3 (Обчислення K2 та K3):** Координати вихорів зміщуються на `0.5·dt·V_1` та `0.5·dt·V_2`, обчислюються проміжні вектори швидкостей `V_2` та `V_3`.
4. **Етап 4 (Обчислення K4):** Координати зміщуються на `dt·V_3`, обчислюється вихідний вектор швидкостей `V_4`.
5. **Етап 5 (Оновлення координат):** Положення вихорів оновлюється за зваженою сумою `Y^{n+1} = Y^n + (dt/6)·(V_1 + 2V_2 + 2V_3 + V_4)`.
6. **Етап 6 (Контроль інваріантів):** Перераховується момент імпульсу `M^{n+1}` та сумарна циркуляція. У разі відхилення від `M₀` понад `1%` генерується попередження.

---

## 6. Деталі розміщення даних у пам'яті (Memory Layout) та SIMD векторний розрахунок

Для досягнення максимальної обчислювальної продуктивності на процесорах із векторними розширеннями AVX-512 та AVX2 координати вихорів зберігаються в орієнтованому на суму Біо — Савара масиві структур (Structure of Arrays, SoA):

- Окремий послідовний масив координат `x[N]` подвійної точності подвоєної вирівняності.
- Окремий послідовний масив координат `y[N]`.
- Окремий послідовний масив інтенсивностей `gamma[N]`.

Таке розміщення дозволяє завантажувати по 8 чисел подвійної точності у векторний регістр `zmm0` однією інструкцією `_mm512_load_pd()`. Векторний розрахунок парних квадратів відстаней `dx² + dy² + ε²` та оберненого значення виконується без проміжних перезавантажень кєш-пам'яті, що прискорює симуляцію у 4–6 разів порівняно зі звичайним масивом структур (AoS).

---

## 7. Контракт потокобезпечності та багатопотоковий розрахунок OpenMP

Обчислення індукованої швидкості системи з `N` вихорів легко паралелиться за допомогою стандарту OpenMP. Оскільки кожна точковий вихор `i` обчислює свою швидкість незалежно від інших, внутрішній цикл по `i` маркується директивою:

```
#pragma omp parallel for schedule(static) default(none) shared(sys, vx, vy)
```

Завдяки відсутності спільних записів у одну й ту саму комірку пам'яті (відсутність явищ False Sharing та Race Conditions) масштабованість розрахунку на 16-ядерних процесорах досягає `92%` лінійного прискорення.

---

## 8. Повноцінні приклади використання мовами C та C++ (`:::tabs`)

Нижче наведено самодостатні приклади використання бібліотеки `libvortex_solver` для розрахунку руху вихорового диполя.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include "vortex_solver.h"

int main(void) {
    vortex_solver_config_t config = {
        .num_vortices = 2,
        .core_radius_eps = 0.01,
        .core_type = VORTEX_CORE_KRASNY,
        .integrator = VORTEX_INTEGRATOR_RK4,
        .dt = 0.005,
        .is_3d = 0
    };

    vortex_point_t points[2] = {
        {.x = -0.5, .y = 0.0, .z = 0.0, .gamma =  1.0},
        {.x =  0.5, .y = 0.0, .z = 0.0, .gamma = -1.0}
    };

    void *solver = NULL;
    vortex_status_t st = vortex_system_create(&config, points, &solver);
    if (st != VORTEX_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації розв'язувача: %d\n", st);
        return 1;
    }

    vortex_invariants_t inv0;
    vortex_system_get_invariants(solver, &inv0);
    printf("Ініціалізація вихорової пари: M0 = %.6f, Total Gamma = %.2f\n", 
           inv0.angular_momentum, inv0.total_circulation);

    for (int step = 0; step < 200; step++) {
        st = vortex_system_step(solver);
        if (st != VORTEX_SUCCESS) {
            fprintf(stderr, "Чисельний збій на кроці %d: %d\n", step, st);
            break;
        }
    }

    vortex_invariants_t inv_end;
    vortex_system_get_invariants(solver, &inv_end);
    printf("Після 200 кроків: M_end = %.6f\n", inv_end.angular_momentum);

    vortex_system_free(solver);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <stdexcept>
#include "vortex_solver.h"

namespace vortex {

class System {
private:
    void* handle_{nullptr};

public:
    System(const vortex_solver_config_t& config, const std::vector<vortex_point_t>& points) {
        if (points.size() != static_cast<size_t>(config.num_vortices)) {
            throw std::invalid_argument("Vector size mismatch with config.num_vortices");
        }
        vortex_status_t st = vortex_system_create(&config, points.data(), &handle_);
        if (st != VORTEX_SUCCESS) {
            throw std::runtime_error("Failed to create vortex system: error code " + std::to_string(st));
        }
    }

    ~System() {
        if (handle_) {
            vortex_system_free(handle_);
        }
    }

    System(const System&) = delete;
    System& operator=(const System&) = delete;

    void step() {
        vortex_status_t st = vortex_system_step(handle_);
        if (st != VORTEX_SUCCESS) {
            throw std::runtime_error("Vortex solver step failed: error code " + std::to_string(st));
        }
    }

    [[nodiscard]] vortex_invariants_t invariants() const {
        vortex_invariants_t inv{};
        vortex_status_t st = vortex_system_get_invariants(handle_, &inv);
        if (st != VORTEX_SUCCESS) {
            throw std::runtime_error("Failed to query invariants: error code " + std::to_string(st));
        }
        return inv;
    }
};

} // namespace vortex

int main() {
    try {
        vortex_solver_config_t cfg{
            2, 0.01, VORTEX_CORE_KRASNY, VORTEX_INTEGRATOR_RK4, 0.005, 0
        };

        std::vector<vortex_point_t> pts = {
            {-0.5, 0.0, 0.0,  1.0},
            { 0.5, 0.0, 0.0, -1.0}
        };

        vortex::System sys(cfg, pts);
        std::cout << "C++ Vortex System initialized. M0 = " << sys.invariants().angular_momentum << "\n";

        for (int i = 0; i < 100; ++i) {
            sys.step();
        }

        std::cout << "Execution completed cleanly. Final M = " << sys.invariants().angular_momentum << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 9. Інтеграція з мовою Python через `ctypes` та CLI інструмент

Завдяки C-сумісному ABI бібліотеку `libvortex_solver` можна підключати до Python без компіляції додаткових C-розширень за допомогою модулю `ctypes`:

```python
import ctypes

class VortexSolverConfig(ctypes.Structure):
    _fields_ = [
        ("num_vortices", ctypes.c_int),
        ("core_radius_eps", ctypes.c_double),
        ("core_type", ctypes.c_int),
        ("integrator", ctypes.c_int),
        ("dt", ctypes.c_double),
        ("is_3d", ctypes.c_int)
    ]

lib = ctypes.CDLL("./libvortex_solver.so")
print("Python ctypes integration initialized successfully.")
```

Утиліта командного рядка `vortex_solver_cli` дозволяє запускати пакетне моделювання вихорових систем із збереженням траєкторій у відкритий формат VTK для візуалізації в утиліті ParaView.
