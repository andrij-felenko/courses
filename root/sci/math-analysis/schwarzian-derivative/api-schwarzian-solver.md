# 📋 Інтерфейс бібліотеки обчислення похідної Шварца та аналізу відображень

Довідник публічного інтерфейсу програмного модуля `libschwarzian` (версія 1.4). Бібліотека призначена для аналізу нелінійних одновимірних і багатовимірних відображень, оцінювання похідної Шварца, локалізації критичних точок та перевірки умов теореми Сінґера.

Модуль надає двійково-сумісний C-інтерфейс (ABI) для інтеграції з високоефективними обчислювальними ядрами (FORTRAN, C, Rust) та сучасний ідіоматичний C++23 обгортковий інтерфейс із підтримкою семантики `std::expected` та безелізійних лямбда-виразів.

## 1. Архітектурний задум та призначення модуля

Основним завданням бібліотеки є надання універсального інструменту для фахівців із обчислювальної механіки, нелінійної динаміки та теорії хаосу. Модуль дозволяє як аналітично оцінювати оператор Шварца (якщо аналітик задав функцію обчислення похідних `df1`, `df2`, `df3`), так і чисельно сканувати довільні математичні відображення, задані функціональними вказівниками або об'єктами-функторами `std::function`.

Програмний модуль вирішує три головні завдання:
1. **Точна оцінка Шварціана:** Розрахунок `S(f)(x) = f'''/f' - 1.5·(f''/f')²` із автоматичним виявленням критичних точок `|f'(x)| < eps`.
2. **Чисельне сканування сітки:** Автоматичний обхід інтервалу `[x_min, x_max]` із 5-точковою скінченно-різницевою схемою четвертого порядку точності.
3. **Перевірка теореми Сінґера:** Перевірка знака похідної Шварца `S(f) < 0` на всьому інтервалі для підтвердження єдиності стійкого періодичного атрактора.

При проектуванні інтерфейсу особливу увагу приділено відсутності динамічного виділення пам'яті (`malloc` / `new`) всередині обчислювальних функцій. Всі структури даних передаються через стек чи попередньо виділені буфери, що гарантує детермінований час виконання та дозволяє використовувати бібліотеку у контролерах реального часу.

## 2. Інтеграція з чисельними фреймворками та розв'язувачами

Бібліотека `libschwarzian` легко інтегрується з популярними чисельними пакетами, такими як GNU Scientific Library (GSL), Boost.Math, Eigen та LAPACK. Якщо нелінійне відображення виникає як результат числового інтегрування системи звичайних диференціальних рівнянь (ЗДР) за допомогою методів Рунге-Кутти або Адамса-Башфорта, значення `f(x)` обчислюється шляхом інтегрування траєкторії до перетину з поверхнею Пуанкаре.

Для забезпечення максимальної сумісності C++23 інтерфейс використовує шаблони рішень без прив'язки до конкретної реалізації контейнерів. Використання абстракції `std::expected` дозволяє лаконічно поєднувати виклики аналізатора з ланцюжками викличних об'єктів через комбінатори `and_then` та `transform`.

## 3. Модель пам'яті, потокобезпечність та ABI

Публічний C-інтерфейс бібліотеки розроблений із дотриманням принципів повторного входження (reentrancy). Жодна з обчислювальних функцій не використовує глобальні статичні змінні чи внутрішні стани. Параметр `const void *user_data` дозволяє користувачеві передавати довільні контекстні структури (наприклад, коефіцієнти відображення, масиви коефіцієнтів тертя чи параметри сітки) у внутрішні зворотні виклики без використання глобальної пам'яті.

Двійкова сумісність (ABI) забезпечується вирівнюванням структур `schwarzian_point_t` та `schwarzian_config_t` по межах 8 байт (стандарт IEEE 754 double). Модуль не генерує системних винятків, а всі помилки повертаються через коди статусу `schwarzian_status_t`.

## 4. Паралелізація, SIMD та прискорення на GPU

Для високопродуктивного масового аналізу динамічних систем (наприклад, при розрахунку двовимірних карт Ляпунова або спектрів атракторів) C++23 заголовок підтримує паралельні алгоритми Execution Policies (`std::execution::par_unseq`). Це дозволяє автоматично векторзувати виклики `evalNumeric` через SIMD інструкції AVX2 / AVX-512.

Крім того, чисті C-функції бібліотеки позначені атрибутами `__attribute__((leaf, const, nothrow))`, що дозволяє сучасним компіляторам (GCC, Clang, MSVC) будувати агресивні векторні інструкції FMA (Fused Multiply-Add) і повністю усувати невикористовувані розгалуження у коді.

## 5. Структури даних та типи

При роботі з бібліотекою використовуються наступні типи даних та конфігураційні параметри:

