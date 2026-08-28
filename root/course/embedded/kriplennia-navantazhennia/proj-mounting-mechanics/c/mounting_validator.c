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
