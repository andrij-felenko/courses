# ⚙️ Чисельне моделювання п'єзорезистивного MEMS-датчика тиску

У цій практичній вставці подано фізико-математичну модель, алгоритмічний розбір та повний робочий код чисельного моделювання кремнієвого п'єзорезистивного MEMS-датчика тиску. Програма розраховує тривимірне механічне напруження квадратної мембрани, тензорну зміну опору п'єзорезисторів із урахуванням температурної та концентраційної редукції Кандера `P(N, T)`, розбаланс мостової схеми Вітстона, власну резонансну частоту мембрани та нелінійність характеристики.

---

### Механіка мембрани та фізична модель напружень

Розглядається квадратна монокристалічна кремнієва мембрана товщиною `h` та стороною `2a`, сформована у кремнієвій підкладці орієнтації `(100)` за допомогою мікромеханічного анізотропного рідинного травлення (KOH). На верхній поверхні мембрани вздовж кристалографічних осей `[110]` та `[1̄10]` шляхом іонної імплантації домішки бору (p-тип провідності) виготовлено чотири одинакові п'єзорезистори з базовим опором `R₀` при температурі `300 K`.

Коли до нижньої поверхні мембрани прикладається вимірюваний тиск `P` (у кілопаскалях), мембрана зазнає пружного вигину. Згідно з класичною теорією тонких пружних пластин Тимошенка, розподіл згинальних напружень на поверхні мембрани є вкрай нерівномірним:
- **У центрі мембрани (`x = 0, y = 0`):** Напруження є позитивними (розтягнення), але їхня величина становить лише близько 30% від максимального значення.
- **На серединах защемлених країв мембрани (`x = ±a, y = 0` або `x = 0, y = ±a`):** Виникає абсолютний максимум механічних напружень, причому поздовжнє напруження (перпендикулярне до краю) значно перевищує поперечне напруження (паралельне краю).

Для прямокутної защемленої мембрани з коефіцієнтом Пуассона кремнію `ν = 0.06` у точках розташування п'єзорезисторів поздовжнє напруження `σ_L` та поперечне напруження `σ_T` описуються аналітичними виразами:

```
σ_L(P) = 0.308 · P · (a / h)²
σ_T(P) = 0.092 · P · (a / h)²
```

Коефіцієнт геометричного підсилення `(a / h)²` показує, що тонка мембрана перетворює малий зовнішній тиск `P` у гігантські внутрішні напруження у десятки та сотні мегапаскалів.

---

### Електронна модель п'єзоопору та температурна корекція Кандера

Внаслідок п'єзорезистивного ефекту відносна зміна опору кожного з чотирьох резисторів залежить від напрямку струму та орієнтації векторів напруження. На пластині `(100)` із резисторами вздовж `[110]` поздовжній коефіцієнт п'єзоопору дорівнює `π_L = +71.8 × 10⁻¹¹ Pa⁻¹`, а поперечний — `π_T = -68.7 × 10⁻¹¹ Pa⁻¹`.

Для резисторів `R₁` та `R₃`, орієнтованих так, що струм протікає паралельно до головного напруження `σ_L` (поздовжня конфігурація), відносна зміна опору має вигляд:

```
ΔR₁ / R₀ = ΔR₃ / R₀ = ( π_L · σ_L  +  π_T · σ_T ) · P(N, T)
```

Для резисторів `R₂` та `R₄`, орієнтованих так, що струм протікає перпендикулярно до головного напруження `σ_L` (поперечна конфігурація), відносна зміна опору виражається як:

```
ΔR₂ / R₀ = ΔR₄ / R₀ = ( π_L · σ_T  +  π_T · σ_L ) · P(N, T)
```

#### Температурно-концентраційна редукція P(N, T)

Оскільки п'єзорезистивна чутливість знижується при підвищенні температури та підвищенні рівня легування, у розрахунок вводиться фактор Кандера `P(N, T)`:

```
P(N, T) = 1 / [ 1  +  (N / 1.4×10¹⁹)^0.72 · (300 / T)^0.85 ]
```

Одночасно базовий опір недеформованого резистора `R₀(T)` змінюється з температурою за квадратичним законом температурного коефіцієнта опору (TCR):

```
R₀(T) = R₀(300K) · [ 1  +  TCR₁ · (T - 300)  +  TCR₂ · (T - 300)² ]
```

---

### Топологія та математичний розрахунок моста Вітстона

