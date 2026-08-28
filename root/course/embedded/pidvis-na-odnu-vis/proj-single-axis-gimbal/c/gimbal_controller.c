/* ============================================================================
 * gimbal_controller.h / gimbal_controller.c
 * Модуль одноосьового гіроскопічного підвісу на чистому C (C99/C11)
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define GIMBAL_DT_SEC          0.005f   /* Крок такту 200 Гц (5 мс) */
#define GIMBAL_SERVO_MIN_US    1000.0f  /* Мінімальний імпульс ШІМ (мкс) */
#define GIMBAL_SERVO_MID_US    1500.0f  /* Нейтральне положення 0° (мкс) */
#define GIMBAL_SERVO_MAX_US    2000.0f  /* Максимальний імпульс ШІМ (мкс) */
#define GIMBAL_MAX_ANGLE_DEG   45.0f    /* Межа ходу шарніра ±45° */
#define GIMBAL_MAX_BIAS_VAR    0.25f    /* Максимальна допустима дисперсія шуму (°/с)² */

/* Стан комплементарного фільтра */
typedef struct {
    float angle_deg;    /* Відфільтрована оцінка кута (градуси) */
    float alpha;        /* Ваговий коефіцієнт довіри до гіроскопа */
} CompFilter;

/* Стан та налаштування ПІД-регулятора */
typedef struct {
    /* Коефіцієнти підсилення */
    float kp;
    float ki;
    float kd;

    /* Межі насичення керування */
    float out_min;
    float out_max;

    /* Стан інтегратора та фільтра похідної */
    float integrator;
    float d_lpf_state;
    float d_lpf_alpha;  /* Коефіцієнт ФНЧ для D-терму */
} GimbalPID;

/* Головна структура одноосьового стабілізатора */
typedef struct {
    CompFilter filter;
    GimbalPID  pid;
    float      gyro_bias_dps;  /* Зсув нуля гіроскопа (°/с) */
    bool       is_calibrated;
} SingleAxisGimbal;

/* Ініціалізація компонентів підвісу */
void gimbal_init(SingleAxisGimbal *gimbal, float alpha, float kp, float ki, float kd, float d_cutoff_hz)
{
    gimbal->filter.angle_deg = 0.0f;
    gimbal->filter.alpha     = alpha;

    gimbal->pid.kp = kp;
    gimbal->pid.ki = ki;
    gimbal->pid.kd = kd;
    gimbal->pid.out_min = -GIMBAL_MAX_ANGLE_DEG;
    gimbal->pid.out_max =  GIMBAL_MAX_ANGLE_DEG;
    gimbal->pid.integrator = 0.0f;
    gimbal->pid.d_lpf_state = 0.0f;

    /* Розрахунок коефіцієнта ФНЧ 1-го порядку для D-ланки: beta = dt / (dt + RC) */
    if (d_cutoff_hz > 0.0f) {
        float rc = 1.0f / (2.0f * 3.14159265f * d_cutoff_hz);
        gimbal->pid.d_lpf_alpha = GIMBAL_DT_SEC / (GIMBAL_DT_SEC + rc);
    } else {
        gimbal->pid.d_lpf_alpha = 1.0f; /* Без фільтрації */
    }

    gimbal->gyro_bias_dps = 0.0f;
    gimbal->is_calibrated = false;
}

/* Калібрування зміщення гіроскопа з перевіркою стаціонарності вибірки */
bool gimbal_calibrate_gyro(SingleAxisGimbal *gimbal, const float *gyro_samples, uint32_t count)
{
    if (count < 10) return false;

    float sum = 0.0f;
    for (uint32_t i = 0; i < count; ++i) {
        sum += gyro_samples[i];
    }
    float mean = sum / (float)count;

    /* Обчислення дисперсії для перевірки нерухомості датчика */
    float var_sum = 0.0f;
    for (uint32_t i = 0; i < count; ++i) {
        float diff = gyro_samples[i] - mean;
        var_sum += diff * diff;
    }
    float variance = var_sum / (float)(count - 1);

    if (variance > GIMBAL_MAX_BIAS_VAR) {
        /* Давач рухався під час калібрування: відхиляємо результат */
        gimbal->is_calibrated = false;
        return false;
    }

    gimbal->gyro_bias_dps = mean;
    gimbal->is_calibrated = true;
    return true;
}

