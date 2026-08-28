# ⚙️ Аеродинамічний калькулятор поляр і режимів польоту

Розрахунок льотно-технічних характеристик літака або безпілотника починається з обробки поляри крила. Сирі дані продувок в аеродинамічній трубі або чисельного моделювання за панельними методами в XFOIL являють собою дискретний набір точок: для кожного кута атаки `α` задано трійку коефіцієнтів `C_L`, `C_D`, `C_M`. Щоби знайти швидкість звалювання, максимальну дальність ширяння, економічну швидкість баражування або режим найдовшого зависання, бортовий алгоритм чи інженерна програма мусить виконати гладку інтерполяцію поляри, обчислити дотичні та врахувати масштабний ефект числа Рейнольдса.

## Алгоритмічна структура та математична основа

Програмний модуль розв'язує комплекс із п'яти задач аеродинамічного аналізу, кожна з яких базується на строгій фізиці обтікання:

### 1. Монотонна інтерполяція табличних даних поляри
Дискретні точки продувки `(α_i, C_{L,i}, C_{D,i}, C_{M,i})` зазвичай задані з кроком 0.5°–1.0°. Використання глобальних поліномів високого степеня тут категорично заборонене через явище Рунге (неконтрольовані паразитичні осциляції на краях діапазону). Калькулятор використовує кусково-лінійну або монотонну кубічну інтерполяцію, яка гарантує збереження фізичного знаку похідних `dC_L/dα > 0` у безодривній зоні та виключає появу від'ємного опору `C_D < 0` між вузлами сітки.

### 2. Визначення критичних точок та меж режиму
- **Кут нульової підйомної сили `α₀`:** знаходиться пошуком кореня рівняння `C_L(α₀) = 0` лінійною інтерполяцією між сусідніми вузлами з різними знаками.
- **Критичний кут атаки `α_crit` та `C_L,max`:** визначають абсолютний максимум підйомної сили. За цим значенням обчислюється мінімальна швидкість звалювання літального апарата `v_stall = √(2W / (ρ·S·C_L,max))`.
- **Мінімальний профільний опір `C_D,min`:** відповідає найменшому лобовому опору форми й тертя, задаючи швидкісну межу апарата.

### 3. Розрахунок характерних дотичних до поляри
Пошук оптимальних режимів польоту зводиться до знаходження точок дотику променів та кривих різного порядку до поляри:

- **Найвигідніший режим (максимальна аеродинамічна якість `K_max`):**
  Максимізує відношення `K = C_L / C_D`. Геометрично це дотична, проведена з початку координат `(0, 0)` до кривої поляри:
  ```
  K_max = (C_L / C_D)_max        [точка дотику прямої з початку координат]
  ```
  Цей режим забезпечує максимальну дальність планування планера без двигуна `d_max = K_max · h` та максимальну дальність польоту гвинтового літака чи далекобійного розвідувального дрона на заданий запас енергії.

- **Економічний режим (максимальна тривалість польоту):**
  Потужність, потрібна для горизонтального польоту, визначається добутком аеродинамічного опору на швидкість: `P = D · v`. Оскільки в горизонтальному польоті підйомна сила дорівнює вазі `L = W`, швидкість виражається як `v = √(2W / (ρ·S·C_L))`. Тоді потрібна тягова потужність становить:
  ```
  P_req = D · v = (W / K) · √(2W / (ρ · S · C_L))
        = √(2W³ / (ρ · S)) · (C_D / C_L^{1.5})        [потужність на подолання опору]
  ```
  Мінімум потрібної потужності двигуна (а отже мінімальне споживання струму акумулятора за секунду часу) відповідає максимуму комплексу `E_max = (C_L^{1.5} / C_D)_max`. Цей режим обирають для максимальної тривалості висіння та патрулювання.

- **Швидкісний крейсерський режим (для реактивних або високошвидкісних БПЛА):**
  Для турбореактивних двигунів витрата палива пропорційна тязі, а не потужності. Максимум дальності на високій швидкості досягається в точці максимуму комплексу `J_max = (C_L^{0.5} / C_D)_max`.

