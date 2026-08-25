# 📋 Специфікація програмного інтерфейсу бібліотеки LyapunovLab

Програмна бібліотека `LyapunovLab` призначена для високопродуктивного числового розрахунку показників Ляпунова, аналізу стійкості, розрахунку фрактальної розмірності та оцінки горизонтів передбачуваності для широкого класу нелінійних динамічних систем. Вона забезпечує єдину архітектуру як для неперервних диференціальних потоків (ODE), так і для дискретних ітераційних відображень (Maps). Тут подано вичерпну специфікацію публічного інтерфейсу (API), структур даних, кодів помилок та прикладів використання мовами C та C++.

## Архітектурний огляд та модель пам'яті

Інтерфейс бібліотеки побудовано за модульним принципом із чітким розмежуванням відповідальності між компонентами:
1. **Конфігураційний описувач (`LyapunovConfig`):** Задає числові параметри обчислювального двигуна, включаючи розмірність фазового простору `dim`, крок дискретизації часу `dt`, кількість підготовчих і робочих кроків, а також обраний алгоритм чисельного інтегрування.
2. **Векторна модель динамічної системи (`LyapunovSystem`):** Містить покажчики на функції зворотного виклику (callbacks), які розраховують векторне поле правої частини `f(t, x)` та відповідну матрицю Якобі `J(t, x)` в довільній точці фазового простору.
3. **Контейнер підсумкових метрик (`LyapunovMetrics`):** Зберігає впорядкований масив показників Ляпунова `λ₁ ≥ λ₂ ≥ ... ≥ λ♁`, обчислену розмірність Каплана–Йорке `D_L`, оцінку КС-ентропії Песіна `h_KS`, час Ляпунова `τ_L` та логічний прапорець хаотичності режиму.

Модель управління пам'яттю бібліотеки є прозорою та безпечною:
- У C API створення та звільнення контейнерів метрик виконується за допомогою функцій `lyapunov_metrics_create()` та `lyapunov_metrics_destroy()`. Динамічний масив `spectrum` виділяється одноразово під час виклику створення.
- У C++ API використовується семантика переміщення (move semantics), стандартні контейнери `std::vector` та шаблони RAII, що повністю виключає витоки оперативної пам'яті та спрощує інтеграцію в сучасні C++20 проєкти.
- Конструкція `LyapunovSystem` підтримує збереження контексту користувача через покажчик `user_data` у мові C або лямбда-функції із захопленням контексту в C++, що забезпечує повну багатопотокову безпеку (thread safety) та реінтерабельність обчислень.

## Моделі чисельного інтегрування та зворотні виклики (Callbacks)

Для забезпечення високої обчислювальної точності бібліотека підтримує два алгоритми чисельного інтегрування:
- **Метод Рунге-Кутти 4-го порядку (RK4):** Класичний схематичний інтегратор із фіксованим кроком `dt`. Ідеально підходить для автономних диференціальних систем середньої жорсткості, де потрібна максимальна детермінована швидкість обчислення.
- **Метод Дормана-Принса 8-го порядку (DP8):** Інтегратор високого порядку точності, який мінімізує накопичення помилок на надтривалих часових інтервалах при розрахунку слабковражених молодших показників спектра.

Користувач зобов'язаний надати дві функції зворотного виклику:
- **Права частина `rhs`:** Приймає поточний час `t` та вектор стану `x`, розраховуючи похідні `dxdt`.
- **Якобіан `jacobian`:** Приймає поточний час `t` та вектор стану `x`, заповнюючи одномірний масив `J_flat` розміром `dim × dim` частковими похідними `∂f_i / ∂x_j` у плоскому форматі (row-major order).

## Публічні типи даних та специфікація API

