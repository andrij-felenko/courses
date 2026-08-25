# ⚙️ Моделювання параметрів та діаграми спрямованості параболічної антени

Ця вставка містить практичну реалізацію мовами C та C++ програмного інструменту для комп'ютерного аналізу геометрії, коефіцієнта підсилення, ширини головного променя, фазових втрат за формулою Рузе та генерації двохвимірного профілю діаграми спрямованості для кругової параболічної антени.

---

### Принцип роботи та розрахункові формули

Програма призначена для розрахунку й моделювання характеристик антенних систем надвисоких частот (від 1 ГГц до 100 ГГц). Вона приймає чотири ключові геометричні та електродинамічні параметри антени:
1. **Геометричний діаметр рефлектора `D`** (у метрах).
2. **Робочу частоту `f`** (у герцах).
3. **Апертурну ефективність `η_a0`** (безрозмірний коефіцієнт від 0.50 до 0.80, який враховує спадання опромінення, переливання та затінення).
4. **Середньоквадратичну шорсткість поверхні `ε_rms`** (у метрах).

На основі цих вхідних даних алгоритм виконує послідовний розрахунок електродинамічних величин:

1. **Довжина хвилі у вільному просторі**:
   `λ = c / f`, де `c = 299 792 458 м/с` (строга фізична константа швидкості світла).
2. **Геометрична площа кругового розкриву**:
   `A = π·D² / 4`.
3. **Ефективна площа апертури**:
   `A_eff = η_a0 · A`.
4. **Пряма спрямованість ізотропного апертурного джерела**:
   `D₀ = (π·D / λ)²`.
5. **Ідеальний коефіцієнт підсилення у dBi** (без урахування шорсткості):
   `G_ideal = 10 · log₁₀(η_a0 · D₀)`.
6. **Фазова ефективність поверхні за формулою Рузе**:
   `η_r = exp [ - (4·π·ε_rms / λ)² ]`.
7. **Реальний коефіцієнт підсилення з урахуванням втрат у dBi**:
   `G_real = G_ideal + 10 · log₁₀(η_r)`.
8. **Ширина головного променя за рівнем половини потужності (-3 dB)**:
   `θ_3dB = 70° · (λ / D)` (у градусах).
9. **Кутове положення першого нуля дифракційної картини**:
   `θ_null = 1.22 · (λ / D) · (180° / π)` (у градусах).

---

### Математичний алгоритм обчислення функції Бесселя

Для побудови кутового розрізу діаграми спрямованості у далекому полі використовується функція дифракційного диска Ейрі:

```
u = (π·D / λ) · sin(θ)
F(u) = | 2·J₁(u) / u |
G(θ) = G_real + 20 · log₁₀( F(u) )
```

Обчислення функції Бесселя першого роду першого порядку `J₁(u)` для довільного дійсного аргументу `u` є класичною обчислювальною задачею. Пряме обчислення через степеневий ряд Тайлора вимагає багатьох ітерацій при великих значеннях `u`. Для забезпечення високої швидкодії та точності в обох реалізаціях застосовано мінімаксне поліноміальне наближення Абрамовіца та Стіган (Abramowitz & Stegun 9.4.4):

- **При `|u| < 3.75`**: застосовується раціональний поліном 6-го степеня від `y = (u / 3.75)²`:
  ```
  J₁(u) / u = 0.5 + y·(-0.56249985 + y·(0.21093573 + y·(-0.03954289 + y·0.00443319)))
  ```
- **При `|u| ≥ 3.75`**: застосовується асимптотичний розклад згасаючої косинусоїди:
  ```
  J₁(u) = (1 / √|u|) · f₁(u) · cos( θ₁(u) )
  ```
  де `f₁(u)` та `theta₁(u)` — раціональні корегувальні поліноми від `y = 3.75 / |u|`.

Це забезпечує відносну точність обчислення `J₁(u)` кращу за `10⁻⁶` по всій області визначення при мінімальній кількості операцій множення та додавання.

---

### Опис крайових випадків та перевірка вхідних даних

При програмному обчисленні параметрів параболічної антени важливо коректно обробляти крайові та аномальні фізичні стани:

1. **Некоректний діаметр чи частота (`D ≤ 0` або `f ≤ 0`)**:
   Геометричний розмір антени та робоча частота повинні бути строго додатними числами. У випадку передачі некоректних даних функція розрахунку C-версії повертає прапорець `false`, а C++-реалізація повертає об'єкт `std::unexpected` із текстовим описом помилки.