### 4. Розрахунок зміщення центру тиску
Центр тиску `x_cp` показує точку прикладання результуючої сили, відносно якої момент дорівнює нулю. Його положення обчислюється через момент фокуса `x_ac = 0.25c`:

```
x_cp / c = 0.25 − (C_M_ac / C_L)        [координата центру тиску в частках хорди]
```

За малих значень `|C_L| < 0.02` центр тиску прямує до нескінченності, оскільки аеродинамічна сила вироджується в чистий момент пари сил. Алгоритм детектує цей крайовий випадок і повертає позначку невизначеності замість ділення на нуль.

### 5. Масштабування за числом Рейнольдса (Low-Re корекція для дронів)
Малорозмірні крила та пропелери БПЛА працюють при малих числах Рейнольдса (`Re = 2·10⁴ ... 10⁵`). Якщо базова поляра виміряна при `Re_0 = 5·10⁵`, опір тертя перераховується за законом примежового шару:

```
C_D,scaled = C_D0 · (Re_0 / Re)^0.20 + ΔC_D,LSB        [масштабна поправка з урахуванням LSB]
```

де `ΔC_D,LSB` — додатковий штраф на утворення ламінарної бульбашки відриву, який лавиноподібно зростає при `Re < 100 000`.

## Реалізація на мовах C та C++

Нижче наведено самодостатній розрахунковий модуль. У вкладці C реалізовано процедурний інтерфейс з фіксованими буферами та кодами повернення. У вкладці C++ реалізовано типобезпечний клас з автоматичним сортуванням, `std::span`, `std::optional` та алгоритмами стандартної бібліотеки.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MAX_POLAR_POINTS 128

typedef struct {
    double alpha_deg; /* Кут атаки (градуси) */
    double cl;        /* Коефіцієнт підйомної сили */
    double cd;        /* Коефіцієнт лобового опору */
    double cm;        /* Коефіцієнт поздовжнього моменту відносно c/4 */
} PolarPoint;

typedef struct {
    PolarPoint points[MAX_POLAR_POINTS];
    size_t count;
    double reynolds_base; /* Базове число Re таблиці */
} AirfoilPolar;

typedef struct {
    double alpha_zero_lift_deg; /* Кут нульової сили alpha_0 */
    double alpha_crit_deg;      /* Критичний кут атаки alpha_crit */
    double cl_max;              /* Максимальний C_L */
    double cd_min;              /* Мінімальний опір C_D,min */
    
    /* Найвигідніший режим (максимальна якість) */
    double k_max;               /* Максимальна якість K = C_L / C_D */
    double alpha_k_max_deg;
    double cl_at_k_max;
    double cd_at_k_max;

    /* Економічний режим (мінімальна потужність двигуна) */
    double e_max;               /* Максимум C_L^(1.5) / C_D */
    double alpha_e_max_deg;
    
    /* Швидкісний режим */
    double j_max;               /* Максимум C_L^(0.5) / C_D */
    double alpha_j_max_deg;
} PolarMetrics;

/* Лінійна інтерполяція значень поляри */
static bool polar_evaluate(const AirfoilPolar* p, double alpha_deg, PolarPoint* out) {
    if (!p || p->count < 2 || !out) return false;
    if (alpha_deg < p->points[0].alpha_deg || alpha_deg > p->points[p->count - 1].alpha_deg) {
        return false; /* За межами таблиці екстраполяція небезпечна */
    }
    for (size_t i = 0; i < p->count - 1; ++i) {
        if (alpha_deg >= p->points[i].alpha_deg && alpha_deg <= p->points[i + 1].alpha_deg) {
            double span = p->points[i + 1].alpha_deg - p->points[i].alpha_deg;
            double t = (span > 1e-9) ? (alpha_deg - p->points[i].alpha_deg) / span : 0.0;
            out->alpha_deg = alpha_deg;
            out->cl = p->points[i].cl + t * (p->points[i + 1].cl - p->points[i].cl);
            out->cd = p->points[i].cd + t * (p->points[i + 1].cd - p->points[i].cd);
            out->cm = p->points[i].cm + t * (p->points[i + 1].cm - p->points[i].cm);
            return true;
        }
    }
    return false;
}

