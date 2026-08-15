# 🛠️ Специфікація API бібліотеки libfeigenbaum

Нижче подано повну референтну документацію програмного інтерфейсу C/C++ бібліотеки `libfeigenbaum`, що призначена для чисельного розрахунку каскадів біфуркацій, знаходження надстійких орбіт та обчислення універсальних констант Фейгенбаума `δ` та `α`.

У цьому розділі докладно описано архітектурні принципи побудови бібліотеки, структуру даних, системні вимоги, керування пам'яттю, обробку помилок, потокобезпечність та специфіку взаємодії з високорівневими мовами програмування.

## 1. Загальний огляд архітектури та C ABI

Бібліотека `libfeigenbaum` розроблена відповідно до стандартів ANSI C (C99) для забезпечення точної сумісності ABI (Application Binary Interface) з іншими мовами програмування (Python, Julia, Rust, Go), а також надає сучасний ідіоматичний C++20 обгортковий інтерфейс із підтримкою RAII, семантики переміщення та типів `std::span` й `std::expected`.

Усі публічні функції C API повертають цілочисельний код помилки типу `FeigenbaumStatus` та приймають структури конфігурації за вказівниками на незмінні дані `const*`.

Проєкт дотримується принципу **нульових динамічних алокацій** у внутрішніх обчислювальних циклах. Виділення пам'яті під масиви біфуркаційного сканування покладається на викликаючу сторону (Caller Allocates), що усуває будь-яку невизначеність щодо передачі прав володіння пам'яттю між бібліотекою та клієнтським кодом.

## 2. Принципи обробки помилок та коди статусів

Модель обробки помилок у `libfeigenbaum` побудована на строгому поверненні статусів через значення результату функції. Жодна з C-функцій не генерує винятків (Exceptions), що забезпечує стабільну роботу в середовищах із вимкненою обробкою винятків (наприклад, у ядрах ОС або у вбудованих мікроконтролерах).

### 2.1. Перелік статусів виконання FeigenbaumStatus

:::tabs
@tab C (ANSI C)
```c
typedef enum {
    FEIGENBAUM_SUCCESS               =  0,  /* Успішне завершення операції */
    FEIGENBAUM_ERR_INVALID_PARAM     = -1,  /* Некоректні вхідні параметри (NULL вказівник, некоректний інтервал) */
    FEIGENBAUM_ERR_MAX_ITERS_REACHED = -2,  /* Перевищено максимальну кількість ітерацій Ньютона без досягнення точності */
    FEIGENBAUM_ERR_DERIVATIVE_ZERO   = -3,  /* Похідна варіаційного рівняння дорівнює нулю (ділення на нуль) */
    FEIGENBAUM_ERR_OUT_OF_MEMORY     = -4,  /* Нестача оперативної пам'яті для виділення буфера орбіти */
    FEIGENBAUM_ERR_NUMERICAL_OVERFLOW= -5   /* Чисельний переповнений стан (NaN або Inf під час ітерацій) */
} FeigenbaumStatus;
```

@tab C++ (C++20 Strong Enum)
```cpp
namespace feigenbaum {

enum class ErrorCode : int {
    Success = 0,
    InvalidParam = -1,
    MaxItersReached = -2,
    DerivativeZero = -3,
    OutOfMemory = -4,
    NumericalOverflow = -5
};

} // namespace feigenbaum
```
:::

В описі помилок статус `FEIGENBAUM_SUCCESS` (або `ErrorCode::Success`) гарантує, що всі вихідні структури заповнені валідними чисельними значеннями. При виникненні будь-якої помилки вихідні буфери залишаються недоторканими, а функція повертає відповідне від'ємне значення коду помилки.

## 3. Детальний розбір структур даних

### 3.1. Конфігурація біфуркаційного сканування BifurcationConfig

:::tabs
@tab C (ANSI C Struct)
```c
typedef struct {
    double r_min;           /* Мінімальне значення параметра r (наприклад, 2.8) */
    double r_max;           /* Максимальне значення параметра r (наприклад, 4.0) */
    size_t r_steps;         /* Кількість дискретних точок сітки по параметру r */
    size_t transient_iters; /* Кількість ітерацій для відсікання перехідного процесу (наприклад, 1000) */
    size_t orbit_iters;     /* Кількість збережених точок орбіти для кожного r (наприклад, 500) */
} BifurcationConfig;
```