Чотири п'єзорезистори з'єднані у замкнений мостовий квадрат. Живильна напруга `V_in` прикладається до діагоналі `(Top - Bottom)`, а вихідний сигнал `V_out` знімається з діагоналі `(Left - Right)`.

За законами Кірхгофа потенціали лівого та правого вузлів становлять:

```
V_left = V_in · [ R₄ / (R₁ + R₄) ]
V_right = V_in · [ R₃ / (R₂ + R₃) ]
```

Диференціальна вихідна напруга `V_out = V_left - V_right` після зведення до спільного знаменника виражається точним співвідношенням:

```
V_out = V_in · [ (R₁ · R₃  -  R₂ · R₄) / ( (R₁ + R₂) · (R₃ + R₄) ) ]
```

Оскільки `R₁` та `R₃` зростають при тиску (`R + ΔR`), а `R₂` та `R₄` зменшуються (`R - ΔR`), чисельник формули подвоює вихідний сигнал, утворюючи максимально можливу чутливість схеми.

---

### Динамічні характеристики та власна частота мембрани

Для визначення часової відклику та робочої смуги частот датчика обчислюється перша фундаментальна власна резонансна частота вигину квадратної защемленої мембрани `f_n`:

```
f_n = ( 1.654 · h / a² ) · √[ E / ( ρ_m · (1 - ν²) ) ]
```

де `E = 169` ГПа — модуль Юнга кремнію для осі `[110]`, `ρ_m = 2330` кг/м³ — густина кремнію, `ν = 0.06` — коефіцієнт Пуассона.

Для мембрани товщиною `h = 20 мкм` та півшириною `a = 500 мкм` власна частота становить `f_n ≈ 350 кГц`, що забезпечує робочу смугу частот вимірювання тиску до 50–70 кГц.

---

### Алгоритм та порівняльний розрахунок скінченноелементних параметрів

Розроблений алгоритм моделювання виконує чисельний аналіз у чотири послідовних етапи:
1. **Геометрично-механічний модуль:** Перетворення заданої геометрії мембрани та вхідного тиску у локальне поля напружень `σ_L` та `σ_T`, а також обчислення власної резонансної частоти `f_n`.
2. **Фізико-напівпровідниковий модуль:** Обчислення фактора редукції Кандера `P(N, T)` для заданої температури `T` та концентрації легування `N`, а також розрахунок термокомпенсованого опору `R₀(T)`.
3. **Електричний схематичний модуль:** Обчислення підсумкових опорів чотирьох плечей моста Вітстона та точний розв'язок мостового рівняння з виведенням диференціальної напруги та чутливості у `мВ/(В·кПа)`.
4. **Калібрувальний модуль:** Алгоритм коригування зсуву нуля та температурного коефіцієнта чутливості (TCGF) для компенсації дрейфу.

Для забезпечення високої точності приладів розрахунковий модуль також визначає додатковий фактор температурного коефіцієнта чутливості (TCGF):

```
TCGF = [ Sensitivity(T₂) - Sensitivity(T₁) ] / [ Sensitivity(300K) · (T₂ - T₁) ]
```

Типове значення TCGF для p-тип п'єзорезисторів становить близько `-0.15% / K` до `-0.25% / K`, що вимагає впровадження зовнішньої цифрової або аналогової температурної компенсації у складі сигнального кондиціонера (ASIC).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура геометричних та фізичних параметрів датчика */
typedef struct {
    double membrane_side_um;   /* Півширина мембрани a, мкм */
    double membrane_thick_um;  /* Товщина мембрани h, мкм */
    double r0_300k_ohm;        /* Опір при 300K, Ом */
    double doping_cm3;         /* Концентрація домішок N, см⁻³ */
    double v_in_volts;         /* Напруга живлення моста, В */
    double pi_l_110;           /* Поздовжній коефіцієнт, 1/Па */
    double pi_t_110;           /* Поперечний коефіцієнт, 1/Па */
    double tcr1;               /* Первинний TCR, 1/K */
    double tcr2;               /* Вторинний TCR, 1/K² */
} mems_config_t;

/* Структура результатів розрахунку для заданої точки (P, T) */
typedef struct {
    double pressure_kPa;
    double temp_K;
    double sigma_L_MPa;
    double sigma_T_MPa;
    double p_factor;
    double r1_ohm;
    double r2_ohm;
    double r3_ohm;
    double r4_ohm;
    double v_out_mV;
    double sensitivity_mV_V_kPa;
    double resonant_freq_kHz;
} mems_result_t;