/* Розрахунок характеристик поляри */
bool polar_analyze(const AirfoilPolar* p, PolarMetrics* out) {
    if (!p || p->count < 3 || !out) return false;

    out->cl_max = -1e9;
    out->cd_min = 1e9;
    out->k_max = -1e9;
    out->e_max = -1e9;
    out->j_max = -1e9;
    out->alpha_zero_lift_deg = 0.0;

    bool found_zero_lift = false;

    for (size_t i = 0; i < p->count; ++i) {
        const PolarPoint* pt = &p->points[i];

        /* Пошук CL_max */
        if (pt->cl > out->cl_max) {
            out->cl_max = pt->cl;
            out->alpha_crit_deg = pt->alpha_deg;
        }

        /* Пошук CD_min */
        if (pt->cd < out->cd_min) {
            out->cd_min = pt->cd;
        }

        /* Пошук alpha_0 (перехід через нуль) */
        if (i > 0 && !found_zero_lift) {
            double prev_cl = p->points[i - 1].cl;
            if ((prev_cl <= 0.0 && pt->cl >= 0.0) || (prev_cl >= 0.0 && pt->cl <= 0.0)) {
                double t = -prev_cl / (pt->cl - prev_cl + 1e-12);
                out->alpha_zero_lift_deg = p->points[i - 1].alpha_deg + t * (pt->alpha_deg - p->points[i - 1].alpha_deg);
                found_zero_lift = true;
            }
        }

        /* Дотичні поляри (лише для додатного CL та CD > 0) */
        if (pt->cl > 0.001 && pt->cd > 0.0001) {
            double k = pt->cl / pt->cd;
            if (k > out->k_max) {
                out->k_max = k;
                out->alpha_k_max_deg = pt->alpha_deg;
                out->cl_at_k_max = pt->cl;
                out->cd_at_k_max = pt->cd;
            }

            double e = pow(pt->cl, 1.5) / pt->cd;
            if (e > out->e_max) {
                out->e_max = e;
                out->alpha_e_max_deg = pt->alpha_deg;
            }

            double j = sqrt(pt->cl) / pt->cd;
            if (j > out->j_max) {
                out->j_max = j;
                out->alpha_j_max_deg = pt->alpha_deg;
            }
        }
    }
    return true;
}

/* Обчислення центру тиску (у частках хорди) */
bool calculate_center_of_pressure(double cl, double cm_c4, double* x_cp_c) {
    if (!x_cp_c) return false;
    if (fabs(cl) < 0.02) {
        return false; /* Невизначеність: ділення на нуль */
    }
    /* x_cp = x_ac - c * (cm / cl), де x_ac = 0.25c */
    *x_cp_c = 0.25 - (cm_c4 / cl);
    return true;
}

