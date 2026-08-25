# 📋 Інтерфейс та конфігурація рушія моделювання маятника

Ця вставка містить повну довідкову специфікацію програмного інтерфейсу (API) та конфігураційних контрактів обчислювального рушія маятника. Вона висвітлює архітектурні рішення розділення стану й конфігурації, описує C та C++ структури даних, сигнатури функцій, коди помилок, параметри консольного CLI-інтерфейсу, схеми експорту даних та фізичні інваріанти валідації стану.

---

### 1. Архітектурні засади та виділення обчислювального контексту

При проектуванні високоефективних обчислювальних рушіїв для фізичного моделювання ключовою вимогою є суворе відокремлення статичних конфігураційних параметрів системи від її динамічного стану, що змінюється на кожному кроці за часом. Такий підхід забезпечує передбачуваність використання пам'яті, потокобезпечність при паралельних розрахунках та нульові накладні витрати на динамічне виділення пам'яті у купі впродовж обчислювального циклу.

Статичні параметри моделі — довжина нитки чи зведена довжина маятника `L`, маса коливального тіла `m`, прискорення вільного падіння `g`, коефіцієнт в'язкого тертя `c`, момент інерції `I`, відстань до центра мас `d`, а також амплітуда й частота зовнішньої вимушувальної сили — об'єднано у незмінну структуру конфігурації `pendulum_config_t`. Ця структура передається за константним посиланням або вказівником у всі обчислювальні процедури, що унеможливлює випадкову зміну фізичних констант під час довготривалого інтегрування.

Динамічний стан системи у поточний момент часу `t` виділено у легковагову структуру `pendulum_state_t`. Вона містить кут відхилення `θ`, кутову швидкість `ω`, кутове прискорення `α`, поточний фізичний час `t` та загальний лічильник виконаних кроків. Оскільки розмір цієї структури є фіксованим і становить 40 байтів, вона легко вміщується у кєш-лінії процесора та може передаватися через стек із максимальною швидкістю.

:::tabs
```c
/* pendulum_types.h - Типи даних та структури конфігурації у мові C */
#ifndef PENDULUM_TYPES_H
#define PENDULUM_TYPES_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PENDULUM_SOLVER_EULER           = 0,
    PENDULUM_SOLVER_VERLET          = 1,
    PENDULUM_SOLVER_RK4             = 2,
    PENDULUM_SOLVER_ADAPTIVE_RK45   = 3
} pendulum_solver_mode_t;

typedef enum {
    PENDULUM_OK                     =  0,
    PENDULUM_ERR_INVALID_PARAM      = -1,
    PENDULUM_ERR_DIVERGENCE         = -2,
    PENDULUM_ERR_ALLOCATION         = -3,
    PENDULUM_ERR_UNSUPPORTED_MODE   = -4
} pendulum_status_t;

typedef struct {
    double length;
    double mass;
    double gravity;
    double damping;
    double inertia;
    double pivot_dist;
    double drive_amplitude;
    double drive_frequency;
} pendulum_config_t;

typedef struct {
    double theta;
    double omega;
    double alpha;
    double time;
    uint64_t step_count;
} pendulum_state_t;

typedef struct {
    double kinetic_energy;
    double potential_energy;
    double total_energy;
    double initial_energy;
    double energy_drift_pct;
} pendulum_metrics_t;

#ifdef __cplusplus
}
#endif

#endif /* PENDULUM_TYPES_H */
```
```cpp
// PendulumTypes.hpp - Ідіоматичні типи даних та строго типізовані перелічення у C++20
#ifndef PENDULUM_TYPES_HPP
#define PENDULUM_TYPES_HPP

#include <cstdint>
#include <cstddef>

namespace physics {

enum class SolverMode : uint8_t {
    Euler = 0,
    Verlet = 1,
    RK4 = 2,
    AdaptiveRK45 = 3
};

enum class Status : int32_t {
    Ok = 0,
    InvalidParameter = -1,
    Divergence = -2,
    AllocationFailed = -3,
    UnsupportedMode = -4
};

struct Config {
    double length{1.0};
    double mass{1.0};
    double gravity{9.80665};
    double damping{0.0};
    double inertia{0.0};
    double pivot_dist{0.0};
    double drive_amplitude{0.0};
    double drive_frequency{0.0};
};

struct State {
    double theta{0.0};
    double omega{0.0};
    double alpha{0.0};
    double time{0.0};
    uint64_t step_count{0};
};

struct Metrics {
    double kinetic_energy{0.0};
    double potential_energy{0.0};
    double total_energy{0.0};
    double initial_energy{0.0};
    double energy_drift_pct{0.0};
};

} // namespace physics

#endif // PENDULUM_TYPES_HPP
```
:::

---

### 2. Детальний розбір конфігураційних полів та правил валідації