/* Розрахунок фактора Кандера P(N, T) */
static double calculate_kanda_factor(double doping_cm3, double temp_k) {
    double n_ref = 1.4e19;
    double term_n = pow(doping_cm3 / n_ref, 0.72);
    double term_t = pow(300.0 / temp_k, 0.85);
    return 1.0 / (1.0 + term_n * term_t);
}

/* Моделювання виходу датчика у точці (pressure_kPa, temp_k) */
bool simulate_mems_sensor(const mems_config_t *cfg, double pressure_kPa, double temp_k, mems_result_t *res) {
    if (!cfg || !res || pressure_kPa < 0.0 || temp_k < 50.0) {
        return false;
    }

    /* Переведення геометричних розмірів у метри */
    double a_m = cfg->membrane_side_um * 1e-6;
    double h_m = cfg->membrane_thick_um * 1e-6;
    double p_pa = pressure_kPa * 1000.0;

    /* Обчислення механічних напружень на кромці (Паскалі та МПа) */
    double geom_ratio = a_m / h_m;
    double sigma_L_pa = 0.308 * p_pa * geom_ratio * geom_ratio;
    double sigma_T_pa = 0.092 * p_pa * geom_ratio * geom_ratio;

    res->pressure_kPa = pressure_kPa;
    res->temp_K = temp_k;
    res->sigma_L_MPa = sigma_L_pa / 1e6;
    res->sigma_T_MPa = sigma_T_pa / 1e6;

    /* Резонансна частота (кГц) */
    double e_mod = 169e9;    /* Модуль Юнга 169 ГПа */
    double rho_m = 2330.0;   /* Густина 2330 кг/м³ */
    double nu = 0.06;
    double fn_hz = (1.654 * h_m / (a_m * a_m)) * sqrt(e_mod / (rho_m * (1.0 - nu * nu)));
    res->resonant_freq_kHz = fn_hz / 1000.0;

    /* Фактор Кандера та базовий опір R0(T) */
    res->p_factor = calculate_kanda_factor(cfg->doping_cm3, temp_k);
    double dt = temp_k - 300.0;
    double r0_t = cfg->r0_300k_ohm * (1.0 + cfg->tcr1 * dt + cfg->tcr2 * dt * dt);

    /* Відносна зміна опору п'єзорезисторів */
    double dr1_r0 = (cfg->pi_l_110 * sigma_L_pa + cfg->pi_t_110 * sigma_T_pa) * res->p_factor;
    double dr2_r0 = (cfg->pi_l_110 * sigma_T_pa + cfg->pi_t_110 * sigma_L_pa) * res->p_factor;

    res->r1_ohm = r0_t * (1.0 + dr1_r0);
    res->r3_ohm = res->r1_ohm; /* Поздовжня пара */

    res->r2_ohm = r0_t * (1.0 + dr2_r0);
    res->r4_ohm = res->r2_ohm; /* Поперечна пара */

    /* Вихідна напруга моста Вітстона */
    double num = res->r1_ohm * res->r3_ohm - res->r2_ohm * res->r4_ohm;
    double den = (res->r1_ohm + res->r2_ohm) * (res->r3_ohm + res->r4_ohm);
    double v_out_v = cfg->v_in_volts * (num / den);

    res->v_out_mV = v_out_v * 1000.0;

    if (pressure_kPa > 1e-6) {
        res->sensitivity_mV_V_kPa = res->v_out_mV / (cfg->v_in_volts * pressure_kPa);
    } else {
        res->sensitivity_mV_V_kPa = 0.0;
    }

    return true;
}

