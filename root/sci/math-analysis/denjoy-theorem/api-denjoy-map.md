# 📋 Інтерфейс бібліотеки аналізу кругових відображень denjoy_map

Заголовочний файл `denjoy_map.h` надає низькорівневий та високорівневий C/C++ інтерфейс для аналізу гладкості, обчислення чисел обертання, перевірки нерівності спотворення Данжуа (Denjoy Distortion Lemma) та виявлення блукаючих інтервалів у кругових відображеннях `f: S¹ → S¹`.

Бібліотека розроблена для застосування у фізичному моделюванні фазових систем, нелінійній механіці, радіотехнічному моделюванні систем ФАПЧ та обчислювальному аналізі фазових портретів. Вона забезпечує високу обчислювальну ефективність, відсутність динамічного виділення пам'яті у гарячих циклах і повну сумісність із стандартами C99 та C++20.

## 1. Архітектурні принципи та дизайн бібліотеки

Проект бібліотеки `denjoy_map` спирається на три головні інженерні принципи:

1. **Безпека та суворе повернення статусів**: Всі процедури API повертають перелічуваний тип статусу `denjoy_status_t` у C або `std::expected` у C++20. Жодна функція не генерує прихованих винятків C++ у низькорівневому шарі C, що дозволяє безпечно використовувати бібліотеку в ядерному контексті або системному програмуванні.
2. **Абстракція підйому через зворотні виклики (callbacks)**: Користувач задає відображення за допомогою двох функцій-вказівників: підйому `F(x)` та його похідної `F'(x)`. Завдяки наявності непрозорого вказівника `user_data`, бібліотека підтримує передачу довільних параметрів системи (наприклад, масивів коефіцієнтів, векторів збурення або контексту розрахунку) без використання глобальних змінних.
3. **Потокобезпечність та відсутність мутабельного глобального стану**: Всі обчислювальні структури даних передаються через параметри функцій. Бібліотека є повністю повторно входжуваною (reentrant) і потокобезпечною (thread-safe), що дозволяє паралельно аналізувати тисячі фазових орбіт на багатоядерних обчислювальних кластерах за допомогою OpenMP або MPI.

## 2. Коди помилок та обробка виняткових ситуацій

Всі функції бібліотеки повертають статус виконання. Це дозволяє явно обробляти граничні випадки та чисельні збої під час інтегрування орбіт.

:::tabs
```c
typedef enum {
    DENJOY_OK                    =  0,  /* Успішне виконання операції */
    DENJOY_ERROR_NULL_POINTER    = -1,  /* Передано нульовий вказівник на конфігурацію або вихідний параметр */
    DENJOY_ERROR_INVALID_PARAM   = -2,  /* Некоректне значення параметра (наприклад, q = 0 або від'ємна кількість ітерацій) */
    DENJOY_ERROR_NON_MONOTONIC   = -3,  /* Відображення втратило монотонність (f'(x) <= 0), відображення не є диффеоморфізмом */
    DENJOY_ERROR_MAX_ITER_EXCEEDED = -4,/* Перевищено максимальну дозволену кількість ітерацій при пошуку числа обертання */
    DENJOY_ERROR_OUT_OF_MEMORY   = -5   /* Помилка виділення пам'яті під час генерації структур розкладу */
} denjoy_status_t;
```
```cpp
enum class Status : int32_t {
    Ok                  =  0,  // Успішне виконання
    NullPointer         = -1,  // Null pointer passed
    InvalidParam        = -2,  // Некоректний параметр
    NonMonotonic        = -3,  // Втрата монотонності (f'(x) <= 0)
    MaxIterExceeded     = -4,  // Перевищено кількість ітерацій
    OutOfMemory         = -5   // Помилка виділення пам'яті
};
```
:::

