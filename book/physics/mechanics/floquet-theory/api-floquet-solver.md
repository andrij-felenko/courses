# 📋 Довідник системного інтерфейсу Floquet Solver (C / C++)

Специфікація системного інтерфейсу розрахункового модуля Floquet Solver призначена для високоефективного чисельного аналізу стійкості періодичних лінійних систем у реальному часі в системах керування роботизованими комплексами, прискорювачами частинок та оптичними пастками. Інтерфейс надає засоби обчислення матриці монодромії, мультиплікаторів Флоке та оцінки покажчиків стійкості для довільної `n`-вимірної лінійної системи з періодичними коефіцієнтами `dx/dt = A(t)·x`.

## 1. Загальні принципи архітектури та мовні рівні

Програмна бібліотека Floquet Solver розроблена за двошаровою архітектурою, яка поєднує низькорівневу сумісність із вбудованими платформами та високорівневу безпеку типів сучасної мови C++20:

* **C-інтерфейс (`floquet_solver.h`)**: Низькорівневий послідовний C-ABI сумісний API. Він призначений для застосування у мікроконтролерних прошивках, реальних ОС (RTOS), драйверах ядер та високонавантажених обчислювальних модулях, де вимагається пряме володіння пам'яттю, відсутність динамічних винятків та відсутність залежностей від стандартної бібліотеки C++. Всі операції повертають явні коди помилок через перелічувальний тип статусу.
* **C++20-інтерфейс (`FloquetSolver.hpp`)**: Об'єктно-орієнтована RAII-обгортка, побудована поверх стандартних контейнерів та концептів C++20. Вона використовує `std::vector` для динамічного керування буферами, `std::span` для передачі нуль-копіювальних зрізів масивів, `std::complex` для обробки комплексних спектрів та `std::expected` для безпечної обробки помилок без застосування механізму винятків `try/catch`.

## 2. Специфікація типів даних, конфігурацій та кодів помилок

### Системні коди повернення

Кожна обчислювальна процедура бібліотеки повертає строго визначений код статусу, який визначає результат виконання:

1. `FLOQUET_SUCCESS` (`FloquetStatus::Success`): Операцію обчислення фундаментальної матриці монодромії, її спектрального розкладу та оцінки покажчиків стійкості виконано повністю успішно.
2. `FLOQUET_ERROR_INVALID_PARAM` (`FloquetStatus::InvalidParam`): Викликач передав недопустимі вхідні параметри конфігурації. До порушень належать: розмірність фазового простору `dim == 0`, від'ємний або нульовий період збудження `period <= 0.0`, кількість сіткових кроків `steps < 10` або нульовий вказівник на функцію праві частини `rhs == NULL`.
3. `FLOQUET_ERROR_INTEGRATION_FAIL` (`FloquetStatus::IntegrationFailure`): Виявлено втрату чисельної точності під час матричного інтегрування. Модуль здійснює автоматичну перевірку інваріанта Ліувілля — Остроградського `det M = exp(∫ tr A ds)`. Якщо чисельний визначник відхиляється від теоретичного значення більше ніж на `10 · tol`, інтегрування вважається недостовірним через недостатню кількість кроків `steps`.
4. `FLOQUET_ERROR_EIGEN_FAIL` (`FloquetStatus::EigenvalueFailure`): Внутрішній ітераційний алгоритм QR-розкладу не зміг досягти збіжності при пошуку власних значень матриці монодромії за встановлену граничну кількість ітерацій.
5. `FLOQUET_ERROR_ALLOCATION` (`FloquetStatus::AllocationError`): Системна служба розподілу пам'яті не змогла виділити потрібний буфер оперативної пам'яті під час виконання `floquet_result_alloc()`.

:::tabs
@tab C (Типи даних)
```c
typedef enum {
    FLOQUET_SUCCESS               =  0,
    FLOQUET_ERROR_INVALID_PARAM   = -1,
    FLOQUET_ERROR_INTEGRATION_FAIL= -2,
    FLOQUET_ERROR_EIGEN_FAIL      = -3,
    FLOQUET_ERROR_ALLOCATION      = -4
} floquet_status_t;

typedef struct {
    size_t dim;               /* Розмірність n (dim >= 1) */
    double period;            /* Фізичний період T (period > 0) */
    size_t steps;             /* Кількість кроків сітки RK4 (steps >= 10) */
    double tol;               /* Допуск чистової стійкості (наприклад, 1e-5) */
} floquet_config_t;
```

