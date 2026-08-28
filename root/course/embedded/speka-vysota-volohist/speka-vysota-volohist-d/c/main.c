#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Фізичні константи Міжнародної стандартної атмосфери ISA */
#define ISA_P0_PA        101325.0f   /* Стандартний тиск на рівні моря, Па */
#define ISA_T0_K         288.15f     /* Стандартна температура на рівні моря, К (+15 °C) */
#define ISA_RHO0         1.2250f     /* Стандартна густина повітря, кг/м³ */
#define ISA_LAPSE_RATE   0.0065f     /* Температурний градієнт, К/м */
#define GAS_CONST_DRY    287.058f    /* Газова стала сухого повітря, Дж/(кг·К) */

/* Структура вхідних метеорологічних та польотних параметрів */
typedef struct {
    float pressure_hpa;     /* Барометричний тиск, гПа */
    float temp_celsius;     /* Температура навколишнього повітря, °C */
    float rel_humidity_pct; /* Відносна вологість, % (0..100) */
    float nominal_twr;      /* Номінальний запас тяги TWR на рівні моря ISA (напр. 2.0) */
    float nominal_time_min; /* Номінальний час польоту на рівні моря ISA, хв */
} FlightEnvInput;

/* Структура результатів розрахунку деградації характеристик */
typedef struct {
    float air_density;       /* Фактична густина вологого повітря, кг/м³ */
    float density_ratio;     /* Відносна густина (rho / rho0) */
    float pressure_alt_m;    /* Барометрична висота Pressure Altitude, м */
    float density_alt_m;     /* Висота за густиною Density Altitude, м */
    float actual_twr;        /* Фактичний максимальний запас тяги до ваги */
    float hover_rpm_mult;    /* Множник необхідних обертів висіння (n / n0) */
    float hover_current_mult;/* Множник струму висіння (I / I0) */
    float copper_heat_mult;  /* Множник виділення тепла в обмотках I²R */
    float est_flight_time_m; /* Оцінкова тривалість польоту, хв */
    bool  is_safe_to_fly;    /* Чи безпечно здійснювати виліт (TWR >= 1.4) */
} AeroDensityReport;

/*
 * Розрахунок параметрів атмосфери та деградації силової установки.
 * Повертає false при некоректних вхідних даних (від'ємний тиск, нереальна температура).
 */
bool calculate_flight_degradation(const FlightEnvInput* in, AeroDensityReport* out) {
    if (!in || !out) return false;
    if (in->pressure_hpa < 300.0f || in->pressure_hpa > 1100.0f) return false;
    if (in->temp_celsius < -50.0f || in->temp_celsius > 65.0f) return false;
    if (in->rel_humidity_pct < 0.0f || in->rel_humidity_pct > 100.0f) return false;
    if (in->nominal_twr <= 0.5f) return false;

    float p_pa = in->pressure_hpa * 100.0f;
    float t_k = in->temp_celsius + 273.15f;

    /* 1. Тиск насиченої пари за формулою Магнуса-Тетенса (у Па) */
    float p_sat_pa = 610.78f * expf((17.27f * in->temp_celsius) / (237.3f + in->temp_celsius));
    float p_v_pa = (in->rel_humidity_pct / 100.0f) * p_sat_pa;

    /* 2. Точна густина вологого повітря за законом Дальтона */
    float rho = (p_pa / (GAS_CONST_DRY * t_k)) * (1.0f - 0.37803f * (p_v_pa / p_pa));
    out->air_density = rho;

    float rho_rel = rho / ISA_RHO0;
    out->density_ratio = rho_rel;

    /* 3. Барометрична висота (Pressure Altitude) */
    out->pressure_alt_m = 44330.8f * (1.0f - powf(p_pa / ISA_P0_PA, 0.190263f));

    /* 4. Точна висота за густиною (Density Altitude) з формули тропосфери ISA */
    out->density_alt_m = 44330.8f * (1.0f - powf(rho_rel, 0.23497f));

    /* 5. Деградація максимальної тяги та TWR */
    out->actual_twr = in->nominal_twr * rho_rel;

    /* 6. Зростання обертів, потужності та струму зависання */
    float hover_scale = 1.0f / sqrtf(rho_rel);
    out->hover_rpm_mult = hover_scale;
    out->hover_current_mult = hover_scale;
    out->copper_heat_mult = 1.0f / rho_rel;

    /* 7. Оцінка часу польоту з урахуванням просадки напруги та ККД */
    float time_reduction_factor = powf(rho_rel, 0.75f);
    out->est_flight_time_m = in->nominal_time_min * time_reduction_factor;

    /* 8. Критерій безпеки вильоту */
    out->is_safe_to_fly = (out->actual_twr >= 1.40f);

    return true;
}