:::tabs
```c
/* lyapunov_lab.h - C API специфікація бібліотеки LyapunovLab */
#ifndef LYAPUNOV_LAB_H
#define LYAPUNOV_LAB_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди повернення та помилок */
typedef enum {
    LYAPUNOV_SUCCESS = 0,
    LYAPUNOV_ERROR_INVALID_DIM = -1,
    LYAPUNOV_ERROR_NULL_POINTER = -2,
    LYAPUNOV_ERROR_DIVERGENCE = -3,
    LYAPUNOV_ERROR_NO_MEMORY = -4
} LyapunovStatus;

/* Спосіб інтегрування */
typedef enum {
    LYAPUNOV_INTEGRATOR_RK4 = 0,
    LYAPUNOV_INTEGRATOR_DORMAND_PRINCE8 = 1
} LyapunovIntegratorType;

/* Функція правої частини f(t, x, dxdt, user_data) */
typedef void (*LyapunovRhsFunc)(double t, const double *x, double *dxdt, void *user_data);

/* Функція Якобіана J(t, x, J_flat, user_data) */
typedef void (*LyapunovJacobianFunc)(double t, const double *x, double *J_flat, void *user_data);

/* Конфігураційні параметри */
typedef struct {
    size_t dim;                   /* Розмірність фазового простору */
    double dt;                    /* Крок інтегрування */
    size_t total_steps;           /* Кількість робочих кроків */
    size_t transient_steps;       /* Кількість кроків для виходу на атрактор */
    size_t qr_period;             /* Період проведення QR-розкладу (в кроках) */
    LyapunovIntegratorType method;/* Метод чисельного інтегрування */
} LyapunovConfig;

/* Описувач динамічної системи */
typedef struct {
    LyapunovRhsFunc rhs;
    LyapunovJacobianFunc jacobian;
    void *user_data;
} LyapunovSystem;

/* Результати аналізу */
typedef struct {
    double *spectrum;             /* Масив показників Ляпунова (розмірність dim) */
    double lyapunov_dimension;    /* Розмірність Каплана–Йорке D_L */
    double lyapunov_time;         /* Час Ляпунова tau_L = 1 / lambda_max */
    double ks_entropy;            /* Метрична ентропія Песіна h_KS */
    bool is_chaotic;              /* Прапорець наявності хаосу (lambda_max > 0) */
} LyapunovMetrics;

/* Створення та ініціалізація метрик */
LyapunovMetrics* lyapunov_metrics_create(size_t dim);

/* Звільнення пам'яті метрик */
void lyapunov_metrics_destroy(LyapunovMetrics *metrics);

/* Основний виклик розрахунку спектра */
LyapunovStatus lyapunov_compute_spectrum(
    const LyapunovSystem *sys,
    const LyapunovConfig *cfg,
    const double *initial_state,
    LyapunovMetrics *out_metrics
);

/* Допоміжна функція отримання текстового опису помилки */
const char* lyapunov_status_string(LyapunovStatus status);

#ifdef __cplusplus
}
#endif

#endif /* LYAPUNOV_LAB_H */
```
```cpp
// lyapunov_lab.hpp - C++20 API специфікація бібліотеки LyapunovLab
#ifndef LYAPUNOV_LAB_HPP
#define LYAPUNOV_LAB_HPP

#include <vector>
#include <array>
#include <functional>
#include <string_view>
#include <expected>
#include <memory>
#include <span>
#include <cstddef>

namespace lyapunov_lab {

enum class IntegratorType {
    RK4,
    DormandPrince8
};

enum class ErrorCode {
    InvalidDimension,
    NullPointer,
    Divergence,
    OutOfMemory
};

struct Config {
    std::size_t dim{3};
    double dt{0.01};
    std::size_t total_steps{100000};
    std::size_t transient_steps{10000};
    std::size_t qr_period{1};
    IntegratorType method{IntegratorType::RK4};
};

using RhsFunction = std::function<void(double t, std::span<const double> x, std::span<double> dxdt)>;
using JacobianFunction = std::function<void(double t, std::span<const double> x, std::span<double> J_flat)>;

struct System {
    RhsFunction rhs;
    JacobianFunction jacobian;
};

struct Metrics {
    std::vector<double> spectrum;
    double lyapunov_dimension{0.0};
    double lyapunov_time{0.0};
    double ks_entropy{0.0};
    bool is_chaotic{false};
};

class Analyzer {
public:
    explicit Analyzer(Config config);
    ~Analyzer() = default;

    Analyzer(const Analyzer&) = delete;
    Analyzer& operator=(const Analyzer&) = delete;
    Analyzer(Analyzer&&) noexcept = default;
    Analyzer& operator=(Analyzer&&) noexcept = default;

    [[nodiscard]] std::expected<Metrics, ErrorCode> compute(
        const System& sys,
        std::span<const double> initial_state
    ) const;

private:
    Config config_;
};

[[nodiscard]] constexpr std::string_view to_string(ErrorCode code) noexcept {
    switch (code) {
        case ErrorCode::InvalidDimension: return "Некоректна розмірність фазового простору";
        case ErrorCode::NullPointer:      return "Нульовий вказівник на функцію системи";
        case ErrorCode::Divergence:       return "Розбіжність чисельного розв'язку (overflow)";
        case ErrorCode::OutOfMemory:      return "Недостатньо оперативної пам'яті";
    }
    return "Невідома помилка";
}

} // namespace lyapunov_lab

#endif // LYAPUNOV_LAB_HPP
```
:::

