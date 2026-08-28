# Акустичний калькулятор шуму повітряного гвинта

Для оцінки акустичної помітності безпілотника, вибору оптимальної кількості лопатей, підбору діаметра гвинта під корисне навантаження та розрахунку санітарних зон шуму потрібен швидкий чисельний інструмент розрахунку спектра звукового тиску. Проектування тихих рушіїв неможливе без зіставлення двох принципово різних типів випромінювання: низькочастотних тональних піків на лопатевих частотах (гармонік BPF) та високочастотного широкосмугового шипіння сходу примежового шару.

Цей проект реалізує комплексний аероакустичний калькулятор на мовах C та C++, що об'єднує класичну формулу Гутіна для дипольного шуму навантаження (Loading Noise), монопольну модель Демінга для шуму витіснення об'єму (Thickness Noise) та напівемпіричну модель Брукса — Поупа — Марколіні (BPM) для широкосмугового шуму сходу турбулентного шару з задньої кромки.

### 1. Теоретичні основи та етапи розрахунку

Розрахунковий конвеєр програми побудовано на послідовному проходженні п'яти фізичних блоків:

#### Крок 1. Кінематика та безрозмірні параметри
На основі діаметра гвинта `D = 2 · R`, числа лопатей `B` та частоти обертання `RPM` визначаються основні кінематичні характеристики:
- Частота обертання вала: `n = RPM / 60` (об/с);
- Кутова швидкість: `Ω = 2π · n` (рад/с);
- Частота проходження лопатей: `BPF = B · n` (Гц);
- Колова швидкість кінців лопатей: `U_tip = Ω · R` (м/с);
- Колове число Маха кінців: `M_tip = U_tip / c₀`, де `c₀ = 343` м/с — швидкість звуку в повітрі при 20 °C.

#### Крок 2. Тональний шум навантаження (дипольна модель Гутіна)
Для кожної гармоніки `m = 1, 2, ..., N` обчислюється її частота `f_m = m · BPF` та порядок функції Бесселя `ν = m · B`.
Аеродинамічні сили (тяга `T` та крутний момент `Q = P / Ω`) вважаються зосередженими на ефективному радіусі прикладання сили `R_eff = 0.80 · R`.
Ефективне число Маха перерізу: `M_eff = 0.80 · M_tip`.

Аргумент циліндричної функції Бесселя першого роду визначається фазовою затримкою на диску:
```
z_m = m · B · M_eff · sin θ
```
де `θ` — полярний кут спостереження відносно осі тяги гвинта.

Середньоквадратичний (RMS) акустичний тиск дипольного шуму навантаження Гутіна становить:
```
p_{load, m} = [ (m · B · Ω) / (2 · 2^(1/2) · π · c₀ · r₀) ] · [ −T · cos θ + (c₀ · Q) / (Ω · R_eff²) ] · J_{mB}(z_m)
```

#### Крок 3. Монопольний шум витіснення товщини (модель Демінга)
Коли лопать зі скінченним об'ємом `V_blade ≈ 0.68 · c · h · R` (де `c` — середня хорда, `h` — максимальна товщина профілю) розсікає середовище, вона витісняє масу газу, створюючи монопольний тиск:
```
p_{thick, m} = − [ (ρ₀ · (m · B · Ω)²) / (2 · 2^(1/2) · π · r₀) ] · V_blade · J_{mB}(z_m)
```

Оскільки монополь товщини та диполь навантаження мають фазовий зсув у 90 градусів (квадратурні джерела), сумарний середньоквадратичний акустичний тиск `m`-ї гармоніки дорівнює:
```
p_m = ( p_{load, m}² + p_{thick, m}² )^(1/2)
```

#### Крок 4. Широкосмуговий шум задньої кромки (модель BPM)
Широкосмугове випромінювання зумовлене дифракцією турбулентних вихорів примежового шару на гострій задній кромці лопаті. Пікова частота широкосмугового спектра визначається числом Струхаля `St = f · δ* / U_eff ≈ 0.10`:
```
f_{peak, bb} = 0.10 · U_eff / δ*
```
де `U_eff ≈ 0.75 · U_tip`, а `δ* ≈ 0.003 · c` — товщина витіснення турбулентного примежового шару перед задньою кромкою.

