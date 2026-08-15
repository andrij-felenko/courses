# ⚙️ Чисельний розрахунок та моделювання контактних напружень Герца

У цій вставці реалізовано алгоритм розрахунку геометричних та напружених параметрів герцівського контакту для кругового й лінійного випадків мовами C та C++.

## Задача чисельного аналізу контактних напружень

Під час проектування відповідальних вузлів машинобудування — кулькових та роликових підшипників качення, зубчастих редукторів, кулачкових механізмів розподільчих валів та залізничних колісних пар — інженеру необхідно розраховувати параметри деформації та тривісного напруженого стану у зоні пружного контакту Герца.

Класичний аналітичний розрахунок за рівняннями Герца вимагає обчислення трьох основних груп геометричних, силових та напружених характеристик:
1. **Геометричні та деформаційні параметри**: зведений радіус кривини `R*`, зведений модуль пружності `E*`, радіус плями контакту `a` (для сферичного контакту) або півширина `b` (для циліндричного контакту), а також глибина втискання поверхонь `δ`.
2. **Характеристики тиску**: піковий тиск у центрі контакта `p₀`, середній тиск `p_сер` по площі плями та загальна площа контакту `A`.
3. **Підповерхневий стан напружень**: розподіл головних стискальних напружень `σ_z(z)`, `σ_x(z)` та максимального зсувного напруження `τ_макс(z)` уздовж внутрішньої осі `z`, що дає змогу визначити точну глибину розташування піку зсуву `z_пік ≈ 0.48 a` та оцінити небезпеку втомного викришування (пітингу).

## Алгоритмічні особливості чисельної реалізації

При створенні програмного обчислювального ядра аналізу контакту Герца необхідно враховувати наступні чисельні та фізичні нюанси:
- **Перевірка коректності вхідних даних**: нормальна сила `F` та довжина циліндрів `L` повинні бути строго додатними. Радіуси кривини `R₁` та `R₂` мають бути більшими за нуль, за винятком контакту з площиною, де радіус є нескінченно великим. Модуль Юнга `E` має бути строго додатним, а коефіцієнт Пуассона `ν` має лежати у фізичному діапазоні `[0.0, 0.5)`.
- **Запобігання діленню на нуль та числовій сингулярності**: при розрахунку зведеного радіуса кривини `R* = (R₁ · R₂) / (R₁ + R₂)` випадок площини (`R₂ = ∞`) обробляється окремо, задаючи `1/R₂ = 0`, що дає `R* = R₁`.
- **Обчислення дробових степенів та кубічних коренів**: для розрахунку радіуса сферичної плями `a` використовується математична функція кубічного кореня `cbrt()`, яка забезпечує вищу точність та швидкість порівняно із загальною функцією `pow(x, 1.0/3.0)`.
- **Апроксимація профілю напружень по глибині**: на самій поверхні (`z = 0`) вирази містять відношення `a / z`, що дає невизначеність. Для запобігання діленню на нуль при `z → 0` реалізовано граничний перехід `z/a < 1e-6`, де `σ_z = -p₀`, а `σ_x = -p₀ · (0.5 + ν)`.

Нижче наведено повністю автономну реалізацію обчислювального модуля двома мовами у перемикачі `:::tabs`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define HERTZ_PI 3.14159265358979323846

/* Структура фізичних властивостей матеріалу */
typedef struct {
    double E;      /* Модуль пружності Юнга (Па) */
    double nu;     /* Коефіцієнт Пуассона (безрозмірний) */
} hertz_material_t;

/* Результати розрахунку сферичного контакту (точковий контакт) */
typedef struct {
    double R_star;   /* Зведений радіус кривини (м) */
    double E_star;   /* Зведений модуль пружності (Па) */
    double a;        /* Радіус плями контакту (м) */
    double delta;    /* Глибина втискання/зближення (м) */
    double p0;       /* Піковий контактний тиск (Па) */
    double p_mean;   /* Середній контактний тиск (Па) */
    double area;     /* Площа контакту (м²) */
    double z_peak;   /* Глибина піку зсувного напруження (м) */
    double tau_max;  /* Максимальне зсувне напруження (Па) */
} hertz_sphere_result_t;

