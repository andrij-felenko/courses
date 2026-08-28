#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CHANNELS 4

typedef struct {
    uint32_t time_ms;
    float setpoint_roll;
    float gyro_roll;
    float motor_pwm[CHANNELS]; /* [0.0 .. 1.0] */
    float vbat;
} log_entry_t;

typedef struct {
    bool crash_detected;
    uint32_t trigger_time_ms;
    int failed_motor_index;
    const char* diagnosis;
} postmortem_result_t;

postmortem_result_t evaluate_crash_log(const log_entry_t* log, size_t len) {
    postmortem_result_t res = {false, 0, -1, "NORMAL_FLIGHT"};
    if (len < 5) return res;

    uint32_t desync_counter[CHANNELS] = {0};

    for (size_t i = 1; i < len; ++i) {
        float dt = (float)(log[i].time_ms - log[i - 1].time_ms) * 0.001f;
        if (dt <= 0.0f) continue;

        /* 1. Перевірка просідання напруги до критичного Brownout */
        if (log[i].vbat < 6.0f) {
            res.crash_detected = true;
            res.trigger_time_ms = log[i].time_ms;
            res.diagnosis = "CRITICAL_BROWNOUT_VOLTAGE_COLLAPSE";
            return res;
        }

        /* 2. Розрахунок кутової похибки стеження */
        float err_roll = fabsf(log[i].setpoint_roll - log[i].gyro_roll);
        float alpha_roll = (log[i].gyro_roll - log[i - 1].gyro_roll) / dt;

        /* 3. Аналіз насичення моторів */
        for (int m = 0; m < CHANNELS; ++m) {
            if (log[i].motor_pwm[m] >= 0.98f) {
                /* Мотор 3 відповідає за створення позитивного кутового прискорення Roll */
                bool is_reaction_opposing = (m == 3 && alpha_roll < -30.0f) ||
                                            (m == 1 && alpha_roll > 30.0f);
                if (is_reaction_opposing && err_roll > 40.0f) {
                    desync_counter[m] += (log[i].time_ms - log[i - 1].time_ms);
                    if (desync_counter[m] >= 25) { /* 25 мс повної відсутності тяги */
                        res.crash_detected = true;
                        res.trigger_time_ms = log[i].time_ms - desync_counter[m];
                        res.failed_motor_index = m;
                        res.diagnosis = "ESC_MOTOR_DESYNCHRONIZATION";
                        return res;
                    }
                }
            } else {
                desync_counter[m] = 0;
            }
        }
    }

    return res;
}