Піковий акустичний тиск широкосмугового шуму на відстані `r₀` оцінюється за скейлінгом теорії Ффіліпс Вільямса — Голла:
```
p_{bb} = 1.2 · 10⁻⁵ · [ (ρ₀ · U_eff^(2.5) · (δ* · R)^(1/2)) / (c₀ · r₀) ]
```

#### Крок 5. Децибели, логарифмічне підсумовування та психоакустичне А-зважування
Обчислений середньоквадратичний тиск переводиться в рівень звукового тиску (Sound Pressure Level, SPL) у децибелах відносно міжнародного порогу чутності `p_ref = 20` мкПа (`2 · 10⁻⁵` Па):
```
SPL_m = 20 · log10( p_m / p_ref )
```

Оскільки людське вухо має різну чутливість до різних частот (найвища чутливість у смузі 1–4 кГц і значне ослаблення нижче 500 Гц), для оцінки реальної гучності спектр фільтрується стандартною кривою А-зважування IEC 61672-1:
```
SPL_{dBA, m} = SPL_{dB, m} + ΔA(f_m)
```

Повний рівень шуму обчислюється енергетичним інтегруванням усіх тональних гармонік та широкосмугової складової:
```
SPL_{total} = 10 · log10( ∑ 10^(SPL_i / 10) )
```

### 2. Реалізація мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define P_REF 20e-6        /* Опорний акустичний тиск: 20 мкПа */
#define RHO_AIR 1.225      /* Густина повітря на рівні моря, кг/м³ */
#define C_SOUND 343.0      /* Швидкість звуку в повітрі (20 °C), м/с */
#define MAX_HARMONICS 6

typedef struct {
    double diameter_m;     /* Діаметр гвинта, м */
    int num_blades;        /* Кількість лопатей B */
    double rpm;            /* Оберти за хвилину */
    double thrust_n;       /* Сила тяги T, Н */
    double power_w;        /* Споживана потужність P, Вт */
    double chord_m;        /* Середня аеродинамічна хорда лопаті, м */
    double thickness_m;    /* Максимальна товщина профілю лопаті, м */
    double distance_m;     /* Відстань до спостерігача r0, м */
    double angle_deg;      /* Кут спрямованості theta від осі тяги, градуси */
} PropellerParams;

typedef struct {
    double bpf_hz;
    double m_tip;
    double u_tip_mps;
    double harmonic_freq[MAX_HARMONICS];
    double harmonic_spl_db[MAX_HARMONICS];
    double harmonic_spl_dba[MAX_HARMONICS];
    double broadband_peak_freq;
    double broadband_spl_db;
    double total_spl_db;
    double total_spl_dba;
} AcousticResult;

/* Обчислення функції Бесселя першого роду J_n(x) степеневим рядом */
static double bessel_jn_series(int n, double x) {
    if (n < 0) {
        return (n % 2 == 0) ? bessel_jn_series(-n, x) : -bessel_jn_series(-n, x);
    }
    if (x == 0.0) {
        return (n == 0) ? 1.0 : 0.0;
    }
    
    double half_x = 0.5 * x;
    double term = 1.0;
    for (int i = 1; i <= n; ++i) {
        term *= (half_x / (double)i);
    }
    
    double sum = term;
    double half_x_sq = half_x * half_x;
    for (int k = 1; k < 60; ++k) {
        term *= -half_x_sq / ((double)k * (double)(n + k));
        sum += term;
        if (fabs(term) < 1e-15 * fabs(sum)) {
            break;
        }
    }
    return sum;
}

/* Коригувальна вага фільтра A-зважування за стандартом IEC 61672-1 */
static double a_weighting_delta(double freq_hz) {
    if (freq_hz < 10.0) return -70.0;
    double f2 = freq_hz * freq_hz;
    double num = 12194.0 * 12194.0 * f2 * f2;
    double den = (f2 + 20.6 * 20.6) * 
                 sqrt((f2 + 107.7 * 107.7) * (f2 + 737.9 * 737.9)) * 
                 (f2 + 12194.0 * 12194.0);
    double ra = num / den;
    return 20.0 * log10(ra) + 2.0;
}

