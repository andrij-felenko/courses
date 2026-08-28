# ⚙️ Інженерний калькулятор монтажу: перевантаження, болти, демпфування та тепло

При проєктуванні вузлів монтажу корисного навантаження інженер одночасно розв'язує три зв'язані фізичні задачі, які не можна розглядати окремо:

1. **Міцнісний розрахунок кріпильних елементів:** перевірка зрізу та розтягу різьбових з'єднань під дією максимальних експлуатаційних перевантажень при маневрах (`G_maneuver = 3–5 g`) та короткочасних ударних перевантажень при жорсткому приземленні (`G_impact = 10–15 g`);
2. **Динамічний аналіз віброізоляції:** визначення власної частоти пружного підвісу `f_0` та перевірка коефіцієнта передавання вібрації `T_R`, щоб уникнути резонансу з оборотними частотами моторів (`f_rot`) та частотою проходження лопатей (`f_BPF`);
3. **Термодинамічний розрахунок охолодження:** прогнозування температури переходу кремнієвого кристала `T_j` для енергоємних AI-процесорів (15–35 Вт) з урахуванням швидкості набігаючого повітряного потоку та площі конвективних ребер радіатора.

## 1. Фізична та розрахункова модель верифікатора

### Механіка болтового з'єднання за Губером-Мізесом

Під дією ударного прискорення `G_impact` на модуль масою `m` діє повна сила інерції `F_total = m · G_impact · g`. При просторовому ударі під кутом 45° на кожен із `N_bolts` болтів припадає комбіноване навантаження, що викликає нормальне напруження розтягу `σ` та дотичне напруження зрізу `τ`:

```
σ = F_tensile / A_core
τ = F_shear / A_core
```

де `A_core` — площа поперечного перерізу стрижня болта по западинах різьби (для M2 це 2.07 мм², для M3 — 5.03 мм², для M4 — 8.78 мм²). Еквівалентне напруження пластичної течії розраховується за четвертою теорією міцності (енергетичний критерій питомої потенціальної енергії формозміни Губера-Мізеса):

```
σ_eq = √ ( σ² + 3 · τ² )
```

Коефіцієнт запасу міцності `SF = σ_yield / σ_eq` повинен перевищувати нормативний поріг `SF ≥ 1.50` для цивільних апаратів або `SF ≥ 2.0` для авіаційних систем підвищеної надійності.

### Динамічний відгук на ударний імпульс

Коли безпілотник зазнає удару об землю або перешкоду, прискорення являє собою напівсинусоїдальний імпульс тривалістю `τ_shock ≈ 10–25 мс`. Динамічний коефіцієнт підсилення удару залежить від співвідношення тривалості імпульсу до власного періоду коливань підвісу `T_0 = 1 / f_0`.

Якщо власна частота підвісу `f_0 = 20 Гц` (`T_0 = 50 мс`), відношення `τ_shock / T_0 ≈ 0.3–0.4` лежить в області динамічного пом'якшення: пружні демпфери встигають деформуватися, поглинаючи до 40–60% пікового зусилля удару, перш ніж воно передасться на чутливу оптику та електроніку сенсора.

### Віброізоляція та частотний відгук

Сукупність `N_dampers` силіконових демпферів із жорсткістю `k_single` утворює пружний вузол із власною частотою:

```
f_0 = (1 / (2 · π)) · √ ( (N_dampers · k_single) / m )
```

На найнижчих обертах двигунів `RPM_min` (режим посадки або кволого зависання) частота збурення `f_rot_min = RPM_min / 60` повинна задовольняти критерій відношення частот `r = f_rot_min / f_0 ≥ 2.5–3.0`. Коефіцієнт передачі коливань `T_R` при коефіцієнті демпфування силікону `ζ ≈ 0.20–0.28` розраховується як:

```
T_R = √ [ (1 + (2 · ζ · r)²) / ((1 - r²)² + (2 · ζ · r)²) ]
```

Підвіс вважається динамічно безпечним, якщо `T_R ≤ 0.25` (гаситься понад 75% вібраційної енергії рами) і повністю відсутній ризик входу в резонансний пік на робочих обертах.

### Фретинг-корозія та вібраційний брязкіт контактів Pogo Pins

