# 📋 Довідник інтерфейсу аналізу нелінійних відображень feigenbaum_calc

Цей довідник містить повну специфікацію програмного інтерфейсу (API) C/C++ бібліотеки `libfeigenbaum`, призначеної для чисельного розрахунку каскадів подвоєння періоду, обчислення універсальних констант Фейгенбаума `δ` та `α`, визначення спектра показників Ляпунова, а також локалізації вікон періодичності в нелінійних дисипативних системах.

Довідник розроблений для розробників обчислювальних модулів фізичного моделювання, систем автоматизованого аналізу хаосу, інженерних пакетів обробки сигналів та наукового програмного забезпечення високої продуктивності. Інтерфейс забезпечує як низкорівневе керування чисельними алгоритмами, так і високорівневі абстракції для обчислення фундаментальних параметрів нелінійних відображень.

## 1. Загальна архітектура та принципи побудови API

Бібліотека `libfeigenbaum` побудована за принципами суворого розділення інтерфейсу та реалізації, інкапсуляції обчислювального стану, відсутності глобального модифіковного стану (гарантія повної потокобезпечності та реентрабельності) та явного керування динамічною пам'яттю.

### 1.1. Потокобезпечність та реентрабельність

Усі функції бібліотеки є чисто функціональними або працюють із локальними екземплярами конфігурацій і структур результатів, переданими за вказівниками. Бібліотека не використовує статичні або глобальні змінні стану. Це дозволяє безпечно викликати будь-які функції `libfeigenbaum` з паралельних потоків виконання (наприклад, через POSIX Threads, OpenMP або `std::jthread`), здійснюючи паралельне сканування простору параметрів `r` або паралельний аналіз різних нелінійних відображень.

Кожен потік виконання може створювати власні структури конфігурації `feigenbaum_config_t`, виділяти незалежні масиви результатів та обчислювати показники Ляпунова без будь-яких міжпотокових блокувань чи взаємних виключень (mutexes). Це забезпечує лінійне масштабування продуктивності на багатоядерних обчислювальних кластерах при скануванні параметричних площин нелінійних відображень.

### 1.2. Модель управління пам'яттю та володіння ресурсами

Усі функції, які генерують масиви точок орбіт або послідовності біфуркаційних значень, використовують чітку модель володіння ресурсами з явним виділенням на стороні бібліотеки та явним звільненням на стороні викликаючої програми:
* У C-версії виділення пам'яті здійснюється за допомогою системного аллокатора `malloc()` / `calloc()`, а звільнення — парними функціями `feigenbaum_free_orbit` та `feigenbaum_free_cascade`. Викликаючий код зобов'язаний перевіряти статус повернення перед доступом до виділених масивів.
* У C++-версії ресурси інкапсулюються у стандартних контейнерах `std::vector<double>`, застосовуючи принцип RAII (англ. *Resource Acquisition Is Initialization*) для повністю автоматичного управління пам'яттю та запобігання витокам у разі виникнення виняткових ситуацій.

---

## 2. Заголовні файли та типи даних

Заголовні файли бібліотеки: `<feigenbaum/feigenbaum.h>` для C та `<feigenbaum/feigenbaum.hpp>` для C++.

### 2.1. Коди повернення та помилок (`feigenbaum_status_t` / `feigenbaum::Status`)

Усі функції API повертають 32-бітний цілочисельний код статусу `feigenbaum_status_t` у C або перелічення `feigenbaum::Status` у C++. Від'ємні значення відповідають критичним помилкам виконання, додатні — застереженням про потенційне зниження точності, а нульове значення свідчить про повний успіх операції.

