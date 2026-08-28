#ifndef BIQUAD_FILTER_H
#define BIQUAD_FILTER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Типи резонансного біквадратного фільтра */
typedef enum {
    BIQUAD_TYPE_BANDPASS = 0,  /* Смуговий резонансний фільтр */
    BIQUAD_TYPE_PEAKING,       /* Резонансний піковий еквалайзер (Peaking EQ) */
    BIQUAD_TYPE_LOWPASS_RES    /* Низькочастотний фільтр з резонансним піком */
} BiquadFilterType;

/* Структура коефіцієнтів та стану біквадратного фільтра */
typedef struct {
    /* Коефіцієнти нормованого різницевого рівняння */
    float b0;
    float b1;
    float b2;
    float a1;
    float a2;

    /* Внутрішній стан (Direct Form II Transposed) */
    float z1;
    float z2;

    /* Збережені конфігураційні параметри */
    float sample_rate;
    float center_freq;
    float Q;
    float gain_db;
    BiquadFilterType type;
} BiquadFilter;

/**
 * @brief Ініціалізувати або переконфігурувати резонансний біквадратний фільтр.
 * @return true при успішній конфігурації, false при невалідних аргументах.
 */
bool biquad_init(BiquadFilter *f, 
                 BiquadFilterType type, 
                 float sample_rate, 
                 float center_freq, 
                 float Q, 
                 float gain_db);

/**
 * @brief Скинути внутрішній стан (очистити історію затримок z1, z2).
 */
void biquad_reset(BiquadFilter *f);

/**
 * @brief Обробити один вхідний відлік сигналу.
 */
static inline float biquad_process_sample(BiquadFilter *f, float in_sample) {
    /* Direct Form II Transposed */
    float out = f->b0 * in_sample + f->z1;
    f->z1 = f->b1 * in_sample - f->a1 * out + f->z2;
    f->z2 = f->b2 * in_sample - f->a2 * out;
    return out;
}

/**
 * @brief Обробити масив відліків у пам'яті (пакетна обробка).
 */
void biquad_process_buffer(BiquadFilter *f, 
                           const float *input, 
                           float *output, 
                           size_t count);

#ifdef __cplusplus
}
#endif

#endif /* BIQUAD_FILTER_H */

/* --- Реалізація функцій C --- */
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

bool biquad_init(BiquadFilter *f, 
                 BiquadFilterType type, 
                 float sample_rate, 
                 float center_freq, 
                 float Q, 
                 float gain_db) 
{
    if (!f || sample_rate <= 0.0f || center_freq <= 0.0f || Q <= 0.001f) {
        return false;
    }

    if (center_freq >= sample_rate * 0.499f) {
        return false;
    }

    f->sample_rate = sample_rate;
    f->center_freq = center_freq;
    f->Q = Q;
    f->gain_db = gain_db;
    f->type = type;

    double w0 = 2.0 * M_PI * (double)center_freq / (double)sample_rate;
    double alpha = sin(w0) / (2.0 * (double)Q);
    double cos_w0 = cos(w0);
    double A = pow(10.0, (double)gain_db / 40.0);

    double b0_raw = 0.0, b1_raw = 0.0, b2_raw = 0.0;
    double a0_raw = 1.0, a1_raw = 0.0, a2_raw = 0.0;

    switch (type) {
        case BIQUAD_TYPE_BANDPASS:
            b0_raw = alpha;
            b1_raw = 0.0;
            b2_raw = -alpha;
            a0_raw = 1.0 + alpha;
            a1_raw = -2.0 * cos_w0;
            a2_raw = 1.0 - alpha;
            break;

        case BIQUAD_TYPE_PEAKING:
            b0_raw = 1.0 + alpha * A;
            b1_raw = -2.0 * cos_w0;
            b2_raw = 1.0 - alpha * A;
            a0_raw = 1.0 + alpha / A;
            a1_raw = -2.0 * cos_w0;
            a2_raw = 1.0 - alpha / A;
            break;

        case BIQUAD_TYPE_LOWPASS_RES:
            b0_raw = (1.0 - cos_w0) / 2.0;
            b1_raw = 1.0 - cos_w0;
            b2_raw = (1.0 - cos_w0) / 2.0;
            a0_raw = 1.0 + alpha;
            a1_raw = -2.0 * cos_w0;
            a2_raw = 1.0 - alpha;
            break;

        default:
            return false;
    }

    f->b0 = (float)(b0_raw / a0_raw);
    f->b1 = (float)(b1_raw / a0_raw);
    f->b2 = (float)(b2_raw / a0_raw);
    f->a1 = (float)(a1_raw / a0_raw);
    f->a2 = (float)(a2_raw / a0_raw);

    biquad_reset(f);
    return true;
}

void biquad_reset(BiquadFilter *f) {
    if (f) {
        f->z1 = 0.0f;
        f->z2 = 0.0f;
    }
}

void biquad_process_buffer(BiquadFilter *f, 
                           const float *input, 
                           float *output, 
                           size_t count) 
{
    if (!f || !input || !output) return;

    for (size_t i = 0; i < count; ++i) {
        output[i] = biquad_process_sample(f, input[i]);
    }
}
