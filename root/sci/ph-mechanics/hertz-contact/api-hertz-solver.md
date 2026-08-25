# 📋 Інтерфейс та довідник функцій бібліотеки контактного аналізу

Ця довідкова вставка містить специфікацію програмного інтерфейсу (API) бібліотеки розрахунку герцівських напружень для сферичних і циліндричних контактів у мовах C та C++.

## Загальні відомості про контракт інтерфейсу

Бібліотека аналізу контактних напружень надає уніфікований та розширюваний програмний контракт (API) для обчислення геометричних деформацій, розподілу тиску та складових тензора напружень у суцільних пружних середовищах. Бібліотека призначена для використання у складі обчислювальних модулів систем автоматизованого інженерного аналізу (САПР/CAD/CAE), алгоритмах оцінки втомного ресурсу та зносу підшипників качення, зубчастих редукторів, кулачкових механізмів, залізничного колесно-рейкового транспорту, а також при розшифровці результатів наноіндентування та атомно-силової мікроскопії.

### Моделі геометрії контактної взаємодії
- `SPHERICAL` (точковий контакт): аналіз взаємодії двох сферичних тіл або сфери з площиною/циліндром у формі кругової чи еліптичної плями контакту.
- `CYLINDRICAL` (лінійний контакт): аналіз взаємодії двох паралельних циліндрів або циліндра з площиною у формі прямокутного майданчика.

### Система одиниць вимірювання та фізичні допуски
Усі функції та структури даних API приймають і повертають значення виключно у базових одиницях міжнародної системи СІ (SI):
- Нормальна стискальна сила `F`: Ньютони (Н)
- Геометричні розміри, радіуси `R1`, `R2`, `a`, `b`, глибина `δ`, `z`: Метьри (м)
- Модулі пружності `E`, `E*` та тиск/напруження `p₀`, `p_сер`, `σ`, `τ`: Паскалі (Па)
- Безрозмірні коефіцієнти Пуассона `ν`: дробові числа у межах `[0.0, 0.5)`

## Специфікація типів даних та структур

У таблиці нижче деталізовано структури даних, які формують контракт бібліотеки розрахунку герцівських напружень.

| Структурний тип / Клас | Призначення у системі | Основні поля / Члени структури |
| :--- | :--- | :--- |
| `hertz_material_t` / `hertz::Material` | Фізичні властивості ізотропного матеріалу | `E` (модуль Юнга, Па), `nu` (коефіцієнт Пуассона) |
| `hertz_sphere_result_t` / `hertz::SphereResult` | Результати розрахунку сферичного контакту | `R_star`, `E_star`, `a`, `delta`, `p0`, `p_mean`, `area`, `z_peak`, `tau_max` |
| `hertz_cylinder_result_t` / `hertz::CylinderResult` | Результати розрахунку циліндричного контакту | `R_star`, `E_star`, `b`, `delta`, `p0`, `p_mean`, `area` |
| `hertz_stress_point_t` / `hertz::StressPoint` | Точка зрізу стану напруження по глибині | `z`, `z_over_a`, `sigma_z`, `sigma_x`, `tau_max` |
| `hertz_error_t` / `hertz::ErrorCode` | Коди помилок виконання та перевірок | `HERTZ_SUCCESS`, `HERTZ_ERR_INVALID_PARAM`, `HERTZ_ERR_GEOMETRY_SINGULAR` |

## Детальний опис функціонального контракту

### 1. Обчислення зведеного радіуса кривини `hertz_calc_r_star`
- **Опис**: обчислює еквівалентний (зведений) радіус кривини `R*` двох викривлених поверхонь за класичною формулою `1/R* = 1/R₁ + 1/R₂`.
- **Вхідні аргументи**:
  - `R1` (double): радіус кривини першого тіла в метрах (`R1 > 0`).
  - `R2` (double): радіус кривини другого тіла в метрах (`R2 > 0`). Для пласкої поверхні передається значення `INFINITY` або велике число `> 1e8`.
- **Значення, що повертається**: зведений радіус `R*` у метрах. Якщо один з аргументів є некоректним (`R1 <= 0` або `R2 <= 0`), функція повертає `0.0`.

### 2. Обчислення зведеного модуля пружності `hertz_calc_e_star`
- **Опис**: обчислює ефективний модуль пружності контакту двох матеріалів за формулою `1/E* = (1 - ν₁²)/E₁ + (1 - ν₂²)/E₂`.
- **Вхідні аргументи**:
  - `mat1` (`hertz_material_t`): структура матеріалу першого тіла.
  - `mat2` (`hertz_material_t`): структура матеріалу другого тіла.