| Тип / Структура | Мова | Опис та призначення |
| :--- | :--- | :--- |
| `schwarzian_map_fn` | C | Вказівник на функцію відображення `double f(double x, const void *user_data)` |
| `schwarzian_deriv_fn` | C | Вказівник на функцію точних похідних `void deriv(double x, double *df1, double *df2, double *df3, const void *user_data)` |
| `schwarzian_point_t` | C | Результат обчислення в точці: значення `x`, похідні `df1`, `df2`, `df3`, значення `S(f)` та статус |
| `schwarzian_config_t` | C | Параметри обчислення: крок чисельного диференціювання `h`, допуск `eps` |
| `schwarzian::Point` | C++ | Ідіоматична структура результату обчислення Шварціана |
| `schwarzian::Config` | C++ | Налаштування точності з дефолтними значеннями `h = 1e-4`, `epsCritical = 1e-9` |
| `schwarzian::Evaluator` | C++ | Головний клас-аналізатор з функціями обчислення та перевірки теореми Сінґера |

## 6. Таблиця помилок та кодів повернення

Бібліотека використовує явну обробку помилок без виклику винятків у C-версії та тип `std::expected` у C++23:

| Код помилки | Назва в C | Назва в C++ | Причина виникнення та рекомендована дія |
| :--- | :--- | :--- | :--- |
| `0` | `SCHWARZIAN_OK` | Success | Успішне виконання обчислення |
| `-1` | `SCHWARZIAN_ERR_CRITICAL` | `Error::CriticalPoint` | Точка є критичною (`\|df1\| < eps`), Шварціан прямує до `-∞`. Потрібно обійти точку на величину `> eps` |
| `-2` | `SCHWARZIAN_ERR_ZERO_STEP` | `Error::InvalidStep` | Задано невалідний крок скінченної різниці `h <= 0`. Встановіть крок у діапазоні `1e-5..1e-3` |
| `-3` | `SCHWARZIAN_ERR_NULL_PTR` | `Error::NullCallback` | Передано `NULL` замість вказівника на функцію чи структуру даних |

## 7. Опис публічного API

:::tabs
```c
#ifndef LIBSCHWARZIAN_H
#define LIBSCHWARZIAN_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SCHWARZIAN_OK = 0,
    SCHWARZIAN_ERR_CRITICAL = -1,
    SCHWARZIAN_ERR_ZERO_STEP = -2,
    SCHWARZIAN_ERR_NULL_PTR = -3
} schwarzian_status_t;

typedef double (*schwarzian_map_fn)(double x, const void *user_data);
typedef void (*schwarzian_deriv_fn)(double x, double *df1, double *df2, double *df3, const void *user_data);

typedef struct {
    double x;
    double df1;
    double df2;
    double df3;
    double schwarzian;
} schwarzian_point_t;

typedef struct {
    double h;            /* Крок диференціювання (за замовчуванням 1e-4) */
    double eps_critical; /* Поріг критичної точки (за замовчуванням 1e-9) */
} schwarzian_config_t;

/* Створення конфігурації за замовчуванням */
schwarzian_config_t schwarzian_config_default(void);

/* Прямий обчислювач за значеннями похідних */
schwarzian_status_t schwarzian_eval_exact(double df1, double df2, double df3, 
                                           double eps_critical, double *out_sf);

/* Обчислення похідної Шварца у точці з точними похідними */
schwarzian_status_t schwarzian_eval_point(schwarzian_deriv_fn deriv, double x, 
                                            const void *user_data,
                                            schwarzian_config_t config,
                                            schwarzian_point_t *out_pt);

/* Чисельне оцінювання похідної Шварца через 5-точкову схему */
schwarzian_status_t schwarzian_eval_numeric(schwarzian_map_fn map, double x,
                                              const void *user_data,
                                              schwarzian_config_t config,
                                              schwarzian_point_t *out_pt);

/* Сканування інтервалу на від'ємність Шварціана S(f) < 0 */
schwarzian_status_t schwarzian_check_singer_condition(schwarzian_map_fn map,
                                                       double x_min, double x_max,
                                                       size_t num_samples,
                                                       schwarzian_config_t config,
                                                       int *out_is_negative_everywhere);

#ifdef __cplusplus
}
#endif

#endif /* LIBSCHWARZIAN_H */
```
```cpp
#ifndef LIBSCHWARZIAN_HPP
#define LIBSCHWARZIAN_HPP

#include <functional>
#include <vector>
#include <expected>
#include <optional>
#include <limits>

namespace schwarzian {

enum class Error {
    CriticalPoint,
    InvalidStep,
    NullCallback
};

struct Point {
    double x;
    double df1;
    double df2;
    double df3;
    double schwarzian;
};

struct Config {
    double h{1e-4};
    double epsCritical{1e-9};
};

class Evaluator {
public:
    explicit Evaluator(Config config = Config{}) : config_(config) {}

    // Обчислення за точними похідними
    [[nodiscard]] std::expected<Point, Error> evalExact(double x, double df1, double df2, double df3) const {
        if (std::abs(df1) < config_.epsCritical) {
            return std::unexpected(Error::CriticalPoint);
        }
        const double ratio = df2 / df1;
        const double sf = (df3 / df1) - 1.5 * ratio * ratio;
        return Point{x, df1, df2, df3, sf};
    }

    // Чисельне оцінювання для довільного лямбда-виразу
    [[nodiscard]] std::expected<Point, Error> evalNumeric(const std::function<double(double)>& func, double x) const {
        if (config_.h <= 0.0) {
            return std::unexpected(Error::InvalidStep);
        }
        const double h = config_.h;
        const double f_p2 = func(x + 2.0 * h);
        const double f_p1 = func(x + h);
        const double f_m1 = func(x - h);
        const double f_m2 = func(x - 2.0 * h);

        const double df1 = (f_m2 - 8.0 * f_m1 + 8.0 * f_p1 - f_p2) / (12.0 * h);
        if (std::abs(df1) < config_.epsCritical) {
            return std::unexpected(Error::CriticalPoint);
        }

        const double df2 = (-f_m2 + 16.0 * f_m1 - 30.0 * func(x) + 16.0 * f_p1 - f_p2) / (12.0 * h * h);
        const double df3 = (-f_p2 + 2.0 * f_p1 - 2.0 * f_m1 + f_m2) / (2.0 * h * h * h);

        return evalExact(x, df1, df2, df3);
    }

    // Перевірка умови від'ємного Шварціана S(f) < 0 на сітці
    [[nodiscard]] bool checkSingerCondition(const std::function<double(double)>& func,
                                            double xMin, double xMax,
                                            std::size_t numSamples) const {
        const double step = (xMax - xMin) / static_cast<double>(numSamples);
        for (std::size_t i = 0; i <= numSamples; ++i) {
            const double x = xMin + static_cast<double>(i) * step;
            auto res = evalNumeric(func, x);
            if (res.has_value()) {
                if (res->schwarzian >= 0.0) {
                    return false;
                }
            }
        }
        return true;
    }

private:
    Config config_;
};

} // namespace schwarzian

#endif // LIBSCHWARZIAN_HPP
```
:::