@tab C++ (Типи даних)
```cpp
enum class FloquetStatus : int32_t {
    Success             =  0,
    InvalidParam        = -1,
    IntegrationFailure  = -2,
    EigenvalueFailure   = -3,
    AllocationError     = -4
};

struct FloquetConfig {
    std::size_t dim{2};
    double period{3.14159265358979323846};
    std::size_t steps{1000};
    double tolerance{1e-5};
};
```
:::

### Детальний опис полів структур конфігурації та результату

* `dim` (`std::size_t dim`): Кількість фазових змінних системи `n`. Задає розмір матриці `A(t)` як `n × n`.
* `period` (`double period`): Фізичний період коефіцієнтного матричного поля `T > 0`. Для звичайного коливального збудження з частотою `ω` дорівнює `T = 2·π / ω`.
* `steps` (`std::size_t steps`): Кількість однакових інтеграційних кроків Рунге — Кутти 4-го порядку на один період `T`. Крок інтегрування обчислюється як `dt = period / steps`.
* `tol` (`double tolerance`): Чисельний допуск порівняння модулів мультиплікаторів. Система вважається стійкою, якщо `max |λ_i| <= 1.0 + tol`.
* `monodromy` (`std::vector<double> monodromy_matrix`): Вихідна числова матриця монодромії `M = Φ(T)` розміру `n × n`, розгорнута у плоский масив за рядками (`row-major ordering`). Елемент `M(i, j)` зберігається під індексом `i * n + j`.
* `re_multipliers` / `im_multipliers` (`std::vector<std::complex<double>> multipliers`): Масив обчислених мультиплікаторів Флоке `λ_i` (власних значень матриці `M`).
* `max_modulus`: Значення максимального модуля мультиплікатора `max |λ_i|`, яке використовується для підсумкової класифікації стійкості.
* `trace`: Слід матриці монодромії `tr M = ∑ M(i, i)`. Для 2D консервативних систем `|tr M| <= 2` слугує швидким індикатором стійкості.
* `is_stable`: Логічний прапорець стійкості, який набуває значення `true`, якщо всі мультиплікатори лежать у межах одиничного кола.

## 3. Сигнатури функцій та програмний інтерфейс

Нижче наведено повний специфікатор заголовкових файлів бібліотеки для обох мовних стандартів.

:::tabs
@tab C (floquet_solver.h)
```c
#ifndef FLOQUET_SOLVER_H
#define FLOQUET_SOLVER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    FLOQUET_SUCCESS                =  0,
    FLOQUET_ERROR_INVALID_PARAM    = -1,
    FLOQUET_ERROR_INTEGRATION_FAIL = -2,
    FLOQUET_ERROR_EIGEN_FAIL       = -3,
    FLOQUET_ERROR_ALLOCATION       = -4
} floquet_status_t;

/* Вказівник на функцію коефіцієнтів A(t): заповнює плоский масив out_matrix (size n*n) */
typedef void (*floquet_rhs_fn)(double t, size_t n, double* out_matrix, void* user_data);

typedef struct {
    size_t dim;               /* Розмірність n */
    double period;            /* Період T */
    size_t steps;             /* Кількість кроків RK4 */
    double tol;               /* Чисельний допуск стійкості */
} floquet_config_t;

typedef struct {
    double* monodromy;        /* Вихідна матриця M розміру n*n (row-major) */
    double* re_multipliers;   /* Дійсна частина мультиплікаторів (розмір n) */
    double* im_multipliers;   /* Уявна частина мультиплікаторів (розмір n) */
    double max_modulus;       /* Максимальний модуль |lambda| */
    double trace;             /* Слід матриці монодромії tr(M) */
    bool is_stable;           /* Прапорець стійкості */
} floquet_result_t;

/* Виділення ресурсів для результату */
floquet_status_t floquet_result_alloc(size_t dim, floquet_result_t* res);

/* Звільнення ресурсів */
void floquet_result_free(floquet_result_t* res);

/* Обчислення матриці монодромії та аналіз мультиплікаторів */
floquet_status_t floquet_solve(
    const floquet_config_t* config,
    floquet_rhs_fn rhs,
    void* user_data,
    floquet_result_t* out_result
);

#ifdef __cplusplus
}
#endif

#endif /* FLOQUET_SOLVER_H */
```