- **Значення, що повертається**: зведений модуль `E*` у Паскалях. Повертає `0.0`, якщо модуль Юнга `E <= 0` або коефіцієнт Пуассона `ν` лежить поза межами `[0, 0.5)`.

### 3. Солвер сферичного контакту `hertz_solve_sphere`
- **Опис**: проводить повний чисельний розрахунок точкового пружного контакту двох сфер або сфери з площиною.
- **Аргументи**:
  - `F` (double): нормальна сила стискання у Ньютонах (`F > 0`).
  - `R1`, `R2` (double): радіуси кривини в метрах.
  - `mat1`, `mat2`: фізичні властивості матеріалів.
  - `out` (вказівник/посилання): об'єкт структури `hertz_sphere_result_t` для запису обчислених результатів.
- **Код повернення**: `HERTZ_SUCCESS` (0) при успішному розрахунку або відповідний від'ємний код помилки.

### 4. Солвер циліндричного контакту `hertz_solve_cylinder`
- **Опис**: проводить розрахунок лінійного контакту двох паралельних циліндрів довжиною `L`.
- **Аргументи**:
  - `F` (double): нормальна сила стискання (Н).
  - `L` (double): активна довжина контакту циліндрів у метрах (`L > 0`).
  - `R1`, `R2` (double): радіуси циліндрів (м).
  - `mat1`, `mat2`: властивості матеріалів.
  - `out`: вказівник на вихідну структуру `hertz_cylinder_result_t`.

### 5. Розрахунок профілю напружень по глибині `hertz_calc_stress_profile`
- **Опис**: розраховує дискретний профіль напружень `σ_z`, `σ_x` та `τ_макс` вздовж осі `z` під центром сферичного контакту.
- **Аргументи**:
  - `sph`: розрахована структура результатів сферичного контакту.
  - `z_max` (double): максимальна глибина аналізу у метрах (рекомендовано `2.0 * a`).
  - `steps` (int): кількість рівновіддалених кроків розрахунку.
  - `out_arr` (масив/вектор): вихідний масив точок напружень.

## Докладна специфікація полів результатів

Для правильної інтерпретації результатів аналізу нижче наведено фізичний зміст кожного поля вихідних структур:

- `a` (м): радіус кругової плями контакту, утвореної під дією сили `F`.
- `b` (м): півширина прямокутного майданчика контакту у випадку циліндрів.
- `delta` (м): абсолютне пружне зближення геометричних центрів двох тіл (глибина втискання).
- `p0` (Па): найбільший нормальний тиск стискування, що діє точно у центрі плями контакту (`r = 0`).
- `p_mean` (Па): середній тиск по площі контакту, що дорівнює `F / A`. Для сфери `p0 = 1.5 * p_mean`, а для циліндра `p0 = (4 / π) * p_mean`.
- `area` (м²): площа деформованого майданчика контакту.
- `z_peak` (м): глибина під поверхнею контакту, на якій максимальне зсувне напруження досягає свого екстремуму `τ_макс`. Для сталевих деталей `z_пік ≈ 0.481 a`.
- `tau_max` (Па): максимальне підповерхневе зсувне напруження, яке порівнюється з межею плинності матеріалу при зсуві `τ_пласт = σ_y / 2`.

## Політика обробки помилок та потокбезпечність

1. **Багатопотокова безпека (Thread Safety)**:
   Усі функції API є строго чисто безстанновими (stateless) і не використовують глобальних змінних, статичних буферів чи викликів `malloc`. Вони є повністю потокбезпечними (thread-safe) та підтримують паралельні розрахунки у сумісних багатопотокових середовищах (OpenMP, std::thread, POSIX threads).
2. **Гарантії відсутності винятків у C++**:
   Усі функції C++ API позначені специфікатором `noexcept` та повертають об'єкти `std::expected<T, std::error_code>`. Це унеможливлює витоки пам'яті та розгортання стеку під час роботи у реальному часі (Real-Time systems, утиліти ядра).

## Заголовочні файли та інтерфейсні оголошення

