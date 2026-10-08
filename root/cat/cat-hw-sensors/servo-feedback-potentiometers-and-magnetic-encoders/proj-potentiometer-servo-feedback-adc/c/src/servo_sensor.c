#include "servo_sensor.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

void ring_buffer_init(ring_buffer_t *rb, float *storage_array, size_t capacity) {
    if (rb == NULL || storage_array == NULL || capacity == 0) {
        return;
    }
    rb->buffer = storage_array;
    rb->capacity = capacity;
    rb->head = 0;
    rb->count = 0;
    rb->running_sum = 0.0;
    for (size_t i = 0; i < capacity; ++i) {
        rb->buffer[i] = 0.0f;
    }
}

float ring_buffer_update(ring_buffer_t *rb, float sample) {
    if (rb == NULL || rb->capacity == 0) {
        return sample;
    }

    if (rb->count < rb->capacity) {
        // Фаза початкового накопичення вибірок
        rb->buffer[rb->head] = sample;
        rb->running_sum += sample;
        rb->count++;
    } else {
        // Заміщуємо найстаріший елемент новим значенням за O(1) без повторного підсумовування
        rb->running_sum = rb->running_sum - rb->buffer[rb->head] + sample;
        rb->buffer[rb->head] = sample;
    }

    rb->head = (rb->head + 1) % rb->capacity;

    return (float)(rb->running_sum / rb->count);
}

void ema_filter_init(ema_filter_t *ema, float alpha) {
    if (ema == NULL) {
        return;
    }
    if (alpha <= 0.0f) {
        alpha = 0.01f;
    } else if (alpha > 1.0f) {
        alpha = 1.0f;
    }
    ema->alpha = alpha;
    ema->filtered_val = 0.0f;
    ema->initialized = false;
}

float ema_filter_update(ema_filter_t *ema, float input) {
    if (ema == NULL) {
        return input;
    }
    if (!ema->initialized) {
        // Перше значення ініціалізує фільтр без фазового запізнення
        ema->filtered_val = input;
        ema->initialized = true;
    } else {
        // Формула ЕМА: y_k = alpha * x_k + (1 - alpha) * y_{k-1}
        ema->filtered_val = ema->alpha * input + (1.0f - ema->alpha) * ema->filtered_val;
    }
    return ema->filtered_val;
}

void servo_sensor_init(servo_sensor_t *sensor, adc_handle_t *adc_handle, 
                      float *rb_storage, size_t rb_capacity, float ema_alpha) {
    if (sensor == NULL) {
        return;
    }
    sensor->adc_handle = adc_handle;
    sensor->last_raw_adc = 0;
    sensor->last_filtered_adc = 0.0f;
    sensor->current_angle_deg = 0.0f;

    ring_buffer_init(&sensor->ring_buf, rb_storage, rb_capacity);
    ema_filter_init(&sensor->ema, ema_alpha);

    // Ініціалізація калібрування за замовчуванням
    sensor->calib.adc_cal_zero = 0;
    sensor->calib.adc_cal_span = 4095;
    sensor->calib.adc_deadband_low = 0;
    sensor->calib.adc_deadband_high = 4095;
    sensor->calib.angle_zero_deg = 0.0f;
    sensor->calib.angle_span_deg = 180.0f;
    sensor->calib.is_calibrated = false;
}

bool servo_sensor_calibrate(servo_sensor_t *sensor, uint16_t raw_zero, float angle_zero,
                            uint16_t raw_span, float angle_span, uint16_t deadband_margin_codes) {
    if (sensor == NULL || raw_zero == raw_span || angle_zero == angle_span) {
        return false;
    }

    sensor->calib.adc_cal_zero = raw_zero;
    sensor->calib.adc_cal_span = raw_span;
    sensor->calib.angle_zero_deg = angle_zero;
    sensor->calib.angle_span_deg = angle_span;

    // Враховуємо полярність підключення потенціометра або магнітного енкодера
    if (raw_span > raw_zero) {
        sensor->calib.adc_deadband_low = raw_zero + deadband_margin_codes;
        sensor->calib.adc_deadband_high = (raw_span > deadband_margin_codes) ? (raw_span - deadband_margin_codes) : raw_span;
    } else {
        sensor->calib.adc_deadband_high = (raw_zero > deadband_margin_codes) ? (raw_zero - deadband_margin_codes) : raw_zero;
        sensor->calib.adc_deadband_low = raw_span + deadband_margin_codes;
    }

    sensor->calib.is_calibrated = true;
    return true;
}

uint16_t servo_sensor_apply_deadband(const sensor_calib_t *calib, uint16_t raw_adc) {
    if (calib == NULL || !calib->is_calibrated) {
        return raw_adc;
    }

    // Пряме мапування (adc_cal_zero < adc_cal_span)
    if (calib->adc_cal_span >= calib->adc_cal_zero) {
        if (raw_adc <= calib->adc_deadband_low) {
            return calib->adc_cal_zero;
        }
        if (raw_adc >= calib->adc_deadband_high) {
            return calib->adc_cal_span;
        }
    } else {
        // Інвертоване мапування (adc_cal_zero > adc_cal_span)
        if (raw_adc >= calib->adc_deadband_high) {
            return calib->adc_cal_zero;
        }
        if (raw_adc <= calib->adc_deadband_low) {
            return calib->adc_cal_span;
        }
    }

    return raw_adc;
}

float servo_sensor_map_adc_to_angle(const sensor_calib_t *calib, float filtered_adc) {
    if (calib == NULL || !calib->is_calibrated) {
        return 0.0f;
    }

    float delta_adc = (float)calib->adc_cal_span - (float)calib->adc_cal_zero;
    if (fabsf(delta_adc) < 1e-5f) {
        return calib->angle_zero_deg;
    }

    float delta_angle = calib->angle_span_deg - calib->angle_zero_deg;
    float normalized_ratio = (filtered_adc - (float)calib->adc_cal_zero) / delta_adc;

    // Обмеження нормованого коефіцієнта в діапазоні [0.0, 1.0] для усунення перерегулювання
    if (normalized_ratio < 0.0f) {
        normalized_ratio = 0.0f;
    } else if (normalized_ratio > 1.0f) {
        normalized_ratio = 1.0f;
    }

    return calib->angle_zero_deg + normalized_ratio * delta_angle;
}

float servo_sensor_read_angle(servo_sensor_t *sensor) {
    if (sensor == NULL || sensor->adc_handle == NULL) {
        return 0.0f;
    }

    // 1. Отримання сирого значення з АЦП
    uint16_t raw_adc = adc_hal_read_raw(sensor->adc_handle);
    sensor->last_raw_adc = raw_adc;

    // 2. Програмне відсікання нелінійних мертвих зон на крайніх межах ходу
    uint16_t deadband_adc = servo_sensor_apply_deadband(&sensor->calib, raw_adc);

    // 3. Первинне приглушення високочастотного шуму: кільцеве ковзне середнє O(1)
    float ma_filtered = ring_buffer_update(&sensor->ring_buf, (float)deadband_adc);

    // 4. Вторинне згладжування: експоненціальний фільтр EMA (y_k = alpha*x_k + (1-alpha)*y_{k-1})
    float dual_filtered = ema_filter_update(&sensor->ema, ma_filtered);
    sensor->last_filtered_adc = dual_filtered;

    // 5. Лінійне дворівневе мапування в фізичний кут повороту (градуси)
    sensor->current_angle_deg = servo_sensor_map_adc_to_angle(&sensor->calib, dual_filtered);

    return sensor->current_angle_deg;
}
