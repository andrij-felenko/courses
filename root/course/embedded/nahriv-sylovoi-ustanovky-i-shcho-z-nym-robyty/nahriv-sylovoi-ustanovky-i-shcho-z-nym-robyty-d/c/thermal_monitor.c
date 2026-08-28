// thermal_monitor.h / thermal_monitor.c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    float r_phase_20c;        // Опір фази мотора при 20°C (Ом)
    float alpha_cu;           // Температурний коефіцієнт міді (0.00393)
    float c_th_winding;       // Теплоємність обмотки (Дж/°C)
    float r_th_wind_to_air;   // Тепловий опір обмотка-повітря (°C/Вт)
    float esc_temp_limit_c;   // Гранична температура ESC (°C)
    float motor_temp_limit_c; // Гранична температура обмотки (°C)
} PropulsionThermalLimits;

typedef struct {
    float motor_temp_est;     // Оцінена температура обмотки (°C)
    float esc_temp_c;         // Виміряна температура регулятора (°C)
    float max_allowed_throttle;// Коефіцієнт обмеження газу (0.0 .. 1.0)
    bool  thermal_alert;      // Сигнал попередження про перегрів
} PropulsionThermalState;

void thermal_monitor_init(PropulsionThermalState *state, float ambient_temp_c) {
    state->motor_temp_est = ambient_temp_c;
    state->esc_temp_c = ambient_temp_c;
    state->max_allowed_throttle = 1.0f;
    state->thermal_alert = false;
}

void thermal_monitor_update(PropulsionThermalState *state,
                            const PropulsionThermalLimits *limits,
                            float phase_current_rms,
                            float esc_telemetry_temp,
                            float ambient_temp_c,
                            float dt_sec) {
    state->esc_temp_c = esc_telemetry_temp;

    // 1. Оновлення теплової моделі мотора (1-полюсна RC-модель)
    float r_copper = limits->r_phase_20c * (1.0f + limits->alpha_cu * (state->motor_temp_est - 20.0f));
    float p_loss_cu = 1.5f * phase_current_rms * phase_current_rms * r_copper;

    float heat_dissipated = (state->motor_temp_est - ambient_temp_c) / limits->r_th_wind_to_air;
    float d_temp = (p_loss_cu - heat_dissipated) / limits->c_th_winding;
    state->motor_temp_est += d_temp * dt_sec;

    // 2. Розрахунок коефіцієнта термотротлінгу
    float throttle_scale_esc = 1.0f;
    if (state->esc_temp_c > (limits->esc_temp_limit_c - 20.0f)) {
        float over = state->esc_temp_c - (limits->esc_temp_limit_c - 20.0f);
        throttle_scale_esc = 1.0f - (over / 20.0f);
        if (throttle_scale_esc < 0.3f) throttle_scale_esc = 0.3f;
    }

    float throttle_scale_motor = 1.0f;
    if (state->motor_temp_est > (limits->motor_temp_limit_c - 25.0f)) {
        float over = state->motor_temp_est - (limits->motor_temp_limit_c - 25.0f);
        throttle_scale_motor = 1.0f - (over / 25.0f);
        if (throttle_scale_motor < 0.3f) throttle_scale_motor = 0.3f;
    }

    state->max_allowed_throttle = (throttle_scale_esc < throttle_scale_motor)
                                  ? throttle_scale_esc : throttle_scale_motor;
    state->thermal_alert = (state->max_allowed_throttle < 0.95f);
}