Кожне поле структури `pendulum_config_t` відповідає за конкретний фізичний аспект маятникової системи і проходить сувору багаторівневу валідацію під час виклику функцій ініціалізації. Якщо хоча б один параметр не відповідає заданому фізичному діапазону, функція ініціалізації негайно повертає код помилки `PENDULUM_ERR_INVALID_PARAM`.

#### Детальний фізичний зміст полів:

1. **`length` (Довжина маятника `L`):**
   Визначає геометричну довжину нитки математичного маятника або зведену довжину фізичного маятника у метрах. Мінімальне допустиме значення становить `1e-6` м (1 мікрометр), що запобігає діленню на нуль у формулах для прискорення `a = −(g/L)·sin(θ)`. Максимальна довжина обмежена значенням `1000.0` м.
2. **`mass` (Маса тіла `m`):**
   Визначає інертну та гравітаційну масу коливального грузила у кілограмах. Маса мусить бути строго додатною (`m > 0`). Хоча у підсумковому рівнянні математичного маятника без тертя маса скорочується, вона є необхідною для обчислення кінетичної та потенціальної енергії, сили натягу нитки `T` та моментів сил при наявності загасання.
3. **`gravity` (Прискорення вільного падіння `g`):**
   Визначає локальне гравітаційне поле у м/с². Значення за замовчуванням дорівнює стандартному земному прискоренню `9.80665` м/с². Для моделювання маятника на Місяці передають `1.62` м/с², на Юпітері — `24.79` м/с², а для умов космічної невагомості — `0.0` м/с².
4. **`damping` (Коефіцієнт загасання `c`):**
   Описує силу в'язкого тертя `F_загас = −c · v`. Вимірюється у Н·с/м. При `c = 0` система є строго консервативною; при `c > 0` енергія системи експоненціально дисипує у тепло.
5. **`inertia` (Момент інерції `I`):**
   Використовується для фізичного маятника (твердого тіла). Вимірюється у кг·м². Якщо `I == 0`, рушій автоматично трактує систему як математичний маятник із точковою масою й обчислює момент інерції за формулою `I = m · L²`.
6. **`pivot_dist` (Відстань до центра мас `d`):**
   Відстань від осі підвісу до центра мас тіла у метрах. Використовується разом із моментом інерції `I` для обчислення повертального моменту `τ = −m · g · d · sin(θ)`.
7. **`drive_amplitude` та `drive_frequency`:**
   Параметри зовнішнього періодичного обертального моменту `τ_ext = A · cos(Ω · t)`. Використовуються для моделювання вимушених коливань, параметричного резонансу та вивчення переходів до детермінованого хаосу.

---

### 3. Алгоритми чисельного інтегрування та вибір кроку сітки

Обчислювальне ядро підтримує чотири класи чисельних інтеграторів, кожен із яких підходить для свого класу фізичних задач:

#### Явний метод Ейлера (`PENDULUM_SOLVER_EULER`)
Найпростіший крок першого порядку `O(dt)`. Не зберігає фазовий об'єм, накачує штучну енергію й приводить до дивергенції. Надається виключно для навчальної демонстрації похибок чисельного диференціювання.

#### Симплектичний метод Верле (`PENDULUM_SOLVER_VERLET`)
Симплектичний інтегратор второго порядку `O(dt²)`. Включає збереження фазової площі (теорема Ліувіля), завдяки чому повна енергія консервативної системи не зростає й не падає протягом мільйонів кроків сітки, а лише дрібно осцилює навколо точного значення.

#### Метод Рунге-Кутти 4-го порядку (`PENDULUM_SOLVER_RK4`)
Класичний чотириетапний метод із локальною похибкою `O(dt⁵)` та глобальною похибкою `O(dt⁴)`. Забезпечує високу точність обчислення траєкторії на помірних проміжках часу.

#### Адаптивний метод Дормана-Принса 5(4) (`PENDULUM_SOLVER_ADAPTIVE_RK45`)
Просунутий метод із автоматичним вибором кроку за часом `dt`. Оцінює локальну похибку шляхом порівняння розв'язків 5-го та 4-го порядків. Якщо похибка перевищує заданий допуск (наприклад `1e-9`), крок автоматично зменшується; якщо похибка занадто мала — крок збільшується. Це дозволяє швидко й точно проходити ділянки траєкторії з високими швидкостями.

---

### 4. Специфікація функцій C та C++ API

Низькорівневий C API гарантує сумісність із будь-якими мовами програмування через FFI, тоді як C++20 API надає об'єктну обгортку з використанням `std::expected`.