:::tabs
```c
/* 
 * hertz_contact.h — C API для розрахунку контакту Герца
 */

#ifndef HERTZ_CONTACT_H
#define HERTZ_CONTACT_H

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання */
typedef enum {
    HERTZ_SUCCESS = 0,
    HERTZ_ERR_INVALID_PARAM = -1,
    HERTZ_ERR_GEOMETRY_SINGULAR = -2,
    HERTZ_ERR_MATERIAL_OUT_OF_BOUNDS = -3,
    HERTZ_ERR_NULL_POINTER = -4
} hertz_error_t;

/* Фізичні властивості ізотропного матеріалу */
typedef struct {
    double E;    /* Модуль пружності першого роду / модуль Юнга (Па) */
    double nu;   /* Коефіцієнт поперечної деформації / Пуассона (0 <= nu < 0.5) */
} hertz_material_t;

/* Результати розрахунку точкового (сферичного) контакту */
typedef struct {
    double R_star;   /* Зведений радіус кривини (м) */
    double E_star;   /* Зведений модуль пружності (Па) */
    double a;        /* Радіус кругової плями контакту (м) */
    double delta;    /* Глибина втискання / сумарне зближення центрів (м) */
    double p0;       /* Максимальний контактний тиск у центрі (Па) */
    double p_mean;   /* Середній контактний тиск (Па) */
    double area;     /* Площа поверхні контакту (м²) */
    double z_peak;   /* Глибина розташування піку зсувного напруження (м) */
    double tau_max;  /* Значення максимального зсувного напруження (Па) */
} hertz_sphere_result_t;

/* Результати розрахунку лінійного (циліндричного) контакту */
typedef struct {
    double R_star;   /* Зведений радіус кривини (м) */
    double E_star;   /* Зведений модуль пружності (Па) */
    double b;        /* Півширина прямокутної плями контакту (м) */
    double delta;    /* Зближення поверхонь циліндрів (м) */
    double p0;       /* Максимальний тиск по осьовій лінії (Па) */
    double p_mean;   /* Середній тиск по площі прямокутника (Па) */
    double area;     /* Площа поверхні контакту 2b * L (м²) */
} hertz_cylinder_result_t;

/* Точка зрізу поля напружень по глибині z */
typedef struct {
    double z;          /* Глибина під поверхнею контакту (м) */
    double z_over_a;   /* Безрозмірна глибина z / a */
    double sigma_z;    /* Головне осьове стискальне напруження (Па) */
    double sigma_x;    /* Головне радіальне стискальне напруження (Па) */
    double tau_max;    /* Максимальне зсувне напруження (Па) */
} hertz_stress_point_t;

/* 
 * Обчислення зведеного радіуса кривини: 1/R* = 1/R1 + 1/R2
 * Приймає радіуси R1 та R2 (м). Для площини передається INFINITY або велике число.
 * Повертає R* (м) або 0.0 при помилці.
 */
double hertz_calc_r_star(double R1, double R2);

/* 
 * Обчислення зведеного модуля пружності: 1/E* = (1-nu1^2)/E1 + (1-nu2^2)/E2
 * Повертає E* (Па) або 0.0 при некоректних матеріалах.
 */
double hertz_calc_e_star(hertz_material_t mat1, hertz_material_t mat2);

/*
 * Солвер сферичного герцівського контакту
 * Параметри:
 *   F    - нормальна сила стискання (Н), має бути > 0
 *   R1   - радіус кривини першого тіла (м)
 *   R2   - радіус кривини другого тіла (м)
 *   mat1 - матеріальні властивості першого тіла
 *   mat2 - матеріальні властивості другого тіла
 *   out  - вказівник на структуру результатів
 * Повертає HERTZ_SUCCESS (0) або код помилки hertz_error_t.
 */
hertz_error_t hertz_solve_sphere(double F, double R1, double R2,
                                 hertz_material_t mat1, hertz_material_t mat2,
                                 hertz_sphere_result_t *out);

/*
 * Солвер циліндричного герцівського контакту
 * Параметри:
 *   F    - нормальна сила стискання (Н)
 *   L    - активна довжина контакту циліндрів (м)
 *   R1, R2 - радіуси кривини циліндрів (м)
 *   mat1, mat2 - властивості матеріалів
 *   out  - вказівник на результат
 */
hertz_error_t hertz_solve_cylinder(double F, double L, double R1, double R2,
                                   hertz_material_t mat1, hertz_material_t mat2,
                                   hertz_cylinder_result_t *out);

/*
 * Обчислення профілю напружень вздовж осі z під центром сферичного контакту
 * Параметри:
 *   sph     - результати сферичного контакту
 *   z_max   - максимальна глибина розрахунку (м)
 *   steps   - кількість кроків дискретизації
 *   out_arr - вихідний масив розміром (steps + 1)
 */
hertz_error_t hertz_calc_stress_profile(const hertz_sphere_result_t *sph,
                                        double z_max, int steps,
                                        hertz_stress_point_t *out_arr);

#ifdef __cplusplus
}
#endif

#endif /* HERTZ_CONTACT_H */
```
```cpp
// 
// hertz_contact.hpp — C++20 API для розрахунку контакту Герца
//

#ifndef HERTZ_CONTACT_HPP
#define HERTZ_CONTACT_HPP

#include <cmath>
#include <vector>
#include <expected>
#include <span>
#include <numbers>
#include <system_error>

namespace hertz {

/* Фізичні властивості матеріалу */
struct Material {
    double E;    // Модуль Юнга (Па)
    double nu;   // Коефіцієнт Пуассона
};

/* Коди помилок виконання */
enum class ErrorCode {
    InvalidForce = 1,
    InvalidGeometry,
    InvalidMaterial,
    NullBuffer
};

/* Клас помилки для std::expected */
class ContactErrorCategory : public std::error_category {
public:
    [[nodiscard]] const char* name() const noexcept override { return "hertz_contact"; }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::InvalidForce: return "Сила стискання має бути строго більшою за нуль";
            case ErrorCode::InvalidGeometry: return "Некоректний або від'ємний радіус кривини";
            case ErrorCode::InvalidMaterial: return "Модуль пружності має бути > 0, коефіцієнт Пуассона у межах [0, 0.5)";
            case ErrorCode::NullBuffer: return "Передано нульовий буфер для результатів";
            default: return "Невідома помилка контактної взаємодії";
        }
    }
};

[[nodiscard]] inline const std::error_category& error_category() noexcept {
    static ContactErrorCategory cat;
    return cat;
}

[[nodiscard]] inline std::error_code make_error_code(ErrorCode e) noexcept {
    return {static_cast<int>(e), error_category()};
}

/* Результати сферичного контакту */
struct SphereResult {
    double R_star;   // Зведений радіус кривини (м)
    double E_star;   // Зведений модуль пружності (Па)
    double a;        // Радіус плями контакту (м)
    double delta;    // Глибина втискання (м)
    double p0;       // Піковий тиск (Па)
    double p_mean;   // Середній тиск (Па)
    double area;     // Площа контакту (м²)
    double z_peak;   // Глибина піку зсуву (м)
    double tau_max;  // Максимальний зсув (Па)
};

/* Результати циліндричного контакту */
struct CylinderResult {
    double R_star;
    double E_star;
    double b;
    double delta;
    double p0;
    double p_mean;   
    double area;     
};

/* Точка профілю напружень */
struct StressPoint {
    double z;          // Глибина (м)
    double z_over_a;   // Безрозмірна глибина z / a
    double sigma_z;    // Осьове напруження (Па)
    double sigma_x;    // Радіальне напруження (Па)
    double tau_max;    // Максимальний зсув (Па)
};

/* Інтерфейсний клас солвера контакту Герца */
class ContactSolver {
public:
    ContactSolver() = delete;

    [[nodiscard]] static constexpr double calc_r_star(double R1, double R2) noexcept {
        return (R1 > 0.0 && R2 > 0.0) ? (R1 * R2) / (R1 + R2) : 0.0;
    }

    [[nodiscard]] static constexpr double calc_e_star(const Material& m1, const Material& m2) noexcept {
        if (m1.E <= 0.0 || m2.E <= 0.0 || m1.nu < 0.0 || m1.nu >= 0.5 || m2.nu < 0.0 || m2.nu >= 0.5) {
            return 0.0;
        }
        const double inv1 = (1.0 - m1.nu * m1.nu) / m1.E;
        const double inv2 = (1.0 - m2.nu * m2.nu) / m2.E;
        return 1.0 / (inv1 + inv2);
    }

    /* Розв'язок для сферичного контакту */
    [[nodiscard]] static std::expected<SphereResult, std::error_code>
    solve_sphere(double F, double R1, double R2, const Material& m1, const Material& m2) noexcept {
        if (F <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidForce));

        const double R_star = calc_r_star(R1, R2);
        const double E_star = calc_e_star(m1, m2);
        if (R_star <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidGeometry));
        if (E_star <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidMaterial));

        SphereResult res{};
        res.R_star = R_star;
        res.E_star = E_star;
        res.a = std::cbrt((3.0 * F * R_star) / (4.0 * E_star));
        res.delta = (res.a * res.a) / R_star;
        res.area = std::numbers::pi * res.a * res.a;
        res.p0 = (3.0 * F) / (2.0 * res.area);
        res.p_mean = F / res.area;
        res.z_peak = 0.481 * res.a;
        res.tau_max = 0.310 * res.p0;

        return res;
    }

    /* Розв'язок для циліндричного контакту */
    [[nodiscard]] static std::expected<CylinderResult, std::error_code>
    solve_cylinder(double F, double L, double R1, double R2, const Material& m1, const Material& m2) noexcept {
        if (F <= 0.0 || L <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidForce));

        const double R_star = calc_r_star(R1, R2);
        const double E_star = calc_e_star(m1, m2);
        if (R_star <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidGeometry));
        if (E_star <= 0.0) return std::unexpected(make_error_code(ErrorCode::InvalidMaterial));

        CylinderResult res{};
        res.R_star = R_star;
        res.E_star = E_star;
        res.b = std::sqrt((4.0 * F * R_star) / (std::numbers::pi * L * E_star));
        res.delta = (2.0 * F / (std::numbers::pi * L * E_star)) * 
                     (1.0 + std::log((std::numbers::pi * L * L * E_star) / (F * R_star)));
        res.p0 = std::sqrt((F * E_star) / (std::numbers::pi * L * R_star));
        res.area = 2.0 * res.b * L;
        res.p_mean = F / res.area;

        return res;
    }

    /* Розрахунок вектора профілю напружень */
    [[nodiscard]] static std::vector<StressPoint>
    calc_stress_profile(const SphereResult& sph, double z_max, std::size_t steps) {
        std::vector<StressPoint> vec;
        if (steps == 0 || z_max <= 0.0) return vec;

        vec.reserve(steps + 1);
        const double dz = z_max / static_cast<double>(steps);
        constexpr double nu = 0.30;

        for (std::size_t i = 0; i <= steps; ++i) {
            const double z = static_cast<double>(i) * dz;
            const double za = (sph.a > 0.0) ? (z / sph.a) : 0.0;

            StressPoint pt{};
            pt.z = z;
            pt.z_over_a = za;

            if (za < 1e-6) {
                pt.sigma_z = -sph.p0;
                pt.sigma_x = -sph.p0 * (0.5 + nu);
            } else {
                pt.sigma_z = -sph.p0 / (1.0 + za * za);
                pt.sigma_x = -sph.p0 * ((1.0 + nu) * (1.0 - za * std::atan(1.0 / za)) - 0.5 / (1.0 + za * za));
            }

            pt.tau_max = 0.5 * std::abs(pt.sigma_z - pt.sigma_x);
            vec.push_back(pt);
        }

        return vec;
    }
};

} // namespace hertz

#endif // HERTZ_CONTACT_HPP
```
:::

## Крайові випадки, захисні гарантії та обмеження

1. **Некоректні геометричні параметри (`R₁ <= 0` або `R₂ <= 0`)**:
   Якщо один із радіусів кривини є від'ємним або дорівнює нулю (за винятком конформного увігнутого контакту, де радіуси віднімаються), функція повертає код помилки `HERTZ_ERR_GEOMETRY_SINGULAR` у C або `ErrorCode::InvalidGeometry` у C++.
2. **Перевищення межі пружності (`p₀ > 1.6 σ_y`)**:
   Теорія Герца припускає строго лінійну пружність. Коли піковий тиск `p₀` досягає приблизно `1.6` від межі текучості матеріалу `σ_y`, у точці `z_пік ≈ 0.48 a` починається пластична деформація. Бібліотека не моделює пластичну течію і повертає математичний розв'язок пружного напівпростору. Для аналізу пластичності слід перевіряти `tau_max <= sigma_y / 2`.
3. **Крайові ефекти циліндрів скінченної довжини**:
   У циліндричному контакті рівняння Герца припускають нескінченну довжину `L` або відсутність концентрації напружень на торцях. Для реальних роликів із прямими торцями на краях виникають піки тиску (концентратори), які усуваються профілюванням роликів (бомбуванням).