:::tabs
```c
typedef enum {
    FEIGENBAUM_SUCCESS               =  0, /* Успішне виконання операції */
    FEIGENBAUM_WARN_LOW_PRECISION    =  1, /* Досягнуто межу машинної точності double */
    FEIGENBAUM_WARN_SLOW_CONVERGENCE =  2, /* Уповільнена збіжність біля точки біфуркації */
    
    FEIGENBAUM_ERR_INVALID_ARG       = -1, /* Передано невалідний аргумент (NULL або out of range) */
    FEIGENBAUM_ERR_NO_MEMORY         = -2, /* Нестача оперативної пам'яті для виділення масивів */
    FEIGENBAUM_ERR_ITER_LIMIT        = -3, /* Перевищено максимальну кількість ітерацій */
    FEIGENBAUM_ERR_DIVERGENCE        = -4, /* Траєкторія пішла на нескінченність (|x| > 1e10) */
    FEIGENBAUM_ERR_MAP_NULL          = -5  /* Не вказано вказівник на функцію відображення */
} feigenbaum_status_t;
```
```cpp
namespace feigenbaum {

enum class Status : int32_t {
    Success               =  0, // Успішне виконання операції
    WarnLowPrecision      =  1, // Досягнуто межу машинної точності double
    WarnSlowConvergence   =  2, // Уповільнена збіжність біля точки біфуркації
    
    ErrInvalidArg         = -1, // Невалідний аргумент
    ErrNoMemory           = -2, // Нестача оперативної пам'яті
    ErrIterLimit          = -3, // Перевищено кількість ітерацій
    ErrDivergence         = -4, // Дивергенція траєкторії
    ErrMapNull            = -5  // Порожній функтор відображення
};

} // namespace feigenbaum
```
:::

#### Докладний зміст та обробка кодів статусів:

1. `FEIGENBAUM_SUCCESS (0)`: Операція завершилася успішно. Усі обчислені масиви та структури є валідними і готовими до читання.
2. `FEIGENBAUM_WARN_LOW_PRECISION (1)`: Зауваження про те, що чисельний алгоритм досяг граничної здатності стандартного 64-бітного плаваючого формату IEEE 754 (`double`). Це виникає при обчисленні біфуркацій високого порядку (`k > 12`), коли параметрична відстань `r_k - r_{k-1}` стає порівнянною з машинним епсилон `2.22e-16`.
3. `FEIGENBAUM_WARN_SLOW_CONVERGENCE (2)`: Зауваження про критичне уповільнення збіжності поблизу точок фліп-біфуркацій, коли мультиплікатор стійкості близький до `-1`. Викликаючому коду рекомендується збільшити параметри `n_transient` у конфігурації.
4. `FEIGENBAUM_ERR_INVALID_ARG (-1)`: Передано недопустимі значення параметрів (наприклад, `r_min > r_max`, від'ємна кількість ітерацій або `NULL` вказівник на обов'язковий аргумент).
5. `FEIGENBAUM_ERR_NO_MEMORY (-2)`: Системний аллокатор не зміг виділити необхідний блок динамічної пам'яті.
6. `FEIGENBAUM_ERR_ITER_LIMIT (-3)`: Чисельний метод розв'язання нелінійних рівнянь (метод Ньютона або бісекції) не досяг заданої точності за максимальну кількість кроків.
7. `FEIGENBAUM_ERR_DIVERGENCE (-4)`: Фазова траєкторія відображення вилетіла за межі допустимої області (`|x_n| > 10¹⁰`), що свідчить про вихід параметра `r` за межі області існування обмежених атракторів.
8. `FEIGENBAUM_ERR_MAP_NULL (-5)`: Передано `NULL` замість вказівника на користувальницьку функцію нелінійного відображення.

---

### 2.2. Конфігураційна структура (`feigenbaum_config_t` / `feigenbaum::Config`)

Структура конфігурації керує параметрами чисельного інтегрування, розмірами вибірок та точністю пошуку точок біфуркацій.

:::tabs
```c
typedef struct {
    double r_min;               /* Початкове значення параметра r (за замовчуванням: 2.8) */
    double r_max;               /* Кінцеве значення параметра r (за замовчуванням: 4.0) */
    size_t r_steps;             /* Кількість кроків дискретизації по r (за замовчуванням: 1000) */
    size_t n_transient;         /* Кількість транзієнтних ітерацій для скидання перехідного процесу (10000) */
    size_t n_samples;           /* Кількість точок орбіти, що зберігаються для біфуркаційної діаграми (200) */
    size_t n_lyapunov;          /* Кількість ітерацій для усереднення показника Ляпунова (50000) */
    double bisection_tol;       /* Точність локалізації точки біфуркації по r (1e-11) */
    size_t max_bisection_iters; /* Максимальна кількість кроків бісекції (100) */
} feigenbaum_config_t;
```
```cpp
namespace feigenbaum {

struct Config {
    double r_min{2.8};
    double r_max{4.0};
    std::size_t r_steps{1000};
    std::size_t n_transient{10000};
    std::size_t n_samples{200};
    std::size_t n_lyapunov{50000};
    double bisection_tol{1e-11};
    std::size_t max_bisection_iters{100};
};

} // namespace feigenbaum
```
:::

