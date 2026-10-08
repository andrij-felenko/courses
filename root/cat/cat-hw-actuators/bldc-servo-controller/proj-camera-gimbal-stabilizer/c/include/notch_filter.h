#ifndef NOTCH_FILTER_H
#define NOTCH_FILTER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file notch_filter.h
 * @brief Оголошення двополюсного БІХ-фільтра (Direct Form II) для приглушення механічних резонансів.
 */

/**
 * @brief Структурні коефіцієнти та буфер станів одноканального Notch-фільтра.
 */
typedef struct {
    float b0; /**< Коефіцієнт чисельника b0 */
    float b1; /**< Коефіцієнт чисельника b1 */
    float b2; /**< Коефіцієнт чисельника b2 */
    float a1; /**< Коефіцієнт знаменника a1 */
    float a2; /**< Коефіцієнт знаменника a2 */
    float w1; /**< Стан затримки z^-1 (w[n-1]) */
    float w2; /**< Стан затримки z^-2 (w[n-2]) */
} notch_filter_single_t;

/**
 * @brief Двоосьовий цифровий Notch-фільтр для сигналів зворотного зв'язку (X/Y або d/q).
 */
typedef struct {
    notch_filter_single_t axis_x; /**< Фільтр першої осі */
    notch_filter_single_t axis_y; /**< Фільтр другої осі */
    float center_freq_hz;         /**< Центральна частота режекції (Гц) */
    float q_factor;               /**< Добротність фільтра Q */
    float sample_rate_hz;         /**< Частота дискретизації (Гц) */
} notch_filter_2axis_t;

/* Прототипи функцій */
void notch_filter_single_init(notch_filter_single_t *filter, float center_freq_hz, float q_factor, float sample_rate_hz);
float notch_filter_single_process(notch_filter_single_t *filter, float input);
void notch_filter_single_reset(notch_filter_single_t *filter);

void notch_filter_2axis_init(notch_filter_2axis_t *filter2a, float center_freq_hz, float q_factor, float sample_rate_hz);
void notch_filter_2axis_process(notch_filter_2axis_t *filter2a, float in_x, float in_y, float *out_x, float *out_y);
void notch_filter_2axis_reset(notch_filter_2axis_t *filter2a);

#endif /* NOTCH_FILTER_H */