Кожен код помилки має чітке динамічне обґрунтування:
- `DENJOY_ERROR_NULL_POINTER` / `Status::NullPointer`: Виникає, якщо передано нульовий вказівник на об'єкт конфігурації або структуру вихідних даних. Запобігає крахам через розіменування null-pointer (NPD crashes).
- `DENJOY_ERROR_INVALID_PARAM` / `Status::InvalidParam`: Сигналізує про некоректно задані параметри розрахунку, такі як від'ємний період `period <= 0`, кількість точок сітки `num_samples < 2` або крок `q_step == 0`.
- `DENJOY_ERROR_NON_MONOTONIC` / `Status::NonMonotonic`: Виникає тоді, коли у процесі сканування по колу похідна `f'(x)` падає до нуля або стає від'ємною (наприклад, при `K ≥ 1` у синус-круговому відображенні). У цьому випадку умова теореми Данжуа припиняє діяти, і бібліотека сигналізує про втрату диффеоморфізму.
- `DENJOY_ERROR_MAX_ITER_EXCEEDED` / `Status::MaxIterExceeded`: Сигналізує про те, що чисельний алгоритм не зміг досягти заданої точності обчислення числа обертання за відведену кількість ітерацій `max_iterations`, що буває поблизу складних резонансних меж.
- `DENJOY_ERROR_OUT_OF_MEMORY` / `Status::OutOfMemory`: Сигналізує про помилку виділення динамічної пам'яті при побудові масивів знаменників ланцюгового дробу.

## 3. Опис структур даних та параметрів

### Конфігурація відображення (`denjoy_map_config_t`)

Структура конфігурації містить вказівники на користувацькі функції підйому та похідної, а також супутні параметри накриття. Вона виступає головним паспортом системи, який передається у всі обчислювальні процедури.

:::tabs
```c
typedef double (*denjoy_lift_fn)(double x, void *user_data);
typedef double (*denjoy_prime_fn)(double x, void *user_data);

typedef struct {
    denjoy_lift_fn  lift;         /* Вказівник на неперервну функцію підйому F(x) на R */
    denjoy_prime_fn prime;        /* Вказівник на функцію похідної F'(x) */
    void           *user_data;    /* Непрозорий вказівник на користувацькі параметри */
    double          period;       /* Період накриття прямої (за замовчуванням 1.0) */
} denjoy_map_config_t;
```
```cpp
using LiftFn  = double(*)(double x, void* user_data);
using PrimeFn = double(*)(double x, void* user_data);

struct MapConfig {
    LiftFn  lift{nullptr};
    PrimeFn prime{nullptr};
    void*   user_data{nullptr};
    double  period{1.0};
};
```
:::

Поля структури мають наступне аналітичне та обчислювальне призначення:
- `lift`: Неперервна функція `F: ℝ → ℝ`, яка задовольняє умову `F(x + period) = F(x) + period`. Задає підйом відображення на розгорнуту чисельну пряму.
- `prime`: Неперервна похідна `F'(x)`. Для диффеоморфізму має бути строго додатною `F'(x) > 0` у всіх точках.
- `user_data`: Непрозорий контекстний вказівник `void*`, який передається без змін у кожний виклик `lift` та `prime`. Включає коефіцієнти зв'язку, амплітуди збурення або фізичні константи.
- `period`: Довжина періоду накриття кола (за замовчуванням `1.0`, але підтримуються кутові системи з періодом `2π`).

### Результати обчислення числа обертання (`denjoy_rotation_info_t`)

Структура акумулює результати обчислення числа обертання Пуанкаре та його арифметичні характеристики:

:::tabs
```c
typedef struct {
    double    rotation_number;    /* Обчислене число обертання rho(f) in [0, 1) */
    int       is_rational;        /* Прапорець раціональності (1 — раціональне p/q, 0 — ірраціональне) */
    long      period;             /* Період орбіти q (якщо число є раціональним p/q, інакше 0) */
    double    error_estimate;     /* Верхня оцінка чисельної похибки обчислення числа обертання */
    long      iterations_used;    /* Фактична кількість використаних ітерацій */
} denjoy_rotation_info_t;
```
```cpp
struct RotationInfo {
    double       rotation_number{0.0};
    bool         is_rational{false};
    std::size_t  period{0};
    double       error_estimate{0.0};
    std::size_t  iterations_used{0};
};
```
:::

Поля структури розшифровуються наступним чином:
- `rotation_number`: Обчислене граничне значення числа обертання `ρ(f) ∈ [0, 1)`.
- `is_rational`: Автоматично встановлюється в `1` (`true`), якщо чисельний алгоритм виявив фазове захоплення та знайдено періодичну орбіту періоду `q`.
- `period`: Довжина періоду замкненої орбіти `q` у разі раціонального числа обертання `p/q`.
- `error_estimate`: Верхня оцінка чисельної похибки, обчислена за різницею ітерацій `|Fⁿ(x)/n - F^{2n}(x)/(2n)|`.
- `iterations_used`: Кількість виконаних кроків ітератора підйому.