#### Поля структури та їхній детальний фізичний зміст:

* `r_min` (тип `double`): Нижня межа інтервалу сканування параметра `r`. Для класичного логістичного відображення використовується значення `2.8`.
* `r_max` (тип `double`): Верхня межа інтервалу сканування параметра `r`. Типове значення `4.0`.
* `r_steps` (тип `size_t`): Дискретизація сітки за параметром `r` при суцільному скануванні діаграми. Визначає кількість розраховуваних вертикальних зрізів.
* `n_transient` (тип `size_t`): Кількість початкових ітерацій відображення, які виконуються без збереження точок. Призначена для повного згасання переходного процесу та притягнення траєкторії до стійкого атрактора.
* `n_samples` (тип `size_t`): Кількість послідовних точок фазового стану, які фіксуються у масиві після завершення перехідного процесу. Наприклад, для 4-циклу ці `200` точок будуть циклічно повторювати 4 значення.
* `n_lyapunov` (тип `size_t`): Кількість ітерацій для усереднення логарифмічної суми похідних при обчисленні показника Ляпунова `λ(r)`. Більші значення забезпечують високу гладкість кривої `λ(r)`.
* `bisection_tol` (тип `double`): Допустима абсолютна похибка за параметром `r` при чисельному локалізуванні точок фліп-біфуркацій `r_k`.
* `max_bisection_iters` (тип `size_t`): Максимально допустима кількість ітерацій при використанні методу ділення навпіл або методу секучих.

---

### 2.3. Сигнатура нелінійного відображення (`feigenbaum_map_fn` / `feigenbaum::MapFunction`)

Бібліотека є повністю універсальною і дозволяє аналізувати довільні однопараметричні відображення `x_{n+1} = f(x_n, r)`.

:::tabs
```c
/* Сигнатура функції відображення f(x, r) та її похідної */
typedef double (*feigenbaum_map_fn)(double x, double r, void *user_data);
typedef double (*feigenbaum_deriv_fn)(double x, double r, void *user_data);
```
```cpp
namespace feigenbaum {

using MapFunction = std::function<double(double x, double r)>;
using DerivativeFunction = std::function<double(double x, double r)>;

} // namespace feigenbaum
```
:::

Вказівник `user_data` (у C) або лямбда-замикання (у C++) дозволяють передавати у функцію відображення додаткові фізичні константи (наприклад, коефіцієнт згасання, нелінійну ємність або частоту зовнішнього збудження) без використання глобальних змінних.

---

### 2.4. Результат аналізу орбіти (`feigenbaum_orbit_res_t` / `feigenbaum::OrbitResult`)

:::tabs
```c
typedef struct {
    double r;                   /* Значення параметра r */
    double lyapunov_exponent;   /* Обчислений показник Ляпунова lambda(r) */
    size_t sample_count;        /* Кількість збережених точок у масиві samples */
    double *samples;            /* Масив точок атрактора розміру sample_count */
    bool is_chaotic;            /* Прапорець: true, якщо lambda > 0 (хаос) */
} feigenbaum_orbit_res_t;
```
```cpp
namespace feigenbaum {

struct OrbitResult {
    double r{0.0};
    double lyapunov_exponent{0.0};
    std::vector<double> samples{};
    bool is_chaotic{false};
};

} // namespace feigenbaum
```
:::

Структура містить повний спектральний та амплітудний портрет стану системи при зафіксованому значення `r`. Поле `is_chaotic` автоматично розраховується на основі знаку показника Ляпунова (`lyapunov_exponent > 0.001`).

