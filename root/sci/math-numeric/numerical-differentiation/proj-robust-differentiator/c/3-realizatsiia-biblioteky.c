#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define PI_F 3.14159265358979323846f

/* --- Модульне розгортання кута (Phase Unwrapping) --- */
float unwrap_angle_diff(float measured_pos, float prev_pos) {
    float diff = measured_pos - prev_pos;
    while (diff > PI_F)  diff -= 2.0f * PI_F;
    while (diff < -PI_F) diff += 2.0f * PI_F;
    return diff;
}

/* --- 1. Спостерігач стану Alpha-Beta-Gamma --- */
typedef struct {
    float pos;          /* оцінене положення x̂ */
    float vel;          /* оцінена швидкість v̂ */
    float acc;          /* оцінене прискорення â */
    float alpha;        /* коефіцієнт корекції положення */
    float beta;         /* коефіцієнт корекції швидкості */
    float gamma;        /* коефіцієнт корекції прискорення */
    float max_accel;    /* обмеження максимального фізичного прискорення */
    bool initialized;
} TrackingDifferentiator;

void track_diff_init(TrackingDifferentiator* td, float alpha, float beta, float gamma, float max_accel) {
    td->pos = 0.0f;
    td->vel = 0.0f;
    td->acc = 0.0f;
    td->alpha = (alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.6f;
    td->beta = (beta > 0.0f && beta <= 1.0f) ? beta : 0.3f;
    td->gamma = (gamma >= 0.0f && gamma <= 1.0f) ? gamma : 0.05f;
    td->max_accel = (max_accel > 0.0f) ? max_accel : 10000.0f;
    td->initialized = false;
}

void track_diff_reset(TrackingDifferentiator* td, float initial_pos) {
    td->pos = initial_pos;
    td->vel = 0.0f;
    td->acc = 0.0f;
    td->initialized = true;
}

void track_diff_update(TrackingDifferentiator* td, float measured_pos, float dt) {
    if (dt <= 0.000001f || dt > 1.0f) {
        return; /* Захист від збою таймера або джиттера */
    }

    if (!td->initialized) {
        track_diff_reset(td, measured_pos);
        return;
    }

    /* 1. Етап прогнозу (інтегрування моделі кінематики) */
    const float pos_pred = td->pos + td->vel * dt + 0.5f * td->acc * dt * dt;
    const float vel_pred = td->vel + td->acc * dt;
    const float acc_pred = td->acc;

    /* 2. Інновація виміру з розгортанням кута */
    const float residual = unwrap_angle_diff(measured_pos, pos_pred);

    /* 3. Етап корекції стану */
    td->pos = pos_pred + td->alpha * residual;
    td->vel = vel_pred + (td->beta / dt) * residual;
    
    float new_acc = acc_pred + (2.0f * td->gamma / (dt * dt)) * residual;

    /* Обмеження прискорення фізичними межами привода */
    if (new_acc > td->max_accel) {
        new_acc = td->max_accel;
    } else if (new_acc < -td->max_accel) {
        new_acc = -td->max_accel;
    }
    td->acc = new_acc;
}

/* --- 2. Диференціатор Тастіна другого порядку --- */
typedef struct {
    float x1, x2;       /* стан фільтра прямої форми II */
    float y_prev;       /* попереднє значення виходу */
    float cutoff_rad;   /* частота зрізу в рад/с */
} TustinDifferentiator2nd;

void tustin2_init(TustinDifferentiator2nd* td, float cutoff_hz) {
    td->x1 = 0.0f;
    td->x2 = 0.0f;
    td->y_prev = 0.0f;
    td->cutoff_rad = 2.0f * PI_F * ((cutoff_hz > 0.1f) ? cutoff_hz : 10.0f);
}

float tustin2_update(TustinDifferentiator2nd* td, float input, float dt) {
    if (dt <= 0.000001f) {
        return td->y_prev;
    }

    /* H(s) = s * omega^2 / (s^2 + 2*zeta*omega*s + omega^2), де zeta = 0.7071 */
    const float w = td->cutoff_rad;
    const float zeta = 0.70710678f;
    const float c = 2.0f / dt;

    const float a0 = c * c + 2.0f * zeta * w * c + w * w;
    const float b0 = (c * w * w) / a0;
    const float b2 = -b0;
    const float a1 = (2.0f * w * w - 2.0f * c * c) / a0;
    const float a2 = (c * c - 2.0f * zeta * w * c + w * w) / a0;

    /* Пряма форма II */
    const float x0 = input - a1 * td->x1 - a2 * td->x2;
    const float output = b0 * x0 + b2 * td->x2;

    td->x2 = td->x1;
    td->x1 = x0;
    td->y_prev = output;

    return output;
}
