#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

/* Константи числової безпеки та захисту від переповнення */
#define CORDIC_MAX_SAFE_INPUT_Q31  (1304032742) /* Гранична амплітуда 1.0 / 1.64676 у форматі Q1.31 */
#define NOISE_DEADBAND_THRESHOLD   (64)         /* Поріг відсікання фонового шуму АЦП */
#define SQRT3_INV_Q15              (18919)      /* Коефіцієнт 1 / sqrt(3) у форматі Q1.15 */

/* Типи координатних кадрів векторного керування */
typedef struct {
    int32_t alpha;
    int32_t beta;
} stationary_frame_t;

typedef struct {
    int32_t d;
    int32_t q;
} rotating_frame_t;

typedef struct {
    int32_t amplitude;
    int32_t angle_bam;
    bool    sensor_fault;
} resolver_telemetry_t;

/* Обмеження амплітуди через алгоритм насичення */
static inline int32_t saturate_input_q31(int32_t val) {
    if (val > CORDIC_MAX_SAFE_INPUT_Q31) {
        return CORDIC_MAX_SAFE_INPUT_Q31;
    }
    if (val < -CORDIC_MAX_SAFE_INPUT_Q31) {
        return -CORDIC_MAX_SAFE_INPUT_Q31;
    }
    return val;
}

/* Перетворення Кларк: фазні струми -> двофазна нерухома система */
stationary_frame_t clarke_transform(int32_t current_a, int32_t current_b) {
    stationary_frame_t out;
    out.alpha = current_a;
    /* beta = (I_a + 2 * I_b) / sqrt(3) у цілочисельній арифметиці */
    int64_t beta_calc = ((int64_t)(current_a + (current_b << 1)) * SQRT3_INV_Q15) >> 15;
    out.beta = (int32_t)beta_calc;
    return out;
}

/* Пряме перетворення Парка на апаратному блоці CORDIC */
rotating_frame_t park_transform_cordic(stationary_frame_t in, int32_t rotor_angle_bam) {
    rotating_frame_t out;

    /* Захист від сингулярності в зоні нульового струму */
    if ((abs(in.alpha) + abs(in.beta)) < NOISE_DEADBAND_THRESHOLD) {
        out.d = 0;
        out.q = 0;
        return out;
    }

    /* Апаратне обмеження для виключення проміжного переповнення */
    int32_t safe_alpha = saturate_input_q31(in.alpha);
    int32_t safe_beta  = saturate_input_q31(in.beta);

    /* Обертання на кут -theta переносить координати в обертову систему */
    int32_t cos_val;
    int32_t sin_val;
    cordic_calc_sin_cos_q31(-rotor_angle_bam, &cos_val, &sin_val);

    out.d = (int32_t)(((int64_t)safe_alpha * cos_val - (int64_t)safe_beta * sin_val) >> 31);
    out.q = (int32_t)(((int64_t)safe_beta * cos_val + (int64_t)safe_alpha * sin_val) >> 31);

    return out;
}

/* Зворотне перетворення Парка: формування напруг для блоку ШІМ */
stationary_frame_t inverse_park_transform_cordic(rotating_frame_t in, int32_t rotor_angle_bam) {
    stationary_frame_t out;
    int32_t cos_val;
    int32_t sin_val;

    /* Обертання вектора напруг на кут +theta ротора */
    cordic_calc_sin_cos_q31(rotor_angle_bam, &cos_val, &sin_val);

    out.alpha = (int32_t)(((int64_t)in.d * cos_val - (int64_t)in.q * sin_val) >> 31);
    out.beta  = (int32_t)(((int64_t)in.d * sin_val + (int64_t)in.q * cos_val) >> 31);

    return out;
}

/* Демодуляція сигналів резольвера у векторному режимі CORDIC */
resolver_telemetry_t demodulate_resolver(int32_t sin_sample, int32_t cos_sample) {
    resolver_telemetry_t result;

    /* Перевірка на обрив лінії або відсутність сигналу */
    if ((abs(sin_sample) + abs(cos_sample)) < NOISE_DEADBAND_THRESHOLD) {
        result.amplitude = 0;
        result.angle_bam = 0;
        result.sensor_fault = true;
        return result;
    }

    /* Виклик апаратного блоку у векторному режимі повертає модуль та фазу */
    CORDIC_HW->CSR = CORDIC_FUNC_MOD_PHASE | CORDIC_PRECISION_24CYCLES;
    CORDIC_HW->WDATA = (uint32_t)cos_sample; /* Координата X */
    CORDIC_HW->WDATA = (uint32_t)sin_sample; /* Координата Y */

    int32_t mag = (int32_t)CORDIC_HW->RDATA;
    int32_t phase_bam = (int32_t)CORDIC_HW->RDATA;

    result.amplitude = mag;
    result.angle_bam = phase_bam;
    result.sensor_fault = false;
    return result;
}