---

### 2.5. Структура каскаду біфуркацій (`feigenbaum_cascade_res_t` / `feigenbaum::CascadeResult`)

:::tabs
```c
typedef struct {
    size_t detected_levels;     /* Кількість виявлених рівнів подвоєння (k = 1, 2, ..., K) */
    double *r_bifurcations;     /* Масив значень параметрів r_k розміру detected_levels */
    double *delta_estimates;    /* Масив оцінок delta_k розміру (detected_levels - 2) */
    double *alpha_estimates;    /* Масив оцінок alpha_k розміру (detected_levels - 1) */
    double r_infinity;          /* Екстрапольована точка накопичення r_inf */
    double delta_limit;         /* Гранична оцінка першої константи Фейгенбаума delta */
    double alpha_limit;         /* Гранична оцінка другої константи Фейгенбаума alpha */
} feigenbaum_cascade_res_t;
```
```cpp
namespace feigenbaum {

struct CascadeResult {
    std::size_t detected_levels{0};
    std::vector<double> r_bifurcations{};
    std::vector<double> delta_estimates{};
    std::vector<double> alpha_estimates{};
    double r_infinity{0.0};
    double delta_limit{0.0};
    double alpha_limit{0.0};
};

} // namespace feigenbaum
```
:::

Ця структура узагальнює глобальний чисельний аналіз каскаду. Вона містить:
* Масив точних значень параметрів біфуркацій `r_k`.
* Послідовність точкових оцінок константи Фейгенбаума `δ_k = (r_k - r_{k-1}) / (r_{k+1} - r_k)`.
* Послідовність точкових оцінок масштабної константи `α_k = d_k / d_{k+1}`.
* Граничне екстрапольоване значення `r_∞` та підсумкові оцінки границь `delta_limit` і `alpha_limit`.

---

## 3. Специфікація функцій public API

### 3.1. Ініціалізація конфігурації

:::tabs
```c
feigenbaum_status_t feigenbaum_config_default(feigenbaum_config_t *cfg);
```
```cpp
namespace feigenbaum {

[[nodiscard]] Config make_default_config() noexcept;

} // namespace feigenbaum
```
:::

* **Призначення:** Ініціалізує структуру конфігурації дефолтними оптимальними параметрами.
* **Вхідні параметри:** `cfg` — вказівник на структуру `feigenbaum_config_t` (в C) або функція створення `Config` (у C++).
* **Поведінка:** Заповнює всі поля структури рекомендованими значеннями (`r_min = 2.8`, `r_max = 4.0`, `r_steps = 1000`, `n_transient = 10000`, `n_samples = 200`, `n_lyapunov = 50000`, `bisection_tol = 1e-11`, `max_bisection_iters = 100`).
* **Повертає статус:** `FEIGENBAUM_SUCCESS` при успіху або `FEIGENBAUM_ERR_INVALID_ARG`, якщо `cfg == NULL`.

---

### 3.2. Обчислення орбіти та показника Ляпунова

:::tabs
```c
feigenbaum_status_t feigenbaum_analyze_r(
    feigenbaum_map_fn map_fn,
    feigenbaum_deriv_fn deriv_fn,
    double r,
    const feigenbaum_config_t *cfg,
    void *user_data,
    feigenbaum_orbit_res_t *out_res
);

void feigenbaum_free_orbit(feigenbaum_orbit_res_t *res);
```
```cpp
namespace feigenbaum {

[[nodiscard]] std::expected<OrbitResult, Status> analyze_parameter(
    MapFunction map_fn,
    DerivativeFunction deriv_fn,
    double r,
    const Config& cfg
) noexcept;

} // namespace feigenbaum
```
:::

* **Призначення:** Виконує чисельний аналіз нелінійного відображення для одного конкретного значення параметра `r`. Обчислює стійкий атрактор та показник Ляпунова.
* **Вхідні параметри:**
  * `map_fn`: Вказівник на функцію відображення `f(x, r)`. Не може бути `NULL`.
  * `deriv_fn`: Вказівник на функцію похідної `f'(x, r)`. Якщо `NULL`, використовується чисельне диференціювання `(f(x+h) - f(x-h))/(2h)` з `h = 1e-7`.
  * `r`: Значення керуючого параметра.
  * `cfg`: Вказівник на структуру конфігурації.
  * `user_data`: Користувальницький вказівник на додаткові дані.
  * `out_res`: Вихідна структура результату. Масив `out_res->samples` виділяється всередині функції.
