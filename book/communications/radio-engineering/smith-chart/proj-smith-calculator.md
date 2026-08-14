# ⚙️ Обчислювач діаграми Сміта та вузлів узгодження

Розробка високочастотних радіочастотних трактів (Wi-Fi 2.4/5.8 ГГц, LoRa 868 МГц, BLE, GPS/GNSS) вимагає автоматизованого синтезу узгоджувальних кіл безпосередньо у програмному забезпеченні векторних аналізаторів кіл (VNA), прошивках автономних вимірювальних приладів та системах автоматизованого проектування (САПР). Створення надійної програмної бібліотеки для обчислень на діаграмі Сміта спирається не лише на базові алгебраїчні формули, а й на глибоке врахування фізичних обмежень реальних дискретних компонентів та друкованих мікросмужкових ліній.

---

### 1. Фізична мотивація та архітектура розрахунків

При проектуванні вихідного каскаду підсилювача потужності (PA) або вхідного каскаду малошумного підсилювача (LNA) імпеданс транзистора чи антени суттєво відрізняється від опорного опору тракту `Z₀ = 50 Ом`. Наприклад, вихідний транзистор підсилювача може мати вхідний імпеданс `Z_in = 5 - j15 Ом` на частоті `2.45 ГГц`. Якщо підключити його безпосередньо до `50`-омної антени, коефіцієнт відбиття перевищить `0.85`, а понад `72%` потужності відіб'ється назад, перегріваючи кристал.

Задача програмного модуля — автоматично сформувати оптимальну топологію узгоджувальної L-мережі, обчислити значення реактивних елементів, а також розрахувати метрики відбиття:
* **Комплексний коефіцієнт відбиття (`Γ`):** Вектор `Γ = Γ_r + jΓ_i` у полярних або декартових координатах.
* **Модуль коефіцієнта відбиття (`|Γ|`):** Ам амплітудне відношення відбитої хвилі до падаючої (`0 ≤ |Γ| ≤ 1`).
* **Фаза коефіцієнта відбиття (`∠Γ`):** Кут зсуву фази відбитої хвилі у градусах чи радіанах.
* **Коефіцієнт стоячої хвилі (SWR / КСХ):** Відношення максимуму напруги стоячої хвилі до мінімуму (`1.0 ≤ SWR < ∞`).
* **Втрати на відбиття (Return Loss, RL):** Відношення падаючої потужності до відбитої в децибелах (`RL = -20 log₁₀|Γ|`).
* **Втрати неузгодження (Mismatch Loss, ML):** Частка потужності, втрачена через відбиття (`ML = -10 log₁₀(1 - |Γ|²)`).

---

### 2. Математичний алгоритм синтезу 4 топологій L-мереж

Двоелементна L-мережа складається з одного реактивного елемента, ввімкненого паралельно (із реактивною провідністю `B_p`), та одного реактивного елемента, ввімкненого послідовно (із реактивним опором `X_s`).

Розрізняють два математичні класи задач залежно від співвідношення активного опору навантаження `R_L` та хвильового опору `Z₀`:

#### Клас А: Активний опір менший за хвильовий (`R_L < Z₀`)
Оскільки початковий опір `R_L` менший за `Z₀`, точка імпедансу лежить поза колом `r = 1.0`. Для того щоб трансформувати опір у `Z₀`, необхідно спочатку підключити **паралельний елемент** з провідністю `B_p`. Паралельний елемент переміщує нормований адмітанс вздовж кола постійної провідності `g = R_L / Z₀` до перетину з колом опору `r = 1.0`. Після цього **послідовним елементом** з опором `X_s` точка зміщується вздовж кола `r = 1.0` строго у центр діаграми `(1.0 + j0)`.

Формули для обчислення паралельної провідності `B_p` та послідовного опору `X_s`:

```
Дискримінант:  D = R_L · (R_L² + X_L² - R_L · Z₀)

B_p1 = (X_L + √(R_L / Z₀) · √D) / (R_L² + X_L²)
X_s1 = (1 / B_p1) + (X_L · Z₀) / R_L - Z₀ / (B_p1 · R_L)

B_p2 = (X_L - √(R_L / Z₀) · √D) / (R_L² + X_L²)
X_s2 = (1 / B_p2) + (X_L · Z₀) / R_L - Z₀ / (B_p2 · R_L)
```

Два розв'язки дають дві фундаментальні топології:
1. **Топологія ФНЧ (Low-Pass L-network):** Паралельний конденсатор `C` (`B_p > 0`) + Послідовна індуктивність `L` (`X_s > 0`). Ця схема придушує вищі гармоніки передавача, тому її обирають у 90% випадків для підсилювачів потужності.
2. **Топологія ФВЧ (High-Pass L-network):** Паралельна індуктивність `L` (`B_p < 0`) + Послідовний конденсатор `C` (`X_s < 0`). Ця схема блокує постійну складову напруги живлення (DC blocking) та зрізає низькочастотні завади.