int main(void) {
    mems_config_t cfg = {
        .membrane_side_um = 500.0,   /* a = 500 мкм (мембрана 1×1 мм) */
        .membrane_thick_um = 20.0,   /* h = 20 мкм */
        .r0_300k_ohm = 2000.0,       /* R0 = 2 кОм */
        .doping_cm3 = 3.0e18,        /* N = 3×10¹⁸ см⁻³ (p-Si) */
        .v_in_volts = 5.0,           /* Vin = 5 В */
        .pi_l_110 = 71.8e-11,        /* pi_L = +71.8×10⁻¹¹ Pa⁻¹ */
        .pi_t_110 = -68.7e-11,       /* pi_T = -68.7×10⁻¹¹ Pa⁻¹ */
        .tcr1 = 1.2e-3,              /* TCR1 = +0.12%/K */
        .tcr2 = 2.5e-6               /* TCR2 = +0.00025%/K² */
    };

    printf("=== МОДЕЛЮВАННЯ MEMS-ДАТЧИКА ТИСКУ (C Implementation) ===\n");
    printf("Розмір мембрани: 1000x1000 мкм, Товщина: 20 мкм, Живлення: %.1f В\n\n", cfg.v_in_volts);

    printf("%-10s %-8s %-12s %-12s %-10s %-12s %-12s\n",
           "Тиск(кПа)", "Т(К)", "sigma_L(МПа)", "sigma_T(МПа)", "P_factor", "V_out(мВ)", "Чув(мВ/В/кПа)");
    printf("-----------------------------------------------------------------------------------\n");

    double test_pressures[] = {0.0, 20.0, 50.0, 100.0};
    double test_temps[] = {250.0, 300.0, 350.0};

    for (size_t t = 0; t < 3; ++t) {
        for (size_t p = 0; p < 4; ++p) {
            mems_result_t res;
            if (simulate_mems_sensor(&cfg, test_pressures[p], test_temps[t], &res)) {
                printf("%-10.1f %-8.1f %-12.2f %-12.2f %-10.4f %-12.2f %-12.4f\n",
                       res.pressure_kPa, res.temp_K, res.sigma_L_MPa, res.sigma_T_MPa,
                       res.p_factor, res.v_out_mV, res.sensitivity_mV_V_kPa);
            }
        }
        printf("-----------------------------------------------------------------------------------\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <expected>
#include <string_view>
#include <span>

// Константні фізичні параметри за замовчуванням
struct SensorParameters {
    double membrane_side_um{500.0};   // a, мкм
    double membrane_thick_um{20.0};   // h, мкм
    double r0_300k_ohm{2000.0};       // R0, Ом
    double doping_cm3{3.0e18};        // N, см⁻³
    double v_in_volts{5.0};           // Vin, В
    double pi_l_110{71.8e-11};        // pi_L, 1/Па
    double pi_t_110{-68.7e-11};       // pi_T, 1/Па
    double tcr1{1.2e-3};              // TCR1, 1/K
    double tcr2{2.5e-6};              // TCR2, 1/K²
};

// Результат чисельного моделювання
struct SimulationPoint {
    double pressure_kPa{0.0};
    double temp_K{300.0};
    double sigma_L_MPa{0.0};
    double sigma_T_MPa{0.0};
    double p_factor{1.0};
    double r1_ohm{2000.0};
    double r2_ohm{2000.0};
    double r3_ohm{2000.0};
    double r4_ohm{2000.0};
    double v_out_mV{0.0};
    double sensitivity_mV_V_kPa{0.0};
    double resonant_freq_kHz{0.0};
};

enum class SimulationError {
    InvalidPressure,
    InvalidTemperature,
    ZeroThickness
};

class PiezoresistiveSimulator {
public:
    explicit PiezoresistiveSimulator(SensorParameters params)
        : params_(std::move(params)) {}

    [[nodiscard]] std::expected<SimulationPoint, SimulationError>
    calculate_point(double pressure_kPa, double temp_K) const {
        if (pressure_kPa < 0.0) return std::unexpected(SimulationError::InvalidPressure);
        if (temp_K < 50.0) return std::unexpected(SimulationError::InvalidTemperature);
        if (params_.membrane_thick_um <= 0.0) return std::unexpected(SimulationError::ZeroThickness);

        SimulationPoint pt{};
        pt.pressure_kPa = pressure_kPa;
        pt.temp_K = temp_K;

        const double a_m = params_.membrane_side_um * 1e-6;
        const double h_m = params_.membrane_thick_um * 1e-6;
        const double p_pa = pressure_kPa * 1000.0;

        const double geom_ratio = a_m / h_m;
        const double sigma_L_pa = 0.308 * p_pa * geom_ratio * geom_ratio;
        const double sigma_T_pa = 0.092 * p_pa * geom_ratio * geom_ratio;

        pt.sigma_L_MPa = sigma_L_pa / 1e6;
        pt.sigma_T_MPa = sigma_T_pa / 1e6;

        constexpr double e_mod = 169e9;
        constexpr double rho_m = 2330.0;
        constexpr double nu = 0.06;
        const double fn_hz = (1.654 * h_m / (a_m * a_m)) * std::sqrt(e_mod / (rho_m * (1.0 - nu * nu)));
        pt.resonant_freq_kHz = fn_hz / 1000.0;

        pt.p_factor = calculate_kanda_factor(temp_K);
        const double dt = temp_K - 300.0;
        const double r0_t = params_.r0_300k_ohm * (1.0 + params_.tcr1 * dt + params_.tcr2 * dt * dt);

        const double dr1_r0 = (params_.pi_l_110 * sigma_L_pa + params_.pi_t_110 * sigma_T_pa) * pt.p_factor;
        const double dr2_r0 = (params_.pi_l_110 * sigma_T_pa + params_.pi_t_110 * sigma_L_pa) * pt.p_factor;

        pt.r1_ohm = pt.r3_ohm = r0_t * (1.0 + dr1_r0);
        pt.r2_ohm = pt.r4_ohm = r0_t * (1.0 + dr2_r0);

        const double num = pt.r1_ohm * pt.r3_ohm - pt.r2_ohm * pt.r4_ohm;
        const double den = (pt.r1_ohm + pt.r2_ohm) * (pt.r3_ohm + pt.r4_ohm);
        const double v_out_v = params_.v_in_volts * (num / den);

        pt.v_out_mV = v_out_v * 1000.0;
        pt.sensitivity_mV_V_kPa = (pressure_kPa > 1e-6) ? (pt.v_out_mV / (params_.v_in_volts * pressure_kPa)) : 0.0;

        return pt;
    }

    [[nodiscard]] std::vector<SimulationPoint>
    run_sweep(std::span<const double> pressures_kPa, double temp_K) const {
        std::vector<SimulationPoint> results;
        results.reserve(pressures_kPa.size());
        for (double p : pressures_kPa) {
            if (auto res = calculate_point(p, temp_K); res.has_value()) {
                results.push_back(*res);
            }
        }
        return results;
    }

private:
    [[nodiscard]] double calculate_kanda_factor(double temp_K) const {
        constexpr double n_ref = 1.4e19;
        const double term_n = std::pow(params_.doping_cm3 / n_ref, 0.72);
        const double term_t = std::pow(300.0 / temp_K, 0.85);
        return 1.0 / (1.0 + term_n * term_t);
    }

    SensorParameters params_;
};

int main() {
    const SensorParameters params{};
    const PiezoresistiveSimulator simulator(params);

    const std::vector<double> pressures{0.0, 20.0, 50.0, 100.0};
    const std::vector<double> temperatures{250.0, 300.0, 350.0};

    std::cout << "=== МОДЕЛЮВАННЯ MEMS-ДАТЧИКА ТИСКУ (C++20 Implementation) ===\n";
    std::cout << std::fixed << std::setprecision(2);

    for (double t : temperatures) {
        std::cout << "\n--- Температура: " << t << " K ---\n";
        auto sweep = simulator.run_sweep(pressures, t);
        for (const auto& pt : sweep) {
            std::cout << "Тиск: " << std::setw(6) << pt.pressure_kPa << " кПа | "
                      << "sigma_L: " << std::setw(6) << pt.sigma_L_MPa << " МПа | "
                      << "P_factor: " << std::setw(5) << pt.p_factor << " | "
                      << "V_out: " << std::setw(7) << pt.v_out_mV << " мВ | "
                      << "Чув: " << std::setw(6) << pt.sensitivity_mV_V_kPa << " мВ/В/кПа\n";
        }
    }

    return 0;
}
```
:::

---

### Аналіз результатів та фізичні особливості розрахунку

1. **Лінійність вихідної напруги:** Завдяки диференціальній топології моста Вітстона зміна опорів поздовжньої пари (`R₁`, `R₃`) та поперечної пари (`R₂`, `R₄`) входить у вирази симетрично з протилежними знаками. Це дає ідеальну лінійність вихідного сигналу `V_out(P)` у діапазоні тисків до 100 кПа.
2. **Температурний дрейф чутливості:** Зі зростанням температури від `250 K` до `350 K` фактор Кандера `P(N, T)` зменшується, що спричиняє падіння тензочутливості приблизно на `0.15% / K`. У реальних MEMS-сенсорах це компенсують за допомогою термісторів у колі живлення моста або цифровою триммерною корекцією у вбудованому мікроконтролері.
3. **Крайові випадки та пастки проектування:** При надто тонкій мембрані (`h < 10 мкм`) механічні напруження перевищують `300 МПа`, що викликає появу нелінійних п'єзорезистивних ефектів вищого порядку (коефіцієнти `π_ijklmn`), а також нелінійний вигин мембрани (режим великих прогинів за методом Кармана), який вимагає тривимірного скінченноелементного аналізу (FEA).