Окремим критичним аспектом модульного монтажу є поведінка контактів Pogo Pins під дією випадкової вібрації широкого спектра (англ. *Random Vibration*). Якщо амплітуда відносного мікрозсуву між золоченим штифтом і контактним майданчиком перевищує 5–10 мкм, виникає механічне стирання гальванічного шару золота. Оголений нікелевий підшар на повітрі окислюється з утворенням твердих діелектричних оксидів (фретинг-корозія), що призводить до стрибкоподібного зростання контактного опору з 20 мОм до 2–5 Ом та втрати пакетів шини Ethernet або скидання живлення процесора. Для запобігання цьому явищу сила попереднього стиску пружини штифта повинна гарантувати відсутність мікроковзання при пікових прискореннях маневру.

### Конвективне тепловідведення в польоті

Тепловий опір радіатора «поверхня-середовище» `R_θsa` залежить від ефективної площі ребер `A_heatsink` та коефіцієнта конвективної тепловіддачі `h_conv`. Примусова конвекція в польоті моделюється емпіричною залежністю від швидкості набігаючого потоку `v_air` (м/с):

```
h_conv = 10.0 + 6.5 · (v_air)^0.8  [Вт/(м²·К)]
R_θsa = 1 / (h_conv · A_heatsink)
```

Сумарний перепад температури від кристала до повітря складається з трьох ланок: `R_θ_total = R_θjc + R_θcs + R_θsa`. Прогнозована температура кристала `T_j = T_ambient + P_watts · R_θ_total` порівнюється з максимально допустимою температурою кремнію `T_j_max` з обов'язковим інженерним запасом не менше 10 °C.

## 2. Реалізація верифікатора на C та C++

Нижче наведено самодостатній інженерний модуль верифікації, який може виконуватися як на бортовому комп'ютері перед польотним завданням, так і в складі наземної станції планування місій.