### Статистика спотворення похідних (`denjoy_distortion_stats_t`)

Структура містить розраховані значення екстремумів похідної `q_k`-ї ітерації та оцінку спотворення за Данжуа:

:::tabs
```c
typedef struct {
    double    q_step;             /* Знаменник наближення числа обертання q_k */
    double    min_derivative;     /* Мінімальне значення похідної (f^{q_k}')(x) по всій сітці на колі */
    double    max_derivative;     /* Максимальне значення похідної (f^{q_k}')(x) по всій сітці на колі */
    double    distortion_ratio;   /* Відношення max_derivative / min_derivative */
    double    log_distortion;     /* Логарифмічне спотворення log(max_derivative) - log(min_derivative) */
    double    estimated_variation;/* Чисельна оцінка повної варіації log f' на колі */
} denjoy_distortion_stats_t;
```
```cpp
struct DistortionStats {
    std::size_t q_step{0};
    double      min_derivative{0.0};
    double      max_derivative{0.0};
    double      distortion_ratio{1.0};
    double      log_distortion{0.0};
    double      estimated_variation{0.0};
};
```
:::

Поля розшифровуються так:
- `q_step`: Знаменник найкращого раціонального наближення числа обертання `q_k`.
- `min_derivative`: Найменше значення похідної `(f^{q_k}')(x)` серед усіх точок сітки семплювання.
- `max_derivative`: Найбільше значення похідної `(f^{q_k}')(x)` серед усіх точок сітки.
- `distortion_ratio`: Відношення `max_derivative / min_derivative`.
- `log_distortion`: Логарифмічне спотворення `log(max_derivative) - log(min_derivative)`.
- `estimated_variation`: Оцінка повної варіації `Var(log f')`.

Завдяки оцінці `log_distortion` користувач може безпосередньо перевірити виконання нерівності Данжуа: якщо `log_distortion` залишається обмеженим при зростанні `q_step`, відображення є `C²`-гладким і не має блукаючих інтервалів.

## 4. Функції публічного API та специфікація викликів

Нижче наведено детальний опис кожної функції публічного інтерфейсу з описом входів, виходів та граничних умов.

### Ініціалізація конфігурації (`denjoy_map_init`)

Функція перевіряє передані вказівники та створює готовий об'єкт конфігурації.

:::tabs
```c
denjoy_status_t denjoy_map_init(
    denjoy_map_config_t *config,
    denjoy_lift_fn lift,
    denjoy_prime_fn prime,
    void *user_data
);
```
```cpp
[[nodiscard]] std::expected<MapConfig, Status> create_map_config(
    LiftFn lift,
    PrimeFn prime,
    void* user_data = nullptr
) noexcept;
```
:::

- **Вхідні параметри**: `lift` — вказівник на функцію підйому; `prime` — вказівник на функцію похідної; `user_data` — контекст.
- **Вихідний результат**: `DENJOY_OK` при успіху або `DENJOY_ERROR_NULL_POINTER` при нульових вказівниках.

### Обчислення числа обертання Пуанкаре (`denjoy_compute_rotation_number`)

Ітерує підйом `F(x)` і вираховує чисельну границю числа обертання Пуанкаре.

:::tabs
```c
denjoy_status_t denjoy_compute_rotation_number(
    const denjoy_map_config_t *config,
    double x0,
    long max_iterations,
    denjoy_rotation_info_t *info
);
```
```cpp
[[nodiscard]] std::expected<RotationInfo, Status> compute_rotation_number(
    const MapConfig& config,
    double x0 = 0.0,
    std::size_t max_iterations = 1000000
) noexcept;
```
:::

- **Вхідні параметри**: `config` — конфігурація відображення; `x0` — початкова точка; `max_iterations` — ліміт ітерацій.
- **Вихідний результат**: Результати записуються в структуру `info`.

### Обчислення похідної `n`-ї ітерації в точці (`denjoy_eval_orbit_derivative`)

