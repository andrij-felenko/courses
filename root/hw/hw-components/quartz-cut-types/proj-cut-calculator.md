# ⚙️ Калькулятор параметрів зрізів кварцу та BVD-моделі

Ця вставка містить інженерний інструмент мовами C та C++ для аналізу та моделювання параметрів кварцових резонаторів різних кристалографічних зрізів. Програма розраховує температурно-частотний дрейф для зрізів AT, BT, SC та годинникових камертонів, оцінює чутливість до похибки кута нарізки пластини, перераховує результати лабораторних вимірювань у чотириелементну еквівалентну схему Баттерворта–ван Дайка (BVD), перевіряє критерії стабільного старту генератора та обчислює накопичену похибку ходу годинника RTC.

### Призначення та алгоритмічна структура інструмента

При проєктуванні прецизійних аналогових та цифрових систем тактування розробник стикається з чотирма взаємопов'язаними інженерними задачами:

1. **Моделювання поведінки частоти в робочому діапазоні:** передбачення максимального відхилення частоти `Δf/f₀` (у ppm) з урахуванням допуску кута нарізки пластини дифрактометром (`angle_offset_min`).
2. **Вилучення фізичних параметрів BVD-моделі:** перетворення виміряних на векторному аналізаторі ланцюгів (VNA) чи імпедансному мосту частот послідовного (`fs`) та паралельного (`fp`) резонансів, статичної ємності (`C₀`) та динамічного опору втрат (`R₁`) у динамічну індуктивність `L₁`, динамічну ємність `C₁` та добротність `Q`.
3. **Оцінка надійності генератора П'єрса:** розрахунок потужності збудження кристала (Drive Level) та коефіцієнта запасу за від'ємним опором (Negative Resistance Margin), що гарантує надійний старт коливань при низьких температурах та захищає кристал від механічного руйнування.
4. **Прогнозування добового дрейфу автономного годинника RTC:** інтегрування параболічної похибки 32.768 кГц камертона для заданого добового теплового профілю.

### Реалізація на мовах C та C++

Нижче наведено повну реалізацію модуля: на стандартному C (структурний інтерфейс) та на ідіоматичному C++20 (об'єктна архітектура, `std::span`, `constexpr` обчислення, робота з `std::optional` та відсутність динамічного виділення пам'яті).

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    CUT_AT,
    CUT_BT,
    CUT_SC,
    CUT_TUNING_FORK_32K
} QuartzCutType;

typedef struct {
    QuartzCutType cut;
    double nominal_freq_hz; /* Номінальна частота в Гц */
    double angle_offset_min; /* Відхилення кута в кутових мінутах (для AT) */
    double t0_deg_c;         /* Температура перегину або вершини */
} QuartzSpec;

typedef struct {
    double fs_hz;    /* Послідовний резонанс */
    double fp_hz;    /* Паралельний резонанс */
    double c0_pf;    /* Статична ємність */
    double r1_ohm;   /* Динамічний опір (ESR) */
    double l1_h;     /* Динамічна індуктивність */
    double c1_ff;    /* Динамічна ємність (фемтофаради) */
    double q_factor; /* Добротність */
    double r_ratio;  /* Відношення ємностей C0 / C1 */
} BvdParameters;

typedef struct {
    double drive_level_uw;     /* Потужність збудження кристала (мкВт) */
    double neg_resistance_ohm; /* Необхідний від'ємний опір інвертора */
    double safety_factor;      /* Коефіцієнт запасу (|R_neg| / R1) */
    bool is_safe_startup;      /* Чи гарантовано безпечний старт */
} OscillatorAnalysis;