@tab C++ (FloquetSolver.hpp)
```cpp
#ifndef FLOQUET_SOLVER_HPP
#define FLOQUET_SOLVER_HPP

#include <vector>
#include <complex>
#include <functional>
#include <span>
#include <expected>
#include <cstdint>

namespace Physics::Mechanics {

enum class FloquetStatus : int32_t {
    Success             =  0,
    InvalidParam        = -1,
    IntegrationFailure  = -2,
    EigenvalueFailure   = -3,
    AllocationError     = -4
};

struct FloquetConfig {
    std::size_t dim{2};
    double period{3.14159265358979323846};
    std::size_t steps{1000};
    double tolerance{1e-5};
};

struct FloquetResult {
    std::vector<double> monodromy_matrix; // row-major n x n
    std::vector<std::complex<double>> multipliers;
    std::vector<std::complex<double>> exponents;
    double max_modulus{0.0};
    double trace{0.0};
    bool is_stable{false};
};

class FloquetSolver {
public:
    using SystemMatrixFn = std::function<void(double t, std::span<double> out_flat_matrix)>;

    explicit FloquetSolver(FloquetConfig config) noexcept
        : m_config(std::move(config)) {}

    [[nodiscard]] std::expected<FloquetResult, FloquetStatus> solve(const SystemMatrixFn& sys_fn) const;

private:
    FloquetConfig m_config;

    void rk4_step(double t, double dt, std::span<double> phi, const SystemMatrixFn& sys_fn, std::vector<double>& scratch) const noexcept;
};

} // namespace Physics::Mechanics

#endif // FLOQUET_SOLVER_HPP
```
:::

## 4. Покроковий розбір прикладів використання

У наведених прикладах розглядається аналіз стійкості періодичної системи Матьє `y'' + (1.5 - 2·0.2·cos(2·t))·y = 0` з періодом `T = π`.

### Опис порядку виконання у мові C
1. Ініціалізується структура конфігурації `floquet_config_t` із параметрами: `dim = 2`, `period = M_PI`, `steps = 1000`, `tol = 1e-5`.
2. Викликається функція `floquet_result_alloc(&config.dim, &result)`, яка виділяє в купі динамічні масиви під матрицю монодромії `2 × 2` та вектор мультиплікаторів розміру `2`.
3. Викликається головна обчислювальна процедура `floquet_solve()`. Всередині неї створюється одинична початкова матриця `Φ(0) = Eye(2)`, виконується 1000 кроків інтегрування RK4 та викликається процедура QR-розкладу для матриці `Φ(T)`.
4. Зчитуються обчислені значення `result.trace`, `result.max_modulus` та прапорець `result.is_stable`.
5. Наприкінці роботи обов'язково викликається `floquet_result_free(&result)` для запобігання витоку пам'яті.

### Опис порядку виконання у мові C++20
1. Створюється об'єкт конфігурації `FloquetConfig` із типізованими полями за замовчуванням.
2. Створюється екземпляр класу `FloquetSolver solver(config)`.
3. Оголошується лямбда-вираз `sys_fn`, який приймає посилання на нуль-копіювальний зріз `std::span<double>` і заповнює 4 елементи матриці `A(t)`.
4. Викликається метод `solver.solve(sys_fn)`, який повертає контейнер `std::expected<FloquetResult, FloquetStatus>`.
5. Результат перевіряється через `if (result)`: при успіху доступ до даних здійснюється через оператор розіменування `result->trace`, а при помилці код опису дістається через `result.error()`. Уся пам'ять звільняється автоматично деструктором `FloquetResult`.