* **Поведінка:** Спочатку ітерує відображення `cfg->n_transient` разів для виходу на атрактор. Після цього записує `cfg->n_samples` точок у виділений масив та обчислює суму логарифмів похідних протягом `cfg->n_lyapunov` кроків.
* **Вимоги до пам'яті:** У C-версії масив `out_res->samples` виділяється через `malloc` і має бути обов'язково звільнений викликом `feigenbaum_free_orbit(out_res)`. У C++ повертається об'єкт `std::expected` з автоматичним керуванням векторним ресурсом.
* **Повертає статус:** `FEIGENBAUM_SUCCESS`, `FEIGENBAUM_ERR_DIVERGENCE` або `FEIGENBAUM_ERR_NO_MEMORY`.

---

### 3.3. Детекція біфуркаційного каскаду та обчислення констант

:::tabs
```c
feigenbaum_status_t feigenbaum_compute_cascade(
    feigenbaum_map_fn map_fn,
    feigenbaum_deriv_fn deriv_fn,
    size_t target_levels,
    const feigenbaum_config_t *cfg,
    void *user_data,
    feigenbaum_cascade_res_t *out_cascade
);

void feigenbaum_free_cascade(feigenbaum_cascade_res_t *cascade);
```
```cpp
namespace feigenbaum {

[[nodiscard]] std::expected<CascadeResult, Status> compute_cascade(
    MapFunction map_fn,
    DerivativeFunction deriv_fn,
    std::size_t target_levels,
    const Config& cfg
) noexcept;

} // namespace feigenbaum
```
:::

* **Призначення:** Виконує автоматичний пошук послідовності точок біфуркацій подвоєння періоду `r_1, r_2, ..., r_K` до заданого рівня `target_levels`. Обчислює послідовності оцінок констант `δ_k` та `α_k`, а також здійснює екстраполяцію точкового граничного значення `r_∞`.
* **Вхідні параметри:**
  * `map_fn`, `deriv_fn`: Функція відображення та її похідна.
  * `target_levels`: Бажана кількість рівнів подвоєння (типово `K = 8...12`).
  * `cfg`: Конфігураційні параметри чисельного пошуку.
  * `user_data`: Додаткові параметри відображення.
  * `out_cascade`: Структура для запису підсумкових масивів та границь.
* **Особливості обчислювального алгоритму:** Для знаходження точки `r_k` бібліотека використовує чисельний алгоритм пошуку нулів для виразу мультиплікатора циклу `M(r) = d/dx [f^{(2^k)}(x*, r)] + 1 = 0`. Метод бісекції комбінується з методом секучих для досягнення точності `cfg->bisection_tol`.
* **Вимоги до пам'яті:** Пам'ять під масиви `r_bifurcations`, `delta_estimates` та `alpha_estimates` виділяється всередині функції і має бути звільнена через `feigenbaum_free_cascade`.
* **Повертає статус:** `FEIGENBAUM_SUCCESS` або `FEIGENBAUM_WARN_LOW_PRECISION`, якщо `target_levels > 12`.

---

## 4. Таблиця вбудованих моделей нелінійних відображень

Бібліотека містить вбудовані реалізації класичних канонічних відображень, доступні через допоміжні селектори та зумовлені функції:

| Ідентифікатор моделі | Математична формула `f(x, r)` | Область визначення `x` | Область параметрів `r` | Клас універсальності |
| :--- | :--- | :--- | :--- | :--- |
| `FEIGENBAUM_MAP_LOGISTIC` | `r · x · (1 - x)` | `[0, 1]` | `[0, 4.0]` | Параболічний (квадратичний) |
| `FEIGENBAUM_MAP_SINE` | `r · sin(π · x)` | `[0, 1]` | `[0, 1.0]` | Параболічний (квадратичний) |
| `FEIGENBAUM_MAP_QUADRATIC` | `1 - a · x²` | `[-1, 1]` | `[0, 2.0]` | Параболічний (квадратичний) |
| `FEIGENBAUM_MAP_QUARTIC` | `1 - a · x⁴` | `[-1, 1]` | `[0, 2.0]` | Четвертого степеня (`δ ≈ 7.2846`) |