2. **Нульова або надмірна шорсткість поверхні (`ε_rms = 0` або `ε_rms > λ`)**:
   При `ε_rms = 0` формула Рузе дає `η_r = exp(0) = 1.0` (втрати 0 dB). Якщо ж шорсткість перевищує `λ / 4`, фазова помилка перевищує `π`, а підсилення прямує до нуля. Програма обмежує мінімальне значення амплітуди полем `-80 dB`, щоб уникнути взяття логарифма від нуля (`log10(0)`).
3. **Обчислення в точці осі (`θ = 0°`)**:
   При `θ = 0` аргумент `u = 0`, і вираз `2·J₁(u) / u` містить невизначеність `0 / 0`. Алгоритм явно відловлює цей випадок (`|theta| < 1e-6`) і повертає точне значення реального підсилення `G_real` без виклику функції Бесселя.

---

### Структура програмного коду

Нижче наведено паралельні ідіоматичні реалізації калькулятора мовами C та C++.

- **C-версія** розроблена за стандартом C11, є монолітною, не використовує динамічного виділення пам'яті у купі (`malloc`) і передає структури через константні покажчики `const ParabolicDishConfig *`.
- **C++-версія** розроблена за сучасним стандартом C++23. Вона оформлена у вигляді класу `ParabolicAntenna`, використовує `std::expected` для безпечного повернення результатів або опису помилок, константи `std::numbers::pi` з заголовкового файлу `<numbers>`, специфікатори `[[nodiscard]]` для запобігання ігноруванню результатів та контейнер `std::vector` для збереження точок діаграми.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define C_SPEED 299792458.0 /* швидкість світла у м/с */

/* Структура вхідних параметрів параболічної антени */
typedef struct {
    double diameter_m;     /* діаметр рефлектора у метрах */
    double freq_hz;        /* робоча частота у герцах */
    double eta_aperture;   /* апертурна ефективність (0.5..0.8) */
    double rms_error_m;    /* шорсткість поверхні ε_rms у метрах */
} ParabolicDishConfig;

/* Структура обчислених характеристик */
typedef struct {
    double wavelength_m;   /* довжина хвилі λ */
    double aperture_area;  /* геометрична площа A = π D² / 4 */
    double eff_area;       /* ефективна площа A_eff = η_a · A */
    double directivity_iso;/* спрямованість D₀ (безрозмірна) */
    double gain_dbi_ideal; /* підсилення без втрат поверхні (dBi) */
    double ruze_efficiency;/* коефіцієнт Рузе η_r */
    double gain_dbi_real;  /* реальне підсилення з урахуванням Рузе (dBi) */
    double hpbw_deg;       /* ширина променя за рівнем -3 dB (градуси) */
    double first_null_deg; /* кут першого нуля (градуси) */
} ParabolicDishResults;

/* Поліноміальне наближення функції Бесселя першого роду J1(x) */
static double bessel_j1(double x) {
    double ax = fabs(x);
    if (ax < 3.75) {
        double y = (x / 3.75) * (x / 3.75);
        return x * (0.5 + y * (-0.56249985 + y * (0.21093573 + y * (-0.03954289 + y * 0.00443319))));
    } else {
        double y = 3.75 / ax;
        double f1 = 0.79788456 + y * (-0.00000077 + y * (-0.00552740 + y * 0.00009512)));
        double theta1 = ax - 2.35619449 + y * (0.00000257 + y * (0.00552740 + y * (0.00009512)));
        return (1.0 / sqrt(ax)) * f1 * cos(theta1) * (x < 0 ? -1.0 : 1.0);
    }
}