@tab C++ (C++20 Struct with Defaults)
```cpp
namespace feigenbaum {

struct Config {
    double r_min = 2.8;
    double r_max = 4.0;
    std::size_t r_steps = 1000;
    std::size_t transient_iters = 1000;
    std::size_t orbit_iters = 500;
};

} // namespace feigenbaum
```
:::

Структура `BifurcationConfig` (або `Config` у C++) задає розмірність сітки та тривалість інтегрування:
- `r_min` та `r_max` визначають межі сканування параметра керування `r`. Значення `r_min` має бути строго меншим за `r_max`, а обидва значення повинні належати інтервалу допустимості `[0.0, 4.0]`.
- `r_steps` задає роздільну здатність параметричної вісі. Для швидкого сканування рекомендується значення 1000–2000, для високодеталізованого рендерингу — від 10000.
- `transient_iters` регулює час релаксації системи до стійкого атрактора. При `r < r_∞` достатньо 1000 ітерацій, у поблизу точок біфуркацій значення варто підвищувати до 5000 для повного вигасання уповільненого перехідного процесу (критичне сповільнення).
- `orbit_iters` визначає кількість точок, які записуються в підсумковий масив для кожного параметра `r`. Для періодичних орбіт вони повторюються, а для хаотичних орбіт будують щільність атрактора.

### 3.2. Результат надстійкого розрахунку SuperstableResult

:::tabs
@tab C (ANSI C Struct)
```c
typedef struct {
    double r_superstable;   /* Точне значення надстійкого параметра R_n */
    double f_val;           /* Невозначений залишок рівняння F(R_n) */
    size_t iterations_used; /* Кількість використаних ітерацій Ньютона-Рафсона */
    double lyapunov_exp;    /* Значення показника Ляпунова у цій точці */
} SuperstableResult;
```

@tab C++ (C++20 Struct)
```cpp
namespace feigenbaum {

struct SuperstablePoint {
    double r_superstable = 0.0;
    double residual = 0.0;
    std::size_t iterations = 0;
    double lyapunov = 0.0;
};

} // namespace feigenbaum
```
:::

Ця структура повертає повну інформацію про знайдену надстійку точку:
- `r_superstable` містить обчислене значення `R_n` з точністю до останнього розряду представлення числа з плаваючою комою (double).
- `f_val` (або `residual`) дає точний невозначений залишок `f^(2ⁿ)(1/2, R_n) - 1/2`, який для збіжного розв'язку не перевищує `10⁻¹²`.
- `iterations_used` показує число кроків метода Ньютона-Рафсона. Завдяки квадратичній швидкості збіжності зазвичай це число не перевищує 5–8 ітерацій.
- `lyapunov_exp` містить значення старшого показника Ляпунова, яке в надстійких точках має бути глибоко від'ємним чиселом.

### 3.3. Обчислені сталі Фейгенбаума FeigenbaumConstants

:::tabs
@tab C (ANSI C Struct)
```c
typedef struct {
    double delta;           /* Обчислена перша стала Фейгенбаума δ_n */
    double alpha;           /* Обчислена друга стала Фейгенбаума α_n */
    double delta_error;     /* Відносна похибка порівняно з точним теоретичним значенням */
    double alpha_error;     /* Відносна похибка порівняно з точним теоретичним значенням */
} FeigenbaumConstants;
```

@tab C++ (C++20 Struct)
```cpp
namespace feigenbaum {

struct Constants {
    double delta = 0.0;
    double alpha = 0.0;
    double delta_error = 0.0;
    double alpha_error = 0.0;
};

} // namespace feigenbaum
```
:::

Структура накопичує розраховані параметричні та просторові масштабні коефіцієнти разом із їхніми відносними похибками відносно канонічних теоретичних значень `δ = 4.66920160910299...` та `α = 2.50290787509589...`.

## 4. Повний публічний заголовочний файл

Нижче наведено повні публічні заголовочні файли для мов C та C++.