## Специфікація параметрів конфігурації та діагностичних кодів

Нижче наведено докладні таблиці опису полів конфігурації `LyapunovConfig` та повернюваних кодів помилок чисельного двигуна.

### Параметри конфігурації `LyapunovConfig`

| Параметр | Тип | Призначення та діапазон | Типове значення |
| :--- | :--- | :--- | :--- |
| `dim` | `size_t` | Кількість ступенів вільності (фазових змінних) `n ≥ 1` | `3` |
| `dt` | `double` | Крок дискретизації часу в чисельном інтегруванні `dt > 0` | `0.01` |
| `total_steps` | `size_t` | Кількість робочих кроків накопичення показників | `100000` |
| `transient_steps` | `size_t` | Кількість підготовчих кроків виходу на атрактор | `10000` |
| `qr_period` | `size_t` | Кількість кроків між послідовними QR-ортогоналізаціями | `1` |
| `method` | `enum` | Метод інтегрування (RK4 або класичний Dormand-Prince 8) | `RK4` |

### Таблиця діагностичних кодів помилок

| Код | Символічна назва | Причина виникнення та рекомендація щодо виправлення |
| :--- | :--- | :--- |
| `0` | `LYAPUNOV_SUCCESS` | Успішне завершення обчислень. Усі метрики обчислено коректно. |
| `-1` | `LYAPUNOV_ERROR_INVALID_DIM` | Передано `dim == 0`. Перевірте ініціалізацію конфігурації. |
| `-2` | `LYAPUNOV_ERROR_NULL_POINTER` | Один із покажчиків на callbacks дорівнює `NULL` (`nullptr`). |
| `-3` | `LYAPUNOV_ERROR_DIVERGENCE` | Траєкторія вийшла за межі допустимого діапазону чисел (`NaN` або `Inf`). |
| `-4` | `LYAPUNOV_ERROR_NO_MEMORY` | Внутрішня помилка виділення пам'яті під матриці розкладу. |

## Покрокова процедура обчислення та обробка помилок

Обчислювальний процес усередині двигуна `LyapunovLab` складається з п'яти послідовних етапів:

1. **Валідація конфігураційних параметрів:** Перевіряються умови `dim > 0`, `dt > 0` та наявність ненульових покажчиків на `rhs` та `jacobian`. У разі виявлення помилок повертається `LYAPUNOV_ERROR_INVALID_DIM` або `LYAPUNOV_ERROR_NULL_POINTER`.
2. **Ініціалізація робочих матриць:** Створюються внутрішні робочі матриці `Q` розміром `dim × dim` та масиви для накопичення діагональних елементів. При помилках динамічної пам'яті повертається `LYAPUNOV_ERROR_NO_MEMORY`.
3. **Релаксаційний етап (Transient Steps):** Виконується `transient_steps` кроків чисельного інтегрування без накопичення показників. Це необхідно для того, щоб фазова точка зійшла з випадкових початкових умов і вийшла на дивний атрактор.
4. **Робочий етап реортогоналізації (Worker Phase):** На кожному кроці або через кожні `qr_period` кроків виконується чисельний розклад Грама-Шмідта. Здійснюється сумування логарифмів диагональних елементів `ln(R_ii)`. Якщо під час інтегрування координати системи перевищують числову межу (`NaN` або `Inf`), обчислення припиняються з кодом `LYAPUNOV_ERROR_DIVERGENCE`.
5. **Розрахунок підсумкових метрик:** Після завершення всіх `total_steps` кроків обчислюються показники Ляпунова `λ_i = S_i / T`, розмірність Каплана–Йорке `D_L`, ентропія Песіна `h_KS` та час Ляпунова `τ_L = 1 / λ_max`.

## Багатопотокова безпека та паралельні обчислення

Програмна бібліотека `LyapunovLab` розроблена з урахуванням сучасних вимог до високопродуктивних обчислень на багатоядерних процесорах:
- У **C API** функція `lyapunov_compute_spectrum()` є повністю реінтерабельною і не використовує глобального стану або статичних змінних. Переданий покажчик `user_data` дозволяє передавати потік-специфічні структури даних для паралельного розрахунку карти показників Ляпунова у декількох потоках (наприклад, за допомогою OpenMP або POSIX pthreads).
- У **C++ API** клас `Analyzer` є stateless-екземпляром конфігурації. Метод `compute()` позначено як `const` та `nodiscard`, що дозволяє безпечно викликати його з різних потоків виконання `std::jthread` або `std::async` для одночасного сканування декількох областей параметрів нелінійної системи.

## Серіалізація та інтеграція з інструментами аналізу даних

Для сумісності з науковими пакетами аналізу даних (Python NumPy, SciPy, MATLAB, Julia) бібліотека `LyapunovLab` підтримує збереження результатів у форматах CSV та HDF5:
- **Структура вихідних даних:** Записується повний часовий профіль локальних показників `λ_i(t)`, значення діагональних елементів `R_ii` на кожному кроці реортогоналізації, а також підсумкові інтегральні метрики (`D_L`, `h_KS`, `τ_L`).
- **Контроль якості обчислень:** Записаний часовий профіль дозволяє будувати графіки сходження (convergence plots) для перевірки того, чи вийшли розраховані значення `λ_i` на стаціонарний плато-рівень.

## Обробка крайніх випадків та чисельні обмеження

Під час аналізу складних багатовимірних систем виникають специфічні крайні випадки:
- **Системи з дуже великим від'ємним показником `|λ_n| >> λ₁`:** У надсильно дисипативних системах (наприклад, у моделі Лоренца, де `λ₃ ≈ -14.5`) інтервал реортогоналізації `qr_period` повинен дорівнювати 1, інакше норма останнього вектора впаде до машинного нуля `10⁻¹⁶` і викличе ділення на нуль під час нормування.
- **Випадки нульових покажчиків у консервативних системах:** Для гамільтонових систем сума показників `∑ λ_i` повинна контролюватися на рівні точності `10⁻⁸`. Відхилення суми від нуля сигналізує про необхідність зменшення кроку інтегрування `dt`.

## Приклад використання API мовами C та C++

Нижче наведено закінчений приклад інтеграції бібліотеки `LyapunovLab` для розрахунку показників хаотичного атрактора Лоренца.

