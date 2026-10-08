#include "notch_filter.h"
#include <math.h>
#include <stddef.h>

/**
 * @file notch_filter.c
 * @brief Реалізація алгоритму режекторної БІХ-фільтрації Direct Form II.
 */

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

/**
 * @brief Скидання стану буферів затримки одноканального фільтра.
 */
void notch_filter_single_reset(notch_filter_single_t *filter) {
    if (filter == NULL) return;
    filter->w1 = 0.0f;
    filter->w2 = 0.0f;
}

/**
 * @brief Ініціалізація та розрахунок коефіцієнтів режекторного БІХ-фільтра.
 * @param filter Вказівник на структуру одноканального фільтра.
 * @param center_freq_hz Центральна частота вирізання f0 (Гц).
 * @param q_factor Добротність Q (визначає ширину смуги глушіння).
 * @param sample_rate_hz Частота дискретизації fs (Гц).
 */
void notch_filter_single_init(notch_filter_single_t *filter, float center_freq_hz, float q_factor, float sample_rate_hz) {
    if (filter == NULL || sample_rate_hz <= 0.0f || center_freq_hz <= 0.0f || q_factor <= 0.0f) {
        return;
    }

    /* Перевірка критерію Найквіста */
    if (center_freq_hz >= (sample_rate_hz * 0.5f)) {
        center_freq_hz = sample_rate_hz * 0.49f;
    }

    /* Нормалізована цифровий частота w0 = 2 * PI * f0 / fs */
    float omega0 = 2.0f * M_PI * center_freq_hz / sample_rate_hz;
    float sin_w0 = sinf(omega0);
    float cos_w0 = cosf(omega0);

    /* Параметр ширини смуги alpha = sin(w0) / (2 * Q) */
    float alpha = sin_w0 / (2.0f * q_factor);

    /* Сирі коефіцієнти передавальної функції H(z) */
    float b0_raw = 1.0f;
    float b1_raw = -2.0f * cos_w0;
    float b2_raw = 1.0f;

    float a0_raw = 1.0f + alpha;
    float a1_raw = -2.0f * cos_w0;
    float a2_raw = 1.0f - alpha;

    /* Нормалізація діленням на a0 */
    float inv_a0 = 1.0f / a0_raw;
    filter->b0 = b0_raw * inv_a0;
    filter->b1 = b1_raw * inv_a0;
    filter->b2 = b2_raw * inv_a0;
    filter->a1 = a1_raw * inv_a0;
    filter->a2 = a2_raw * inv_a0;

    notch_filter_single_reset(filter);
}

/**
 * @brief Виконання різницевого рівняння Direct Form II для одного відліку.
 * w[n] = x[n] - a1*w[n-1] - a2*w[n-2]
 * y[n] = b0*w[n] + b1*w[n-1] + b2*w[n-2]
 */
float notch_filter_single_process(notch_filter_single_t *filter, float input) {
    if (filter == NULL) return input;

    /* Обчислення внутрішньої змінної стану w[n] */
    float w0 = input - (filter->a1 * filter->w1) - (filter->a2 * filter->w2);

    /* Обчислення вихідного фільтрованого відліку y[n] */
    float output = (filter->b0 * w0) + (filter->b1 * filter->w1) + (filter->b2 * filter->w2);

    /* Зсув буфера станів затримки */
    filter->w2 = filter->w1;
    filter->w1 = w0;

    return output;
}

/**
 * @brief Ініціалізація двоосьового Notch-фільтра.
 */
void notch_filter_2axis_init(notch_filter_2axis_t *filter2a, float center_freq_hz, float q_factor, float sample_rate_hz) {
    if (filter2a == NULL) return;

    filter2a->center_freq_hz = center_freq_hz;
    filter2a->q_factor = q_factor;
    filter2a->sample_rate_hz = sample_rate_hz;

    notch_filter_single_init(&filter2a->axis_x, center_freq_hz, q_factor, sample_rate_hz);
    notch_filter_single_init(&filter2a->axis_y, center_freq_hz, q_factor, sample_rate_hz);
}

/**
 * @brief Скидання станів обох осей фільтра.
 */
void notch_filter_2axis_reset(notch_filter_2axis_t *filter2a) {
    if (filter2a == NULL) return;
    notch_filter_single_reset(&filter2a->axis_x);
    notch_filter_single_reset(&filter2a->axis_y);
}

/**
 * @brief Фільтрація двох осей сигналів у реальному часі.
 */
void notch_filter_2axis_process(notch_filter_2axis_t *filter2a, float in_x, float in_y, float *out_x, float *out_y) {
    if (filter2a == NULL) return;

    if (out_x != NULL) {
        *out_x = notch_filter_single_process(&filter2a->axis_x, in_x);
    }
    if (out_y != NULL) {
        *out_y = notch_filter_single_process(&filter2a->axis_y, in_y);
    }
}