:::tabs
@tab C Header (feigenbaum.h)
```c
#ifndef FEIGENBAUM_H
#define FEIGENBAUM_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    FEIGENBAUM_SUCCESS               =  0,
    FEIGENBAUM_ERR_INVALID_PARAM     = -1,
    FEIGENBAUM_ERR_MAX_ITERS_REACHED = -2,
    FEIGENBAUM_ERR_DERIVATIVE_ZERO   = -3,
    FEIGENBAUM_ERR_OUT_OF_MEMORY     = -4,
    FEIGENBAUM_ERR_NUMERICAL_OVERFLOW= -5
} FeigenbaumStatus;

typedef struct {
    double r_min;
    double r_max;
    size_t r_steps;
    size_t transient_iters;
    size_t orbit_iters;
} BifurcationConfig;

typedef struct {
    double r_superstable;
    double f_val;
    size_t iterations_used;
    double lyapunov_exp;
} SuperstableResult;

typedef struct {
    double delta;
    double alpha;
    double delta_error;
    double alpha_error;
} FeigenbaumConstants;

/* Публічні функції C API */

FeigenbaumStatus feigenbaum_compute_diagram(
    const BifurcationConfig* config,
    double* out_orbit_buffer
);

FeigenbaumStatus feigenbaum_find_superstable(
    int period_power,
    double r_guess,
    double tolerance,
    size_t max_iters,
    SuperstableResult* out_result
);

FeigenbaumStatus feigenbaum_estimate_constants(
    const double* r_superstable_array,
    size_t array_length,
    FeigenbaumConstants* out_constants
);

FeigenbaumStatus feigenbaum_compute_lyapunov(
    double r,
    size_t num_iters,
    double* out_lyapunov
);

#ifdef __cplusplus
}
#endif

#endif /* FEIGENBAUM_H */
```

@tab C++ Header (feigenbaum.hpp)
```cpp
#pragma once
#include <vector>
#include <expected>
#include <span>
#include <cstddef>

namespace feigenbaum {

enum class ErrorCode {
    InvalidParam = -1,
    MaxItersReached = -2,
    DerivativeZero = -3,
    OutOfMemory = -4,
    NumericalOverflow = -5
};

struct Config {
    double r_min = 2.8;
    double r_max = 4.0;
    std::size_t r_steps = 1000;
    std::size_t transient_iters = 1000;
    std::size_t orbit_iters = 500;
};

struct SuperstablePoint {
    double r_superstable = 0.0;
    double residual = 0.0;
    std::size_t iterations = 0;
    double lyapunov = 0.0;
};

struct Constants {
    double delta = 0.0;
    double alpha = 0.0;
    double delta_error = 0.0;
    double alpha_error = 0.0;
};

class Solver {
public:
    explicit Solver(Config config) : config_(config) {}

    [[nodiscard]] std::expected<std::vector<double>, ErrorCode> 
    compute_bifurcation_mesh() const;

    [[nodiscard]] std::expected<SuperstablePoint, ErrorCode> 
    find_superstable(int period_power, double r_guess, double tol = 1e-12) const;

    [[nodiscard]] static std::expected<Constants, ErrorCode> 
    estimate_constants(std::span<const double> r_superstable_series);

    [[nodiscard]] std::expected<double, ErrorCode> 
    compute_lyapunov(double r, std::size_t num_iters = 50000) const;

private:
    Config config_;
};

} // namespace feigenbaum
```
:::

## 5. Детальний опис публічних функцій API

### 5.1. feigenbaum_compute_diagram

:::tabs
@tab C Signature
```c
FeigenbaumStatus feigenbaum_compute_diagram(
    const BifurcationConfig* config,
    double* out_orbit_buffer
);
```

@tab C++ Signature
```cpp
[[nodiscard]] std::expected<std::vector<double>, ErrorCode> 
feigenbaum::Solver::compute_bifurcation_mesh() const;
```
:::

- **Призначення:** Обчислює точкову масивно-параметричну сітку біфуркаційного дерева.
- **Аргументи C:**
  - `config`: Вказівник на структуру конфігурації. Не може бути `NULL`.
  - `out_orbit_buffer`: Попередньо виділений масив розмірністю `r_steps * orbit_iters` елементів типу `double`.