/* Масштабування опору для низьких чисел Рейнольдса дронів */
double scale_cd_for_reynolds(double cd_base, double re_base, double re_target) {
    if (re_target <= 1000.0 || re_base <= 1000.0) return cd_base;
    
    /* Масштабування ламінарно-турбулентного тертя */
    double scale = pow(re_base / re_target, 0.20);
    double cd_scaled = cd_base * scale;

    /* Штраф на ламінарну бульбашку відриву (LSB) при Re < 10^5 */
    if (re_target < 100000.0) {
        double lsb_factor = (100000.0 - re_target) / 100000.0;
        cd_scaled += 0.015 * lsb_factor * lsb_factor;
    }
    return cd_scaled;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>
#include <algorithm>
#include <iomanip>

struct PolarPoint {
    double alpha_deg{0.0}; // Кут атаки (градуси)
    double cl{0.0};        // Коефіцієнт підйомної сили
    double cd{0.0};        // Коефіцієнт лобового опору
    double cm{0.0};        // Коефіцієнт поздовжнього моменту (c/4)
};

struct PolarMetrics {
    double alpha_zero_lift_deg{0.0};
    double alpha_crit_deg{0.0};
    double cl_max{-1e9};
    double cd_min{1e9};

    double k_max{-1e9}; // (C_L / C_D)_max — максимальна якість
    double alpha_k_max_deg{0.0};
    double cl_at_k_max{0.0};
    double cd_at_k_max{0.0};

    double e_max{-1e9}; // (C_L^1.5 / C_D)_max — економічний режим
    double alpha_e_max_deg{0.0};

    double j_max{-1e9}; // (C_L^0.5 / C_D)_max — швидкісний режим
    double alpha_j_max_deg{0.0};
};

class AirfoilPolarAnalyzer {
public:
    explicit AirfoilPolarAnalyzer(std::vector<PolarPoint> points, double reynolds_base = 500000.0)
        : points_(std::move(points)), reynolds_base_(reynolds_base) {
        std::ranges::sort(points_, [](const auto& a, const auto& b) {
            return a.alpha_deg < b.alpha_deg;
        });
    }

    [[nodiscard]] std::optional<PolarPoint> evaluate(double alpha_deg) const {
        if (points_.size() < 2 || alpha_deg < points_.front().alpha_deg || alpha_deg > points_.back().alpha_deg) {
            return std::nullopt;
        }

        auto it = std::ranges::lower_bound(points_, alpha_deg, {}, &PolarPoint::alpha_deg);
        if (it == points_.begin()) return *it;

        const auto& p1 = *(it - 1);
        const auto& p2 = *it;
        const double span = p2.alpha_deg - p1.alpha_deg;
        const double t = (span > 1e-9) ? (alpha_deg - p1.alpha_deg) / span : 0.0;

        return PolarPoint{
            .alpha_deg = alpha_deg,
            .cl = p1.cl + t * (p2.cl - p1.cl),
            .cd = p1.cd + t * (p2.cd - p1.cd),
            .cm = p1.cm + t * (p2.cm - p1.cm)
        };
    }

    [[nodiscard]] std::optional<PolarMetrics> analyze() const {
        if (points_.size() < 3) return std::nullopt;

        PolarMetrics metrics{};
        bool found_zero_lift = false;

        for (size_t i = 0; i < points_.size(); ++i) {
            const auto& pt = points_[i];

            if (pt.cl > metrics.cl_max) {
                metrics.cl_max = pt.cl;
                metrics.alpha_crit_deg = pt.alpha_deg;
            }

            if (pt.cd < metrics.cd_min) {
                metrics.cd_min = pt.cd;
            }

            if (i > 0 && !found_zero_lift) {
                const double prev_cl = points_[i - 1].cl;
                if ((prev_cl <= 0.0 && pt.cl >= 0.0) || (prev_cl >= 0.0 && pt.cl <= 0.0)) {
                    const double t = -prev_cl / (pt.cl - prev_cl + 1e-12);
                    metrics.alpha_zero_lift_deg = points_[i - 1].alpha_deg + t * (pt.alpha_deg - points_[i - 1].alpha_deg);
                    found_zero_lift = true;
                }
            }

            if (pt.cl > 0.001 && pt.cd > 0.0001) {
                const double k = pt.cl / pt.cd;
                if (k > metrics.k_max) {
                    metrics.k_max = k;
                    metrics.alpha_k_max_deg = pt.alpha_deg;
                    metrics.cl_at_k_max = pt.cl;
                    metrics.cd_at_k_max = pt.cd;
                }

                const double e = std::pow(pt.cl, 1.5) / pt.cd;
                if (e > metrics.e_max) {
                    metrics.e_max = e;
                    metrics.alpha_e_max_deg = pt.alpha_deg;
                }

                const double j = std::sqrt(pt.cl) / pt.cd;
                if (j > metrics.j_max) {
                    metrics.j_max = j;
                    metrics.alpha_j_max_deg = pt.alpha_deg;
                }
            }
        }
        return metrics;
    }

    [[nodiscard]] static std::optional<double> centerOfPressure(double cl, double cm_c4) noexcept {
        if (std::abs(cl) < 0.02) {
            return std::nullopt; // Близько до нульової підйомної сили — центр тиску невизначений
        }
        return 0.25 - (cm_c4 / cl);
    }

    [[nodiscard]] double scaleForReynolds(double cd_base, double re_target) const noexcept {
        if (re_target <= 1000.0 || reynolds_base_ <= 1000.0) return cd_base;

        const double scale = std::pow(reynolds_base_ / re_target, 0.20);
        double cd_scaled = cd_base * scale;

        if (re_target < 100000.0) {
            const double lsb_factor = (100000.0 - re_target) / 100000.0;
            cd_scaled += 0.015 * lsb_factor * lsb_factor; // Додатковий опір LSB
        }
        return cd_scaled;
    }

private:
    std::vector<PolarPoint> points_;
    double reynolds_base_{500000.0};
};
```
:::

## Інженерні пастки та крайові випадки

1. **Сингулярність центру тиску при `C_L → 0`:**
   У точці нульової підйомної сили вираз `x_cp = 0.25 − C_{M0} / C_L` прямує до `±∞`. Результуюча сила дорівнює нулю, а ненульовий момент пари сил не має єдиної точки прикладання. Програмний код захищений умовою `|C_L| < 0.02`, яка повертає `std::nullopt` або `false`. Для балансування автопілота використовують виключно аеродинамічний фокус `x_ac = 0.25c`, відносно якого похідна моменту строго дорівнює нулю `dC_M/dα = 0`.

2. **Хвилястість поляри через ламінарні бульбашки (Low-Re шум):**
   При експериментальних продувках на малих числах Рейнольдса (`Re < 10^5`) на полярі з'являються локальні сходинки та плато через стрибкоподібне переміщення точки ламінарного відриву `S`. Простий пошук максимуму може застрягти в локальному екстремумі. У промислових алгоритмах сирі точки перед пошуком дотичних згладжують кубічними B-сплайнами з контролем другої похідної `d²C_D/dC_L² > 0`.

3. **Небезпека екстраполяції в закритичну зону (`α > α_crit`):**
   Після початку зриву потоку аналітичні співвідношення лінійної теорії тонкого профілю повністю втрачають чинність. Проста лінійна екстраполяція значень `C_L` та `C_D` за межі виміряної таблиці категорично заборонена. Для моделювання режимів глибокого звалювання, парашутування та плоских штопорів застосовують нелінійну модель Вітерни–Коррігана (Viterna-Corrigan post-stall model). Вона плавно зшиває експериментальну поляру біля точки зриву `α_crit` з аналітичною моделлю обтікання тонкої пластини під кутами до 90°, де домінує чистий вихровий опір тиску:
   ```
   C_D(α) = B₁ · sin² α + B₂ · cos α        [модель Вітерни для закритичного опору]
   C_L(α) = A₁ · sin(2α) + A₂ · (cos² α / sin α)
   ```
   де коефіцієнти `A₁, A₂, B₁, B₂` обчислюються зі збереження неперервності кривих та їхніх похідних у точці `α_crit`.

4. **Інтеграція в контур автопілота (PX4 / ArduPilot):**
   У реальних системах автоматичного керування польотом (наприклад, у модулі TECS — Total Energy Control System) обчислені метрики поляри використовуються для динамічного обмеження допустимого діапазону швидкостей. Автопілот встановлює мінімальну дозволену швидкість горизонтального маневру `v_min = 1.3 · v_stall`, а для тривалого патрулювання автоматично призначає цільову повітряну швидкість рівною швидкості економічного режиму `v_econ`, досягаючи максимального радіуса дії без втручання оператора.