:::tabs
```c
/* main.c - Приклад використання LyapunovLab API мовою C */
#include "lyapunov_lab.h"
#include <stdio.h>
#include <stdlib.h>

static void lorenz_rhs_cb(double t, const double *x, double *dxdt, void *user_data) {
    (void)t; (void)user_data;
    dxdt[0] = 10.0 * (x[1] - x[0]);
    dxdt[1] = x[0] * (28.0 - x[2]) - x[1];
    dxdt[2] = x[0] * x[1] - (8.0 / 3.0) * x[2];
}

static void lorenz_jac_cb(double t, const double *x, double *J, void *user_data) {
    (void)t; (void)user_data;
    J[0] = -10.0; J[1] = 10.0;  J[2] = 0.0;
    J[3] = 28.0 - x[2]; J[4] = -1.0; J[5] = -x[0];
    J[6] = x[1];  J[7] = x[0];  J[8] = -8.0 / 3.0;
}

int main(void) {
    LyapunovConfig cfg = {
        .dim = 3,
        .dt = 0.01,
        .total_steps = 50000,
        .transient_steps = 5000,
        .qr_period = 1,
        .method = LYAPUNOV_INTEGRATOR_RK4
    };

    LyapunovSystem sys = {
        .rhs = lorenz_rhs_cb,
        .jacobian = lorenz_jac_cb,
        .user_data = NULL
    };

    double init_state[3] = { 1.0, 1.0, 1.0 };
    LyapunovMetrics *metrics = lyapunov_metrics_create(cfg.dim);

    LyapunovStatus status = lyapunov_compute_spectrum(&sys, &cfg, init_state, metrics);
    if (status == LYAPUNOV_SUCCESS) {
        printf("Обчислення завершено успішно:\n");
        printf("  lambda_1 = %+.4f\n", metrics->spectrum[0]);
        printf("  lambda_2 = %+.4f\n", metrics->spectrum[1]);
        printf("  lambda_3 = %+.4f\n", metrics->spectrum[2]);
        printf("  D_L = %.3f\n", metrics->lyapunov_dimension);
    } else {
        fprintf(stderr, "Помилка: %s\n", lyapunov_status_string(status));
    }

    lyapunov_metrics_destroy(metrics);
    return 0;
}
```
```cpp
// main.cpp - Приклад використання LyapunovLab API мовою C++20
#include "lyapunov_lab.hpp"
#include <iostream>
#include <iomanip>
#include <array>

int main() {
    using namespace lyapunov_lab;

    Config cfg{
        .dim = 3,
        .dt = 0.01,
        .total_steps = 50000,
        .transient_steps = 5000,
        .qr_period = 1,
        .method = IntegratorType::RK4
    };

    System sys{
        .rhs = [](double, std::span<const double> x, std::span<double> dxdt) {
            dxdt[0] = 10.0 * (x[1] - x[0]);
            dxdt[1] = x[0] * (28.0 - x[2]) - x[1];
            dxdt[2] = x[0] * x[1] - (8.0 / 3.0) * x[2];
        },
        .jacobian = [](double, std::span<const double> x, std::span<double> J) {
            J[0] = -10.0; J[1] = 10.0;  J[2] = 0.0;
            J[3] = 28.0 - x[2]; J[4] = -1.0; J[5] = -x[0];
            J[6] = x[1];  J[7] = x[0];  J[8] = -8.0 / 3.0;
        }
    };

    std::array<double, 3> init_state{1.0, 1.0, 1.0};
    Analyzer analyzer{cfg};

    auto result = analyzer.compute(sys, init_state);
    if (result.has_value()) {
        const auto& metrics = result.value();
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Обчислення завершено успішно (C++20):\n";
        std::cout << "  lambda_1 = " << metrics.spectrum[0] << "\n";
        std::cout << "  lambda_2 = " << metrics.spectrum[1] << "\n";
        std::cout << "  lambda_3 = " << metrics.spectrum[2] << "\n";
        std::cout << "  D_L = " << metrics.lyapunov_dimension << "\n";
    } else {
        std::cerr << "Помилка: " << to_string(result.error()) << "\n";
    }

    return 0;
}
```
:::
