# ⚙️ Чисельне моделювання спектра ЧТ та розрахунок температури зірок

Практична чисельна реалізація алгоритмів обчислення спектральної випромінювальної здатності Планка, чисельного інтегрування потоку за методом Симпсона, підгонки спектра зірок для визначення їхньої температури та пошуку максимуму за методом Ньютона-Рафсона.

---

## 1. Задача чисельного моделювання та алгоритмічна схема

Чисельне моделювання спектрального випромінювання абсолютно чорного тіла є важливим складником розробки оптичних систем, астрофізичних спектрометрів, інфрачервоних сенсорів та систем космічної термостабілізації. Моделювання випромінювання дозволяє інженерам розраховувати потужність сигналів, що потрапляють на чутливі елементи фотоприймачів, та оптимізувати параметри оптичних фільтрів для виявлення теплових об'єктів.

Реалізація цих алгоритмів вимагає вирішення трьох основних обчислювальних задач:

1. **Обчислення точного спектрального розподілу `R(λ, T)`** у заданому діапазоні довжин хвиль від `λ_min` до `λ_max` із надійним захистом від переповнення (floating point overflow) чи ділення на нуль в експоненті при малих довжинах хвиль.
2. **Обчислення інтегральної потужності випромінювання** `R_total = ∫ R(λ, T) dλ` у скінченному спектральному інтервалі (наприклад, у зоні чутливості матриці ІЧ-детектора) методом Симпсона та порівняння результату із теоретичним виразом Стефана-Больцмана `σ · T⁴`.
3. **Оцінка ефективної температури зоряної фотосфери** за виміряним співвідношенням інтенсивностей випромінювання на двох довжинах хвиль `λ₁` та `λ₂` (метод колірної температури).

### 1.1 Алгоритмічні підводні камені та захист обчислень
При розробці високопродуктивного програмного забезпечення для розрахунку спектрів Планка виникають критичні обчислювальні пастки, пов'язані з обмеженнями арифметики з плаваючою комою стандарту IEEE 754:

- **Переповнення при `λ → 0`:** Аргумент експоненти `x = h·c / (λ·k_B·T)` при малих довжинах хвиль стає дуже великим. У типі `double` значення `exp(x)` переповнюється при `x > 709.78`. Для запобігання аварійного завершення алгоритм повинен явно перевіряти аргумент: якщо `x > 700.0`, функція повертає `0.0`, оскільки чисельний внесок таких хвиль є знехтувно малим (`1 / exp(700) < 10⁻³⁰⁴`).
- **Скасування значущих цифр при `λ → ∞`:** При великих довжинах хвиль або дуже високих температурах аргумент `x ≪ 1`. Пряме обчислення `exp(x) - 1` втрачає точність через віднімання близьких чисел. Застосування спеціалізованої математичної функції `expm1(x)` дозволяє зберегти точність до останнього біта мантиси.
- **Ділення на нуль в околі виродження:** При передачі некоректних або від'ємних значень температури чи довжини хвилі алгоритми повинні повертати явний код помилки або некоректний стан (наприклад, через `std::expected` у C++20), запобігаючи генерації нечисел `NaN`.

---

## 2. Реалізація мовами C та C++

У цьому розділі наведено реальні робочі програми мовами C та C++. Для C використовується класична структура з покажчиками та передачею масивів, а для C++20 — сучасна ідіоматична обгортка з `std::expected`, `constexpr` та безпечною обробкою помилок.

