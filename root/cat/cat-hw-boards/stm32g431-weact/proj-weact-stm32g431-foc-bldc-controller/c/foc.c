#include "foc.h"
#include "mcu_periph.h"
#include <math.h>

#ifndef SQRT3
#define SQRT3 1.73205080756887729353f
#endif

void pi_controller_init(pi_controller_t *pi, float kp, float ki, float out_min, float out_max) {
    if (!pi) return;
    pi->kp = kp;
    pi->ki = ki;
    pi->integral = 0.0f;
    pi->out_min = out_min;
    pi->out_max = out_max;
}

float pi_controller_update(pi_controller_t *pi, float setpoint, float measured, float dt) {
    if (!pi || dt <= 0.0f) return 0.0f;

    float error = setpoint - measured;
    float p_term = pi->kp * error;

    // Накопичення інтеграла з захистом від насичення (anti-windup)
    pi->integral += pi->ki * error * dt;
    if (pi->integral > pi->out_max) pi->integral = pi->out_max;
    if (pi->integral < pi->out_min) pi->integral = pi->out_min;

    float output = p_term + pi->integral;
    if (output > pi->out_max) output = pi->out_max;
    if (output < pi->out_min) output = pi->out_min;

    return output;
}

void pi_controller_reset(pi_controller_t *pi) {
    if (pi) {
        pi->integral = 0.0f;
    }
}

void foc_init(foc_state_t *foc, float bus_voltage, uint16_t pwm_period) {
    if (!foc) return;

    foc->i_a = 0.0f;
    foc->i_b = 0.0f;
    foc->i_c = 0.0f;
    foc->i_alpha = 0.0f;
    foc->i_beta = 0.0f;
    foc->i_d = 0.0f;
    foc->i_q = 0.0f;
    foc->target_i_d = 0.0f;
    foc->target_i_q = 0.0f;
    foc->target_speed = 0.0f;
    foc->measured_speed = 0.0f;
    foc->electrical_angle = 0.0f;
    foc->v_d = 0.0f;
    foc->v_q = 0.0f;
    foc->v_alpha = 0.0f;
    foc->v_beta = 0.0f;
    foc->duty_a = 0;
    foc->duty_b = 0;
    foc->duty_c = 0;

    foc->bus_voltage = bus_voltage > 1.0f ? bus_voltage : 24.0f;
    foc->pwm_period = pwm_period;

    // Максимально припустима напруга фази
    float max_voltage = foc->bus_voltage / SQRT3;
    pi_controller_init(&foc->pi_d, 2.5f, 500.0f, -max_voltage, max_voltage);
    pi_controller_init(&foc->pi_q, 2.5f, 500.0f, -max_voltage, max_voltage);

    // ПІ-регулятор швидкості генерує заданий струм Iq
    pi_controller_init(&foc->pi_speed, 0.05f, 1.2f, -10.0f, 10.0f);
}

void foc_clarke_transform(float i_a, float i_b, float *i_alpha, float *i_beta) {
    if (!i_alpha || !i_beta) return;
    *i_alpha = i_a;
    *i_beta = (i_a + 2.0f * i_b) * (1.0f / SQRT3);
}

void foc_park_transform(float i_alpha, float i_beta, float cos_th, float sin_th, float *i_d, float *i_q) {
    if (!i_d || !i_q) return;
    *i_d =  i_alpha * cos_th + i_beta * sin_th;
    *i_q = -i_alpha * sin_th + i_beta * cos_th;
}

void foc_inv_park_transform(float v_d, float v_q, float cos_th, float sin_th, float *v_alpha, float *v_beta) {
    if (!v_alpha || !v_beta) return;
    *v_alpha = v_d * cos_th - v_q * sin_th;
    *v_beta  = v_d * sin_th + v_q * cos_th;
}

void foc_svpwm(float v_alpha, float v_beta, float v_bus, uint16_t pwm_period, 
               uint16_t *duty_a, uint16_t *duty_b, uint16_t *duty_c) {
    if (!duty_a || !duty_b || !duty_c || v_bus <= 0.1f) return;

    // 1. Проектні відносні напруги фаз
    float v_a = v_alpha;
    float v_b = -0.5f * v_alpha + (SQRT3 * 0.5f) * v_beta;
    float v_c = -0.5f * v_alpha - (SQRT3 * 0.5f) * v_beta;

    // 2. Центрування напруг інжекцією нульової послідовності (Space Vector Modulation)
    float v_max = v_a;
    if (v_b > v_max) v_max = v_b;
    if (v_c > v_max) v_max = v_c;

    float v_min = v_a;
    if (v_b < v_min) v_min = v_b;
    if (v_c < v_min) v_min = v_c;

    float v_zero = 0.5f * (v_max + v_min);

    // 3. Коефіцієнти заповнення у нормалізованому діапазоні [0.0, 1.0]
    float d_a = ((v_a - v_zero) / v_bus) + 0.5f;
    float d_b = ((v_b - v_zero) / v_bus) + 0.5f;
    float d_c = ((v_c - v_zero) / v_bus) + 0.5f;

    if (d_a > 1.0f) d_a = 1.0f; else if (d_a < 0.0f) d_a = 0.0f;
    if (d_b > 1.0f) d_b = 1.0f; else if (d_b < 0.0f) d_b = 0.0f;
    if (d_c > 1.0f) d_c = 1.0f; else if (d_c < 0.0f) d_c = 0.0f;

    // 4. Переведення у значення лічильника ARR таймера ШІМ
    *duty_a = (uint16_t)(d_a * pwm_period);
    *duty_b = (uint16_t)(d_b * pwm_period);
    *duty_c = (uint16_t)(d_c * pwm_period);
}

void foc_update_current_loop(foc_state_t *foc, float dt) {
    if (!foc) return;

    // Зчитування миттєвого струму фаз
    phase_currents_t currents;
    mcu_periph_read_phase_currents(&currents);
    foc->i_a = currents.i_a;
    foc->i_b = currents.i_b;
    foc->i_c = currents.i_c;

    // Швидка тригонометрія за допомогою CORDIC
    float cos_th = 1.0f;
    float sin_th = 0.0f;
    mcu_periph_cordic_cos_sin(foc->electrical_angle, &cos_th, &sin_th);

    // Перетворення Кларк та Парка
    foc_clarke_transform(foc->i_a, foc->i_b, &foc->i_alpha, &foc->i_beta);
    foc_park_transform(foc->i_alpha, foc->i_beta, cos_th, sin_th, &foc->i_d, &foc->i_q);

    // Контури регулювання струмів Id та Iq
    foc->v_d = pi_controller_update(&foc->pi_d, foc->target_i_d, foc->i_d, dt);
    foc->v_q = pi_controller_update(&foc->pi_q, foc->target_i_q, foc->i_q, dt);

    // Зворотне перетворення та ШІМ
    foc_inv_park_transform(foc->v_d, foc->v_q, cos_th, sin_th, &foc->v_alpha, &foc->v_beta);
    foc_svpwm(foc->v_alpha, foc->v_beta, foc->bus_voltage, foc->pwm_period,
              &foc->duty_a, &foc->duty_b, &foc->duty_c);

    // Запис результатів у периферійні регістри ШІМ
    mcu_periph_set_duty_cycles(foc->duty_a, foc->duty_b, foc->duty_c);
}

void foc_update_speed_loop(foc_state_t *foc, float dt) {
    if (!foc) return;
    foc->target_i_q = pi_controller_update(&foc->pi_speed, foc->target_speed, foc->measured_speed, dt);
}