/* Розрахунок відхилення частоти (ppm) від температури */
double quartz_calculate_ppm(const QuartzSpec* spec, double temp_deg_c) {
    double dt = temp_deg_c - spec->t0_deg_c;
    
    switch (spec->cut) {
        case CUT_AT: {
            /* Чутливість лінійного коефіцієнта: -0.0847 ppm/(°C · arcmin) */
            double a1 = -0.0847 * spec->angle_offset_min;
            double a2 = -0.0004;
            double a3 = 0.000095;
            return (a1 * dt) + (a2 * dt * dt) + (a3 * dt * dt * dt);
        }
        case CUT_BT: {
            double b2 = -0.040;
            return b2 * dt * dt;
        }
        case CUT_SC: {
            /* SC-зріз: кубічна крива з точкою перегину близько 92 °C */
            double c1 = 0.0;
            double c2 = -0.0003;
            double c3 = 0.000075;
            return (c1 * dt) + (c2 * dt * dt) + (c3 * dt * dt * dt);
        }
        case CUT_TUNING_FORK_32K: {
            double k2 = -0.035;
            return k2 * dt * dt;
        }
        default:
            return 0.0;
    }
}

/* Обчислення параметрів еквівалентної схеми Баттерворта-Ван Дайка */
bool quartz_extract_bvd(double fs_hz, double fp_hz, double c0_pf, double r1_ohm, BvdParameters* out_bvd) {
    if (fs_hz <= 0.0 || fp_hz <= fs_hz || c0_pf <= 0.0 || r1_ohm <= 0.0) {
        return false;
    }
    
    double c0_farads = c0_pf * 1e-12;
    double delta_f = fp_hz - fs_hz;
    
    /* C1 = 2 * C0 * (fp - fs) / fs */
    double c1_farads = 2.0 * c0_farads * (delta_f / fs_hz);
    
    /* L1 = 1 / (4 * pi^2 * fs^2 * C1) */
    double omega_s = 2.0 * M_PI * fs_hz;
    double l1_henry = 1.0 / (omega_s * omega_s * c1_farads);
    
    /* Q = omega_s * L1 / R1 */
    double q = (omega_s * l1_henry) / r1_ohm;
    
    out_bvd->fs_hz = fs_hz;
    out_bvd->fp_hz = fp_hz;
    out_bvd->c0_pf = c0_pf;
    out_bvd->r1_ohm = r1_ohm;
    out_bvd->l1_h = l1_henry;
    out_bvd->c1_ff = c1_farads * 1e15; /* фФ */
    out_bvd->q_factor = q;
    out_bvd->r_ratio = c0_farads / c1_farads;
    
    return true;
}

/* Оцінка стабільності генератора П'єрса */
bool quartz_analyze_oscillator(double freq_hz, double c0_pf, double cl_pf, double r1_ohm, 
                               double vpp_volts, OscillatorAnalysis* out_analysis) {
    if (freq_hz <= 0.0 || cl_pf <= 0.0 || r1_ohm <= 0.0 || vpp_volts <= 0.0) {
        return false;
    }

    double c_total = (c0_pf + cl_pf) * 1e-12;
    double omega = 2.0 * M_PI * freq_hz;
    
    /* Струм через кристал: I_rms = (V_pp / (2 * sqrt(2))) * omega * (C0 + CL) */
    double v_rms = vpp_volts / (2.0 * sqrt(2.0));
    double i_rms = v_rms * omega * c_total;
    
    /* Потужність розсіювання: P = I_rms^2 * R1 */
    double power_watts = i_rms * i_rms * r1_ohm;
    out_analysis->drive_level_uw = power_watts * 1e6;
    
    /* Рекомендований запас за від'ємним опором: |-R| >= 5 * R1 */
    out_analysis->neg_resistance_ohm = 5.0 * r1_ohm;
    out_analysis->safety_factor = 5.0;
    
    /* Критерій безпеки: потужність для ВЧ резонатора < 100 мкВт, для 32 кГц < 1 мкВт */
    double max_allowed_uw = (freq_hz < 100000.0) ? 1.0 : 100.0;
    out_analysis->is_safe_startup = (out_analysis->drive_level_uw <= max_allowed_uw);
    
    return true;
}

/* Розрахунок похибки ходу RTC за добу (секунди) */
double rtc_daily_drift_seconds(double temp_deg_c) {
    QuartzSpec spec = {
        .cut = CUT_TUNING_FORK_32K,
        .nominal_freq_hz = 32768.0,
        .angle_offset_min = 0.0,
        .t0_deg_c = 25.0
    };
    double ppm = quartz_calculate_ppm(&spec, temp_deg_c);
    return (ppm * 1e-6) * 86400.0;
}

