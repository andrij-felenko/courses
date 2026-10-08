#include <stdbool.h>
#include <stdint.h>

typedef struct {
    float v_bus_volts;
    float temp_stator_c;
    float temp_mosfet_c;
    float i_q_target_amp;
    float i_q_max_limit_amp;
    bool brake_resistor_active;
} ServoProtectionState;

void update_servo_protection(ServoProtectionState *state) {
    const float V_BUS_MAX_THRESHOLD = 52.0f; // Вольти
    const float TEMP_CRITICAL_C     = 95.0f; // Градуси Цельсія
    const float TEMP_WARN_C         = 75.0f; // Початок дроТлювання
    const float I_Q_NOMINAL_MAX     = 30.0f; // Ампери

    // 1. Апаратний захист від зворотної ЕРС (гальмівний ключ)
    if (state->v_bus_volts > V_BUS_MAX_THRESHOLD) {
        state->brake_resistor_active = true;
    } else if (state->v_bus_volts < (V_BUS_MAX_THRESHOLD - 2.0f)) {
        state->brake_resistor_active = false;
    }

    // 2. Теплове дроТлювання струму I_q (Thermal Throttling)
    float max_temp = (state->temp_stator_c > state->temp_mosfet_c) 
                     ? state->temp_stator_c : state->temp_mosfet_c;

    if (max_temp >= TEMP_CRITICAL_C) {
        state->i_q_max_limit_amp = 0.0f; // Повне відключення за перегрівом
    } else if (max_temp > TEMP_WARN_C) {
        float scale = (TEMP_CRITICAL_C - max_temp) / (TEMP_CRITICAL_C - TEMP_WARN_C);
        state->i_q_max_limit_amp = I_Q_NOMINAL_MAX * scale;
    } else {
        state->i_q_max_limit_amp = I_Q_NOMINAL_MAX;
    }

    // 3. Обмеження заданого струму
    if (state->i_q_target_amp > state->i_q_max_limit_amp) {
        state->i_q_target_amp = state->i_q_max_limit_amp;
    } else if (state->i_q_target_amp < -state->i_q_max_limit_amp) {
        state->i_q_target_amp = -state->i_q_max_limit_amp;
    }
}