Обчислює накопичений добуток похідних `(fⁿ)'(x_0) = ∏_{k=0}^{n-1} f'(f^k(x_0))` вздовж орбіти.

:::tabs
```c
denjoy_status_t denjoy_eval_orbit_derivative(
    const denjoy_map_config_t *config,
    double x0,
    long n,
    double *out_derivative
);
```
```cpp
[[nodiscard]] std::expected<double, Status> eval_orbit_derivative(
    const MapConfig& config,
    double x0,
    std::size_t n
) noexcept;
```
:::

- **Вхідні параметри**: `x0` — початкова фаза; `n` — кількість кроків орбіти.

### Перевірка нерівності спотворення Данжуа (`denjoy_check_distortion`)

Сканує коло сіткою точок та обчислює показники спотворення для знаменника `q_k`.

:::tabs
```c
denjoy_status_t denjoy_check_distortion(
    const denjoy_map_config_t *config,
    long q_k,
    int num_samples,
    denjoy_distortion_stats_t *stats
);
```
```cpp
[[nodiscard]] std::expected<DistortionStats, Status> check_distortion(
    const MapConfig& config,
    std::size_t q_k,
    std::size_t num_samples = 2000
) noexcept;
```
:::

- **Вхідні параметри**: `q_k` — знаменник наближення; `num_samples` — кількість точок сітки семплювання.

### Перевірка монотонності та $C^1$-диффеоморфізму (`denjoy_verify_diffeomorphism`)

Перевіряє строгу монотонність відображення, переконуючись у строгості `f'(x) > 0`.

:::tabs
```c
denjoy_status_t denjoy_verify_diffeomorphism(
    const denjoy_map_config_t *config,
    int num_samples,
    double *min_prime_val
);
```
```cpp
[[nodiscard]] std::expected<double, Status> verify_diffeomorphism(
    const MapConfig& config,
    std::size_t num_samples = 1000
) noexcept;
```
:::

## 5. Граничні випадки та обробка чисельних ризиків

При розробці надійного промислового коду на базі `denjoy_map` необхідно враховувати наступні чисельні та фізичні граничні випадки:

1. **Втрата монотонності при `K = 1`**:
   У разі моделювання синус-кругового відображення при `K = 1` функція `denjoy_verify_diffeomorphism` поверне статус `DENJOY_ERROR_NON_MONOTONIC` або `Status::NonMonotonic`, оскільки в точці `x = 0` похідна дорівнює `0`. У цьому випадку додаток має перейти до аналізу драбини диявола замість перевірки теореми Данжуа.

2. **Переповнення при логарифмуванні похідних**:
   При довгому ітеруванні орбіт (`n > 100 000`) безпосередній добуток `(fⁿ)'(x) = ∏ f'(f^k(x))` може виходити за межі діапазону `double` (`10⁻³⁰⁸ ... 10³⁰⁸`). Таке чисельне переповнення запобігається всередині функції `denjoy_check_distortion` за допомогою логарифмічного сумування `log_dist = ∑ log(f')`.

3. **Багатопотокова паралелізація**:
   Оскільки структура `denjoy_map_config_t` є незмінною (read-only) під час обчислень, одна і та сама конфігурація може одночасно використовуватися декількома робочими потоками (threads) для обчислення орбіт із різними початковими точками `x_0`.

4. **Інтеграція з іншими мовами через C-ABI**:
   Завдяки стандартному C-ABI (C Application Binary Interface), бібліотека `denjoy_map.h` легко імпортується у високорівневі середовища: Python через `ctypes` або `cffi`, Julia через `ccall`, Rust через `bindgen`. Це забезпечує поєднання обчислювальної швидкості C з гнучкістю наукової візуалізації.

## 6. Повний приклад використання у C та C++

Нижче наведено повні, готові до збірки приклади використання бібліотеки мовами C99 та C++20.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "denjoy_map.h"

/* Контекст користувацьких параметрів відображення */
typedef struct {
    double omega;
    double k;
} arnold_params_t;

/* Функція підйому F(x) */
static double arnold_lift(double x, void *user_data) {
    arnold_params_t *p = (arnold_params_t *)user_data;
    return x + p->omega - (p->k / (2.0 * M_PI)) * sin(2.0 * M_PI * x);
}

