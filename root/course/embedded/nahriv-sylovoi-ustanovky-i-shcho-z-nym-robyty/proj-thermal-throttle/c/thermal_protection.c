// thermal_protection.h / thermal_protection.c
#include <stdint.h>
#include <stdbool.h>

#define THERMAL_MAX_CHANNELS 4

typedef struct {
    // Параметри мотора
    float r_phase_20c;       // Опір фази при 20°C (Ом)
    float alpha_copper;      // Температурний коефіцієнт міді (0.00393 1/°C)
    float c_th_wind;         // Теплоємність міді обмоток (Дж/°C)
    float c_th_core;         // Теплоємність статора (Дж/°C)
    float r_th_wind_core;    // Тепловий опір обмотка-залізо (°C/Вт)
    float r_th_core_air_base;// Базовий тепловий опір залізо-повітря без обдуву (°C/Вт)
    float k_iron_loss;       // Емпіричний коефіцієнт втрат у залізі

    // Пороги тротлінгу для регулятора (°C)
    float esc_temp_warn;     // Початок лінійного тротлінгу (напр. 95°C)
    float esc_temp_crit;     // Повний тротлінг / мінімальна тяга (напр. 115°C)

    // Пороги тротлінгу для мотора (°C)
    float motor_temp_warn;   // Початок тротлінгу обмотки (напр. 100°C)
    float motor_temp_crit;   // Критична межа ізоляції/магнітів (напр. 130°C)
    float min_throttle_scale;// Мінімальний коефіцієнт газу при тротлінгу (напр. 0.35f)
} ThermalConfig;

typedef struct {
    float t_wind_est;        // Оцінка температури обмотки (°C)
    float t_core_est;        // Оцінка температури статора (°C)
    float esc_temp_filtered; // Фільтрована температура телеметрії ESC (°C)
    float throttle_scale;    // Поточний коефіцієнт обмеження газу (0.0 .. 1.0)
    bool  is_overheated;     // Прапорець активного захисту від перегріву
} ThermalState;

typedef struct {
    ThermalConfig config;
    ThermalState  channels[THERMAL_MAX_CHANNELS];
    float         ambient_temp_c;
} ThermalManager;

void thermal_init(ThermalManager *mgr, const ThermalConfig *cfg, float amb_temp) {
    mgr->config = *cfg;
    mgr->ambient_temp_c = amb_temp;
    for (int i = 0; i < THERMAL_MAX_CHANNELS; ++i) {
        mgr->channels[i].t_wind_est = amb_temp;
        mgr->channels[i].t_core_est = amb_temp;
        mgr->channels[i].esc_temp_filtered = amb_temp;
        mgr->channels[i].throttle_scale = 1.0f;
        mgr->channels[i].is_overheated = false;
    }
}

// Оновлення теплового стану мотора та ESC на одному каналі
void thermal_update_channel(ThermalManager *mgr, uint8_t ch, float current_amps,
                            uint32_t erpm, float esc_raw_temp, float dt_sec) {
    if (ch >= THERMAL_MAX_CHANNELS || dt_sec <= 0.0f) return;

    ThermalState *st = &mgr->channels[ch];
    const ThermalConfig *cfg = &mgr->config;

    // 1. Фільтрація виміряної температури ESC (Low-Pass Filter, стала часу ~0.5 с)
    float alpha_lpf = dt_sec / (0.5f + dt_sec);
    st->esc_temp_filtered += alpha_lpf * (esc_raw_temp - st->esc_temp_filtered);

    // 2. Тепловий спостерігач мотора
    // Опір міді з урахуванням температури
    float r_cu = cfg->r_phase_20c * (1.0f + cfg->alpha_copper * (st->t_wind_est - 20.0f));
    float p_copper = 1.5f * current_amps * current_amps * r_cu;

    // Магнітні втрати в статорі
    float erpm_k = (float)erpm * 0.001f;
    float p_iron = cfg->k_iron_loss * erpm_k * erpm_k;

    // Динамічний тепловий опір у повітря (конвекція зростає з обертами)
    float airflow_factor = 1.0f + 0.05f * erpm_k;
    float r_th_air = cfg->r_th_core_air_base / airflow_factor;

    // Теплові потоки
    float q_wind_to_core = (st->t_wind_est - st->t_core_est) / cfg->r_th_wind_core;
    float q_core_to_air  = (st->t_core_est - mgr->ambient_temp_c) / r_th_air;

    // Диференціальні рівняння нагріву (метод Ейлера)
    float d_t_wind = (p_copper - q_wind_to_core) / cfg->c_th_wind;
    float d_t_core = (q_wind_to_core + p_iron - q_core_to_air) / cfg->c_th_core;

    st->t_wind_est += d_t_wind * dt_sec;
    st->t_core_est += d_t_core * dt_sec;

    // 3. Розрахунок коефіцієнтів тротлінгу
    // Тротлінг за температурою ESC
    float scale_esc = 1.0f;
    if (st->esc_temp_filtered > cfg->esc_temp_warn) {
        float span = cfg->esc_temp_crit - cfg->esc_temp_warn;
        scale_esc = 1.0f - (st->esc_temp_filtered - cfg->esc_temp_warn) / span;
        if (scale_esc < cfg->min_throttle_scale) scale_esc = cfg->min_throttle_scale;
    }

    // Тротлінг за оцінкою температури обмотки мотора
    float scale_motor = 1.0f;
    if (st->t_wind_est > cfg->motor_temp_warn) {
        float span = cfg->motor_temp_crit - cfg->motor_temp_warn;
        scale_motor = 1.0f - (st->t_wind_est - cfg->motor_temp_warn) / span;
        if (scale_motor < cfg->min_throttle_scale) scale_motor = cfg->min_throttle_scale;
    }

    // Беремо найсуворіше обмеження з двох компонентів
    float target_scale = (scale_esc < scale_motor) ? scale_esc : scale_motor;

    // Швидкісне згладжування тротлінгу (Rate Limiter) для виключення ривків тяги
    float max_slew = 0.5f * dt_sec; // Максимальна зміна газу не більше 50%/сек
    if (target_scale < st->throttle_scale) {
        st->throttle_scale -= max_slew;
        if (st->throttle_scale < target_scale) st->throttle_scale = target_scale;
    } else {
        st->throttle_scale += max_slew;
        if (st->throttle_scale > target_scale) st->throttle_scale = target_scale;
    }

    st->is_overheated = (st->throttle_scale < 0.98f);
}

// Застосування теплового обмеження до вхідної команди газу
float thermal_apply_throttle(const ThermalManager *mgr, uint8_t ch, float requested_throttle) {
    if (ch >= THERMAL_MAX_CHANNELS) return requested_throttle;
    if (requested_throttle <= 0.0f) return 0.0f;
    return requested_throttle * mgr->channels[ch].throttle_scale;
}