:::tabs
```c
// mounting_validator.c — Інженерний калькулятор надійності монтажу навантаження на БПЛА
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ── 1. Вхідні структури даних ───────────────────────────────────────────────

typedef struct {
    float yield_strength_mpa;  // Межа плинності матеріалу болта, МПа (наприклад, 900 для 10.9)
    float core_area_mm2;       // Площа перерізу різьбового стрижня, мм² (M3 = 5.03 мм²)
    int   bolt_count;          // Кількість болтів кріплення
} BoltConfig;

typedef struct {
    float mass_kg;             // Повна маса модуля навантаження, кг
    float power_watts;         // Теплове виділення електроніки, Вт
    float t_junction_max_c;    // Гранична робоча температура кремнію, °C
    float r_th_jc_c_per_w;     // Тепловий опір "перехід-корпус", °C/Вт
    float r_th_cs_c_per_w;     // Тепловий опір термоінтерфейсу (TIM), °C/Вт
    float heatsink_area_m2;    // Площа ребер алюмінієвого радіатора, м²
} PayloadConfig;

typedef struct {
    float damper_k_single_n_per_m; // Жорсткість одного демпфера, Н/м
    int   damper_count;            // Кількість демпферів у паралельній схемі
    float damping_ratio_zeta;      // Коефіцієнт демпфування (типово 0.20-0.28 для силікону)
} DamperConfig;

typedef struct {
    float rpm_min;             // Мінімальні оберти моторів, об/хв
    float rpm_max;             // Максимальні оберти моторів, об/хв
    int   blade_count;         // Кількість лопатей на гвинті (2 або 3)
    float g_maneuver;          // Максимальне перевантаження маневру, g (наприклад, 4.5)
    float g_impact;            // Ударне перевантаження при жорсткій посадці, g (наприклад, 12.0)
    float t_ambient_c;         // Температура навколишнього повітря, °C
    float airspeed_m_s;        // Швидкість набігаючого потоку, м/с (0 для висіння)
} FlightEnv;

// ── 2. Результати розрахунку ────────────────────────────────────────────────

typedef struct {
    float bolt_shear_stress_mpa;
    float bolt_tensile_stress_mpa;
    float bolt_von_mises_mpa;
    float bolt_safety_factor;
    bool  bolt_ok;

    float natural_freq_hz;
    float f_rot_min_hz;
    float f_rot_max_hz;
    float transmissibility_at_min_rpm;
    bool  resonance_safe;

    float r_th_sa_c_per_w;
    float total_r_th_c_per_w;
    float predicted_t_junction_c;
    bool  thermal_ok;
} ValidationReport;

// ── 3. Функції інженерного аналізу ──────────────────────────────────────────

ValidationReport validate_mounting(const PayloadConfig *p, const BoltConfig *b,
                                  const DamperConfig *d, const FlightEnv *env) {
    ValidationReport rep = {0};
    const float g_const = 9.80665f;

    // 1. Механічний аналіз болтового кріплення при ударі g_impact
    float total_impact_force_n = p->mass_kg * env->g_impact * g_const;
    float force_per_bolt_n = total_impact_force_n / (float)b->bolt_count;

    // Припускаємо просторове навантаження: розклад сили на зріз і розтяг під кутом 45°
    float shear_force = force_per_bolt_n * 0.7071f;
    float tensile_force = force_per_bolt_n * 0.7071f;

    rep.bolt_shear_stress_mpa = shear_force / b->core_area_mm2;
    rep.bolt_tensile_stress_mpa = tensile_force / b->core_area_mm2;

    // Еквівалентне напруження за Губером-Мізесом: sigma_eq = sqrt(sigma^2 + 3*tau^2)
    rep.bolt_von_mises_mpa = sqrtf(
        rep.bolt_tensile_stress_mpa * rep.bolt_tensile_stress_mpa +
        3.0f * rep.bolt_shear_stress_mpa * rep.bolt_shear_stress_mpa
    );

    rep.bolt_safety_factor = b->yield_strength_mpa / rep.bolt_von_mises_mpa;
    rep.bolt_ok = (rep.bolt_safety_factor >= 1.5f); // Нормативний запас >= 1.5

    // 2. Динамічний аналіз демпферів та віброізоляції
    float k_total = d->damper_k_single_n_per_m * (float)d->damper_count;
    rep.natural_freq_hz = (1.0f / (2.0f * (float)M_PI)) * sqrtf(k_total / p->mass_kg);

    rep.f_rot_min_hz = env->rpm_min / 60.0f;
    rep.f_rot_max_hz = env->rpm_max / 60.0f;

    // Перевірка найнижчої частоти: r = f_rot_min / f_0
    float r = rep.f_rot_min_hz / rep.natural_freq_hz;
    float zeta = d->damping_ratio_zeta;

    float tr_num = 1.0f + powf(2.0f * zeta * r, 2.0f);
    float tr_den = powf(1.0f - r * r, 2.0f) + powf(2.0f * zeta * r, 2.0f);
    rep.transmissibility_at_min_rpm = sqrtf(tr_num / tr_den);

    // Безпечно, якщо f_0 < f_rot_min / sqrt(2) і TR <= 0.25 (гасіння > 75%)
    rep.resonance_safe = (rep.natural_freq_hz * 1.4142f < rep.f_rot_min_hz) &&
                         (rep.transmissibility_at_min_rpm <= 0.25f);

    // 3. Тепловий аналіз радіатора в повітряному потоці
    // Модель примусової конвекції вздовж ребер: h_forced ≈ 10 + 6.5 * (v^0.8)
    float h_coeff = 10.0f + 6.5f * powf(fmaxf(env->airspeed_m_s, 0.0f), 0.8f);
    rep.r_th_sa_c_per_w = 1.0f / (h_coeff * p->heatsink_area_m2);

    rep.total_r_th_c_per_w = p->r_th_jc_c_per_w + p->r_th_cs_c_per_w + rep.r_th_sa_c_per_w;
    rep.predicted_t_junction_c = env->t_ambient_c + p->power_watts * rep.total_r_th_c_per_w;
    rep.thermal_ok = (rep.predicted_t_junction_c <= p->t_junction_max_c - 10.0f); // 10°C запас

    return rep;
}

// ── 4. Головний демонстраційний цикл ────────────────────────────────────────

int main(void) {
    PayloadConfig payload = {
        .mass_kg = 0.650f,             // 650 грамів (камера + AI SoC)
        .power_watts = 22.0f,          // 22 Вт (Jetson Orin Nano під навантаженням)
        .t_junction_max_c = 100.0f,    // Максимум 100 °C
        .r_th_jc_c_per_w = 0.8f,       // Кристал-корпус: 0.8 °C/Вт
        .r_th_cs_c_per_w = 0.4f,       // Термопрокладка: 0.4 °C/Вт
        .heatsink_area_m2 = 0.024f     // 240 см² ефективної площі ребер
    };

    BoltConfig bolts = {
        .yield_strength_mpa = 900.0f,  // Сталь класу міцності 10.9
        .core_area_mm2 = 5.03f,        // Гвинти M3
        .bolt_count = 4                // 4 точки монтажу
    };

    DamperConfig dampers = {
        .damper_k_single_n_per_m = 3500.0f, // Shore 30A: 3.5 Н/мм = 3500 Н/м
        .damper_count = 4,                  // 4 кульки
        .damping_ratio_zeta = 0.24f         // Силікон середньої в'язкості
    };

    FlightEnv env = {
        .rpm_min = 4500.0f,            // 4500 об/хв на холостому висінні
        .rpm_max = 8200.0f,            // 8200 об/хв на повному газі
        .blade_count = 2,              // 2-лопатеві гвинти
        .g_maneuver = 4.0f,            // 4g у віражах
        .g_impact = 12.0f,             // 12g при жорсткому приземленні
        .t_ambient_c = 35.0f,          // Спекотний літній день (+35 °C)
        .airspeed_m_s = 15.0f          // Політ зі швидкістю 15 м/с (54 км/год)
    };

    ValidationReport rep = validate_mounting(&payload, &bolts, &dampers, &env);

    printf("================ ЗВІТ ВЕРИФІКАЦІЇ МОНТАЖУ НАВАНТАЖЕННЯ ================\n");
    printf("1. МЕХАНІЧНА МІЦНІСТЬ БОЛТІВ (12g удар):\n");
    printf("   - Напруження за Мізесом: %.1f МПа\n", rep.bolt_von_mises_mpa);
    printf("   - Коефіцієнт запасу (SF): %.2f (Поріг >= 1.50) -> %s\n\n",
           rep.bolt_safety_factor, rep.bolt_ok ? "ПРОЙДЕНО [OK]" : "ВІДХИЛЕНО [FAIL]");

    printf("2. ВІБРОІЗОЛЯЦІЯ ДЕМПФЕРІВ:\n");
    printf("   - Власна частота підвісу f_0: %.2f Гц\n", rep.natural_freq_hz);
    printf("   - Діапазон частот обертання двигунів: %.1f .. %.1f Гц\n", rep.f_rot_min_hz, rep.f_rot_max_hz);
    printf("   - Коефіцієнт передавання T_R на min RPM: %.3f (Гасіння %.1f%%) -> %s\n\n",
           rep.transmissibility_at_min_rpm,
           (1.0f - rep.transmissibility_at_min_rpm) * 100.0f,
           rep.resonance_safe ? "ПРОЙДЕНО [OK]" : "ВІДХИЛЕНО [FAIL]");

    printf("3. ТЕПЛОВИЙ РЕЖИМ AI-ПРОЦЕСОРА (Швидкість %.1f м/с):\n", env.airspeed_m_s);
    printf("   - Тепловий опір радіатор-повітря R_th_sa: %.2f °C/Вт\n", rep.r_th_sa_c_per_w);
    printf("   - Сумарний опір R_th_total: %.2f °C/Вт\n", rep.total_r_th_c_per_w);
    printf("   - Прогнозована температура кристала T_j: %.1f °C (Стеля %.1f °C) -> %s\n",
           rep.predicted_t_junction_c, payload.t_junction_max_c,
           rep.thermal_ok ? "ПРОЙДЕНО [OK]" : "ПЕРЕГРІВ [FAIL]");
    printf("=======================================================================\n");

    return 0;
}
```
```cpp
// mounting_validator.hpp / .cpp — Ідіоматичний C++20 модуль верифікації кріплення
#include <iostream>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <format>
#include <expected>
#include <span>

namespace drone::mounting {

// ── Сильно типізовані конфігураційні структури ─────────────────────────────

struct BoltSpecs {
    float yield_strength_mpa{900.0f}; // Клас 10.9: 900 МПа
    float core_area_mm2{5.03f};       // M3 = 5.03 мм²
    int   bolt_count{4};
};

struct PayloadSpecs {
    float mass_kg{0.650f};
    float power_watts{22.0f};
    float max_junction_temp_c{100.0f};
    float r_th_jc{0.8f};             // °C/Вт
    float r_th_cs{0.4f};             // °C/Вт
    float heatsink_area_m2{0.024f};  // 240 см²
};

struct DamperSpecs {
    float single_stiffness_n_per_m{3500.0f};
    int   damper_count{4};
    float damping_ratio_zeta{0.24f};
};

struct FlightEnvironment {
    float rpm_min{4500.0f};
    float rpm_max{8200.0f};
    int   blade_count{2};
    float g_maneuver{4.0f};
    float g_impact{12.0f};
    float ambient_temp_c{35.0f};
    float airspeed_m_s{15.0f};
};

struct ValidationSummary {
    float bolt_von_mises_mpa;
    float bolt_safety_factor;
    bool  bolt_passed;

    float natural_frequency_hz;
    float transmissibility_min_rpm;
    bool  vibration_passed;

    float total_thermal_resistance;
    float predicted_junction_temp_c;
    bool  thermal_passed;

    [[nodiscard]] constexpr bool is_fully_valid() const noexcept {
        return bolt_passed && vibration_passed && thermal_passed;
    }
};

enum class FailureReason {
    InvalidMass,
    ZeroBolts,
    ExcessiveStress,
    ResonanceRisk,
    ThermalOverheat
};

// ── Клас верифікатора надійності ───────────────────────────────────────────

class MountingValidator {
public:
    static std::expected<ValidationSummary, FailureReason> validate(
        const PayloadSpecs& payload,
        const BoltSpecs& bolts,
        const DamperSpecs& dampers,
        const FlightEnvironment& env
    ) noexcept {
        if (payload.mass_kg <= 0.0f) {
            return std::unexpected(FailureReason::InvalidMass);
        }
        if (bolts.bolt_count <= 0) {
            return std::unexpected(FailureReason::ZeroBolts);
        }

        constexpr float g_acc = 9.80665f;
        ValidationSummary summary{};

        // 1. Аналіз болтів (Von Mises)
        const float total_impact_force = payload.mass_kg * env.g_impact * g_acc;
        const float force_per_bolt = total_impact_force / static_cast<float>(bolts.bolt_count);

        const float shear_stress = (force_per_bolt * 0.7071f) / bolts.core_area_mm2;
        const float tensile_stress = (force_per_bolt * 0.7071f) / bolts.core_area_mm2;

        summary.bolt_von_mises_mpa = std::sqrt(
            tensile_stress * tensile_stress + 3.0f * shear_stress * shear_stress
        );
        summary.bolt_safety_factor = bolts.yield_strength_mpa / summary.bolt_von_mises_mpa;
        summary.bolt_passed = (summary.bolt_safety_factor >= 1.50f);

        // 2. Аналіз віброізоляції
        const float total_k = dampers.single_stiffness_n_per_m * static_cast<float>(dampers.damper_count);
        summary.natural_frequency_hz = (1.0f / (2.0f * std::numbers::pi_v<float>)) *
                                       std::sqrt(total_k / payload.mass_kg);

        const float f_rot_min = env.rpm_min / 60.0f;
        const float r = f_rot_min / summary.natural_frequency_hz;
        const float z = dampers.damping_ratio_zeta;

        const float tr_num = 1.0f + std::pow(2.0f * z * r, 2.0f);
        const float tr_den = std::pow(1.0f - r * r, 2.0f) + std::pow(2.0f * z * r, 2.0f);
        summary.transmissibility_min_rpm = std::sqrt(tr_num / tr_den);

        summary.vibration_passed = (summary.natural_frequency_hz * 1.4142f < f_rot_min) &&
                                   (summary.transmissibility_min_rpm <= 0.25f);

        // 3. Аналіз теплового режиму
        const float airspeed = std::max(env.airspeed_m_s, 0.0f);
        const float h_conv = 10.0f + 6.5f * std::pow(airspeed, 0.8f);
        const float r_th_sa = 1.0f / (h_conv * payload.heatsink_area_m2);

        summary.total_thermal_resistance = payload.r_th_jc + payload.r_th_cs + r_th_sa;
        summary.predicted_junction_temp_c = env.ambient_temp_c +
                                            payload.power_watts * summary.total_thermal_resistance;
        summary.thermal_passed = (summary.predicted_junction_temp_c <= payload.max_junction_temp_c - 10.0f);

        return summary;
    }
};

} // namespace drone::mounting

int main() {
    using namespace drone::mounting;

    PayloadSpecs payload{};
    BoltSpecs bolts{};
    DamperSpecs dampers{};
    FlightEnvironment env{};

    auto result = MountingValidator::validate(payload, bolts, dampers, env);

    if (!result) {
        std::cerr << "Помилка валідації параметрів монтажу!\n";
        return 1;
    }

    const auto& res = result.value();
    std::cout << "================ C++20 МОНТАЖНИЙ АНАЛІЗАТОР ================\n";
    std::cout << std::format("Болти: напруження {:.1f} МПа, Запас: {:.2f} [{}]\n",
                             res.bolt_von_mises_mpa, res.bolt_safety_factor,
                             res.bolt_passed ? "OK" : "FAIL");
    std::cout << std::format("Віброізоляція: f_0 = {:.2f} Гц, T_R = {:.3f} [{}]\n",
                             res.natural_frequency_hz, res.transmissibility_min_rpm,
                             res.vibration_passed ? "OK" : "FAIL");
    std::cout << std::format("Тепло: T_j = {:.1f} °C, R_th = {:.2f} °C/Вт [{}]\n",
                             res.predicted_junction_temp_c, res.total_thermal_resistance,
                             res.thermal_passed ? "OK" : "FAIL");
    std::cout << std::format("Загальний статус допуску до польоту: {}\n",
                             res.is_fully_valid() ? "СХВАЛЕНО" : "ЗАБЛОКОВАНО");
    std::cout << "=============================================================\n";

    return 0;
}
```
:::