:::tabs
```c
/* 
 * blackbody_sim.c — Чисельне моделювання спектра Планка мовою C.
 * Компіляція: gcc -O2 -std=c99 blackbody_sim.c -lm -o blackbody_sim
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Fundamental physical constants (CODATA 2018) */
#define CONST_H  6.62607015e-34  /* Planck constant, J*s */
#define CONST_C  2.99792458e8    /* Speed of light, m/s */
#define CONST_KB 1.380649e-23    /* Boltzmann constant, J/K */
#define CONST_SIGMA 5.670374419e-8 /* Stefan-Boltzmann constant, W/(m^2*K^4) */

/* Spectral radiance R(lambda, T) in W/(m^2 * m) */
double planck_radiation_lambda(double lambda_m, double temp_k) {
    if (lambda_m <= 0.0 || temp_k <= 0.0) {
        return 0.0;
    }
    
    /* Argument of exponential: hc / (lambda * k * T) */
    double exponent_arg = (CONST_H * CONST_C) / (lambda_m * CONST_KB * temp_k);
    
    /* Protection against floating point overflow */
    if (exponent_arg > 700.0) {
        return 0.0;
    }
    
    double denominator = exp(exponent_arg) - 1.0;
    if (denominator <= 0.0) {
        return 0.0;
    }
    
    double numerator = 2.0 * M_PI * CONST_H * CONST_C * CONST_C;
    double lambda5 = lambda_m * lambda_m * lambda_m * lambda_m * lambda_m;
    
    return numerator / (lambda5 * denominator);
}

/* Numerical integration of R(lambda, T) over [lambda_a, lambda_b] using Simpson's 1/3 rule */
double integrate_planck_simpson(double temp_k, double lambda_a, double lambda_b, int num_steps) {
    if (num_steps % 2 != 0) {
        num_steps++; /* Simpson's rule requires an even number of intervals */
    }
    
    double h = (lambda_b - lambda_a) / num_steps;
    double sum = planck_radiation_lambda(lambda_a, temp_k) + planck_radiation_lambda(lambda_b, temp_k);
    
    for (int i = 1; i < num_steps; i++) {
        double lambda = lambda_a + i * h;
        double weight = (i % 2 == 0) ? 2.0 : 4.0;
        sum += weight * planck_radiation_lambda(lambda, temp_k);
    }
    
    return (h / 3.0) * sum;
}

/* Find peak wavelength (Wien's law) using Newton-Raphson method */
double find_wien_peak_lambda(double temp_k) {
    /* Solving 5*(1 - exp(-x)) = x for x */
    double x = 5.0;
    for (int iter = 0; iter < 20; iter++) {
        double f = 5.0 * (1.0 - exp(-x)) - x;
        double f_prime = 5.0 * exp(-x) - 1.0;
        double next_x = x - f / f_prime;
        if (fabs(next_x - x) < 1e-12) {
            x = next_x;
            break;
        }
        x = next_x;
    }
    return (CONST_H * CONST_C) / (CONST_KB * temp_k * x);
}

int main(void) {
    double temp_sun = 5778.0; /* Effective temperature of the Sun, K */
    
    printf("=== МОДЕЛЮВАННЯ ВИПРОМІНЮВАННЯ ЧОРНОГО ТІЛА (Сонце T = %.0f K) ===\n\n", temp_sun);
    
    /* 1. Peak wavelength */
    double lambda_peak = find_wien_peak_lambda(temp_sun);
    printf("1. Максимум випромінювання (Закон Віна):\n");
    printf("   lambda_max = %.2f нм (зелена частина видимого спектра)\n\n", lambda_peak * 1e9);
    
    /* 2. Spectral power density at key wavelengths */
    printf("2. Спектральна випромінювальна здатність R(lambda):\n");
    double test_lambdas_nm[] = {200.0, 380.0, 500.0, 750.0, 1500.0, 3000.0};
    int num_samples = sizeof(test_lambdas_nm) / sizeof(test_lambdas_nm[0]);
    
    for (int i = 0; i < num_samples; i++) {
        double lam_m = test_lambdas_nm[i] * 1e-9;
        double r_val = planck_radiation_lambda(lam_m, temp_sun);
        printf("   lambda = %6.1f нм: R = %12.4e Вт/(м^2 * м)\n", test_lambdas_nm[i], r_val);
    }
    
    /* 3. Total flux integration vs Stefan-Boltzmann theory */
    double lambda_start = 1e-9;    /* 1 nm */
    double lambda_end   = 50e-6;   /* 50 um */
    double flux_simpson = integrate_planck_simpson(temp_sun, lambda_start, lambda_end, 10000);
    double flux_theory  = CONST_SIGMA * pow(temp_sun, 4.0);
    
    printf("\n3. Інтегральний потік випромінювання:\n");
    printf("   Чисельне інтегрування (1 нм - 50 мкм): %.4e Вт/м^2\n", flux_simpson);
    printf("   Теоретичне значення (Закон Стефана-Больцмана): %.4e Вт/м^2\n", flux_theory);
    printf("   Відносна похибка: %.4f%%\n", fabs(flux_simpson - flux_theory) / flux_theory * 100.0);
    
    return 0;
}
```
```cpp
// blackbody_sim.cpp — Ідіоматична реалізація чисельного аналізу спектрів на C++20.
// Компіляція: g++ -O2 -std=c++20 blackbody_sim.cpp -o blackbody_sim

#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <iomanip>

namespace blackbody {

// Константи CODATA 2018 у constexpr
constexpr double h_planck = 6.626'070'15e-34;  // Дж*с
constexpr double c_light  = 2.997'924'58e8;    // м/с
constexpr double k_boltz  = 1.380'649e-23;     // Дж/К
constexpr double stefan_b = 5.670'374'419e-8;  // Вт/(м^2*К^4)

enum class CalculationError {
    InvalidTemperature,
    InvalidWavelength,
    Overflow
};

// Обчислення спектральної випромінювальної здатності Планка R(lambda, T)
[[nodiscard]] constexpr auto planck_radiance(double lambda_m, double temp_k) 
    -> std::expected<double, CalculationError> 
{
    if (temp_k <= 0.0) {
        return std::unexpected(CalculationError::InvalidTemperature);
    }
    if (lambda_m <= 0.0) {
        return std::unexpected(CalculationError::InvalidWavelength);
    }

    const double arg = (h_planck * c_light) / (lambda_m * k_boltz * temp_k);
    if (arg > 700.0) {
        return 0.0; // Експоненційний спад до нуля при малих довжинах хвиль
    }

    const double denom = std::exp(arg) - 1.0;
    if (denom <= 0.0) {
        return std::unexpected(CalculationError::Overflow);
    }

    const double num = 2.0 * std::numbers::pi * h_planck * c_light * c_light;
    const double lambda5 = std::pow(lambda_m, 5);
    return num / (lambda5 * denom);
}

// Чисельне інтегрування за методом Симпсона
[[nodiscard]] auto integrate_spectrum(double temp_k, double lam_start, double lam_end, std::size_t intervals = 10000) 
    -> double 
{
    if (intervals % 2 != 0) {
        intervals++;
    }
    
    const double step = (lam_end - lam_start) / static_cast<double>(intervals);
    double sum = planck_radiance(lam_start, temp_k).value_or(0.0) 
               + planck_radiance(lam_end, temp_k).value_or(0.0);

    for (std::size_t i = 1; i < intervals; ++i) {
        const double lam = lam_start + static_cast<double>(i) * step;
        const double weight = (i % 2 == 0) ? 2.0 : 4.0;
        sum += weight * planck_radiance(lam, temp_k).value_or(0.0);
    }

    return (step / 3.0) * sum;
}

// Знаходження піку випромінювання (закон Віна) методом Ньютона
[[nodiscard]] auto wien_peak_wavelength(double temp_k) -> double {
    double x = 4.96511423;
    for (int iter = 0; iter < 10; ++iter) {
        const double f = 5.0 * (1.0 - std::exp(-x)) - x;
        const double df = 5.0 * std::exp(-x) - 1.0;
        x -= f / df;
    }
    return (h_planck * c_light) / (k_boltz * temp_k * x);
}

// Оцінка температури зорі за відношенням інтенсивностей на двох хвилях R(lambda1) / R(lambda2)
[[nodiscard]] auto estimate_color_temperature(double lambda1, double lambda2, double ratio_measured) -> double {
    double t_low = 1000.0;
    double t_high = 40000.0;
    
    for (int iter = 0; iter < 30; ++iter) {
        double t_mid = 0.5 * (t_low + t_high);
        double r1 = planck_radiance(lambda1, t_mid).value_or(1.0);
        double r2 = planck_radiance(lambda2, t_mid).value_or(1.0);
        double ratio_sim = r1 / r2;
        
        if (ratio_sim < ratio_measured) {
            t_low = t_mid;
        } else {
            t_high = t_mid;
        }
    }
    return 0.5 * (t_low + t_high);
}

} // namespace blackbody

int main() {
    constexpr double temp_sun = 5778.0;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== C++20 МОДЕЛЮВАННЯ СПЕКТРА ЧОРНОГО ТІЛА ===\n\n";

    const double peak_lam = blackbody::wien_peak_wavelength(temp_sun);
    std::cout << "1. Пік випромінювання Віна для T = " << temp_sun << " K: "
              << peak_lam * 1e9 << " нм\n\n";

    // Аналіз по точках
    const std::vector<double> sample_wavelengths_nm{300.0, 400.0, 500.0, 600.0, 700.0, 1000.0};
    std::cout << "2. Спектральні значення R(lambda):\n";
    for (double lam_nm : sample_wavelengths_nm) {
        auto radiance = blackbody::planck_radiance(lam_nm * 1e-9, temp_sun);
        if (radiance) {
            std::cout << "   λ = " << std::setw(5) << lam_nm << " нм -> R = "
                      << std::scientific << *radiance << " Вт/(м^2*м)\n" << std::fixed;
        }
    }

    // Інтегрування
    const double integrated_flux = blackbody::integrate_spectrum(temp_sun, 1e-9, 50e-6);
    const double theoretical_flux = blackbody::stefan_b * std::pow(temp_sun, 4);

    std::cout << "\n3. Перевірка закону Стефана-Больцмана:\n";
    std::cout << "   Чисельний інтеграл: " << std::scientific << integrated_flux << " Вт/м^2\n";
    std::cout << "   Теоретичний потік: " << theoretical_flux << " Вт/м^2\n";
    std::cout << "   Точність: " << std::fixed << (100.0 * (1.0 - integrated_flux / theoretical_flux)) << "%\n";

    // Тест визначення температури зорі
    constexpr double lam_blue = 440e-9;  // B-фільтр
    constexpr double lam_red  = 640e-9;  // R-фільтр
    double r_blue = blackbody::planck_radiance(lam_blue, temp_sun).value_or(1.0);
    double r_red  = blackbody::planck_radiance(lam_red, temp_sun).value_or(1.0);
    double measured_ratio = r_blue / r_red;

    double estimated_temp = blackbody::estimate_color_temperature(lam_blue, lam_red, measured_ratio);
    std::cout << "\n4. Метод колірної температури (оцінка за виміряним відношенням B/R):\n";
    std::cout << "   Задана T = " << temp_sun << " K, відновлена T = " << estimated_temp << " K\n";

    return 0;
}
```
:::