/* Крок комплементарної фільтрації */
float comp_filter_update(CompFilter *f, float raw_gyro_dps, float gyro_bias_dps,
                         float ay, float az, float dt)
{
    /* 1. Компенсована кутова швидкість гіроскопа */
    float rate_dps = raw_gyro_dps - gyro_bias_dps;

    /* 2. Передбачення інтегруванням */
    float pred_angle = f->angle_deg + rate_dps * dt;

    /* 3. Кут нахилу за вектором тяжіння акселерометра */
    float acc_angle_deg = atan2f(ay, az) * (180.0f / 3.14159265f);

    /* 4. Комплементарне злиття */
    f->angle_deg = f->alpha * pred_angle + (1.0f - f->alpha) * acc_angle_deg;

    return f->angle_deg;
}

/* Крок розрахунку ПІД з динамічним Anti-Windup Clamping */
float pid_update(GimbalPID *pid, float setpoint_deg, float current_angle_deg,
                 float measured_rate_dps, float dt)
{
    /* 1. Похибка кута */
    float error = setpoint_deg - current_angle_deg;

    /* 2. Пропорційна ланка */
    float p_term = pid->kp * error;

    /* 3. Диференціальна ланка (Derivative on Measurement) з ФНЧ */
    float d_raw = -measured_rate_dps;
    pid->d_lpf_state += pid->d_lpf_alpha * (d_raw - pid->d_lpf_state);
    float d_term = pid->kd * pid->d_lpf_state;

    /* 4. Попереднє керування без нового інтеграла */
    float u_tentative = p_term + pid->integrator + d_term;

    /* 5. Захист від насичення інтегратора: Clamping Anti-Windup */
    bool is_saturated = false;
    if (u_tentative > pid->out_max || u_tentative < pid->out_min) {
        is_saturated = true;
    }

    /* Інтегруємо лише якщо привід не в насиченні АБО знак помилки протилежний знаку насичення */
    bool same_sign = (u_tentative * error > 0.0f);
    if (!is_saturated || !same_sign) {
        pid->integrator += pid->ki * error * dt;
    }

    /* 6. Повний вихід регулятора із жорстким обмеженням */
    float u_out = p_term + pid->integrator + d_term;
    if (u_out > pid->out_max) u_out = pid->out_max;
    if (u_out < pid->out_min) u_out = pid->out_min;

    return u_out;
}

/* Перерахунок кута відхилення сервоприводу в мікросекунди ШІМ */
uint16_t servo_output_map(float correction_deg)
{
    /* Мапування діапазону [-45°, +45°] на [1000 мкс, 2000 мкс], де 0° = 1500 мкс */
    float us_per_deg = (GIMBAL_SERVO_MAX_US - GIMBAL_SERVO_MIN_US) / (2.0f * GIMBAL_MAX_ANGLE_DEG);
    float pulse_us = GIMBAL_SERVO_MID_US + correction_deg * us_per_deg;

    if (pulse_us < GIMBAL_SERVO_MIN_US) pulse_us = GIMBAL_SERVO_MIN_US;
    if (pulse_us > GIMBAL_SERVO_MAX_US) pulse_us = GIMBAL_SERVO_MAX_US;

    return (uint16_t)(pulse_us + 0.5f);
}

/* Головний крок обробки (викликається кожні 5 мс за перериванням таймера) */
uint16_t gimbal_step(SingleAxisGimbal *gimbal, float raw_gyro_dps, float ay, float az)
{
    /* 1. Оновлення оцінки кута */
    float current_angle = comp_filter_update(&gimbal->filter, raw_gyro_dps,
                                            gimbal->gyro_bias_dps, ay, az, GIMBAL_DT_SEC);

    /* 2. Кутова швидкість за вирахуванням зміщення */
    float rate_dps = raw_gyro_dps - gimbal->gyro_bias_dps;

    /* 3. Уставка стабілізації горизонту (0.0 градусів) */
    float target_angle = 0.0f;

    /* 4. Розрахунок кутової корекції ПІД */
    float correction_deg = pid_update(&gimbal->pid, target_angle, current_angle,
                                      rate_dps, GIMBAL_DT_SEC);

    /* 5. Формування сигналу ШІМ для сервоприводу */
    return servo_output_map(correction_deg);
}
