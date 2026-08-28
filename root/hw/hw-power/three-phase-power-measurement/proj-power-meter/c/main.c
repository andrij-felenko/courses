/* c */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define SAMPLES_PER_PERIOD 128
#define NUM_PHASES 3

/* Структура результатів вимірювання для однієї фази */
typedef struct {
    float v_rms;       /* Діюча напруга, В */
    float i_rms;       /* Діючий струм, А */
    float p_active;    /* Активна потужність, Вт */
    float q_reactive;  /* Реактивна потужність, вар */
    float s_apparent;  /* Повна потужність, ВА */
    float power_factor;/* Коефіцієнт потужності cos(phi) */
} PhaseResult;

/* Структура загального стану трифазного аналізатора */
typedef struct {
    PhaseResult phases[NUM_PHASES];
    float p_total;
    float q_total;
    float s_total;
    float pf_total;
    float i_neutral_rms;
    double energy_kwh_accumulated;
} ThreePhaseResult;

/* Конфігурація коефіцієнтів калібрування тракту */
typedef struct {
    float v_scale;     /* Коефіцієнт масштабування напруги, В/LSD */
    float i_scale;     /* Коефіцієнт масштабування струму, А/LSD */
    float v_offset;    /* Зміщення нуля АЦП напруги */
    float i_offset;    /* Зміщення нуля АЦП струму */
} MeterCalibration;

/* Обчислення параметрів потужності за один період 50 Гц */
bool process_three_phase_frame(const float raw_v[NUM_PHASES][SAMPLES_PER_PERIOD],
                               const float raw_i[NUM_PHASES][SAMPLES_PER_PERIOD],
                               const MeterCalibration* cal,
                               ThreePhaseResult* out_result)
{
    if (!cal || !out_result) return false;

    float sum_p_total = 0.0f;
    float sum_q_total = 0.0f;
    const int q_shift = SAMPLES_PER_PERIOD / 4; /* Зсув на 90 градусів = 32 відліки */

    /* Цикл розрахунку по кожній із 3 фаз */
    for (int ph = 0; ph < NUM_PHASES; ++ph) {
        float sum_v2 = 0.0f;
        float sum_i2 = 0.0f;
        float sum_p  = 0.0f;
        float sum_q  = 0.0f;

        for (int k = 0; k < SAMPLES_PER_PERIOD; ++k) {
            /* Вилучення зміщення та масштабування */
            float v = (raw_v[ph][k] - cal->v_offset) * cal->v_scale;
            float i = (raw_i[ph][k] - cal->i_offset) * cal->i_scale;

            sum_v2 += v * v;
            sum_i2 += i * i;
            sum_p  += v * i;

            /* Квадратурний відлік напруги для Q (із кільцевим зсувом) */
            int k_q = (k >= q_shift) ? (k - q_shift) : (k + SAMPLES_PER_PERIOD - q_shift);
            float v_90 = (raw_v[ph][k_q] - cal->v_offset) * cal->v_scale;
            sum_q += v_90 * i;
        }

        PhaseResult* res = &out_result->phases[ph];
        res->v_rms = sqrtf(sum_v2 / (float)SAMPLES_PER_PERIOD);
        res->i_rms = sqrtf(sum_i2 / (float)SAMPLES_PER_PERIOD);
        res->p_active = sum_p / (float)SAMPLES_PER_PERIOD;
        res->q_reactive = sum_q / (float)SAMPLES_PER_PERIOD;
        res->s_apparent = res->v_rms * res->i_rms;

        if (res->s_apparent > 1e-5f) {
            res->power_factor = res->p_active / res->s_apparent;
            if (res->power_factor > 1.0f) res->power_factor = 1.0f;
            if (res->power_factor < -1.0f) res->power_factor = -1.0f;
        } else {
            res->power_factor = 1.0f;
        }

        sum_p_total += res->p_active;
        sum_q_total += res->q_reactive;
    }

    /* Розрахунок струму нейтралі iN(t) = iA(t) + iB(t) + iC(t) */
    float sum_in2 = 0.0f;
    for (int k = 0; k < SAMPLES_PER_PERIOD; ++k) {
        float iA = (raw_i[0][k] - cal->i_offset) * cal->i_scale;
        float iB = (raw_i[1][k] - cal->i_offset) * cal->i_scale;
        float iC = (raw_i[2][k] - cal->i_offset) * cal->i_scale;
        float iN = iA + iB + iC;
        sum_in2 += iN * iN;
    }
    out_result->i_neutral_rms = sqrtf(sum_in2 / (float)SAMPLES_PER_PERIOD);

    /* Загальні трифазні підсумки */
    out_result->p_total = sum_p_total;
    out_result->q_total = sum_q_total;
    out_result->s_total = sqrtf(sum_p_total * sum_p_total + sum_q_total * sum_q_total);
    out_result->pf_total = (out_result->s_total > 1e-5f) ? (out_result->p_total / out_result->s_total) : 1.0f;

    /* Інтегрування активної енергії за кадр тривалістю 0.02 с (50 Гц) */
    double frame_duration_sec = 0.02;
    double energy_joules = (double)out_result->p_total * frame_duration_sec;
    out_result->energy_kwh_accumulated += energy_joules / 3600000.0;

    return true;
}