---

## 3. Детальний аналіз математичних методів та результатів розрахунку

### 3.1 Метод Симпсона для складних підінтегральних функцій
Формула Симпсона (параболічних трапецій) заснована на наближенні підінтегральної функції квадратичним поліномом на кожній парі суміжних відрізків. Для гладких невироджених функцій, таких як спектральна випромінювальна здатність Планка, похибка чисельного інтегрування пропорційна четвертому степеню кроку `O(h⁴)`. 

При використанні `10000` інтервалів інтегрування в діапазоні від `1` нм до `50` мкм відносна похибка обчислення повного потоку порівняно з теоретичним законом Стефана-Больцмана `σ · T⁴` становить менше ніж `0.001%`. Невелика залишкова різниця виникає через те, що чисельне інтегрування обмежене верхньою межею `50` мкм, тоді як теоретичний інтеграл обчислюється до нескінченності.

### 3.2 Астрофізичний метод визначення температури зірок
В астрофізиці прямо виміряти абсолютний потік енергії від віддаленої зорі часто неможливо через невизначеність її точної відстані та кутового розміру. Проте співвідношення інтенсивностей випромінювання на двох фіксованих довжинах хвиль `R(λ₁) / R(λ₂)` залежить **виключно від температури фотосфери `T`** і не залежить від відстані до зорі чи її радіуса.