- **Повертане значення:** `FEIGENBAUM_SUCCESS` у разі успішного виконання або `FEIGENBAUM_ERR_INVALID_PARAM`, якщо вказівники є нульовими. У C++ повертає `std::expected` із масивом векторів орбіт або кодом помилки.
- **Вимоги до потокобезпечності:** Функція є чистою (pure) та повністю потокобезпечною (thread-safe). Вона не використовує внутрішній глобальний стан і може викликатися з різних паралельних потоків OpenMP або pthreads.
- **Опис внутрішнього алгоритму:** Для кожного дискретного кроку `r_i = r_min + i * (r_max - r_min) / (r_steps - 1)` функція запускає ітераційний процес `x_{k+1} = r_i * x_k * (1 - x_k)` з початкової точки `x_0 = 0.5`. Після виконання `transient_iters` пропускних кроків наступні `orbit_iters` точок послідовно записуються у буфер за адресою `out_orbit_buffer + i * orbit_iters`.

### 5.2. feigenbaum_find_superstable

:::tabs
@tab C Signature
```c
FeigenbaumStatus feigenbaum_find_superstable(
    int period_power,
    double r_guess,
    double tolerance,
    size_t max_iters,
    SuperstableResult* out_result
);
```

@tab C++ Signature
```cpp
[[nodiscard]] std::expected<feigenbaum::SuperstablePoint, feigenbaum::ErrorCode> 
feigenbaum::Solver::find_superstable(int period_power, double r_guess, double tol) const;
```
:::

- **Призначення:** Знаходить надстійке значення параметра `R_n` для циклу періоду `2ⁿ` методом Ньютона-Рафсона з використанням варіаційного рівняння чутливості `w = dx / dr`.
- **Аргументи C:**
  - `period_power`: Ступінь подвоєння `n` (наприклад, `n = 3` відповідає періоду `2³ = 8`).
  - `r_guess`: Початкове наближення для параметричного пошуку (наприклад, `3.5546`).
  - `tolerance`: Заданий поріг невозначеного залишку (наприклад, `1e-12`).
  - `max_iters`: Максимальна дозволена кількість ітерацій Ньютона (наприклад, `100`).
  - `out_result`: Вказівник на вихідну структуру `SuperstableResult`.
- **Повертане значення:** `FEIGENBAUM_SUCCESS` при знаходженні кореня або відповідний від'ємний код помилки.
- **Опис математичної схеми:** На кожному кроці Ньютона `r_{m+1} = r_m - F(r_m) / F'(r_m)` функція обчислює значення складеного відображення `F(r) = f^(2ⁿ)(1/2, r) - 1/2` та його градієнта `F'(r)` через накопичення чутливості `w_{k+1} = f' * w_k + ∂f/∂r`. Критерієм зупинки слугує нерівність `|F(r_m)| < tolerance`.

### 5.3. feigenbaum_estimate_constants

:::tabs
@tab C Signature
```c
FeigenbaumStatus feigenbaum_estimate_constants(
    const double* r_superstable_array,
    size_t array_length,
    FeigenbaumConstants* out_constants
);
```

@tab C++ Signature
```cpp
[[nodiscard]] static std::expected<feigenbaum::Constants, feigenbaum::ErrorCode> 
feigenbaum::Solver::estimate_constants(std::span<const double> r_superstable_series);
```
:::

- **Призначення:** Розраховує оцінки універсальних констант Фейгенбаума `δ` та `α` за послідовністю знайдених надстійких точок `R_0, R_1, ..., R_{k-1}`.
- **Вхідні обмеження:** Довжина масиву `array_length` повинна бути не меншою за 4 для розрахунку принаймні двох послідовних відношень `δ_n`.
- **Обчислювальний механізм:** Усереднює останні граничні відношення `δ_k = (R_k - R_{k-1}) / (R_{k+1} - R_k)` та `α_k = d_k / d_{k+1}`, обчислюючи відносні відхилення від точних констант.

### 5.4. feigenbaum_compute_lyapunov

:::tabs
@tab C Signature
```c
FeigenbaumStatus feigenbaum_compute_lyapunov(
    double r,
    size_t num_iters,
    double* out_lyapunov
);
```

@tab C++ Signature
```cpp
[[nodiscard]] std::expected<double, feigenbaum::ErrorCode> 
feigenbaum::Solver::compute_lyapunov(double r, std::size_t num_iters) const;
```
:::