:::tabs
```c
/* pendulum_solver.h - Сигнатури функцій C API */
#ifndef PENDULUM_SOLVER_H
#define PENDULUM_SOLVER_H

#include "pendulum_types.h"

#ifdef __cplusplus
extern "C" {
#endif

pendulum_status_t pendulum_init(const pendulum_config_t *config,
                                double initial_theta,
                                double initial_omega,
                                pendulum_state_t *state);

pendulum_status_t pendulum_step(const pendulum_config_t *config,
                                pendulum_solver_mode_t mode,
                                double dt,
                                pendulum_state_t *state);

pendulum_status_t pendulum_get_metrics(const pendulum_config_t *config,
                                       const pendulum_state_t *state,
                                       double initial_energy,
                                       pendulum_metrics_t *metrics);

pendulum_status_t pendulum_calc_period_theory(const pendulum_config_t *config,
                                              double initial_theta_deg,
                                              double *out_period_sec);

#ifdef __cplusplus
}
#endif

#endif /* PENDULUM_SOLVER_H */
```
```cpp
// PendulumSolver.hpp - Ідіоматична обгортка C++20 з використанням std::expected
#ifndef PENDULUM_SOLVER_HPP
#define PENDULUM_SOLVER_HPP

#include <cmath>
#include <numbers>
#include <expected>
#include <utility>
#include "PendulumTypes.hpp"

namespace physics {

class PendulumEngine {
public:
    explicit PendulumEngine(Config config) noexcept : config_{config} {}

    [[nodiscard]] std::expected<State, Status>
    initialize(double theta0_rad, double omega0_rad_s = 0.0) noexcept {
        if (config_.length <= 0.0 || config_.mass <= 0.0 || config_.gravity < 0.0) {
            return std::unexpected(Status::InvalidParameter);
        }

        current_state_.theta = theta0_rad;
        current_state_.omega = omega0_rad_s;
        current_state_.alpha = compute_alpha(theta0_rad, omega0_rad_s);
        current_state_.time = 0.0;
        current_state_.step_count = 0;

        initial_energy_ = compute_total_energy(current_state_);
        return current_state_;
    }

    [[nodiscard]] std::expected<State, Status>
    step(SolverMode mode, double dt) noexcept {
        if (dt <= 0.0) {
            return std::unexpected(Status::InvalidParameter);
        }

        if (mode == SolverMode::RK4) {
            step_rk4(dt);
        } else if (mode == SolverMode::Verlet) {
            step_verlet(dt);
        } else {
            return std::unexpected(Status::UnsupportedMode);
        }

        current_state_.time += dt;
        current_state_.step_count++;
        current_state_.alpha = compute_alpha(current_state_.theta, current_state_.omega);

        if (std::isnan(current_state_.theta) || std::isinf(current_state_.theta)) {
            return std::unexpected(Status::Divergence);
        }

        return current_state_;
    }

    [[nodiscard]] Metrics metrics() const noexcept {
        Metrics m{};
        double e_kin = 0.5 * config_.mass * config_.length * config_.length * current_state_.omega * current_state_.omega;
        double e_pot = config_.mass * config_.gravity * config_.length * (1.0 - std::cos(current_state_.theta));
        m.kinetic_energy = e_kin;
        m.potential_energy = e_pot;
        m.total_energy = e_kin + e_pot;
        m.initial_energy = initial_energy_;
        m.energy_drift_pct = (initial_energy_ > 1e-12) 
            ? std::abs(m.total_energy - initial_energy_) / initial_energy_ * 100.0 
            : 0.0;
        return m;
    }

    [[nodiscard]] double theoretical_period(double theta0_deg) const noexcept {
        double rad0 = theta0_deg * (std::numbers::pi / 180.0);
        double t0 = 2.0 * std::numbers::pi * std::sqrt(config_.length / config_.gravity);
        double k = std::sin(rad0 / 2.0);
        double k2 = k * k;
        return t0 * (1.0 + 0.25 * k2 + (9.0 / 64.0) * k2 * k2);
    }

private:
    [[nodiscard]] double compute_alpha(double th, double om) const noexcept {
        double damping_torque = config_.damping * om;
        double gravity_torque = config_.mass * config_.gravity * config_.length * std::sin(th);
        double eff_inertia = (config_.inertia > 0.0) ? config_.inertia : (config_.mass * config_.length * config_.length);
        return -(gravity_torque + damping_torque) / eff_inertia;
    }

    [[nodiscard]] double compute_total_energy(const State& s) const noexcept {
        double e_kin = 0.5 * config_.mass * config_.length * config_.length * s.omega * s.omega;
        double e_pot = config_.mass * config_.gravity * config_.length * (1.0 - std::cos(s.theta));
        return e_kin + e_pot;
    }

    void step_rk4(double dt) noexcept {
        auto deriv = [this](double th, double om) {
            return std::pair{om, compute_alpha(th, om)};
        };

        auto [k1_th, k1_om] = deriv(current_state_.theta, current_state_.omega);
        auto [k2_th, k2_om] = deriv(current_state_.theta + 0.5 * dt * k1_th, current_state_.omega + 0.5 * dt * k1_om);
        auto [k3_th, k3_om] = deriv(current_state_.theta + 0.5 * dt * k2_th, current_state_.omega + 0.5 * dt * k2_om);
        auto [k4_th, k4_om] = deriv(current_state_.theta + dt * k3_th, current_state_.omega + dt * k3_om);

        current_state_.theta += (dt / 6.0) * (k1_th + 2.0 * k2_th + 2.0 * k3_th + k4_th);
        current_state_.omega += (dt / 6.0) * (k1_om + 2.0 * k2_om + 2.0 * k3_om + k4_om);
    }

    void step_verlet(double dt) noexcept {
        double a_curr = compute_alpha(current_state_.theta, current_state_.omega);
        current_state_.theta += current_state_.omega * dt + 0.5 * a_curr * dt * dt;
        double a_next = compute_alpha(current_state_.theta, current_state_.omega);
        current_state_.omega += 0.5 * (a_curr + a_next) * dt;
    }

    Config config_;
    State current_state_{};
    double initial_energy_{0.0};
};

} // namespace physics

#endif // PENDULUM_SOLVER_HPP
```
:::

