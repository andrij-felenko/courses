#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PI_F 3.14159265358979323846f

// ── 1. Двоквардатний режекторний фільтр (Biquad Notch Filter) ──────────────
typedef struct {
    float b0, b1, b2;
    float a1, a2;
    float x1, x2;
    float y1, y2;
} BiquadFilter;

void biquad_notch_init(BiquadFilter *f, float center_hz, float cutoff_hz, float dt) {
    float omega = 2.0f * PI_F * center_hz * dt;
    float octaves = log2f(center_hz / cutoff_hz) * 2.0f;
    if (octaves < 0.1f) octaves = 0.1f;
    float alpha = sinf(omega) * sinhf(logf(2.0f) / 2.0f * octaves * omega / sinf(omega));

    float b0 = 1.0f;
    float b1 = -2.0f * cosf(omega);
    float b2 = 1.0f;
    float a0 = 1.0f + alpha;
    float a1 = -2.0f * cosf(omega);
    float a2 = 1.0f - alpha;

    f->b0 = b0 / a0;
    f->b1 = b1 / a0;
    f->b2 = b2 / a0;
    f->a1 = a1 / a0;
    f->a2 = a2 / a0;
    f->x1 = f->x2 = f->y1 = f->y2 = 0.0f;
}

float biquad_update(BiquadFilter *f, float in) {
    float out = (f->b0 * in) + (f->b1 * f->x1) + (f->b2 * f->x2) - (f->a1 * f->y1) - (f->a2 * f->y2);
    f->x2 = f->x1;
    f->x1 = in;
    f->y2 = f->y1;
    f->y1 = out;
    return out;
}

// ── 2. ПІД-регулятор осі з Anti-Windup та Feedforward ───────────────────────
typedef struct {
    float kp;
    float ki;
    float kd;
    float k_ff;
    float i_term;
    float i_max;
    float out_max;
    float prev_meas;
    float prev_setpoint;
    BiquadFilter d_filter;
} AxisPID;

void axis_pid_init(AxisPID *pid, float kp, float ki, float kd, float k_ff,
                   float i_max, float out_max, float notch_center_hz, float dt) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->k_ff = k_ff;
    pid->i_term = 0.0f;
    pid->i_max = i_max;
    pid->out_max = out_max;
    pid->prev_meas = 0.0f;
    pid->prev_setpoint = 0.0f;
    biquad_notch_init(&pid->d_filter, notch_center_hz, notch_center_hz * 0.7f, dt);
}

float axis_pid_update(AxisPID *pid, float target_rate, float meas_rate, float dt) {
    float error = target_rate - meas_rate;

    // 1. Пропорційна дія
    float p_out = pid->kp * error;

    // 2. Прямий зв'язок (похідна від зміни цілі пілота)
    float d_setpoint = (target_rate - pid->prev_setpoint) / dt;
    pid->prev_setpoint = target_rate;
    float ff_out = pid->k_ff * d_setpoint;

    // 3. Диференційна дія: D-on-Measurement з фільтрацією Notch
    float raw_d = -(meas_rate - pid->prev_meas) / dt;
    pid->prev_meas = meas_rate;
    float filtered_d = biquad_update(&pid->d_filter, raw_d);
    float d_out = pid->kd * filtered_d;

    // Сума швидких ланок
    float u_fast = p_out + d_out + ff_out;

    // 4. Інтегральна дія з умовним інтегруванням (Conditional Anti-Windup)
    float potential_i = pid->i_term + (pid->ki * error * dt);
    if (potential_i > pid->i_max) potential_i = pid->i_max;
    if (potential_i < -pid->i_max) potential_i = -pid->i_max;

    float potential_total = u_fast + potential_i;
    bool saturated = (potential_total > pid->out_max && error > 0.0f) ||
                     (potential_total < -pid->out_max && error < 0.0f);

    if (!saturated) {
        pid->i_term = potential_i;
    }

    // Підсумкове обмеження виходу
    float total_out = u_fast + pid->i_term;
    if (total_out > pid->out_max) total_out = pid->out_max;
    if (total_out < -pid->out_max) total_out = -pid->out_max;

    return total_out;
}

// ── 3. Матриця мікшування Quad-X з Air Mode ────────────────────────────────
typedef struct {
    float m1, m2, m3, m4;
} MotorOutputs;

MotorOutputs mixer_quad_x_update(float throttle, float roll, float pitch, float yaw) {
    MotorOutputs out;

    // Базові лінійні рівняння мікшування
    out.m1 = throttle - roll + pitch + yaw; // Rear-Right (CW)
    out.m2 = throttle - roll - pitch - yaw; // Front-Right (CCW)
    out.m3 = throttle + roll + pitch - yaw; // Rear-Left (CCW)
    out.m4 = throttle + roll - pitch + yaw; // Front-Left (CW)

    // Пошук екстремумів для динамічного зсуву діапазону (Air Mode)
    float min_m = out.m1;
    if (out.m2 < min_m) min_m = out.m2;
    if (out.m3 < min_m) min_m = out.m3;
    if (out.m4 < min_m) min_m = out.m4;

    float max_m = out.m1;
    if (out.m2 > max_m) max_m = out.m2;
    if (out.m3 > max_m) max_m = out.m3;
    if (out.m4 > max_m) max_m = out.m4;

    if (min_m < 0.0f) {
        float shift_up = -min_m;
        out.m1 += shift_up;
        out.m2 += shift_up;
        out.m3 += shift_up;
        out.m4 += shift_up;
        max_m += shift_up;
    }

    if (max_m > 1.0f) {
        float shift_down = max_m - 1.0f;
        out.m1 -= shift_down;
        out.m2 -= shift_down;
        out.m3 -= shift_down;
        out.m4 -= shift_down;
    }

    // Фінальне затискання у діапазон [0.0, 1.0]
    if (out.m1 < 0.0f) out.m1 = 0.0f; else if (out.m1 > 1.0f) out.m1 = 1.0f;
    if (out.m2 < 0.0f) out.m2 = 0.0f; else if (out.m2 > 1.0f) out.m2 = 1.0f;
    if (out.m3 < 0.0f) out.m3 = 0.0f; else if (out.m3 > 1.0f) out.m3 = 1.0f;
    if (out.m4 < 0.0f) out.m4 = 0.0f; else if (out.m4 > 1.0f) out.m4 = 1.0f;

    return out;
}