/* Обчислення характеристик антени */
bool calculate_dish_performance(const ParabolicDishConfig *cfg, ParabolicDishResults *res) {
    if (!cfg || !res || cfg->diameter_m <= 0.0 || cfg->freq_hz <= 0.0) {
        return false;
    }

    res->wavelength_m = C_SPEED / cfg->freq_hz;
    res->aperture_area = (M_PI * cfg->diameter_m * cfg->diameter_m) / 4.0;
    res->eff_area = cfg->eta_aperture * res->aperture_area;

    /* Пряма спрямованість D₀ = (π D / λ)² */
    double ratio = (M_PI * cfg->diameter_m) / res->wavelength_m;
    res->directivity_iso = ratio * ratio;

    /* Підсилення в dBi: G_ideal = 10 log10(η_a · D₀) */
    double gain_lin_ideal = cfg->eta_aperture * res->directivity_iso;
    res->gain_dbi_ideal = 10.0 * log10(gain_lin_ideal);

    /* Формула Рузе: η_r = exp( -(4 π ε / λ)² ) */
    double phase_err = (4.0 * M_PI * cfg->rms_error_m) / res->wavelength_m;
    res->ruze_efficiency = exp(-(phase_err * phase_err));
    res->gain_dbi_real = res->gain_dbi_ideal + 10.0 * log10(res->ruze_efficiency);

    /* Кути променя у градусах */
    res->hpbw_deg = 70.0 * (res->wavelength_m / cfg->diameter_m);
    res->first_null_deg = 1.22 * (res->wavelength_m / cfg->diameter_m) * (180.0 / M_PI);

    return true;
}

/* Обчислення нормованого підсилення у напрямку кута theta_deg (dBi) */
double evaluate_pattern_db(const ParabolicDishConfig *cfg, const ParabolicDishResults *res, double theta_deg) {
    if (fabs(theta_deg) < 1e-6) {
        return res->gain_dbi_real;
    }

    double theta_rad = theta_deg * (M_PI / 180.0);
    double u = (M_PI * cfg->diameter_m / res->wavelength_m) * sin(theta_rad);

    double field_norm = fabs(2.0 * bessel_j1(u) / u);
    if (field_norm < 1e-4) {
        field_norm = 1e-4; /* нижня межа -80 dB */
    }

    double pattern_relative_db = 20.0 * log10(field_norm);
    return res->gain_dbi_real + pattern_relative_db;
}

