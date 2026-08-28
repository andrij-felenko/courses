#include <math.h>
#include <stdbool.h>
#include <stdint.h>

#define NUM_MOTORS                4
#define RESIDUAL_THRESHOLD_RAD_S2 15.0f   // Поріг неузгодженості кутового прискорення
#define FAULT_ACCUMULATOR_MAX     100     // 100 мс стійкої аномалії для фіксації відмови

typedef struct {
    float roll_moment_cmd;
    float pitch_moment_cmd;
    float gyro_accel_roll;
    float gyro_accel_pitch;
    float inertia_xx;
    float inertia_yy;
    int fault_counter[NUM_MOTORS];
    bool motor_failed[NUM_MOTORS];
} motor_fault_detector_t;

void motor_fault_detector_init(motor_fault_detector_t *det, float i_xx, float i_yy) {
    det->inertia_xx = i_xx;
    det->inertia_yy = i_yy;
    for (int i = 0; i < NUM_MOTORS; ++i) {
        det->fault_counter[i] = 0;
        det->motor_failed[i] = false;
    }
}

void motor_fault_detector_update(motor_fault_detector_t *det,
                                 float tau_roll_cmd,
                                 float tau_pitch_cmd,
                                 float gyro_dot_roll,
                                 float gyro_dot_pitch,
                                 const float motor_thrusts[NUM_MOTORS],
                                 int dt_ms) {
    // Очікуване кутове прискорення від прикладеного моменту
    float alpha_roll_exp = tau_roll_cmd / det->inertia_xx;
    float alpha_pitch_exp = tau_pitch_cmd / det->inertia_yy;

    float err_roll = fabsf(alpha_roll_exp - gyro_dot_roll);
    float err_pitch = fabsf(alpha_pitch_exp - gyro_dot_pitch);

    // Квадрокоптер X-схеми:
    // Мотор 1: +Roll, -Pitch; Мотор 2: -Roll, -Pitch
    // Мотор 3: -Roll, +Pitch; Мотор 4: +Roll, +Pitch
    bool suspect[NUM_MOTORS] = { false };

    if (err_roll > RESIDUAL_THRESHOLD_RAD_S2 || err_pitch > RESIDUAL_THRESHOLD_RAD_S2) {
        if (gyro_dot_roll < alpha_roll_exp && gyro_dot_pitch > alpha_pitch_exp) suspect[0] = true; // Відмова М1
        if (gyro_dot_roll > alpha_roll_exp && gyro_dot_pitch > alpha_pitch_exp) suspect[1] = true; // Відмова М2
        if (gyro_dot_roll > alpha_roll_exp && gyro_dot_pitch < alpha_pitch_exp) suspect[2] = true; // Відмова М3
        if (gyro_dot_roll < alpha_roll_exp && gyro_dot_pitch < alpha_pitch_exp) suspect[3] = true; // Відмова М4
    }

    for (int i = 0; i < NUM_MOTORS; ++i) {
        if (suspect[i] && motor_thrusts[i] > 0.2f) {
            det->fault_counter[i] += dt_ms;
            if (det->fault_counter[i] >= FAULT_ACCUMULATOR_MAX) {
                det->motor_failed[i] = true;
            }
        } else {
            if (det->fault_counter[i] > 0) det->fault_counter[i] -= dt_ms;
        }
    }
}