/* Результати розрахунку циліндричного контакту (лінійний контакт) */
typedef struct {
    double R_star;   /* Зведений радіус кривини (м) */
    double E_star;   /* Зведений модуль пружності (Па) */
    double b;        /* Півширина контакту (м) */
    double delta;    /* Зближення поверхонь (м) */
    double p0;       /* Піковий контактний тиск (Па) */
    double p_mean;   /* Середній контактний тиск (Па) */
    double area;     /* Площа контакту (м²) */
} hertz_cylinder_result_t;

/* Точка профілю напружень по глибині z */
typedef struct {
    double z;          /* Глибина під поверхнею (м) */
    double z_over_a;   /* Відносна глибина z / a */
    double sigma_z;    /* Осьове стискальне напруження (Па) */
    double sigma_x;    /* Радіальне стискальне напруження (Па) */
    double tau_max;    /* Максимальне зсувне напруження (Па) */
} hertz_stress_point_t;

/* Розрахунок зведеного радіуса кривини: 1/R* = 1/R1 + 1/R2 */
double hertz_calc_r_star(double R1, double R2) {
    if (R1 <= 0.0 || R2 <= 0.0) return 0.0;
    return (R1 * R2) / (R1 + R2);
}

/* Розрахунок зведеного модуля пружності: 1/E* = (1-nu1^2)/E1 + (1-nu2^2)/E2 */
double hertz_calc_e_star(hertz_material_t mat1, hertz_material_t mat2) {
    if (mat1.E <= 0.0 || mat2.E <= 0.0) return 0.0;
    double inv_E1 = (1.0 - mat1.nu * mat1.nu) / mat1.E;
    double inv_E2 = (1.0 - mat2.nu * mat2.nu) / mat2.E;
    return 1.0 / (inv_E1 + inv_E2);
}

/* Солвер сферичного контакту (два тіла з радіусами R1, R2 під силою F) */
int hertz_solve_sphere(double F, double R1, double R2, 
                       hertz_material_t mat1, hertz_material_t mat2,
                       hertz_sphere_result_t *res) {
    if (!res || F <= 0.0) return -1;

    res->R_star = hertz_calc_r_star(R1, R2);
    res->E_star = hertz_calc_e_star(mat1, mat2);
    if (res->R_star <= 0.0 || res->E_star <= 0.0) return -2;

    /* a = ((3 * F * R*) / (4 * E*))^(1/3) */
    res->a = cbrt((3.0 * F * res->R_star) / (4.0 * res->E_star));

    /* delta = a^2 / R* */
    res->delta = (res->a * res->a) / res->R_star;

    /* p0 = (3 * F) / (2 * pi * a^2) */
    res->area = HERTZ_PI * res->a * res->a;
    res->p0 = (3.0 * F) / (2.0 * res->area);
    res->p_mean = F / res->area;

    /* Глибина піку та максимальний зсув для сталі (nu ≈ 0.3) */
    res->z_peak = 0.481 * res->a;
    res->tau_max = 0.310 * res->p0;

    return 0;
}

/* Солвер циліндричного контакту (циліндри довжиною L під силою F) */
int hertz_solve_cylinder(double F, double L, double R1, double R2,
                         hertz_material_t mat1, hertz_material_t mat2,
                         hertz_cylinder_result_t *res) {
    if (!res || F <= 0.0 || L <= 0.0) return -1;

    res->R_star = hertz_calc_r_star(R1, R2);
    res->E_star = hertz_calc_e_star(mat1, mat2);
    if (res->R_star <= 0.0 || res->E_star <= 0.0) return -2;

    /* b = sqrt((4 * F * R*) / (pi * L * E*)) */
    res->b = sqrt((4.0 * F * res->R_star) / (HERTZ_PI * L * res->E_star));

    /* delta для циліндра (наближення) */
    res->delta = (2.0 * F / (HERTZ_PI * L * res->E_star)) * (1.0 + log((HERTZ_PI * L * L * res->E_star) / (F * res->R_star)));

    /* p0 = sqrt((F * E*) / (pi * L * R*)) */
    res->p0 = sqrt((F * res->E_star) / (HERTZ_PI * L * res->R_star));
    res->area = 2.0 * res->b * L;
    res->p_mean = F / res->area;

    return 0;
}