#### Клас Б: Активний опір більший за хвильовий (`R_L > Z₀`)
Якщо початковий активний опір `R_L` більший за `Z₀`, точка лежить усередині кола `r = 1.0`. Спочатку умикають **послідовний елемент** `X_s`, який виводить імпеданс на коло провідності `g = 1.0`, після чого **паралельним елементом** `B_p` точку зміщують у центр `(1.0 + j0)`.

Формули для Класу Б:

```
X_s1 = -X_L + √(R_L · (Z₀ - R_L) + X_L²)
B_p1 = √(Z₀ / R_L - 1 + (X_L / R_L)²) / Z₀

X_s2 = -X_L - √(R_L · (Z₀ - R_L) + X_L²)
B_p2 = -√(Z₀ / R_L - 1 + (X_L / R_L)²) / Z₀
```

---

### 3. Фізичні обмеження та реальні SMD-компоненти

При переведенні розрахованих значень `B_p` та `X_s` у фізичні Фаради та Генрі необхідно враховувати обмеження реальної компонентної бази:

```
C = B_p / (2π · f)
L = X_s / (2π · f)
```

#### Паразитні ефекти чип-компонентів (корпуси 0402 / 0603):
1. **Власна резонансна частота (Self-Resonant Frequency, SRF):** Будь-яка SMD-індуктивність володіє паразитною міжевитковою ємністю. На частотах вище SRF індуктивність втрачає свої властивості та перетворюється на конденсатор! Наприклад, індуктивність `10 нГн` у корпусі `0402` зазвичай має SRF біля `3.5 ГГц`. На частоті `5.8 ГГц` її використовувати неможливо.
2. **Добротність компонентів (Q-factor):** Реальні індуктивності мають послідовний опір втрат `ESR`, а їхня добротність `Q = X_L / ESR` становить лише `15..40` на частотах `2.4 ГГц`. Реальні керамічні конденсатори (типу NPO/C0G) мають добротність `Q > 200..500`. Тому втрати у синтезованій L-мережі майже повністю визначаються добротністю індуктивності.
3. **Крок номіналів рядів E24 / E96:** Розраховані значення (наприклад, `1.68 пФ` та `3.98 нГн`) відсутні у стандартних рядах номіналів. Програма повинна розраховувати чутливість КСХ до округлення номіналів до найближчих стандартних значень `1.8 пФ` та `3.9 нГн`.

---

### 4. Шлейфове узгодження на мікросмужкових лініях (Single-Stub Tuning)

На надвисоких частотах (понад `3–5 ГГц`) використання дискретних SMD-компонентів стає неефективним через паразитні параметри розварювальних площадок. Замість дискретних C та L використовують **відрізки мікросмужкових ліній (шлейфи)**, витравлені безпосередньо на друкованій платі.

Одношлейфове узгодження (Single-Stub Matching) полягає у підключенні на відстані `d` від навантаження паралельного шлейфу довжиною `l`:
* **Відстань `d`:** Вибирається так, щоб вхідний адмітанс лінії у точці підключення мав дійсну частину `Re{y(d)} = 1.0`.
* **Довжина шлейфу `l`:** Вибирається так, щоб реактивна провідність шлейфу `b_stub` була рівною за модулем та протилежною за знаком реактивній провідності лінії `b(d)`: `b_stub = -b(d)`.

Для короткозамкненого шлейфу (Short-Circuited Stub) провідність дорівнює `b_stub = -cot(βl)`.
Для відкритого шлейфу (Open-Circuited Stub) провідність дорівнює `b_stub = tan(βl)`.

---

### 5. Повний програмний код мовами C та C++

Наводимо завершений, автономний код обчислювального модуля. Реалізація мовою C99 використовує стандартний заголовок `<complex.h>` і орієнтована на вбудовані мікроконтролери та прошивки VNA. Реалізація мовою C++17 використовує `std::complex`, `std::optional` та об'єктно-орієнтовану інкапсуляцію.