Алгоритм бінарного пошуку або методом ділення навпіл (як показано у функції `estimate_color_temperature`), порівнюючи виміряне відношення фотометричних сигналів (наприклад, синього `B = 440` нм та червоного `R = 640` нм фільтрів) із теоретичною функцією Планка, дозволяє відновити температуру зоряної поверхні з точністю до кількох кельвінів.

### 3.3 Оптимізація обчислень для реального часу
У тепловізійній техніці та мікроболометричних матрицях обчислення спектрального інтеграла виконується для кожного з мільйона пікселів кадрів зі частотою 60 Гц. Пряме чисельне інтегрування функції Планка у реальному часі вимагає забагато обчислювальних ресурсів процесора. Тому на практиці застосовують попередньо розраховані таблиці значень (Look-Up Tables, LUT) або апроксимаційні поліноми Магнуса та Сарджента, які зводять розрахунок температури пікселя до кількох швидких арифметичних операцій.

Крім того, застосування векторних інструкцій сучасної архітектури SIMD (AVX2, AVX-512 або ARM Neon) дозволяє паралельно обчислювати вирази Планка для 8 або 16 пікселів матриці одночасно, забезпечуючи високу продуктивність цифрової обробки відеопотоків термографічних камер.

---

## 4. Чисельний розрахунок колірності Планка у просторі CIE XYZ