---

## 5. Приклад інтеграції бібліотеки у C/C++ проєкт

:::tabs
```c
/* main.c - Приклад інтеграції мовою C */
#include <stdio.h>
#include <math.h>
#include "feigenbaum/feigenbaum.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static double sine_map(double x, double r, void *user_data) {
    (void)user_data;
    return r * sin(M_PI * x);
}

static double sine_deriv(double x, double r, void *user_data) {
    (void)user_data;
    return r * M_PI * cos(M_PI * x);
}

int main(void) {
    feigenbaum_config_t cfg;
    feigenbaum_config_default(&cfg);
    cfg.r_min = 0.7;
    cfg.r_max = 1.0;

    feigenbaum_cascade_res_t cascade;
    feigenbaum_status_t status = feigenbaum_compute_cascade(
        sine_map, sine_deriv, 8, &cfg, NULL, &cascade
    );

    if (status >= 0) {
        printf("--- Результати C-API для Синус-відображення ---\n");
        printf("Виявлено рівнів біфуркацій: %zu\n", cascade.detected_levels);
        for (size_t i = 0; i < cascade.detected_levels; ++i) {
            printf("  r_%zu = %.9f\n", i + 1, cascade.r_bifurcations[i]);
        }
        printf("\nОцінка delta: %.7f\n", cascade.delta_limit);
        printf("Оцінка alpha: %.7f\n", cascade.alpha_limit);

        feigenbaum_free_cascade(&cascade);
    }
    return 0;
}
```
```cpp
// main.cpp - Приклад інтеграції мовою C++20
#include <iostream>
#include <cmath>
#include <format>
#include "feigenbaum/feigenbaum.hpp"

int main() {
    auto sine_map = [](double x, double r) { return r * std::sin(std::numbers::pi * x); };
    auto sine_deriv = [](double x, double r) { return r * std::numbers::pi * std::cos(std::numbers::pi * x); };

    feigenbaum::Config cfg = feigenbaum::make_default_config();
    cfg.r_min = 0.7;
    cfg.r_max = 1.0;

    auto result = feigenbaum::compute_cascade(sine_map, sine_deriv, 8, cfg);

    if (result) {
        const auto& cascade = *result;
        std::cout << "--- Результати C++20 API для Синус-відображення ---\n";
        std::cout << std::format("Виявлено рівнів: {}\n", cascade.detected_levels);
        for (std::size_t i = 0; i < cascade.detected_levels; ++i) {
            std::cout << std::format("  r_{} = {:.9f}\n", i + 1, cascade.r_bifurcations[i]);
        }
        std::cout << std::format("\nОцінка delta: {:.7f}\n", cascade.delta_limit);
        std::cout << std::format("Оцінка alpha: {:.7f}\n", cascade.alpha_limit);
    }
    return 0;
}
```
:::

---

## 6. Рекомендації з продуктивності та налаштування точності

При використанні бібліотеки `libfeigenbaum` для високоточних наукових обчислень рекомендується враховувати наступні практичні поради:
1. **Забезпечення аналітичної похідної:** Завжди передавайте аналітичну функцію похідної `deriv_fn`. Використання чисельного диференціювання через скінченні різниці уповільнює обчислення показника Ляпунова приблизно удвічі та додає накопичену похибку округлення при `n_lyapunov > 10⁵`.
2. **Паралельне сканування:** Для побудови високроздільних біфуркаційних діаграм розділяйте діапазон `[r_min, r_max]` на незалежні субінтервали та викликайте `analyze_parameter` у паралельних потоках.
3. **Оптимізація компіляції:** При збірці бібліотеки використовуйте прапорці компілятора `-O3 -march=native -ffast-math` для векторної автовекторизації цикла обчислення логарифмів.