- **Призначення:** Обчислює старший показник Ляпунова `λ_L(r)` шляхом логарифмічного усереднення похідних вздовж ітерацій траєкторії.
- **Особливості виконання:** Автоматично додає регуляризаційний параметр `ε = 1e-12` під логарифм у разі наближення похідної до нуля, що запобігає генерації обчислювальних винятків `IEEE 754 -Inf`.

## 6. Таблиця кодів помилок та реакцій системи

| Код помилки | Символічна назва | Причина виникнення | Рекомендована дія клієнтського коду |
| :--- | :--- | :--- | :--- |
| `0` | `FEIGENBAUM_SUCCESS` | Операцію виконано успішно | Продовжувати обробку даних |
| `-1` | `FEIGENBAUM_ERR_INVALID_PARAM` | Передано `NULL` вказівник або `r_min >= r_max` | Перевірити аргументи перед викликом |
| `-2` | `FEIGENBAUM_ERR_MAX_ITERS_REACHED` | Ньютон не збігся за `max_iters` кроків | Уточнити початкове наближення `r_guess` |
| `-3` | `FEIGENBAUM_ERR_DERIVATIVE_ZERO` | Градієнт `w = dx/dr` дорівнює нулю | Змінити початкову точку `r_guess` |
| `-4` | `FEIGENBAUM_ERR_OUT_OF_MEMORY` | Не вдалося виділити буфер орбіти | Зменшити розмірність сітки `r_steps` |
| `-5` | `FEIGENBAUM_ERR_NUMERICAL_OVERFLOW` | Значення орбіти вийшло за межі `[0, 1]` | Перевірити при належність `r` інтервалу `[0, 4]` |

## 7. Інструкції зі збирання та конфігурування CMake

Бібліотека `libfeigenbaum` збирається за допомогою кросплатформенної системи CMake (версії 3.16 або новішої).

Типовий сценарій компіляції з вихідного коду під Linux або macOS включає створення окремого каталогу збірки та виклик компілятора:

```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON ..
make -j4
```

Для інтеграції у C++ проєкти достатньо підключити заголовочний файл `#include <feigenbaum.hpp>` та лінкуватися з бібліотекою `-lfeigenbaum`. Завдяки повній відсутності зовнішніх залежностей (zero dependency policy), бібліотека легко вбудовується як Git-підмодуль (submodule) або через CMake `FetchContent`.

## 8. Приклад використання C++ API у клієнтському коді

Нижче наведено ілюстративний приклад використання обгортки C++20 для обчислення надстійкої точки `R_3` періоду 8:

```cpp
#include <feigenbaum.hpp>
#include <iostream>

int main() {
    feigenbaum::Config config{
        .r_min = 3.0,
        .r_max = 3.57,
        .r_steps = 2000,
        .transient_iters = 2000,
        .orbit_iters = 1000
    };

    feigenbaum::Solver solver(config);
    
    // Знаходження надстійкої точки R_3 (період 8)
    auto result = solver.find_superstable(3, 3.5546);
    
    if (result) {
        std::cout << "Знайдено R_3: " << result->r_superstable << "\n";
        std::cout << "Показник Ляпунова: " << result->lyapunov << "\n";
    } else {
        std::cerr << "Помилка розрахунку: " << static_cast<int>(result.error()) << "\n";
    }

    return 0;
}
```

## 9. Потокобезпечність та стратегії оптимізації пам'яті

Усі функції бібліотеки `libfeigenbaum` розроблені за принципами функціональної чистоти:
1. **Відсутність побічних ефектів:** Функції не змінюють глобальний стан програми та не використовують статичні буфери.
2. **Нульові динамічні алокацій у внутрішніх циклах:** Виділення пам'яті відбувається виключно на етапі ініціалізації масивів.
3. **Підтримка векторизації SIMD:** Внутрішні обчислювальні цикли оптимізовані для компіляторного автоматичного векторування (AVX-512 / ARM Neon).

Ці властивості роблять `libfeigenbaum` ідеальним рішенням для побудови високонавантажених обчислювальних систем нелінійного аналізу та моделювання хаосу в режимі реального часу.

## 10. Вказівки щодо створення прив'язок до інших мов (FFI Bindings)

C ABI бібліотеки розроблено з урахуванням простого створення прив'язок (FFI) до високорівневих мов:

- **Python (ctypes / cffi):** Функції повертають стандартизований статус `int32_t`, що дозволяє автоматично перетворювати від'ємні коди помилок у відповідні Python-винятки `PyFeigenbaumError`.
- **Rust (bindgen):** Усі структури мають прозоре розташування у пам'яті `#[repr(C)]`, що дозволяє генерувати безпечні обгортки без додаткових витрат часу виконання.
- **Julia (ccall):** Прямий виклик C-функцій через `ccall` забезпечує продуктивність на рівні нативного коду при збереженні зручності інтерактивного аналізу у REPL.

## 11. Специфікація паралелізації та інтеграція з OpenMP

Обчислення біфуркаційної діаграми є повністю незалежним для кожного значення параметра `r`, що належить до категорії задач із паралелізмом без взаємодії (embarrassingly parallel computation).

:::tabs
@tab C (OpenMP Parallel Loop)
```c
#pragma omp parallel for schedule(dynamic, 16)
for (size_t i = 0; i < config->r_steps; ++i) {
    /* Незалежне обчислення орбіти для параметричної точки r_i */
}
```

@tab C++ (C++20 Parallel Execution Policy)
```cpp
#include <execution>
#include <algorithm>

std::for_each(std::execution::par_unseq, r_indices.begin(), r_indices.end(),
    [&](std::size_t i) {
        /* Незалежне обчислення орбіти для параметричної точки r_i */
    }
);
```
:::

Динамічне планування `schedule(dynamic, 16)` вибрано через те, що точки у періодичній зоні потребують значно менше обчислювальних ресурсів порівняно з хаотичними точками, де розрахунок похідних та показаників Ляпунова вимагає довших траєкторій.

## 12. Вимоги до пропускної здатності пам'яті (Memory Bandwidth Analysis)

При генерації великих біфуркаційного сіток (наприклад, `r_steps = 10000`, `orbit_iters = 1000`) обсяг вихідного масиву дорівнює `10000 * 1000 * 8 байт = 80 МБ`.

Для запобігання ефекту пляшкового горла пам'яті (Memory Bottleneck) реалізація виконує запис у масив орбіт послідовно в неперервні блоки пам'яті (Contiguous Memory Layout), що дозволяє контролеру пам'яті процесора максимально ефективно використовувати кеш-лінії L1/L2 та протокол попереднього завантаження (Hardware Prefetching).

## 13. Система логування та трасування

Для відлагодження чисельних процесив у режимі розробки бібліотека підтримує підключення зворотного виклику логування (Logging Callback):

:::tabs
@tab C Logging Callback
```c
typedef void (*FeigenbaumLogCallback)(int level, const char* message);

FeigenbaumStatus feigenbaum_set_log_callback(FeigenbaumLogCallback callback);
```

@tab C++ Logging Callback
```cpp
using LogCallback = std::function<void(int level, std::string_view message)>;

void feigenbaum::Solver::set_log_callback(LogCallback callback);
```
:::

Якщо зворотний виклик встановлено, бібліотека надсилає діагностичні повідомлення про кількість використаних ітерацій Ньютона, невозначені залишки та проміжні значення сталих Фейгенбаума без використання стандартного потоку виводу `stdout`.

## 14. Асинхронний C++20 інтерфейс на основі std::future

Для GUI-застосунків та інтерактивних панелей аналізу C++20 обгортка надає асинхронні методи для виконання важких чисельних обчислень у фонових потоках:

:::tabs
@tab C++ Async Method
```cpp
[[nodiscard]] std::future<std::expected<std::vector<double>, ErrorCode>> 
compute_bifurcation_mesh_async() const;
```

@tab C Threads Equivalent
```c
typedef struct {
    const BifurcationConfig* config;
    double* out_buffer;
    FeigenbaumStatus status;
} FeigenbaumThreadTask;

void* feigenbaum_async_worker(void* arg);
```
:::

Це дозволяє графічному інтерфейсу залишатися чуйним під час обчислення 10 мільйонів точок фазового простору та отримувати результати за допомогою механізму обіцянок (Promises).

## 15. Автоматизоване розгортання та тестове покриття

Пакет `libfeigenbaum` поставляється із повним набором юніт-тестів на базі фреймворку `GoogleTest` та системних інтеграційних тестів.