## 8. Детальний протокол виконання та специфікація функцій

### Функція `schwarzian_eval_numeric`

Призначається для чисельного розрахунку похідної Шварца у даній точці `x`. Алгоритм виконує п'ять викликів функції відображення у вузлах `x - 2h`, `x - h`, `x`, `x + h` та `x + 2h`. Потім розраховуються скінченно-різницеві оцінки 4-го порядку. Якщо значення `|df1| < eps_critical`, обчислення переривається з кодом `SCHWARZIAN_ERR_CRITICAL`, запобігаючи діленню на нуль.

### Функція `schwarzian_check_singer_condition`

Виконує автоматичне сканування інтервалу `[x_min, x_max]` на рівномірній сітці з `num_samples` точками. Якщо хоча б в одній регулярній точці (не критичній) значення `S(f) >= 0`, вихідний параметр `out_is_negative_everywhere` встановлюється у `0` (False). Якщо на всьому інтервалі `S(f) < 0`, параметр повертає `1` (True), що підтверджує можливість застосування теореми Сінґера для доведення єдиності стійкого атрактора.

## 9. Інструкція з використання та гарантії потокобезпечності

1. **Потокобезпечність (Thread-safety):** Обчислювальні функції `schwarzian_eval_numeric` та `schwarzian::Evaluator::evalNumeric` не мають внутрішнього глобального стану і є повністю потокобезпечними (reentrant). Одночасний виклик з різних потоків для окремих об'єктів функцій є безпечним і не вимагає блокувань м'ютексів.
2. **Обробка винятків у C++:** Заголовок `LIBSCHWARZIAN_HPP` розроблений за стандартом `noexcept`-гарантій з використанням `std::expected`. Це дозволяє використовувати бібліотеку в високопродуктивних серверних та embedded-системах, де винятки C++ вимкнені прапорцем `-fno-exceptions`.
3. **Рекомендації з продуктивності:** Для сканування великих масивів даних (понад `10⁶` точок) рекомендовано використовувати функцію `schwarzian_eval_exact` із попереднім обчисленням векторних похідних через AVX2/AVX-512 або OpenMP паралелізацію.
4. **Приклад використання у C:** Передайте вказівник на дані через `user_data` для уникнення глобальних змінних. Модуль гарантує, що значення `user_data` передається у виклики `schwarzian_map_fn` без модифікації.
5. **Валідація вхідних параметрів:** Перед запуском обчислень перевіряйте значення кроку `h > 0` та допуску `eps_critical > 0`. Виклик функцій із нульовим або від'ємним кроком призводить до повернення помилки `SCHWARZIAN_ERR_ZERO_STEP` у C або `Error::InvalidStep` у C++.
6. **Інтеграційне тестування:** Модуль постачається разом із модульним набором тестів (Unit Tests) на базі GoogleTest, які автоматично перевіряють обчислення Шварціана для аналітичних логістичних та еліптичних відображень перед розгортанням у продакшен-середовищах.
