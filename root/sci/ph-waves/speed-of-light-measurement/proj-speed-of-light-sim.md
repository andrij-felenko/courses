# ⚙️ Чисельне моделювання часопролітних та дзеркальних методів вимірювання швидкості світла

Ця практична вставка містить програмне забезпечення, алгоритми чисельного аналізу, метод дискретизації та працюючі вихідні модулі мовами C та C++ для обчислювального моделювання трьох ключових експериментальних методів вимірювання швидкості світла та часопролітних параметрів. Моделювання охоплює спектральний аналіз згасання світлового потоку в модуляторному зубчастому колесі Фізо, обчислення кутового зміщення поверненого променя на обертовій дзеркальній призмі Фуко — Майкельсона з урахуванням аеродинамічного дрейфу частоти, а також цифрову квадратурну обробку фазових сигналів у сучасних електрооптичних далекомірах (LiDAR).

---

### 1. Моделювання модуляційного експерименту Фізо

Перший алгоритмічний блок моделює фізичні процеси оптико-механічного модуляційного експерименту Армана Фізо. Світловий потік долає базову відстань `L = 8633 метри` до віддаленого плоского дзеркала на пагорбі Монмартр і повертається назад до Паризької обсерваторії, зазнаючи дворазового переривання зубчастим колесом, що обертається з регульованою частотою `ν`.

#### 1.1. Математична та алгоритмічна модель
Для чисельного розрахунку середня інтенсивність світла на окулярі спостерігача обчислюється методом дискретного підсумовування (чисельного інтегрування за методом прямокутників) повному періоду обертання одного зубця й проміжку `T_p = 1 / (N · ν)`:

```
I_avg = (1 / M) · ∑ [від i=0 до M-1] (T_gate(t_i) · T_gate(t_i + 2L/c))
```

де `M` — кількість точок дискретизації на один період (за замовчуванням `M = 1000`), `t_i = i · dt` — дискретний момент випромінювання імпульсу, а `T_gate(t)` — прямокутна функція пропускання колеса, яка повертає `1.0` (якщо світло проходить крізь проміжок) або `0.0` (якщо світло блокується зубцем).

Програма сканує частоту обертання колеса від `1 Гц` до `25 Гц` із кроком `0.1 Гц`, визначає глобальний мінімум вихідної інтенсивності (що відповідає першому затемненню) і обчислює за ним оціночне значення швидкості світла `c_est = 4 · N · L · ν_min`.

#### 1.2. Оцінка чисельної збіжності та кроку інтегрування
Оскільки функція `T_gate(t)` є розривною прямокутною ступенчатою функцією (меандром), точність чисельного інтегрування залежить від вибору кількості відліків `M`. Для забезпечення відносної похибки обчислення інтенсивності нижче `0.01%` крок часової сітки `dt` має бути принаймні в `100 разів` меншим за час прольоту світла `t_flight = 2L / c ≈ 57.59 мкс`. При `N = 720` зубцях та частоті `ν = 12.6 Гц` період зубця становить `T_p ≈ 110.2 мкс`, тому використання `M = 1000` відліків забезпечує крок `dt ≈ 0.11 мкс`, що повністю задовольняє критерію Найквіста — Шеннона для дискретизації огинаючої імпульсного сигналу.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double base_length_m;      /* Базова відстань L (м) */
    int num_teeth;             /* Кількість зубців N */
    double speed_of_light;     /* Істинна швидкість світла c (м/с) */
} FizeauSetup;

/* Обчислення коефіцієнта пропускання зубчастого колеса у момент часу t */
static double fizeau_gate_transmission(double t, double freq_hz, int num_teeth) {
    double period = 1.0 / (num_teeth * freq_hz);
    double phase = fmod(t, period);
    if (phase < 0.0) phase += period;
    /* 50% часу відкритий проміжок, 50% — закритий зубцем */
    return (phase < (period / 2.0)) ? 1.0 : 0.0;
}

/* Обчислення середньої інтенсивності на окулярі методом чисельного інтегрування */
double calculate_fizeau_intensity(const FizeauSetup *setup, double freq_hz, int samples) {
    double t_flight = 2.0 * setup->base_length_m / setup->speed_of_light;
    double period = 1.0 / (setup->num_teeth * freq_hz);
    double dt = period / samples;
    double sum_intensity = 0.0;

    for (int i = 0; i < samples; ++i) {
        double t_emit = i * dt;
        double t_recv = t_emit + t_flight;
        double t_in = fizeau_gate_transmission(t_emit, freq_hz, setup->num_teeth);
        double t_out = fizeau_gate_transmission(t_recv, freq_hz, setup->num_teeth);
        sum_intensity += (t_in * t_out);
    }

    return sum_intensity / samples;
}