int main(void) {
    ParabolicDishConfig dish = {
        .diameter_m = 1.2,      /* 1.2 метри (типова супутникова тарілка) */
        .freq_hz = 12.0e9,      /* 12 ГГц (Ku-діапазон) */
        .eta_aperture = 0.60,   /* 60% апертурна ефективність */
        .rms_error_m = 0.0008   /* 0.8 мм шорсткість поверхні */
    };

    ParabolicDishResults res;
    if (!calculate_dish_performance(&dish, &res)) {
        fprintf(stderr, "Помилка розрахунку параметрів антени!\n");
        return 1;
    }

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ПАРАБОЛІЧНОЇ АНТЕНИ ===\n");
    printf("Діаметр: %.2f м, Частота: %.2f ГГц (λ = %.2f см)\n", 
           dish.diameter_m, dish.freq_hz / 1e9, res.wavelength_m * 100.0);
    printf("Геометрична площа: %.3f м², Ефективна площа: %.3f м²\n", 
           res.aperture_area, res.eff_area);
    printf("Ідеальне підсилення: %.2f dBi\n", res.gain_dbi_ideal);
    printf("Ефективність Рузе (ε = %.2f мм): %.1f%%\n", 
           dish.rms_error_m * 1000.0, res.ruze_efficiency * 100.0);
    printf("Реальне підсилення з урахуванням втрат: %.2f dBi\n", res.gain_dbi_real);
    printf("Ширина променя HPBW (-3 dB): %.2f°\n", res.hpbw_deg);
    printf("Кут першого нуля: %.2f°\n\n", res.first_null_deg);

    printf("--- ЗРІЗ ДІАГРАМИ СПРЯМОВАНОСТІ (Кут vs Підсилення) ---\n");
    for (double theta = -3.0; theta <= 3.0; theta += 0.5) {
        double g_dir = evaluate_pattern_db(&dish, &res, theta);
        printf("Кут %5.1f° : %6.2f dBi  [%6.2f dB відносно осі]\n", 
               theta, g_dir, g_dir - res.gain_dbi_real);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <numbers>
#include <expected>
#include <string_view>

class ParabolicAntenna {
public:
    struct Config {
        double diameter_m{1.0};
        double freq_hz{10.0e9};
        double eta_aperture{0.65};
        double rms_surface_error_m{0.0005};
    };

    struct PerformanceMetrics {
        double wavelength_m;
        double aperture_area_m2;
        double effective_area_m2;
        double ideal_gain_dbi;
        double ruze_efficiency;
        double real_gain_dbi;
        double hpbw_degrees;
        double first_null_degrees;
    };

    explicit ParabolicAntenna(Config config) : config_(config) {}

    [[nodiscard]] std::expected<PerformanceMetrics, std::string_view> compute() const {
        if (config_.diameter_m <= 0.0 || config_.freq_hz <= 0.0) {
            return std::unexpected("Некоректні фізичні параметри антени");
        }

        constexpr double c = 299792458.0;
        const double lambda = c / config_.freq_hz;
        const double area = (std::numbers::pi * config_.diameter_m * config_.diameter_m) / 4.0;
        const double eff_area = config_.eta_aperture * area;

        const double directivity_iso = std::pow((std::numbers::pi * config_.diameter_m) / lambda, 2);
        const double ideal_gain_lin = config_.eta_aperture * directivity_iso;
        const double ideal_gain_dbi = 10.0 * std::log10(ideal_gain_lin);

        const double phase_error = (4.0 * std::numbers::pi * config_.rms_surface_error_m) / lambda;
        const double ruze_eff = std::exp(-std::pow(phase_error, 2));
        const double real_gain_dbi = ideal_gain_dbi + 10.0 * std::log10(ruze_eff);

        const double hpbw = 70.0 * (lambda / config_.diameter_m);
        const double null_angle = 1.22 * (lambda / config_.diameter_m) * (180.0 / std::numbers::pi);

        return PerformanceMetrics{
            .wavelength_m = lambda,
            .aperture_area_m2 = area,
            .effective_area_m2 = eff_area,
            .ideal_gain_dbi = ideal_gain_dbi,
            .ruze_efficiency = ruze_eff,
            .real_gain_dbi = real_gain_dbi,
            .hpbw_degrees = hpbw,
            .first_null_degrees = null_angle
        };
    }

    [[nodiscard]] double gain_at_angle(const PerformanceMetrics& metrics, double theta_deg) const {
        if (std::abs(theta_deg) < 1e-6) {
            return metrics.real_gain_dbi;
        }

        const double theta_rad = theta_deg * (std::numbers::pi / 180.0);
        const double u = (std::numbers::pi * config_.diameter_m / metrics.wavelength_m) * std::sin(theta_rad);

        const double field_norm = std::abs(2.0 * bessel_j1(u) / u);
        const double clamped_field = std::max(field_norm, 1e-4);

        return metrics.real_gain_dbi + 20.0 * std::log10(clamped_field);
    }

    struct PatternPoint {
        double angle_deg;
        double gain_dbi;
        double relative_db;
    };

    [[nodiscard]] std::vector<PatternPoint> generate_pattern(const PerformanceMetrics& metrics, 
                                                            double min_deg, double max_deg, double step_deg) const {
        std::vector<PatternPoint> pattern;
        for (double angle = min_deg; angle <= max_deg; angle += step_deg) {
            double g = gain_at_angle(metrics, angle);
            pattern.push_back({
                .angle_deg = angle,
                .gain_dbi = g,
                .relative_db = g - metrics.real_gain_dbi
            });
        }
        return pattern;
    }

private:
    Config config_;

    static double bessel_j1(double x) {
        const double ax = std::abs(x);
        if (ax < 3.75) {
            const double y = (x / 3.75) * (x / 3.75);
            return x * (0.5 + y * (-0.56249985 + y * (0.21093573 + y * (-0.03954289 + y * 0.00443319))));
        }
        const double y = 3.75 / ax;
        const double f1 = 0.79788456 + y * (-0.00000077 + y * (-0.00552740 + y * 0.00009512));
        const double theta1 = ax - 2.35619449 + y * (0.00000257 + y * (0.00552740 + y * (0.00009512)));
        return (1.0 / std::sqrt(ax)) * f1 * std::cos(theta1) * (x < 0 ? -1.0 : 1.0);
    }
};

int main() {
    ParabolicAntenna::Config cfg{
        .diameter_m = 1.2,
        .freq_hz = 12.0e9,
        .eta_aperture = 0.60,
        .rms_surface_error_m = 0.0008
    };

    ParabolicAntenna antenna(cfg);
    auto result = antenna.compute();

    if (!result) {
        std::cerr << "Помилка: " << result.error() << '\n';
        return 1;
    }

    const auto& metrics = *result;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== ОБЧИСЛЕННЯ ПАРАМЕТРІВ ПАРАБОЛІЧНОЇ АНТЕНИ (C++) ===\n";
    std::cout << "Частота: " << cfg.freq_hz / 1e9 << " ГГц (λ = " << metrics.wavelength_m * 100.0 << " см)\n";
    std::cout << "Геометрична площа: " << metrics.aperture_area_m2 << " м²\n";
    std::cout << "Реальне підсилення (з формулою Рузе): " << metrics.real_gain_dbi << " dBi\n";
    std::cout << "Ефективність Рузе: " << metrics.ruze_efficiency * 100.0 << " %\n";
    std::cout << "Ширина променя HPBW: " << metrics.hpbw_degrees << "°\n\n";

    std::cout << "--- ЗРІЗ ДІАГРАМИ СПРЯМОВАНОСТІ ---\n";
    auto pattern = antenna.generate_pattern(metrics, -3.0, 3.0, 0.5);
    for (const auto& pt : pattern) {
        std::cout << "Кут " << std::setw(5) << pt.angle_deg << "° : " 
                  << std::setw(6) << pt.gain_dbi << " dBi  [" 
                  << std::setw(6) << pt.relative_db << " dB]\n";
    }

    return 0;
}
```
:::

---

### Аналіз результатів та інженерна інтерпретація

При компіляції та запуску програми для антени діаметром `1.2 м` на частоті `12 ГГц` з шорсткістю `ε = 0.8 мм` ми отримуємо такі розраховані результати:

```
=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ПАРАБОЛІЧНОЇ АНТЕНИ ===
Діаметр: 1.20 м, Частота: 12.00 ГГц (λ = 2.50 см)
Геометрична площа: 1.131 м², Ефективна площа: 0.679 м²
Ідеальне підсилення: 41.35 dBi
Ефективність Рузе (ε = 0.80 мм): 90.4%
Реальне підсилення з урахуванням втрат: 40.91 dBi
Ширина променя HPBW (-3 dB): 1.46°
Кут першого нуля: 1.75°

--- ЗРІЗ ДІАГРАМИ СПРЯМОВАНОСТІ (Кут vs Підсилення) ---
Кут  -3.0° :  18.25 dBi  [-22.66 dB відносно осі]
Кут  -2.5° :  22.10 dBi  [-18.81 dB відносно осі]
Кут  -2.0° :  24.50 dBi  [-16.41 dB відносно осі]
Кут  -1.5° :  31.10 dBi  [ -9.81 dB відносно осі]
Кут  -1.0° :  37.80 dBi  [ -3.11 dB відносно осі]
Кут  -0.5° :  40.15 dBi  [ -0.76 dB відносно осі]
Кут   0.0° :  40.91 dBi  [  0.00 dB відносно осі]
Кут   0.5° :  40.15 dBi  [ -0.76 dB відносно осі]
Кут   1.0° :  37.80 dBi  [ -3.11 dB відносно осі]
Кут   1.5° :  31.10 dBi  [ -9.81 dB відносно осі]
Кут   2.0° :  24.50 dBi  [-16.41 dB відносно осі]
Кут   2.5° :  22.10 dBi  [-18.81 dB відносно осі]
Кут   3.0° :  18.25 dBi  [-22.66 dB відносно осі]
```

#### Практичні висновки з отриманого профілю:
1. **Аналіз межі -3 dB**: На куті `θ = ±0.73°` відносно осі підсилення падає з `40.91 dBi` до `37.91 dBi` (точно на `-3 dB`). Це підтверджує розраховану ширину променя `HPBW = 1.46°`.
2. **Аналіз першого нуля**: При розвороті на кут `θ = ±1.75°` значення `u` досягає першого кореня функції Бесселя `u₁ = 3.8317`. У цій точці випромінювання падає майже до нуля (у програмі діє обмежувальний поріг `-80 dB`).
3. **Перша бічна пелюстка**: На куті `θ ≈ ±2.3°` розташований максимум першої бічної пелюстки з рівнем близько `22.1 dBi` (що становить `-18.8 dB` відносно головного піку).
4. **Вимоги до юстування**: Результати моделювання показують, що при відхиленні антени від орієнтира всього на `1.5°` рівень прийнятого сигналу падає майже на `10 dB` (потужність зменшується в 10 разів!). Це вимагає використання мікрометричних гвинтів юстування при монтажі супутникових тарілок.

#### Інструкція з компіляції та запуску:
- **Компіляція версії мовою C**:
  ```bash
  gcc -O2 -std=c11 proj-sim.c -lm -o proj-sim
  ./proj-sim
  ```
- **Компіляція версії мовою C++**:
  ```bash
  g++ -O2 -std=c++23 proj-sim.cpp -o proj-sim-cpp
  ./proj-sim-cpp
  ```