:::tabs
```c
/* ============================================================================
 * C99 Implementation: Full RF Smith Chart & L-Match Calculator Module
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    L_TOPOLOGY_PARALLEL_C_SERIES_L = 0,
    L_TOPOLOGY_PARALLEL_L_SERIES_C = 1,
    L_TOPOLOGY_SERIES_L_PARALLEL_C = 2,
    L_TOPOLOGY_SERIES_C_PARALLEL_L = 3,
    L_TOPOLOGY_UNSUPPORTED = -1
} l_topology_t;

typedef struct {
    double complex z_raw;
    double complex z_norm;
    double complex gamma;
    double gamma_mag;
    double gamma_phase_deg;
    double vswr;
    double return_loss_db;
    double mismatch_loss_db;
} rf_smith_point_t;

typedef struct {
    l_topology_t topology;
    double c_farads;
    double l_henries;
    bool valid;
} l_match_solution_t;

/* Комплексний аналіз точки на діаграмі Сміта */
rf_smith_point_t rf_smith_analyze(double complex z_load, double z0) {
    rf_smith_point_t pt;
    pt.z_raw = z_load;
    
    if (z0 <= 0.0) {
        z0 = 50.0;
    }
    
    pt.z_norm = z_load / z0;
    pt.gamma = (pt.z_norm - 1.0) / (pt.z_norm + 1.0);
    pt.gamma_mag = cabs(pt.gamma);
    pt.gamma_phase_deg = carg(pt.gamma) * 180.0 / M_PI;

    if (pt.gamma_mag >= 0.9999) {
        pt.vswr = 999.0;
        pt.return_loss_db = 0.0;
        pt.mismatch_loss_db = 99.0;
    } else {
        pt.vswr = (1.0 + pt.gamma_mag) / (1.0 - pt.gamma_mag);
        pt.return_loss_db = -20.0 * log10(pt.gamma_mag);
        pt.mismatch_loss_db = -10.0 * log10(1.0 - pt.gamma_mag * pt.gamma_mag);
    }
    
    return pt;
}

/* Синтез ФНЧ L-мережі для навантаження R_L < Z₀ */
l_match_solution_t rf_smith_solve_lowpass_r_less(double complex z_load, double z0, double freq_hz) {
    l_match_solution_t sol;
    sol.valid = false;
    sol.topology = L_TOPOLOGY_PARALLEL_C_SERIES_L;
    sol.c_farads = 0.0;
    sol.l_henries = 0.0;

    double r_l = creal(z_load);
    double x_l = cimag(z_load);
    double omega = 2.0 * M_PI * freq_hz;

    if (r_l <= 0.0 || r_l >= z0 || omega <= 0.0) {
        return sol;
    }

    double rad = r_l * (r_l * r_l + x_l * x_l - r_l * z0);
    if (rad < 0.0) {
        return sol;
    }

    double b_p = (x_l + sqrt(r_l / z0) * sqrt(rad)) / (r_l * r_l + x_l * x_l);
    double x_s = (1.0 / b_p) + (x_l * z0) / r_l - z0 / (b_p * r_l);

    if (b_p > 0.0 && x_s > 0.0) {
        sol.c_farads = b_p / omega;
        sol.l_henries = x_s / omega;
        sol.valid = true;
    }

    return sol;
}

/* Друкований вивід звіту розрахунку */
void rf_smith_print_report(double complex z_load, double z0, double freq_hz) {
    rf_smith_point_t pt = rf_smith_analyze(z_load, z0);
    
    printf("=====================================================\n");
    printf("     ЗВІТ АНАЛІЗУ ДІАГРАМИ СМІТА ТА УЗГОДЖЕННЯ\n");
    printf("=====================================================\n");
    printf("Робоча частота:     %.2f МГц\n", freq_hz / 1e6);
    printf("Опорний опір Z₀:    %.1f Ом\n", z0);
    printf("Опір навантаження:  %.2f + j(%.2f) Ом\n", creal(z_load), cimag(z_load));
    printf("Нормований опір z:  %.3f + j(%.3f)\n", creal(pt.z_norm), cimag(pt.z_norm));
    printf("-----------------------------------------------------\n");
    printf("Комплексний Γ:       %.4f + j(%.4f)\n", creal(pt.gamma), cimag(pt.gamma));
    printf("Модуль |Γ|:          %.4f\n", pt.gamma_mag);
    printf("Фаза ∠Γ:             %.2f°\n", pt.gamma_phase_deg);
    printf("КСХ (VSWR):          %.2f : 1\n", pt.vswr);
    printf("Return Loss (RL):    %.2f дБ\n", pt.return_loss_db);
    printf("Mismatch Loss (ML):  %.2f дБ\n", pt.mismatch_loss_db);
    printf("-----------------------------------------------------\n");

    l_match_solution_t sol = rf_smith_solve_lowpass_r_less(z_load, z0, freq_hz);
    if (sol.valid) {
        printf("СИНТЕЗОВАНО L-МЕРЕЖУ (ФНЧ, R_L < Z₀):\n");
        printf("  - Паралельний конденсатор (C): %.2f пФ\n", sol.c_farads * 1e12);
        printf("  - Послідовна індуктивність (L): %.2f нГн\n", sol.l_henries * 1e9);
    } else {
        printf("УВАГА: Потрібна інша топологія (R_L >= Z₀ або висока реактивність).\n");
    }
    printf("=====================================================\n\n");
}

int main(void) {
    /* Приклад 1: Wi-Fi антена 2.45 ГГц */
    rf_smith_print_report(25.0 + 50.0 * I, 50.0, 2.45e9);

    /* Приклад 2: Низькоомний транзистор 915 МГц */
    rf_smith_print_report(10.0 - 15.0 * I, 50.0, 915.0e6);

    return 0;
}
```
```cpp
// ============================================================================
// C++17/C++20 Implementation: Modern Smith Engine & Matching Solver
// ============================================================================
#include <iostream>
#include <complex>
#include <cmath>
#include <optional>
#include <numbers>
#include <iomanip>
#include <string_view>

namespace rf::smith {

enum class LMatchTopology {
    ParallelC_SeriesL,
    ParallelL_SeriesC,
    SeriesL_ParallelC,
    SeriesC_ParallelL
};

struct SmithPointMetrics {
    std::complex<double> z_raw;
    std::complex<double> z_norm;
    std::complex<double> gamma;
    double gamma_mag;
    double gamma_phase_deg;
    double vswr;
    double return_loss_db;
    double mismatch_loss_db;
};

struct LMatchSolution {
    LMatchTopology topology;
    double c_farads{0.0};
    double l_henries{0.0};
};

class Calculator {
public:
    [[nodiscard]] static SmithPointMetrics analyze(
        std::complex<double> z_load, double z0 = 50.0) noexcept 
    {
        if (z0 <= 0.0) z0 = 50.0;

        const std::complex<double> z_norm = z_load / z0;
        const std::complex<double> gamma = (z_norm - 1.0) / (z_norm + 1.0);
        const double mag = std::abs(gamma);
        const double phase_deg = std::arg(gamma) * 180.0 / std::numbers::pi;

        if (mag >= 0.9999) {
            return {z_load, z_norm, gamma, mag, phase_deg, 999.0, 0.0, 99.0};
        }

        const double vswr = (1.0 + mag) / (1.0 - mag);
        const double rl_db = -20.0 * std::log10(mag);
        const double ml_db = -10.0 * std::log10(1.0 - mag * mag);

        return {z_load, z_norm, gamma, mag, phase_deg, vswr, rl_db, ml_db};
    }

    [[nodiscard]] static std::optional<LMatchSolution> synthesize_lowpass_r_less(
        std::complex<double> z_load, double freq_hz, double z0 = 50.0) noexcept 
    {
        const double r_l = z_load.real();
        const double x_l = z_load.imag();
        const double omega = 2.0 * std::numbers::pi * freq_hz;

        if (r_l <= 0.0 || r_l >= z0 || omega <= 0.0) {
            return std::nullopt;
        }

        const double rad = r_l * (r_l * r_l + x_l * x_l - r_l * z0);
        if (rad < 0.0) {
            return std::nullopt;
        }

        const double b_p = (x_l + std::sqrt(r_l / z0) * std::sqrt(rad)) / (r_l * r_l + x_l * x_l);
        const double x_s = (1.0 / b_p) + (x_l * z0) / r_l - z0 / (b_p * r_l);

        if (b_p <= 0.0 || x_s <= 0.0) {
            return std::nullopt;
        }

        return LMatchSolution{
            LMatchTopology::ParallelC_SeriesL,
            b_p / omega,
            x_s / omega
        };
    }
};

void print_analysis(std::complex<double> z_load, double freq_hz, double z0 = 50.0) {
    const auto m = Calculator::analyze(z_load, z0);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "--- Звіт аналізу Smith Engine (C++17) ---\n";
    std::cout << "Частота:            " << freq_hz / 1e6 << " МГц\n";
    std::cout << "Імпеданс Z_L:       " << z_load.real() << " + j(" << z_load.imag() << ") Ом\n";
    std::cout << "Коефіцієнт Γ:       " << m.gamma.real() << " + j(" << m.gamma.imag() << ")\n";
    std::cout << "Модуль |Γ|:          " << m.gamma_mag << "\n";
    std::cout << "КСХ (VSWR):          " << std::setprecision(2) << m.vswr << " : 1\n";
    std::cout << "Return Loss:        " << m.return_loss_db << " дБ\n";

    if (const auto sol = Calculator::synthesize_lowpass_r_less(z_load, freq_hz, z0)) {
        std::cout << "L-Мережа (ФНЧ):      C = " << sol->c_farads * 1e12 << " пФ, L = "
                  << sol->l_henries * 1e9 << " нГн\n";
    }
    std::cout << "-----------------------------------------\n\n";
}

} // namespace rf::smith

int main() {
    rf::smith::print_analysis({25.0, 50.0}, 2.45e9);
    rf::smith::print_analysis({15.0, -30.0}, 868.0e6);
    return 0;
}
```
:::