/* Функція похідної F'(x) */
static double arnold_prime(double x, void *user_data) {
    arnold_params_t *p = (arnold_params_t *)user_data;
    return 1.0 - p->k * cos(2.0 * M_PI * x);
}

int main(void) {
    arnold_params_t params = {
        .omega = (sqrt(5.0) - 1.0) / 2.0,  /* Золотий перетин */
        .k = 0.4                            /* Субкритичний режим K < 1 */
    };

    denjoy_map_config_t config;
    if (denjoy_map_init(&config, arnold_lift, arnold_prime, &params) != DENJOY_OK) {
        fprintf(stderr, "Помилка ініціалізації конфігурації\n");
        return 1;
    }

    /* Перевірка гладкості диффеоморфізму */
    double min_deriv = 0.0;
    if (denjoy_verify_diffeomorphism(&config, 1000, &min_deriv) != DENJOY_OK) {
        printf("Увага: відображення втратило монотонність! Мін. похідна = %.6f\n", min_deriv);
        return 1;
    }
    printf("Відображення є строго монотонним. Мін. похідна = %.6f\n", min_deriv);

    /* Обчислення числа обертання */
    denjoy_rotation_info_t rot_info;
    if (denjoy_compute_rotation_number(&config, 0.0, 500000L, &rot_info) == DENJOY_OK) {
        printf("Обчислене число обертання rho(f) = %.8f\n", rot_info.rotation_number);
    }

    /* Перевірка нерівності Данжуа для q = 610 */
    denjoy_distortion_stats_t dist_stats;
    if (denjoy_check_distortion(&config, 610, 2000, &dist_stats) == DENJOY_OK) {
        printf("--- Спотворення для q = 610 ---\n");
        printf("Мін. похідна q-ї ітерації: %.6f\n", dist_stats.min_derivative);
        printf("Макс. похідна q-ї ітерації: %.6f\n", dist_stats.max_derivative);
        printf("Логарифмічне спотворення:  %.6f (<= Var(log f'))\n", dist_stats.log_distortion);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <expected>
#include <span>
#include <cmath>
#include <numbers>

namespace denjoy {

class CircleMapSystem {
public:
    using LiftFn = double(*)(double, void*);
    using PrimeFn = double(*)(double, void*);

    CircleMapSystem(LiftFn lift, PrimeFn prime, void* user_data = nullptr) {
        config_.lift = lift;
        config_.prime = prime;
        config_.user_data = user_data;
        config_.period = 1.0;
    }

    [[nodiscard]] std::expected<double, denjoy_status_t>
    compute_rotation_number(long iterations = 500000L) const noexcept {
        denjoy_rotation_info_t info{};
        auto status = denjoy_compute_rotation_number(&config_, 0.0, iterations, &info);
        if (status != DENJOY_OK) {
            return std::unexpected(status);
        }
        return info.rotation_number;
    }

    [[nodiscard]] std::expected<denjoy_distortion_stats_t, denjoy_status_t>
    analyze_distortion(long q_step, int num_samples = 2000) const noexcept {
        denjoy_distortion_stats_t stats{};
        auto status = denjoy_check_distortion(&config_, q_step, num_samples, &stats);
        if (status != DENJOY_OK) {
            return std::unexpected(status);
        }
        return stats;
    }

private:
    denjoy_map_config_t config_{};
};

} // namespace denjoy

int main() {
    struct Params { double omega; double k; } params{ (std::numbers::sqrt5 - 1.0) / 2.0, 0.35 };

    auto lift = [](double x, void* ptr) -> double {
        auto* p = static_cast<Params*>(ptr);
        return x + p->omega - (p->k / (2.0 * std::numbers::pi)) * std::sin(2.0 * std::numbers::pi * x);
    };

    auto prime = [](double x, void* ptr) -> double {
        auto* p = static_cast<Params*>(ptr);
        return 1.0 - p->k * std::cos(2.0 * std::numbers::pi * x);
    };

    denjoy::CircleMapSystem system(lift, prime, &params);

    if (auto rot = system.compute_rotation_number(); rot) {
        std::cout << "C++20: Число обертання rho = " << *rot << "\n";
    }

    if (auto dist = system.analyze_distortion(987); dist) {
        std::cout << "C++20: Логарифмічне спотворення при q=987: " << dist->log_distortion << "\n";
    }

    return 0;
}
```
:::