Тестове покриття охоплює:
1. **Перевірку точності Ньютона-Рафсона:** Порівняння знайдених надстійких точок `R_1, ..., R_8` із еталонними значеннями з точністю `10⁻¹¹`.
2. **Перевірку стабільності при нестачі пам'яті:** Стрес-тестування виділення великих буферів.
3. **Санітайзери пам'яті та потоків (AddressSanitizer / ThreadSanitizer):** Компільований контроль відсутності витоків пам'яті (Memory Leaks) та умов гонитви (Race Conditions) при розпаралелюванні через OpenMP.

## 16. Крайові випадки та виняткові режими обчислень

Розробка специфікації API враховує наступні граничні фізичні та чисельні режими:
- **Переповнення значень параметра `r > 4.0`:** У разі виходу параметра `r` за верхню межу 4.0 траєкторія логістичного відображення залишає одиничний інтервал `[0, 1]` і розбігається до нескінченності `-∞`. Функція виявляє цей стан та повертає статус `FEIGENBAUM_ERR_NUMERICAL_OVERFLOW`.
- **Початок сканування в нулі `r = 0`:** При `r = 0` орбіта миттєво колапсує у нуль `x = 0`, що є виродженим станом.
- **Точки критичного сповільнення біля `r_∞`:** При наближенні до точки накопичення `r_∞ ≈ 3.5699456` час релаксації прямує до нескінченності. Для таких точок специфікація вимагає автоматичного тимчасового збільшення параметра `transient_iters` у 5 разів.

## 17. Підтримка графічних прискорювачів GPU

Для задач масового рендерингу та двовимірного картографування параметричного простору бібліотека поставляється з опціональним модулем `libfeigenbaum_cuda`.

:::tabs
@tab C CUDA Interface
```c
FeigenbaumStatus feigenbaum_cuda_compute_diagram(
    const BifurcationConfig* config,
    double* d_out_orbit_buffer,
    void* cuda_stream
);
```

@tab C++ CUDA Modern Interface
```cpp
namespace feigenbaum::cuda {

[[nodiscard]] std::expected<void, ErrorCode> 
compute_diagram(const Config& config, double* d_out_buffer, void* stream = nullptr);

} // namespace feigenbaum::cuda
```
:::

Передача `cuda_stream` дозволяє асинхронно суміщати обчислення орбіт на графічному прискорювачі з передачею попередньо оброблених точок по шині PCIe у пам'ять центрального процесора.

## 18. Безпека типів та відповідність сучасним C++ стандартам

C++20 обгортка бібліотеки усуває ризики небезпечного приведення типів та витоків ресурсів завдяки застосуванню типів `std::span` замість сирих вказівників та довжин масивів:
- Вхідні масиви надстійких точок передаються як `std::span<const double>`, що унеможливлює вихід за межі масиву (Out of Bounds Access).
- Результати обчислень повертаються через `std::expected<T, ErrorCode>`, що змушує викликаючий код явно обробляти моменти помилок перед доступом до даних.

## 19. Довгострокова підтримка LTS та сумісність компиляторів

Розробники `libfeigenbaum` гарантують підтримку зворотної сумісності C API протягом усіх випусків серії 1.x LTS. Проєкт регулярно протестований на статичний аналіз коду за допомогою інструментів `cppcheck`, `clang-tidy` та `Coverity Scan`, що підтверджує відсутність критичних вразливостей пам'яті, потенційних витоків буферів та некоректних поводжень із вказівниками.

## 20. Підсумкове резюме специфікації API

Подана специфікація програмного інтерфейсу бібліотеки `libfeigenbaum` забезпечує повне охоплення задач розрахунку та моделювання нелінійної динаміки каскаду подвоєння періоду. Поєднання суворого C ABI, ідіоматичної обгортки C++20, нульових динамічних алокацій у циклах та розпаралелювання OpenMP робить цю бібліотеку надійним інструментом як для наукових досліджень, так і для інженерних застосувань у реальному часі.

## 21. Політика сумісності та семантичне версіонування

Бібліотека дотримується стандартів семантичного версіонування (Semantic Versioning 2.0.0). Будь-які зміни у структурах даних `BifurcationConfig` або сигнатурах функцій C API призводять до мажорного підвищення версії. Сумісність ABI гарантується у межах усіх мінорних випусків однієї серії.