/* Інтегрування добового дрейфу за добовим синусоїдальним температурним профілем */
double rtc_diurnal_drift_seconds(double t_mean, double t_amplitude) {
    double total_drift_sec = 0.0;
    int steps = 24; /* 24 погодинні точки */
    for (int h = 0; h < steps; ++h) {
        double hour_angle = (2.0 * M_PI * (double)h) / 24.0;
        double current_temp = t_mean + t_amplitude * sin(hour_angle);
        total_drift_sec += rtc_daily_drift_seconds(current_temp) / 24.0;
    }
    return total_drift_sec;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <string_view>
#include <span>
#include <numbers>
#include <optional>
#include <vector>
#include <iomanip>

enum class QuartzCut {
    AtCut,
    BtCut,
    ScCut,
    TuningFork32k
};

struct QuartzSpec {
    QuartzCut cut{QuartzCut::AtCut};
    double nominal_freq_hz{16'000'000.0};
    double angle_offset_min{0.0}; /* Відхилення кута в кутових мінутах */
    double t0_deg_c{25.0};        /* Точка перегину / вершина параболи */
};

struct BvdModel {
    double fs_hz{0.0};
    double fp_hz{0.0};
    double c0_pf{0.0};
    double r1_ohm{0.0};
    double l1_h{0.0};
    double c1_ff{0.0};            /* фемтофаради (10^-15 Ф) */
    double q_factor{0.0};
    double capacitance_ratio{0.0};
};

struct OscillatorHealth {
    double drive_level_uw{0.0};
    double min_neg_resistance_ohm{0.0};
    double safety_factor{5.0};
    bool is_safe_startup{false};
};

class QuartzAnalyzer {
public:
    [[nodiscard]] static constexpr double calculate_ppm(const QuartzSpec& spec, double temp_deg_c) noexcept {
        const double dt = temp_deg_c - spec.t0_deg_c;
        
        switch (spec.cut) {
            case QuartzCut::AtCut: {
                /* Чутливість першого коефіцієнта: -0.0847 ppm / (°C · arcmin) */
                const double a1 = -0.0847 * spec.angle_offset_min;
                constexpr double a2 = -0.0004;
                constexpr double a3 = 0.000095;
                return (a1 * dt) + (a2 * dt * dt) + (a3 * dt * dt * dt);
            }
            case QuartzCut::BtCut: {
                constexpr double b2 = -0.040;
                return b2 * dt * dt;
            }
            case QuartzCut::ScCut: {
                constexpr double c1 = 0.0;
                constexpr double c2 = -0.0003;
                constexpr double c3 = 0.000075;
                return (c1 * dt) + (c2 * dt * dt) + (c3 * dt * dt * dt);
            }
            case QuartzCut::TuningFork32k: {
                constexpr double k2 = -0.035;
                return k2 * dt * dt;
            }
        }
        return 0.0;
    }

    [[nodiscard]] static std::optional<BvdModel> extract_bvd(
        double fs_hz, double fp_hz, double c0_pf, double r1_ohm) noexcept 
    {
        if (fs_hz <= 0.0 || fp_hz <= fs_hz || c0_pf <= 0.0 || r1_ohm <= 0.0) {
            return std::nullopt;
        }

        const double c0_farads = c0_pf * 1e-12;
        const double delta_f = fp_hz - fs_hz;
        const double c1_farads = 2.0 * c0_farads * (delta_f / fs_hz);
        
        const double omega_s = 2.0 * std::numbers::pi * fs_hz;
        const double l1_henry = 1.0 / (omega_s * omega_s * c1_farads);
        const double q = (omega_s * l1_henry) / r1_ohm;

        return BvdModel{
            .fs_hz = fs_hz,
            .fp_hz = fp_hz,
            .c0_pf = c0_pf,
            .r1_ohm = r1_ohm,
            .l1_h = l1_henry,
            .c1_ff = c1_farads * 1e15,
            .q_factor = q,
            .capacitance_ratio = c0_farads / c1_farads
        };
    }

    [[nodiscard]] static std::optional<OscillatorHealth> analyze_oscillator(
        double freq_hz, double c0_pf, double cl_pf, double r1_ohm, double vpp_volts) noexcept
    {
        if (freq_hz <= 0.0 || cl_pf <= 0.0 || r1_ohm <= 0.0 || vpp_volts <= 0.0) {
            return std::nullopt;
        }

        const double c_total = (c0_pf + cl_pf) * 1e-12;
        const double omega = 2.0 * std::numbers::pi * freq_hz;
        const double v_rms = vpp_volts / (2.0 * std::numbers::sqrt2);
        const double i_rms = v_rms * omega * c_total;
        const double power_watts = i_rms * i_rms * r1_ohm;

        const double max_allowed_uw = (freq_hz < 100'000.0) ? 1.0 : 100.0;
        const double power_uw = power_watts * 1e6;

        return OscillatorHealth{
            .drive_level_uw = power_uw,
            .min_neg_resistance_ohm = 5.0 * r1_ohm,
            .safety_factor = 5.0,
            .is_safe_startup = (power_uw <= max_allowed_uw)
        };
    }

    [[nodiscard]] static constexpr double rtc_daily_drift_seconds(double temp_deg_c) noexcept {
        constexpr QuartzSpec rtc_spec{
            .cut = QuartzCut::TuningFork32k,
            .nominal_freq_hz = 32768.0,
            .angle_offset_min = 0.0,
            .t0_deg_c = 25.0
        };
        const double ppm = calculate_ppm(rtc_spec, temp_deg_c);
        return (ppm * 1e-6) * 86400.0;
    }

    [[nodiscard]] static double rtc_diurnal_drift_seconds(double t_mean, double t_amplitude) noexcept {
        double total_drift = 0.0;
        constexpr int steps = 24;
        for (int h = 0; h < steps; ++h) {
            const double hour_angle = (2.0 * std::numbers::pi * static_cast<double>(h)) / 24.0;
            const double current_temp = t_mean + t_amplitude * std::sin(hour_angle);
            total_drift += rtc_daily_drift_seconds(current_temp) / 24.0;
        }
        return total_drift;
    }
};
```
:::

---

### Покроковий розбір алгоритму та фізичні інваріанти

Розглянемо, як саме працюють розрахункові функції та які фізичні закономірності вони перевіряють:

#### 1. Моделювання температурного поліному (`calculate_ppm`)
Функція реалізує розклад у ряд Тейлора для чотирьох типів кристалографічних зрізів.
Для **AT-зрізу** алгоритм враховує вплив технологічної похибки кута нарізки (`angle_offset_min`). При нульовій похибці лінійний коефіцієнт `a₁` дорівнює нулю, і крива має симетричну S-подібну форму. Якщо кут зміщено на `+1.5′`, функція автоматично обчислює `a₁ = −0.0847 · 1.5 = −0.127 ppm/°C`, нахиляючи криву та показуючи інженеру реальне погіршення стабільності на межах діапазону.
Для **SC-зрізу** кубічний поліном розраховується від точки перегину `T₀ = 92 °C`, що відповідає умовам термостатованого генератора.
Для **BT-зрізу** та **камертона 32 кГц** реалізовано квадратичні параболи з коефіцієнтами `−0.040` та `−0.035` відповідно.

#### 2. Вилучення еквівалентної схеми Баттерворта-Ван Дайка (`extract_bvd`)
Алгоритм базується на точних співвідношеннях між резонансними частотами п'єзоелектричного чотириполюсника:
1. Знаходження динамічної ємності `C₁`:
   Оскільки відносна відстань між паралельним (`fp`) та послідовним (`fs`) резонансами визначається п'єзоелектричним зв'язком `(fp − fs)/fs ≈ C₁ / (2·C₀)`, функція обчислює `C₁ = 2 · C₀ · (fp − fs) / fs`.
2. Знаходження динамічної індуктивності `L₁`:
   Послідовний резонанс визначається формулою Томсона `ωs = 1 / √(L₁·C₁)`. Звідси `L₁ = 1 / (ωs² · C₁)`.
3. Розрахунок добротності `Q`:
   Добротність послідовного механічного контуру обчислюється як відношення характеристичного реактивного опору до опору втрат: `Q = ωs · L₁ / R₁`.

Фізичні інваріанти та перевірка коректності даних:
* `fp` завжди має бути строго більшою за `fs` (`fp > fs`). Якщо вимірювання дали `fp <= fs`, функція повертає помилку (`std::nullopt`), сигналізуючи про некоректне калібрування вимірювального стенда.
* Відношення ємностей `r = C₀ / C₁` для фізично реальних кварців лежить у межах від 150 до 1000. Менші значення свідчать про керамічний резонатор, а більші — про паразитні ємності вимірювального кабелю.

#### 3. Аналіз безпеки генератора П'єрса (`analyze_oscillator`)
Стабільність роботи кварцового генератора залежить від балансу амплітуди й фази в петлі зворотного зв'язку:
1. **Потужність розсіювання (Drive Level):**
   Струм високої частоти через кристал створює напругу `V_rms` на навантажувальній ємності `C_L`. Струм через гілку втрат `R₁` викликає виділення тепла: `P = I_rms² · R₁`. Якщо потужність перевищує 100 мкВт для AT-кварцу, починається прискорене старіння та зсув частоти через термопружний ефект. Для камертона 32 кГц перевищення 1 мкВт може зламати кварцові зубці.
2. **Коефіцієнт запасу за від'ємним опором (Oscillation Allowance):**
   Щоб генератор надійно запускався при екстремальних температурах (де `R₁` зростає через загустіння кріплень), підсилювач повинен забезпечувати від'ємний вхідний опір `|−R_neg|` щонайменше у 5 разів більший за `R₁` кристала (`|−R_neg| ≥ 5·R₁`).

---

### Практичний розрахунковий приклад

Розглянемо роботу аналізатора на реальному прикладі резонатора 16.000 МГц (AT-зріз) у корпусі HC-49/SMD:

Вхідні виміряні параметри:
* `fs = 16 000 000 Гц`
* `fp = 16 032 000 Гц` (`Δf = 32 кГц`)
* `C₀ = 4.5 пФ`
* `R₁ = 25 Ом`
* Навантажувальні конденсатори схеми: `CL1 = CL2 = 22 пФ` (`C_L = 11 пФ + 3 пФ монтажу = 14 пФ`)
* Розмах напруги на виводі інвертора: `V_pp = 2.0 В`

Розрахунок BVD-параметрів:

```
1. Динамічна ємність C1:
C1 = 2 · C0 · (fp - fs) / fs
= 2 · 4.5·10⁻¹² · (32000 / 16000000)
= 9.0·10⁻¹² · 0.002
= 1.8·10⁻¹⁴ Ф = 18.0 фФ

2. Динамічна індуктивність L1:
ωs = 2 · π · 16·10⁶ ≈ 1.0053·10⁸ рад/с
L1 = 1 / (ωs² · C1)
= 1 / ((1.0053·10⁸)² · 1.8·10⁻¹⁴)
= 1 / (1.0106·10¹⁶ · 1.8·10⁻¹⁴)
= 1 / 181.91 ≈ 0.005497 Гн = 5.50 мГн

3. Добротність Q:
Q = ωs · L1 / R1
= (1.0053·10⁸ · 0.00550) / 25
= 552915 / 25 ≈ 22 100

4. Відношення ємностей r:
r = C0 / C1 = 4.5 пФ / 0.018 пФ = 250
```

Розрахунок потужності збудження (Drive Level):

```
C_total = C0 + CL = 4.5 пФ + 14.0 пФ = 18.5 пФ
V_rms = V_pp / (2 · √2) = 2.0 / 2.8284 ≈ 0.707 В
I_rms = V_rms · ω · C_total
= 0.707 · (1.0053·10⁸) · (18.5·10⁻¹²)
= 0.707 · 0.00186 ≈ 1.315·10⁻³ А = 1.315 мА

P_drive = I_rms² · R1
= (1.315·10⁻³)² · 25
= 1.729·10⁻⁶ · 25 ≈ 4.32·10⁻⁵ Вт = 43.2 мкВт
```

Висновок аналізатора:
1. Добротність `Q = 22 100` та відношення ємностей `r = 250` відповідають якісному AT-кварцу.
2. Потужність збудження `43.2 мкВт` менша за гранично допустимі `100 мкВт`, що гарантує довговічність і відсутність термопружного зсуву частоти.
3. Необхідний від'ємний опір інвертора мікроконтролера становить `|−R_neg| ≥ 5 · 25 Ом = 125 Ом`, що легко забезпечується будь-яким сучасним ядром ARM Cortex-M або ESP32.

---

### Практичні методики лабораторного тестування та трасування

При перевірці розрахунків на реальному обладнанні необхідно уникати типових інженерних пасток вимірювання високодобротних кварцових кіл:

#### 1. Методика вимірювання від'ємного опору (Negative Resistance Test)
Для перевірки запасу стійкості генератора в розрив одного з виводів резонатора послідовно впаюють змінний безіндуктивний потенціометр (або набір SMD-резисторів 0402 номіналом від 10 Ом до 1 кОм).
* Поступово збільшують додатковий опір `R_add`, доки генератор не зірве стійкі коливання або перестане запускатися після зняття живлення.
* Граничний від'ємний опір інвертора визначається як:
  ```
  |−R_neg| = R_add_max + R₁
  ```
* Якщо отримане значення `|−R_neg|` менше ніж `5 · R₁`, необхідно або зменшити навантажувальні ємності `C_L` (що знижує навантаження на інвертор), або збільшити струм збудження генератора в регістрах конфігурації мікроконтролера (наприклад, параметр `Drive Strength` у STM32).

#### 2. Запобігання паразитним впливам щупів осцилографа
Підключення стандартного пасивного щупа 10:1 (вхідна ємність 10–15 пФ) безпосередньо до виводу `OSC_IN` чи `OSC_OUT` паралізує роботу генератора або зміщує його частоту на сотні ppm, оскільки ємність щупа додається до навантажувальної ємності `C_L`.
* Правильний метод вимірювання частоти: спостереження за виходом системного тактового сигналу (MCO — Microcontroller Clock Output), де буферизована частота виводиться на звичайний цифровий пін GPIO.
* Якщо необхідно побачити форму коливань на самому кристалі: використовувати тільки активний польовий FET-щуп із вхідною ємністю `< 0.5 пФ` та підключатися виключно до виходу інвертора `OSC_OUT` (низькоомний вихід), а не до чутливого входу `OSC_IN`.

#### 3. Трасування друкованої плати для високочастотних резонаторів
* Кварцовий резонатор і обидва конденсатори `CL1`, `CL2` розміщують на мінімальній відстані від виводів мікроконтролера (довжина доріжок < 5 мм).
* Під резонатором на верхньому шарі забороняється прокладати будь-які інші сигнальні траси.
* Контур заземлення конденсаторів `CL1`, `CL2` з'єднують безпосередньо з найближчою аналоговою землею мікроконтролера (VSS_OSC), утворюючи суцільне захисне кільце *(Guard Ring)*, що екранує слабкий сигнал генератора від цифрових завад силових шин та імпульсних стабілізаторів.

#### 4. Діагностика провалів активності (Activity Dips)
Провали активності — це раптове збільшення еквівалентного послідовного опору `R₁` у вузькому температурному діапазоні (іноді завширшки всього 1–2 °C), що супроводжується локальним стрибком частоти. Вони виникають тоді, коли температурний коефіцієнт небажаної паразитної моди (наприклад, контурного зсуву або згину) перетинає температурну характеристику основної товщинної моди. У точці перетину енергія перекачується в паразитну моду, викликаючи різке падіння добротності.

Для виявлення провалів активності резонатор розміщують у термокамері та повільно (зі швидкістю не більше 0.5 °C/хв) сканують діапазон від −40 °C до +85 °C, безперервно вимірюючи опір `R₁` за допомогою імпедансного аналізатора. Резонатори з провалами активності, де `R₁` перевищує допустимий ліміт інвертора, підлягають відбраковуванню, оскільки в реальному виробі вони спричинять періодичні раптові зависання або зриви тактування процесора при досягненні критичної температури.