/* Розрахунок акустичного випромінювання гвинта */
void calculate_propeller_noise(const PropellerParams *p, AcousticResult *res) {
    double radius = 0.5 * p->diameter_m;
    double r_eff = 0.80 * radius;
    double n_rps = p->rpm / 60.0;
    double omega = 2.0 * M_PI * n_rps;
    
    res->bpf_hz = (double)p->num_blades * n_rps;
    res->u_tip_mps = omega * radius;
    res->m_tip = res->u_tip_mps / C_SOUND;
    
    double theta_rad = p->angle_deg * M_PI / 180.0;
    double sin_theta = sin(theta_rad);
    double cos_theta = cos(theta_rad);
    
    double torque = (omega > 0.0) ? (p->power_w / omega) : 0.0;
    double blade_volume = p->chord_m * p->thickness_m * radius * 0.68;
    
    double m_eff = 0.80 * res->m_tip;
    double sum_p_sq = 0.0;
    double sum_p_sq_a = 0.0;
    
    for (int m = 1; m <= MAX_HARMONICS; ++m) {
        int order = m * p->num_blades;
        double freq = (double)m * res->bpf_hz;
        res->harmonic_freq[m - 1] = freq;
        
        double arg_bessel = (double)order * m_eff * sin_theta;
        double j_val = bessel_jn_series(order, arg_bessel);
        
        /* 1. Шум навантаження (диполь Гутіна) */
        double gutin_bracket = -p->thrust_n * cos_theta + 
                               (C_SOUND * torque) / (omega * r_eff * r_eff);
        double p_load = ((double)order * omega / (2.0 * sqrt(2.0) * M_PI * C_SOUND * p->distance_m)) *
                        gutin_bracket * j_val;
        
        /* 2. Шум товщини (монополь Демінга) */
        double p_thick = -(RHO_AIR * pow((double)order * omega, 2) / 
                          (2.0 * sqrt(2.0) * M_PI * p->distance_m)) *
                         blade_volume * j_val;
        
        /* Повний RMS акустичний тиск гармоніки */
        double p_total = sqrt(p_load * p_load + p_thick * p_thick);
        if (p_total < 1e-12) p_total = 1e-12;
        
        double spl_db = 20.0 * log10(p_total / P_REF);
        double a_weight = a_weighting_delta(freq);
        double spl_dba = spl_db + a_weight;
        
        res->harmonic_spl_db[m - 1] = spl_db;
        res->harmonic_spl_dba[m - 1] = spl_dba;
        
        sum_p_sq += pow(10.0, spl_db / 10.0);
        sum_p_sq_a += pow(10.0, spl_dba / 10.0);
    }
    
    /* 3. Широкосмуговий шум задньої кромки (апроксимація моделі BPM) */
    double u_eff = 0.75 * res->u_tip_mps;
    double delta_star = 0.003 * p->chord_m;
    res->broadband_peak_freq = 0.10 * u_eff / delta_star;
    
    double p_bb = 1.2e-5 * (RHO_AIR * pow(u_eff, 2.5) * sqrt(delta_star * radius) / 
                           (C_SOUND * p->distance_m));
    if (p_bb < 1e-12) p_bb = 1e-12;
    res->broadband_spl_db = 20.0 * log10(p_bb / P_REF);
    
    sum_p_sq += pow(10.0, res->broadband_spl_db / 10.0);
    double bb_dba = res->broadband_spl_db + a_weighting_delta(res->broadband_peak_freq);
    sum_p_sq_a += pow(10.0, bb_dba / 10.0);
    
    res->total_spl_db = 10.0 * log10(sum_p_sq);
    res->total_spl_dba = 10.0 * log10(sum_p_sq_a);
}