:::tabs
@tab C (Приклад виклику)
```c
#include "floquet_solver.h"
#include <stdio.h>
#include <math.h>

/* Система Матьє у C-стилі */
static void mathieu_rhs(double t, size_t n, double* out_matrix, void* user_data) {
    (void)user_data;
    double a = 1.5;
    double q = 0.2;
    double f_t = a - 2.0 * q * cos(2.0 * t);

    out_matrix[0 * n + 0] = 0.0;
    out_matrix[0 * n + 1] = 1.0;
    out_matrix[1 * n + 0] = -f_t;
    out_matrix[1 * n + 1] = 0.0;
}

int main(void) {
    floquet_config_t config = {
        .dim = 2,
        .period = 3.141592653589793,
        .steps = 1000,
        .tol = 1e-5
    };

    floquet_result_t result;
    if (floquet_result_alloc(config.dim, &result) != FLOQUET_SUCCESS) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    floquet_status_t status = floquet_solve(&config, mathieu_rhs, NULL, &result);
    if (status == FLOQUET_SUCCESS) {
        printf("Обчислення успішне!\n");
        printf("Слід M: %.6f\n", result.trace);
        printf("Максимальний модуль |lambda|: %.6f\n", result.max_modulus);
        printf("Система стійка: %s\n", result.is_stable ? "ТАК" : "НІ");
    } else {
        fprintf(stderr, "Помилка обчислення: %d\n", status);
    }

    floquet_result_free(&result);
    return 0;
}
```

@tab C++ (Приклад виклику)
```cpp
#include "FloquetSolver.hpp"
#include <iostream>
#include <cmath>

int main() {
    using namespace Physics::Mechanics;

    FloquetConfig config{
        .dim = 2,
        .period = 3.14159265358979323846,
        .steps = 1000,
        .tolerance = 1e-5
    };

    FloquetSolver solver(config);

    double a = 1.5;
    double q = 0.2;

    auto sys_fn = [a, q](double t, std::span<double> out_matrix) {
        double f_t = a - 2.0 * q * std::cos(2.0 * t);
        out_matrix[0] = 0.0;
        out_matrix[1] = 1.0;
        out_matrix[2] = -f_t;
        out_matrix[3] = 0.0;
    };

    auto result = solver.solve(sys_fn);

    if (result) {
        std::cout << "Обчислення C++ успішне!\n";
        std::cout << "Слід M: " << result->trace << "\n";
        std::cout << "Максимальний модуль |lambda|: " << result->max_modulus << "\n";
        std::cout << "Система стійка: " << (result->is_stable ? "ТАК" : "НІ");
    } else {
        std::cerr << "Помилка обчислення з кодом: " << static_cast<int>(result.error()) << "\n";
    }

    return 0;
}
```
:::

## 5. Інваріанти, виняткові ситуації та багатопоточність

### Інваріанти володіння пам'яттю
У C-API структура `floquet_result_t` містить три динамічні масиви. Спроба викликати `floquet_solve()` з несформованою структурою або спроба повторного звільнення пам'яті `floquet_result_free()` призведе до аварійного завершення програми. У C++ об'єкт `FloquetResult` є повноцінним типом даних із правильною семантикою переміщення та копіювання (`move/copy constructors`).

### Оптимізація пам'яті та локальність кешу
Оскільки чисельний розрахунок матриці монодромії виконується в циклах високої частоти, структура даних використовувати розгортання двовимірних матриць `n × n` у безперервний одинвимірний масив за рядками (`row-major order`). Це забезпечує максимальну ефективність кешування другого та третього рівнів (L2/L3 cache locality) та дозволяє процесору використовувати векторні SIMD-інструкції (AVX-512, NEON) під час проведення матричного множення `K = A(t) · Φ`.

### Чисельна стійкість та контроль визначника Ліувілля
Під час інтегрування систем великої розмірності (`n > 10`) або систем із сильним параметричним збудженням крок інтегрування `dt = T / steps` має підбиратися так, щоб забезпечити стійкість алгоритму RK4. Модуль проводить внутрішню перевірку інваріанта: для гамільтонових систем із нулевим слідом `tr A(t) = 0` обчислений визначник `det M` мусить дорівнювати 1.0. Якщо значення `|det M - 1.0| > 10 · tol`, функція повертає код `FLOQUET_ERROR_INTEGRATION_FAIL`.

### Гарантії багатопотокової безпеки
Класи `FloquetSolver` та функції C-API є повністю потокобезпечними за умови, що функція праві частини `rhs` або лямбда `sys_fn` не використовує спільних глобальних даних із модифікацією. Об'єкти `FloquetSolver` є незмінними (`immutable`) після конструювання, що дозволяє виконувати паралельні обчислення на багатоядерних процесорах без застосування м'ютексів. Для сканування двовимірних параметричних сіток `(a, q)` рекомендується використовувати `std::execution::par` або `OpenMP`, передаючи окремий екземпляр `FloquetSolver` чи спільний посилальний екземпляр у кожен потік обчислень.
