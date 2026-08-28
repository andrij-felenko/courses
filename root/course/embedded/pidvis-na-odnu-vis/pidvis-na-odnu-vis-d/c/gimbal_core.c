/* ============================================================================
 * gimbal_core.c — Ядро одноосьової стабілізації на C
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define DT 0.005f  /* 200 Гц */

typedef struct {
    float angle_deg;
    float alpha;
} CompFilter;

typedef struct {
    float kp, ki, kd;
    float out_min, out_max;
    float integrator;
    float d_filter_state;
    float d_lpf_beta;
} GimbalPID;

float comp_filter_step(CompFilter *f, float gyro_rate_dps, float ay, float az) {
    /* 1. Інтегрування гіроскопа */
    float pred = f->angle_deg + gyro_rate_dps * DT;

    /* 2. Нахил за вектором тяжіння */
    float acc_angle = atan2f(ay, az) * (180.0f / 3.14159265f);

    /* 3. Злиття */
    f->angle_deg = f->alpha * pred + (1.0f - f->alpha) * acc_angle;
    return f->angle_deg;
}

float pid_step(GimbalPID *pid, float setpoint, float measured_angle, float gyro_rate_dps) {
    float error = setpoint - measured_angle;
    float p_term = pid->kp * error;

    /* D-терм за гіроскопом з ФНЧ */
    float d_raw = -gyro_rate_dps;
    pid->d_filter_state += pid->d_lpf_beta * (d_raw - pid->d_filter_state);
    float d_term = pid->kd * pid->d_filter_state;

    /* Попередній вихід для перевірки насичення */
    float u_tentative = p_term + pid->integrator + d_term;

    /* Clamping Anti-Windup */
    bool saturated = (u_tentative > pid->out_max || u_tentative < pid->out_min);
    bool same_direction = (u_tentative * error > 0.0f);

    if (!saturated || !same_direction) {
        pid->integrator += pid->ki * error * DT;
    }

    float u_out = p_term + pid->integrator + d_term;
    if (u_out > pid->out_max) u_out = pid->out_max;
    if (u_out < pid->out_min) u_out = pid->out_min;

    return u_out;
}