---

### 5. Специфікація консольного CLI-інтерфейсу

Для використання ядра в скриптах та наукових конвеєрах розроблено CLI-утиліту `pendulum-sim-cli`.

#### Опції та прапорці запуску

```
Використання: pendulum-sim-cli [ОПЦІЇ]

Фізичні параметри системи:
  -l, --length <ФЛОАТ>        Довжина маятника L у метрах (за замовчуванням: 1.0)
  -m, --mass <ФЛОАТ>          Маса маятника m у кг (за замовчуванням: 1.0)
  -g, --gravity <ФЛОАТ>       Прискорення вільного падіння g у м/с² (за замовчуванням: 9.80665)
  -c, --damping <ФЛОАТ>       Коефіцієнт демпфування c у Н·с/м (за замовчуванням: 0.0)
  -a, --angle <ФЛОАТ>         Початковий кут θ₀ у градусах (за замовчуванням: 30.0)
  -w, --omega <ФЛОАТ>         Початкова кутова швидкість у рад/с (за замовчуванням: 0.0)

Параметри чисельного інтегрування:
  -s, --solver <ТИП>          Тип інтегратора: rk4 | verlet | euler (за замовчуванням: rk4)
  -d, --dt <ФЛОАТ>            Крок часу в секундах (за замовчуванням: 0.001)
  -t, --time <ФЛОАТ>          Загальний час симуляції в секундах (за замовчуванням: 10.0)

Налаштування виводу:
  -o, --output <ФАЙЛ>         Вихідний файл для запису (за замовчуванням: stdout)
  -f, --format <ФОРМАТ>       Формат даних: csv | tsv | json (за замовчуванням: csv)
  -v, --verbose               Виводити розширені метрики та дрейф енергії
  -h, --help                  Відобразити довідкову інформацію
```

#### Приклад підсумкового JSON-звіту

```json
{
  "simulation": {
    "solver": "rk4",
    "dt": 0.001,
    "total_time": 10.0,
    "status": "COMPLETED"
  },
  "config": {
    "length_m": 1.0,
    "mass_kg": 1.0,
    "gravity_m_s2": 9.80665,
    "damping": 0.0,
    "initial_angle_deg": 30.0
  },
  "results": {
    "measured_period_sec": 2.04041,
    "theoretical_period_sec": 2.04040,
    "relative_error_pct": 0.00049,
    "max_energy_drift_pct": 0.000012
  }
}
```

---

### 6. Фізичні інваріанти та правила перевірки стану

Під час роботи обчислювального ядра на кожному кроці інтегрування виконуються наступні фізичні перевірки:

1. **Нормалізація фазового кута:** значення кута `θ` після кожного кроку приводиться до інтервалу `[−π, +π]` за допомогою функції `fmod(θ + π, 2π) − π`. Це упереджує втрату точності чисел із плаваючою комою при обчисленні `sin(θ)` під час тривалого обертального руху.
2. **Перевірка на збереження енергії:** у системі без загасання (`damping == 0`) обчислювальне ядро перевіряє відносний дрейф енергії `|E(t) − E(0)| / E(0)`. Якщо цей показник перевищує `0.05` (5%), симуляція зупиняється з поверненням коду `PENDULUM_ERR_DIVERGENCE`.
3. **Перевірка NaN/Inf:** якщо будь-яка з координат отримує неозначене значення, симуляція негайно переривається з кодом `PENDULUM_ERR_DIVERGENCE`.