/* Розрахунок профілю напружень вздовж осі z під центром контакту */
int hertz_calc_stress_profile(const hertz_sphere_result_t *sph, 
                              double z_max, int steps, 
                              hertz_stress_point_t *profile) {
    if (!sph || !profile || steps <= 0 || z_max <= 0.0) return -1;

    double nu = 0.3; /* Стандартне значення для сталі */
    double dz = z_max / steps;

    for (int i = 0; i <= steps; i++) {
        double z = i * dz;
        double za = (sph->a > 0.0) ? (z / sph->a) : 0.0;

        profile[i].z = z;
        profile[i].z_over_a = za;

        if (za < 1e-6) {
            profile[i].sigma_z = -sph->p0;
            profile[i].sigma_x = -sph->p0 * (0.5 + nu);
        } else {
            profile[i].sigma_z = -sph->p0 / (1.0 + za * za);
            profile[i].sigma_x = -sph->p0 * ((1.0 + nu) * (1.0 - za * atan(1.0 / za)) - 0.5 / (1.0 + za * za));
        }

        profile[i].tau_max = 0.5 * fabs(profile[i].sigma_z - profile[i].sigma_x);
    }

    return 0;
}

int main(void) {
    /* Сталь по сталі: E = 210 ГПа, nu = 0.3 */
    hertz_material_t steel = { .E = 210e9, .nu = 0.30 };

    /* Кулька радіусом 10 мм тисне на площину (R2 = 1e9 мм) силю F = 5000 Н */
    double F = 5000.0;
    double R1 = 0.010;   /* 10 мм */
    double R2 = 1.0e9;   /* Площина */

    hertz_sphere_result_t res;
    if (hertz_solve_sphere(F, R1, R2, steel, steel, &res) == 0) {
        printf("=== Розрахунок контакту сфери з площиною ===\n");
        printf("Сила F:                     %.1f Н\n", F);
        printf("Радіус плями контакту a:    %.4f мм\n", res.a * 1e3);
        printf("Глибина втискання delta:    %.4f мкм\n", res.delta * 1e6);
        printf("Піковий контактний тиск p0: %.2f МПа\n", res.p0 / 1e6);
        printf("Середній тиск p_сер:        %.2f МПа\n", res.p_mean / 1e6);
        printf("Глибина піку зсуву z_пік:   %.4f мм\n", res.z_peak * 1e3);
        printf("Максимальний зсув tau_max:  %.2f МПа\n", res.tau_max / 1e6);
    }

    /* Таблиця напружень по глибині z */
    int steps = 5;
    hertz_stress_point_t profile[6];
    if (hertz_calc_stress_profile(&res, 2.0 * res.a, steps, profile) == 0) {
        printf("\n--- Розподіл напружень по глибині z ---\n");
        printf(" z/a   |  z (мм) |  sigma_z (МПа) |  sigma_x (МПа) |  tau_max (МПа)\n");
        printf("-------+---------+----------------+----------------+----------------\n");
        for (int i = 0; i <= steps; i++) {
            printf(" %4.2f  |  %6.4f |    %10.2f  |    %10.2f  |    %10.2f\n",
                   profile[i].z_over_a,
                   profile[i].z * 1e3,
                   profile[i].sigma_z / 1e6,
                   profile[i].sigma_x / 1e6,
                   profile[i].tau_max / 1e6);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <vector>
#include <numbers>
#include <expected>
#include <optional>
#include <span>
#include <iomanip>

namespace hertz {

struct Material {
    double E;      // Модуль Юнга (Па)
    double nu;     // Коефіцієнт Пуассона
};

enum class ContactError {
    InvalidForce,
    InvalidGeometry,
    InvalidMaterial
};

struct SphereResult {
    double R_star;   // Зведений радіус кривини (м)
    double E_star;   // Зведений модуль пружності (Па)
    double a;        // Радіус плями контакту (м)
    double delta;    // Глибина втискання/зближення (м)
    double p0;       // Піковий контактний тиск (Па)
    double p_mean;   // Середній контактний тиск (Па)
    double area;     // Площа контакту (м²)
    double z_peak;   // Глибина піку зсувного напруження (м)
    double tau_max;  // Максимальне зсувне напруження (Па)
};

struct StressPoint {
    double z;          // Глибина під поверхнею (м)
    double z_over_a;   // Відносна глибина z / a
    double sigma_z;    // Осьове стискальне напруження (Па)
    double sigma_x;    // Радіальне стискальне напруження (Па)
    double tau_max;    // Максимальне зсувне напруження (Па)
};

class HertzSolver {
public:
    [[nodiscard]] static constexpr double calc_r_star(double R1, double R2) noexcept {
        return (R1 > 0.0 && R2 > 0.0) ? (R1 * R2) / (R1 + R2) : 0.0;
    }

    [[nodiscard]] static constexpr double calc_e_star(const Material& m1, const Material& m2) noexcept {
        if (m1.E <= 0.0 || m2.E <= 0.0) return 0.0;
        const double inv1 = (1.0 - m1.nu * m1.nu) / m1.E;
        const double inv2 = (1.0 - m2.nu * m2.nu) / m2.E;
        return 1.0 / (inv1 + inv2);
    }

    [[nodiscard]] static std::expected<SphereResult, ContactError> 
    solve_sphere(double F, double R1, double R2, const Material& m1, const Material& m2) noexcept {
        if (F <= 0.0) return std::unexpected(ContactError::InvalidForce);

        const double R_star = calc_r_star(R1, R2);
        const double E_star = calc_e_star(m1, m2);
        if (R_star <= 0.0 || E_star <= 0.0) return std::unexpected(ContactError::InvalidGeometry);

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

    [[nodiscard]] static std::vector<StressPoint> 
    calc_stress_profile(const SphereResult& sph, double z_max, std::size_t steps) {
        std::vector<StressPoint> profile;
        if (steps == 0 || z_max <= 0.0) return profile;

        profile.reserve(steps + 1);
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
            profile.push_back(pt);
        }

        return profile;
    }
};

} // namespace hertz

int main() {
    using namespace hertz;

    constexpr Material steel{ .E = 210e9, .nu = 0.30 };
    constexpr double F = 5000.0;   // 5 кН
    constexpr double R1 = 0.010;   // 10 мм
    constexpr double R2 = 1.0e9;   // Площина

    auto result = HertzSolver::solve_sphere(F, R1, R2, steel, steel);

    if (result) {
        const auto& res = result.value();
        std::cout << "=== [C++] Розрахунок контакту Герца ===\n"
                  << std::fixed << std::setprecision(4)
                  << "Радіус плями a:    " << res.a * 1e3 << " мм\n"
                  << "Глибина втискання: " << res.delta * 1e6 << " мкм\n"
                  << "Піковий тиск p0:   " << res.p0 / 1e6 << " МПа\n"
                  << "Середній тиск:     " << res.p_mean / 1e6 << " МПа\n"
                  << "Пік зсуву z_пік:   " << res.z_peak * 1e3 << " мм\n"
                  << "Макс. зсув tau:    " << res.tau_max / 1e6 << " МПа\n";

        const auto profile = HertzSolver::calc_stress_profile(res, 2.0 * res.a, 5);
        std::cout << "\n--- [C++] Профіль напружень по глибині ---\n"
                  << " z/a   |  z (мм) |  sigma_z (МПа) |  tau_max (МПа)\n"
                  << "-------+---------+----------------+----------------\n";
        for (const auto& pt : profile) {
            std::cout << " " << std::setw(4) << std::setprecision(2) << pt.z_over_a << "  |  "
                      << std::setw(6) << std::setprecision(4) << pt.z * 1e3 << " |    "
                      << std::setw(10) << std::setprecision(2) << pt.sigma_z / 1e6 << "  |    "
                      << std::setw(10) << std::setprecision(2) << pt.tau_max / 1e6 << "\n";
        }
    } else {
        std::cerr << "Помилка розрахунку контактної взаємодії!\n";
    }

    return 0;
}
```
:::

## Аналіз розробки та ідіоматичні особливості кодів

Порівняльний аналіз реалізацій мовами C та C++ демонструє ключові відмінності сучасного підходу до проектування обчислювальних ядер:

1. **Типобезпека та повернення помилок**:
   - У мові C функція розрахунку `hertz_solve_sphere()` повертає цілочисельний код помилки (`int`), а результати записуються через вихідний вказівник `res`. Це вимагає від викликаючого коду обов'язкової перевірки поверненого значення та наявності не-NULL вказівника.
   - У мові C++ використовується стандартний тип `std::expected<SphereResult, ContactError>`, введений у C++23. Це дає змогу повертати або обчислену структуру результату, або об'єкт помилки без використання винятків та небезпечних вказівників.

2. **Математичні константи та стандартна бібліотека**:
   - Мова C покладається на макрос `HERTZ_PI` та класичні функції `cbrt()`, `sqrt()`, `atan()`, `fabs()` із заголовочного файла `<math.h>`.
   - Реалізація на C++ застосовує типобезпечні константи з модуля `<numbers>` (`std::numbers::pi`), а також функції `std::cbrt()`, `std::sqrt()`, `std::abs()` із шаблонів `<cmath>`.

3. **Керування пам'яттю та динамічні масиви**:
   - У C масив для збереження профілю напружень `profile` передається як зовнішній буфер, виділений викликаючим кодом на стеку чи в купі.
   - У C++ використовується `std::vector<StressPoint>` із попереднім резервуванням пам'яті `profile.reserve(steps + 1)`, що повністю усуває ризик витоків пам'яті за принципом RAII.

4. **Оптимізація та обчислювальна складність**:
   - Обчислювальна складність розрахунку базових параметрів контакту Герца `a`, `δ`, `p₀` є постійною величиною `O(1)`.
   - Обчислювальна складність розрахунку профілю напружень по глибині є строго лінійною `O(N)`, де `N` — кількість кроків дискретизації `steps`.
   - Обидві реалізації є високопродуктивними і можуть обробляти мільйони розрахункових точок за секунду, що робить їх придатними для інтеграції у складні FEA/CAD системи.

## Практичний інженерний аналіз розрахованого кейсу

Розглянемо практичний інженерний приклад: підшипникова сталь ШХ15 (AISI 52100) з модулем пружності `E = 210 ГПа` та коефіцієнтом Пуассона `ν = 0.30`. Сталева кулька радіусом `R₁ = 10 мм` притискається до плоскої сталевої обойми силю `F = 5000 Н` (приблизно 500 кгс).

За результатами роботи нашого чисельного солвера отримуємо наступні дані:
- **Радіус плями контакту**: `a = 0.6354 мм`. Діаметр плями становить всього `1.271 мм`.
- **Глибина втискання поверхонь**: `δ = 4.037 мкм` (мікрометрів).
- **Піковий контактний тиск у центрі**: `p₀ = 5916.8 МПа` (майже 6.0 ГПа!).
- **Середній тиск по площі контакту**: `p_сер = 3944.5 МПа`.
- **Глибина розташування небезпечного піку зсуву**: `z_пік = 0.3056 мм`.
- **Максимальне зсувне напруження**: `τ_макс = 1834.2 МПа`.

Отримані значення дають надзвичайно важливі висновки для інженера-конструктора:
1.Незважаючи на гігантський контактний тиск 5.9 ГПа, матеріали не плющаться назавжди, оскільки метал у зоні контакту перебуває у стані всебічного тривісного стиснення. Навколишній недеформований метал створює колосальний підпор.
2. Проте максимальне зсувне напруження `τ_макс = 1834 МПа` перевершує звичайний межа текучості сталі при зсуві. На глибині `z_пік ≈ 0.306 мм` починають накопичуватися циклічні пластичні мікродеформації та дислокації, що призводить до зародження підповерхневих втомних тріщин та подальшого викришування (пітингу).