Для моделювання візуального сприйняття світла нагрітих тіл людським оком спектральний розподіл Планка `R(λ, T)` інтегрують із трьома стандартними функціями додавання кольору Міжнародної комісії з освітлення (CIE 1931): `x̄(λ)`, `ȳ(λ)` та `z̄(λ)`.

ТРИТИПУЛЬНІ КООРДИНАТИ CIE XYZ обчислюються як:

```
X(T) = ∫ R(λ, T) · x̄(λ) dλ
Y(T) = ∫ R(λ, T) · ȳ(λ) dλ
Z(T) = ∫ R(λ, T) · z̄(λ) dλ
```

Після цього визначають нормовані хроматичні координати `x` та `y`:

```
x = X / (X + Y + Z)
y = Y / (X + Y + Z)
```

При зміні температури від 1000 K до 20 000 K хроматичні координати `(x, y)` описують у колірному просторі плавно вигнуту криву, яка називається **треком Планка** (*Planckian locus*). Нагріте тіло послідовно змінює колір від глибокого червоного (1000 K), оранжевого (2500 K), теплого білого (3000 K), нейтрального білого Сонця (5800 K) до блакитно-синього (15 000 K).

Ці обчислення є базою для розробки алгоритмів балансу білого у цифрових фотоапаратах та систем керування колірною температурою світлодіодних світильників.

---

## 5. Багатохвильова спектральна пірометрія

У реальних промислових умовах вимірювання температури розплавленого металу чи кераміки ускладнюється тим, що коефіцієнт чорноти `ε(λ)` невідомий заздалегідь і змінюється внаслідок окислення поверхні.

Для усунення цієї невизначеності застосовують **багатохвильову пірометрію**. Вимірюючи спектральну яскравість на `N` довжинах хвиль `λ₁, λ₂, ..., λ_N`, складають систему із `N` нелінійних рівнянь:

```
S(λ_i) = ε(λ_i) · B(λ_i, T)
```

Припускаючи, що спектральна залежність коефіцієнта чорноти описується гладкою функцією з малою кількістю параметрів (наприклад, `ln(ε(λ)) = a₀ + a₁ · λ`), систему рівнянь розв'язують методом найменших квадратів (Levenberg-Marquardt), одночасно знаходячи як точну температуру `T`, так і коефіцієнти чорноти поверхні `ε(λ)`.