## 3. Аналіз граничних випадків та інженерні рішення

### Граничний випадок 1: Тривале зависання у спекотний день
Коли безпілотник зависає над точкою спостереження за температури повітря `+35 °C`, швидкість набігання дорівнює нулю (`v_air = 0`). Коефіцієнт тепловіддачі падає до `h_conv = 10 Вт/(м²·К)`. Для радіатора площею `0.024 м²` опір `R_θsa` зростає з 0.58 до 4.16 °C/Вт, а сумарний тепловий опір сягає `5.36 °C/Вт`. При потужності 22 Вт перегрів кристала складе `ΔT = 22 · 5.36 = 118 °C`, що разом із фоновими 35 °C дає `T_j = 153 °C` — процесор миттєво згорить або аварійно вимкнеться.

*Інженерне рішення:* розміщення ребер радіатора безпосередньо в зоні спадного струменя пропелера (downwash) зі швидкістю `v_downwash ≈ 7–10 м/с`, що повертає `h_conv` до рівня `40–50 Вт/(м²·К)`.

### Граничний випадок 2: Температурна деградація силікону взимку
При польотах у зимових умовах (−15 °C … −25 °C) твердість силіконових демпферів зростає на 40–70% (Shore 30A перетворюється на 50A–55A). Жорсткість `k_single` підскакує з 3500 до 6000 Н/м, піднімаючи власну частоту `f_0` з 23.3 Гц до 30.6 Гц. При зниженні газу під час спуску (3200 об/хв, `f_rot = 53.3 Гц`) відношення частот падає до `r = 53.3 / 30.6 = 1.74 ≈ √2`, де підвіс повністю втрачає віброізолюючі властивості (`T_R ≈ 1.0`), передаючи вібрацію моторів прямо на камеру.

*Інженерне рішення:* використання низькотемпературного фторсилікону (FVMQ) або тросових демпферів із нержавіючої сталі 316, модуль пружності яких не залежить від температури повітря.