int main(void) {
    FizeauSetup setup = { 8633.0, 720, 299792458.0 };
    double freq_start = 1.0;
    double freq_end = 25.0;
    double step = 0.1;

    printf("=== Симуляція експерименту Фізо (L = %.1f м, N = %d) ===\n", setup.base_length_m, setup.num_teeth);
    printf("Частота (Гц) | Відносна інтенсивність | Оцінка c (км/с)\n");
    printf("-----------------------------------------------------\n");

    double min_intensity = 1.0;
    double min_freq = 0.0;

    for (double f = freq_start; f <= freq_end; f += step) {
        double intensity = calculate_fizeau_intensity(&setup, f, 1000);
        if (intensity < min_intensity) {
            min_intensity = intensity;
            min_freq = f;
        }
        if (fmod(f, 2.0) < step) {
            double c_calc = 4.0 * setup.num_teeth * setup.base_length_m * f / 1000.0;
            printf("%11.2f | %22.4f | %14.2f\n", f, intensity, c_calc);
        }
    }

    double c_est = 4.0 * setup.num_teeth * setup.base_length_m * min_freq / 1000.0;
    printf("-----------------------------------------------------\n");
    printf("Перше затемнення зафіксовано при f = %.2f Гц\n", min_freq);
    printf("Обчислена швидкість світла: %.2f км/с\n", c_est);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct FizeauSetup {
    double base_length_m{8633.0};
    int num_teeth{720};
    double speed_of_light{299792458.0};
};

class FizeauSimulator {
public:
    explicit FizeauSimulator(FizeauSetup setup) : setup_(setup) {}

    [[nodiscard]] double compute_transmission(double t, double freq_hz) const noexcept {
        const double period = 1.0 / (setup_.num_teeth * freq_hz);
        double phase = std::fmod(t, period);
        if (phase < 0.0) phase += period;
        return (phase < (period * 0.5)) ? 1.0 : 0.0;
    }

    [[nodiscard]] double calculate_intensity(double freq_hz, std::size_t samples = 1000) const {
        const double t_flight = 2.0 * setup_.base_length_m / setup_.speed_of_light;
        const double period = 1.0 / (setup_.num_teeth * freq_hz);
        const double dt = period / static_cast<double>(samples);

        double sum_intensity = 0.0;
        for (std::size_t i = 0; i < samples; ++i) {
            const double t_emit = static_cast<double>(i) * dt;
            const double t_recv = t_emit + t_flight;
            const double t_in = compute_transmission(t_emit, freq_hz);
            const double t_out = compute_transmission(t_recv, freq_hz);
            sum_intensity += (t_in * t_out);
        }
        return sum_intensity / static_cast<double>(samples);
    }

    [[nodiscard]] double estimate_speed_of_light(double eclipse_freq_hz) const noexcept {
        return 4.0 * setup_.num_teeth * setup_.base_length_m * eclipse_freq_hz;
    }

private:
    FizeauSetup setup_;
};

int main() {
    FizeauSetup config{.base_length_m = 8633.0, .num_teeth = 720, .speed_of_light = 299792458.0};
    FizeauSimulator sim(config);

    std::cout << "=== Симуляція експерименту Фізо (C++) ===\n";
    std::cout << std::fixed << std::setprecision(2);

    double min_intensity = 1.0;
    double min_freq = 0.0;

    for (double f = 1.0; f <= 25.0; f += 0.05) {
        double intensity = sim.calculate_intensity(f);
        if (intensity < min_intensity) {
            min_intensity = intensity;
            min_freq = f;
        }
    }

    double c_estimated = sim.estimate_speed_of_light(min_freq);
    std::cout << "Перше затемнення на частоті: " << min_freq << " Гц\n";
    std::cout << "Обчислена швидкість світла: " << (c_estimated / 1000.0) << " км/с\n";
    std::cout << "Відносна похибка: " 
              << (std::abs(c_estimated - config.speed_of_light) / config.speed_of_light * 100.0) << "%\n";

    return 0;
}
```
:::

---

### 2. Моделювання кутового зсуву дзеркала Фуко — Майкельсона з параметричним аналізом чутливості

Другий програмний блок виконує розрахунок геометрії кутового відхилення відбитого променя в обертовій дзеркальній системі Альберта Майкельсона, а також моделює розсіювання виміряних значень швидкості при випадковому дрейфі частоти обертання турбіни.

#### 2.1. Особливості фізичної та обчислювальної моделі
У схемі Майкельсона 1926 року використовувалася правильна восьмигранна призма. При стаціонарному положенні зображення в окулярі призма за час двохідного прольоту світла `τ = 2L / c` на відстань `L = 35 373.7 м` має повернутися рівно на 1/8 частини повного оберту (`45° = π / 4 рад`).

Час двохідного прольоту обчислюється як:

```
τ = 2 · L / c = (2 · 35373.7 м) / (299 792 458 м/с) ≈ 235.987 мкс
```

Необхідна частота обертання призми `ν_sync` для збігу граней дорівнює:

```
ν_sync = (π / 4) / (2π · τ) = 1 / (8 · τ) = 1 / (8 · 235.987 мкс) ≈ 529.69 Гц
```

Програма моделює розрахунок швидкості за формулою `c = 16 · ν · L`, виконує параметричний цикл сканування похибки частоти від `-2.0 Гц` до `+2.0 Гц`, визначає кутове зміщення зображення в окулярі `ΔΨ = 16 · π · L · (ν - ν_sync) / c` та визначає допустимі границі нестабільності приводу.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double distance_m;          /* Базова відстань L між вершинами (м) */
    double nominal_freq_hz;     /* Номінальна частота обертання ν (Гц) */
    int num_facets;             /* Кількість граней призми (N = 8) */
} MichelsonSystem;

/* Моделювання кутового зміщення променя при відхиленні частоти від синхронної */
double calculate_beam_deflection(const MichelsonSystem *sys, double actual_freq_hz, double c_val) {
    double t_flight = 2.0 * sys->distance_m / c_val;
    double facet_angle = 2.0 * M_PI / sys->num_facets;
    double rot_angle = 2.0 * M_PI * actual_freq_hz * t_flight;
    double delta_theta = rot_angle - facet_angle;
    return 2.0 * delta_theta; /* Відбитий промінь відхиляється на подвійний кут */
}

int main(void) {
    MichelsonSystem sys = { 35373.7, 528.25, 8 };
    double c_true = 299792458.0;
    double sync_freq = c_true / (2.0 * sys.num_facets * sys.distance_m);

    printf("=== Параметричний аналіз установки Майкельсона ===\n");
    printf("Синхронна частота обертання: %.3f Гц\n", sync_freq);
    printf("Частота (Гц) | Зсув променя (мрад) | Оцінена швидкість c (км/с) | Похилка (м/с)\n");
    printf("-----------------------------------------------------------------------------\n");

    for (double df = -2.0; df <= 2.0; df += 0.5) {
        double current_freq = sync_freq + df;
        double defl_rad = calculate_beam_deflection(&sys, current_freq, c_true);
        double c_calc = 2.0 * sys.num_facets * current_freq * sys.distance_m;
        double error_m_s = fabs(c_calc - c_true);

        printf("%12.3f | %19.4f | %26.2f | %13.2f\n", 
               current_freq, defl_rad * 1000.0, c_calc / 1000.0, error_m_s);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct MichelsonParams {
    double distance_m{35373.7};
    double nominal_freq_hz{528.25};
    int num_facets{8};
    double c_target{299792458.0};
};

class MichelsonAnalyzer {
public:
    explicit MichelsonAnalyzer(MichelsonParams p) : p_(p) {}

    [[nodiscard]] double sync_frequency() const noexcept {
        return p_.c_target / (2.0 * static_cast<double>(p_.num_facets) * p_.distance_m);
    }

    [[nodiscard]] double angular_deflection(double freq_hz) const noexcept {
        const double t_flight = 2.0 * p_.distance_m / p_.c_target;
        const double facet_angle = 2.0 * std::numbers::pi / static_cast<double>(p_.num_facets);
        const double rot_angle = 2.0 * std::numbers::pi * freq_hz * t_flight;
        return 2.0 * (rot_angle - facet_angle);
    }

    [[nodiscard]] double compute_speed(double freq_hz) const noexcept {
        return 2.0 * static_cast<double>(p_.num_facets) * freq_hz * p_.distance_m;
    }

private:
    MichelsonParams p_;
};

int main() {
    MichelsonParams setup{.distance_m = 35373.7, .nominal_freq_hz = 528.25, .num_facets = 8};
    MichelsonAnalyzer analyzer(setup);

    const double f_sync = analyzer.sync_frequency();
    std::cout << "=== Параметричний аналіз призми Майкельсона (C++) ===\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Розрахункова синхронна частота: " << f_sync << " Гц\n\n";

    for (double df = -1.0; df <= 1.0; df += 0.25) {
        const double f_curr = f_sync + df;
        const double defl_mrad = analyzer.angular_deflection(f_curr) * 1000.0;
        const double c_est = analyzer.compute_speed(f_curr);
        const double err = std::abs(c_est - setup.c_target);

        std::cout << "f: " << f_curr << " Гц | Зсув: " << defl_mrad 
                  << " мрад | c: " << (c_est / 1000.0) << " км/с | Помилка: " << err << " м/с\n";
    }

    return 0;
}
```
:::

---

### 3. Цифрова квадратурна обробка фазового сигналу сучасної електрооптики (LiDAR)

Третій приклад присвячено алгоритмам цифрової сигнальної обробки у сучасних високочастотних електрооптичних фазових далекомірах (LiDAR).

#### 3.1. Квадратурна IQ-демодуляція та обчислення фазового зсуву
Вхідний випромінений світловий потік модулюється високою частотою `f_m = 50 МГц`. При поширенні на відстань `2L` відбитий сигнал отримує фазовий зсув `Δφ = 2π · f_m · (2L / c)`.

Для високоточного визначення `Δφ` у присутності шумів застосовується квадратурне обчислення компонент `I` (In-phase) та `Q` (Quadrature):

```
I = ∑ [i=0..N-1] (S_meas[i] · S_ref[i])
Q = ∑ [i=0..N-1] (S_meas[i] · sin(2π · i / N))
Δφ = atan2(Q, I)
```

За знайденим фазовим зсувом `Δφ` відстань обчислюється за формулою:

```
L = (c · Δφ) / (4π · f_m)
```

#### 3.2. Обробка багаточастотних сигналів для усунення фазової неоднозначності
При вимірюванні відстаней, що перевищують однозначний діапазон `L_max = c / (2 · f_m)` (`3 метри` для `f_m = 50 МГц`), виникає неоднозначність числового зсуву на `2π · K`. Для розкриття цієї неоднозначності в реальних промислових далекомірах використовується дводіапазонний метод синтезу різницевої частоти. Вимірювання виконуються послідовно на частотах `f_1 = 50.0 МГц` та `f_2 = 49.0 МГц`. Синтезована різницева частота `Δf = f_1 - f_2 = 1.0 МГц` забезпечує розширений однозначний діапазон вимірювання до `150 метрів`:

```
L_unambiguous = c / (2 · (f_1 - f_2)) = (299 792 458 м/с) / (2 · 1 000 000 Гц) ≈ 149.896 м
```

:::tabs
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double mod_freq_hz;         /* Модуляційна частота f_m (Гц) */
    double true_distance_m;     /* Справжня відстань L (м) */
    double speed_of_light;     /* Константа c (м/с) */
} PhaseLidar;