int main(void) {
    PropellerParams drone_prop = {
        .diameter_m = 0.254,      /* 10 дюймів */
        .num_blades = 2,
        .rpm = 6000.0,
        .thrust_n = 7.5,          /* 7.5 Н тяги (висіння 1.5 кг квадрокоптера) */
        .power_w = 85.0,
        .chord_m = 0.022,
        .thickness_m = 0.0025,
        .distance_m = 10.0,       /* 10 метрів */
        .angle_deg = 110.0        /* Кут максимального випромінювання */
    };
    
    AcousticResult result;
    calculate_propeller_noise(&drone_prop, &result);
    
    printf("=== Аероакустичний розрахунок гвинта дрона ===\n");
    printf("Діаметр: %.1f мм | Лопатей: %d | Оберти: %.0f RPM\n", 
           drone_prop.diameter_m * 1000.0, drone_prop.num_blades, drone_prop.rpm);
    printf("Швидкість кінчиків: %.1f м/с (M_tip = %.3f)\n", 
           result.u_tip_mps, result.m_tip);
    printf("Лопатева частота (BPF): %.1f Гц\n\n", result.bpf_hz);
    
    printf("Тональний спектр (формула Гутіна + шум товщини):\n");
    for (int i = 0; i < MAX_HARMONICS; ++i) {
        printf("  Гармоніка %d (%6.1f Гц): %5.1f дБ | %5.1f дБА\n", 
               i + 1, result.harmonic_freq[i], 
               result.harmonic_spl_db[i], result.harmonic_spl_dba[i]);
    }
    
    printf("\nШирокосмуговий шум (вихід з задньої кромки BPM):\n");
    printf("  Пікова частота: %.0f Гц | Рівень: %.1f дБ\n", 
           result.broadband_peak_freq, result.broadband_spl_db);
           
    printf("\nПідсумковий рівень шуму на відстані %.1f м:\n", drone_prop.distance_m);
    printf("  Сумарний SPL:  %.1f дБ (лінійний)\n", result.total_spl_db);
    printf("  Сумарний SPL:  %.1f дБА (A-зважений)\n", result.total_spl_dba);
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <iomanip>

namespace aeroacoustics {

constexpr double kPref = 20e-6;        // 20 мкПа (поріг чутності)
constexpr double kRhoAir = 1.225;      // кг/м³
constexpr double kSoundSpeed = 343.0;  // м/с (повітря 20 °C)

struct PropellerSpec {
    double diameter_m{0.254};
    int num_blades{2};
    double rpm{6000.0};
    double thrust_n{7.5};
    double power_w{85.0};
    double chord_m{0.022};
    double thickness_m{0.0025};
    double distance_m{10.0};
    double directivity_angle_deg{110.0};
};

struct HarmonicDetail {
    int index{0};
    double frequency_hz{0.0};
    double spl_db{0.0};
    double spl_dba{0.0};
};

struct AcousticReport {
    double bpf_hz{0.0};
    double tip_speed_mps{0.0};
    double tip_mach{0.0};
    std::vector<HarmonicDetail> harmonics;
    double broadband_peak_hz{0.0};
    double broadband_spl_db{0.0};
    double total_spl_db{0.0};
    double total_spl_dba{0.0};
};

// Обчислення функції Бесселя першого роду J_n(x) степеневим рядом
[[nodiscard]] constexpr double bessel_jn(int n, double x) noexcept {
    if (n < 0) {
        return (n % 2 == 0) ? bessel_jn(-n, x) : -bessel_jn(-n, x);
    }
    if (x == 0.0) {
        return (n == 0) ? 1.0 : 0.0;
    }
    
    const double half_x = 0.5 * x;
    double term = 1.0;
    for (int i = 1; i <= n; ++i) {
        term *= (half_x / static_cast<double>(i));
    }
    
    double sum = term;
    const double half_x_sq = half_x * half_x;
    for (int k = 1; k < 60; ++k) {
        term *= -half_x_sq / (static_cast<double>(k) * static_cast<double>(n + k));
        sum += term;
        if (std::abs(term) < 1e-15 * std::abs(sum)) {
            break;
        }
    }
    return sum;
}

// Фільтр частотної корекції A-зважування (IEC 61672-1)
[[nodiscard]] inline double calculate_a_weighting(double freq_hz) noexcept {
    if (freq_hz < 10.0) return -70.0;
    const double f2 = freq_hz * freq_hz;
    const double num = 12194.0 * 12194.0 * f2 * f2;
    const double den = (f2 + 20.6 * 20.6) * 
                       std::sqrt((f2 + 107.7 * 107.7) * (f2 + 737.9 * 737.9)) * 
                       (f2 + 12194.0 * 12194.0);
    return 20.0 * std::log10(num / den) + 2.0;
}

// Розрахунок повної акустичної моделі
[[nodiscard]] AcousticReport evaluate_propeller_noise(const PropellerSpec& spec, int num_harmonics = 6) {
    AcousticReport report;
    const double radius = 0.5 * spec.diameter_m;
    const double r_eff = 0.80 * radius;
    const double n_rps = spec.rpm / 60.0;
    const double omega = 2.0 * std::numbers::pi * n_rps;
    
    report.bpf_hz = static_cast<double>(spec.num_blades) * n_rps;
    report.tip_speed_mps = omega * radius;
    report.tip_mach = report.tip_speed_mps / kSoundSpeed;
    
    const double theta_rad = spec.directivity_angle_deg * std::numbers::pi / 180.0;
    const double sin_theta = std::sin(theta_rad);
    const double cos_theta = std::cos(theta_rad);
    
    const double torque = (omega > 0.0) ? (spec.power_w / omega) : 0.0;
    const double blade_volume = spec.chord_m * spec.thickness_m * radius * 0.68;
    const double m_eff = 0.80 * report.tip_mach;
    
    double linear_energy_sum = 0.0;
    double a_weighted_energy_sum = 0.0;
    
    report.harmonics.reserve(num_harmonics);
    for (int m = 1; m <= num_harmonics; ++m) {
        const int order = m * spec.num_blades;
        const double freq = static_cast<double>(m) * report.bpf_hz;
        const double arg_bessel = static_cast<double>(order) * m_eff * sin_theta;
        const double j_val = bessel_jn(order, arg_bessel);
        
        // 1. Шум навантаження (диполь Гутіна)
        const double gutin_bracket = -spec.thrust_n * cos_theta + 
                                     (kSoundSpeed * torque) / (omega * r_eff * r_eff);
        const double p_load = (static_cast<double>(order) * omega / 
                              (2.0 * std::numbers::sqrt2 * std::numbers::pi * kSoundSpeed * spec.distance_m)) *
                              gutin_bracket * j_val;
                              
        // 2. Шум товщини (монополь Демінга)
        const double p_thick = -(kRhoAir * std::pow(static_cast<double>(order) * omega, 2) / 
                                (2.0 * std::numbers::sqrt2 * std::numbers::pi * spec.distance_m)) *
                                blade_volume * j_val;
                                
        const double p_total = std::max(1e-12, std::sqrt(p_load * p_load + p_thick * p_thick));
        const double spl_db = 20.0 * std::log10(p_total / kPref);
        const double spl_dba = spl_db + calculate_a_weighting(freq);
        
        report.harmonics.push_back({m, freq, spl_db, spl_dba});
        linear_energy_sum += std::pow(10.0, spl_db / 10.0);
        a_weighted_energy_sum += std::pow(10.0, spl_dba / 10.0);
    }
    
    // 3. Широкосмуговий шум сходу з задньої кромки (BPM)
    const double u_eff = 0.75 * report.tip_speed_mps;
    const double delta_star = 0.003 * spec.chord_m;
    report.broadband_peak_hz = 0.10 * u_eff / delta_star;
    
    const double p_bb = std::max(1e-12, 1.2e-5 * (kRhoAir * std::pow(u_eff, 2.5) * 
                                 std::sqrt(delta_star * radius) / (kSoundSpeed * spec.distance_m)));
    report.broadband_spl_db = 20.0 * std::log10(p_bb / kPref);
    
    linear_energy_sum += std::pow(10.0, report.broadband_spl_db / 10.0);
    const double bb_dba = report.broadband_spl_db + calculate_a_weighting(report.broadband_peak_hz);
    a_weighted_energy_sum += std::pow(10.0, bb_dba / 10.0);
    
    report.total_spl_db = 10.0 * std::log10(linear_energy_sum);
    report.total_spl_dba = 10.0 * std::log10(a_weighted_energy_sum);
    
    return report;
}

} // namespace aeroacoustics

int main() {
    using namespace aeroacoustics;
    
    PropellerSpec drone_prop{
        .diameter_m = 0.254,     // 10 дюймів
        .num_blades = 2,
        .rpm = 6000.0,
        .thrust_n = 7.5,         // 7.5 Н тяги
        .power_w = 85.0,
        .chord_m = 0.022,
        .thickness_m = 0.0025,
        .distance_m = 10.0,
        .directivity_angle_deg = 110.0
    };
    
    const auto report = evaluate_propeller_noise(drone_prop);
    
    std::cout << "=== Аероакустичний розрахунок гвинта дрона (C++20) ===\n"
              << std::fixed << std::setprecision(1)
              << "Діаметр: " << drone_prop.diameter_m * 1000.0 << " мм | Лопатей: " 
              << drone_prop.num_blades << " | Оберти: " << drone_prop.rpm << " RPM\n"
              << "Швидкість кінчиків: " << report.tip_speed_mps << " м/с (M_tip = " 
              << std::setprecision(3) << report.tip_mach << ")\n"
              << std::setprecision(1)
              << "Лопатева частота (BPF): " << report.bpf_hz << " Гц\n\n"
              << "Тональний спектр (Гутін + Демінг):\n";
              
    for (const auto& h : report.harmonics) {
        std::cout << "  Гармоніка " << h.index << " (" << std::setw(6) << h.frequency_hz 
                  << " Гц): " << std::setw(5) << h.spl_db << " дБ | " 
                  << std::setw(5) << h.spl_dba << " дБА\n";
    }
    
    std::cout << "\nШирокосмуговий шум (схід з кромки BPM):\n"
              << "  Пікова частота: " << report.broadband_peak_hz << " Гц | Рівень: " 
              << report.broadband_spl_db << " дБ\n"
              << "\nПідсумковий рівень шуму на відстані " << drone_prop.distance_m << " м:\n"
              << "  Сумарний SPL:  " << report.total_spl_db << " дБ (лінійний)\n"
              << "  Сумарний SPL:  " << report.total_spl_dba << " дБА (A-зважений)\n";
              
    return 0;
}
```
:::

### 3. Чисельні пастки, верифікація та інженерний аналіз

#### Чисельні пастки при розрахунку функцій Бесселя
Для високих гармонік багатолопатевих гвинтів порядок функції `ν = m · B` стрімко зростає. Наприклад, для чотирилопатевого гвинта (`B = 4`) на 5-й гармоніці порядок становить `ν = 20`. Якщо при цьому колове число Маха невелике (`M_eff = 0.25`), аргумент Бесселя дорівнює `z = 20 · 0.25 · sin 110° ≈ 4.7`.

У такій конфігурації співвідношення `z / ν ≈ 0.235` перебуває глибоко в зоні субелементарного згасання. Пряме обчислення степеневим рядом вимагає ділення на `20! ≈ 2.43 · 10¹⁸`, що для типів з плаваючою комою одинарної точності (`float`) спричиняє миттєве переповнення діапазону (underflow) до нуля. Реалізація утиліти вимагає використання `double` із подвійною точністю та контролю відносного внеску доданка `fabs(term) < 1e-15 * fabs(sum)`. Для порядків `ν > 40` прямий ряд слід замінювати на зворотно-рекурентну схему Міллера або асимптотичний розклад Дебая.

#### Межі застосування за відстанню (критерій Релея для дальнього поля)
Формула Гутіна строго діє лише в дальній хвильовій зоні спостереження. Відстань до мікрофона `r₀` мусить задовольняти двом геометричним нерівностям:
1. `r₀ ≫ R` (відстань значно більша за радіус диска, щоб джерело можна було вважати компактним);
2. `r₀ > 2 · D² / λ` (критерій хвильової зони Фраунгофера, де фазові спотворення по апертурі диска не перевищують `π/8`).

Для типового дрона з діаметром пропелера `D = 0.254` м на основній частоті `BPF = 200` Гц довжина хвилі становить `λ = 343 / 200 = 1.715` м. Тоді хвильова межа починається з відстані:
```
r_{min} = 2 · (0.254)² / 1.715 ≈ 0.075 м
```
Проте для 5-ї гармоніки (`f₅ = 1000` Гц, `λ = 0.343` м) хвильова межа зсувається далі:
```
r_{min, 5} = 2 · (0.254)² / 0.343 ≈ 0.376 м
```
Вимірювання шуму мікрофоном на відстанях ближче за 1 метр потрапляють у ближню гідродинамічну зону, де пульсації тиску зумовлені локальними неакустичними вихорами обтікання, і формула Гутіна даватиме суттєву похибку.

#### Монтажні ефекти рами та взаємодія з променями
У реальному квадрокоптері пропелер встановлюється над циліндричним або прямокутним променем рами. Коли лопать проходить над променем, виникає стрибок опору та нестаціонарний сплеск піднімальної сили через стиснення повітряного шару між лопаткою та балкою. Цей ефект взаємодії (Blade-Arm Interaction) створює додатковий диполь нестаціонарного навантаження, який підсилює випромінювання на гармоніках BPF на 3–8 дБА порівняно з розрахунком ізольованого гвинта.