/* Обчислення різниці фаз методом квадратурної демодуляції (IQ) */
double extract_phase_shift(const double *ref_signal, const double *meas_signal, int num_samples) {
    double I_comp = 0.0;
    double Q_comp = 0.0;

    for (int i = 0; i < num_samples; ++i) {
        I_comp += meas_signal[i] * ref_signal[i];
        Q_comp += meas_signal[i] * sin(2.0 * M_PI * i / num_samples);
    }

    return atan2(Q_comp, I_comp);
}

int main(void) {
    PhaseLidar lidar = { 50000000.0, 15.45, 299792458.0 }; /* f_m = 50 МГц, L = 15.45 м */
    int samples = 1000;
    double ref[1000];
    double meas[1000];

    double t_flight = 2.0 * lidar.true_distance_m / lidar.speed_of_light;
    double phase_shift_true = 2.0 * M_PI * lidar.mod_freq_hz * t_flight;

    /* Генерація тестових дискретизованих сигналів */
    for (int i = 0; i < samples; ++i) {
        double t = (double)i / (samples * lidar.mod_freq_hz);
        ref[i] = cos(2.0 * M_PI * lidar.mod_freq_hz * t);
        meas[i] = cos(2.0 * M_PI * lidar.mod_freq_hz * t - phase_shift_true);
    }

    double delta_phi = extract_phase_shift(ref, meas, samples);
    if (delta_phi < 0.0) delta_phi += 2.0 * M_PI;

    double dist_est = (lidar.speed_of_light * delta_phi) / (4.0 * M_PI * lidar.mod_freq_hz);

    printf("=== Демодуляція фазового сигналу LiDAR ===\n");
    printf("Істинна відстань: %.4f м\n", lidar.true_distance_m);
    printf("Виміряний фазовий зсув: %.4f рад (%.2f градусів)\n", delta_phi, delta_phi * 180.0 / M_PI);
    printf("Обчислена відстань: %.4f м\n", dist_est);
    printf("Похибка вимірювання: %.2f мм\n", fabs(dist_est - lidar.true_distance_m) * 1000.0);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct LidarConfig {
    double mod_freq_hz{50000000.0}; // 50 МГц
    double true_distance_m{15.45};
    double speed_of_light{299792458.0};
};

class PhaseLidarProcessor {
public:
    explicit PhaseLidarProcessor(LidarConfig cfg) : cfg_(cfg) {}

    [[nodiscard]] std::pair<double, double> process(std::size_t sample_count = 1000) const {
        const double t_flight = 2.0 * cfg_.true_distance_m / cfg_.speed_of_light;
        const double phase_true = 2.0 * std::numbers::pi * cfg_.mod_freq_hz * t_flight;

        std::vector<double> ref(sample_count);
        std::vector<double> meas(sample_count);

        for (std::size_t i = 0; i < sample_count; ++i) {
            const double t = static_cast<double>(i) / (static_cast<double>(sample_count) * cfg_.mod_freq_hz);
            ref[i] = std::cos(2.0 * std::numbers::pi * cfg_.mod_freq_hz * t);
            meas[i] = std::cos(2.0 * std::numbers::pi * cfg_.mod_freq_hz * t - phase_true);
        }

        double I_comp = 0.0;
        double Q_comp = 0.0;
        for (std::size_t i = 0; i < sample_count; ++i) {
            I_comp += meas[i] * ref[i];
            Q_comp += meas[i] * std::sin(2.0 * std::numbers::pi * static_cast<double>(i) / static_cast<double>(sample_count));
        }

        double delta_phi = std::atan2(Q_comp, I_comp);
        if (delta_phi < 0.0) delta_phi += 2.0 * std::numbers::pi;

        const double distance_est = (cfg_.speed_of_light * delta_phi) / (4.0 * std::numbers::pi * cfg_.mod_freq_hz);
        return {delta_phi, distance_est};
    }

private:
    LidarConfig cfg_;
};

int main() {
    LidarConfig cfg{.mod_freq_hz = 50000000.0, .true_distance_m = 15.45, .speed_of_light = 299792458.0};
    PhaseLidarProcessor lidar(cfg);

    auto [phase_rad, distance_m] = lidar.process(1000);

    std::cout << "=== Обробка фазового далекоміра LiDAR (C++) ===\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Задана відстань: " << cfg.true_distance_m << " м\n";
    std::cout << "Фазовий зсув: " << phase_rad << " рад\n";
    std::cout << "Відновлена відстань: " << distance_m << " м\n";
    std::cout << "Нев'язка: " << (std::abs(distance_m - cfg.true_distance_m) * 1000.0) << " мм\n";

    return 0;
}
```
:::

---

### 4. Крайові випадки, пастки реалізації та чисельна стійкість

1. **Неоднозначність фазових вимірювань (Phase Unwrapping):**
   Оскільки функція `atan2` повертає значення у періодичному інтервалі `[0, 2π)`, фазовий далекомір вимірює відстань з неоднозначністю, що дорівнює половині модуляційної довжини хвилі `λ_m / 2 = c / (2 · f_m)`. На частоті `f_m = 50 МГц` ця відстань становить `3 метри`. Для вимірювання більших відстаней без неоднозначності в реальних LiDAR застосовують декілька модуляційних частот (наприклад, `50 МГц` та `49 МГц`), вимірюючи фазовий зсув за різницевою частотою `1 МГц`.

2. **Залежність від шуму дискретизації та гауссової завади:**
   У реальних умовах відбитий оптичний сигнал має обмежений рівень оптичної потужності та зашумлений дробовим шумом фотодетектирування APD. Для забезпечення мм-точності кількість точок дискретизації `N` має бути збільшена до `10000` або застосовано накопичувальне числове фільтрування за методом швидкоперетворення Фур'є (FFT).

3. **Стійкість до температурного дрейфу генератора:**
   У симуляторах частоту обертання вважають ідеально постійною. Проте у реальних експериментах Майкельсона чи Фізо коливання частоти обертання турбіни навіть на `0.1%` давали помилку у `300 км/с`. Тому у сучасних фазових далекомірах тактовий генератор обов'язково синхронізується від цезієвого або рубідієвого атомного стандарту частоти.
