#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура стану фільтра DCOC */
typedef struct {
    float mean_i;
    float mean_q;
    float alpha;
} dcoc_filter_t;

/* Структура стану компенсатора IQ дисбалансу */
typedef struct {
    float p_i;       /* Потужність I каналу */
    float p_q;       /* Потужність Q каналу */
    float p_iq;      /* Взаємна кореляція I та Q */
    float mu;        /* Швидкість адаптації LMS */
    float c_phase;   /* Коефіцієнт фазової корекції */
    float c_gain;    /* Коефіцієнт амплітудної корекції */
} iq_calibrator_t;

/* Ініціалізація DCOC */
void dcoc_init(dcoc_filter_t *dcoc, float alpha) {
    dcoc->mean_i = 0.0f;
    dcoc->mean_q = 0.0f;
    dcoc->alpha = alpha;
}

/* Обробка буфера фільтром DCOC */
void dcoc_process(dcoc_filter_t *dcoc, float *i_buf, float *q_buf, size_t count) {
    const float alpha = dcoc->alpha;
    const float one_minus_alpha = 1.0f - alpha;

    for (size_t n = 0; n < count; ++n) {
        dcoc->mean_i = one_minus_alpha * dcoc->mean_i + alpha * i_buf[n];
        dcoc->mean_q = one_minus_alpha * dcoc->mean_q + alpha * q_buf[n];

        i_buf[n] -= dcoc->mean_i;
        q_buf[n] -= dcoc->mean_q;
    }
}

/* Ініціалізація IQ компенсатора */
void iq_calibrator_init(iq_calibrator_t *iq, float mu) {
    iq->p_i = 1.0f;
    iq->p_q = 1.0f;
    iq->p_iq = 0.0f;
    iq->mu = mu;
    iq->c_phase = 0.0f;
    iq->c_gain = 1.0f;
}

/* Адаптивне калібрування IQ дисбалансу за методом Ґрама-Шмідта */
void iq_calibrator_process(iq_calibrator_t *iq, float *i_buf, float *q_buf, size_t count) {
    const float mu = iq->mu;

    for (size_t n = 0; n < count; ++n) {
        const float i_in = i_buf[n];
        const float q_in = q_buf[n];

        /* Оновлення статистики адаптації */
        iq->p_i  = (1.0f - mu) * iq->p_i  + mu * (i_in * i_in);
        iq->p_q  = (1.0f - mu) * iq->p_q  + mu * (q_in * q_in);
        iq->p_iq = (1.0f - mu) * iq->p_iq + mu * (i_in * q_in);

        /* Обчислення коефіцієнтів компенсації */
        if (iq->p_i > 1e-9f && iq->p_q > 1e-9f) {
            iq->c_phase = iq->p_iq / iq->p_i;
            iq->c_gain  = sqrtf(iq->p_i / iq->p_q);
        }

        /* Застосування ортогоналізації Ґрама-Шмідта */
        const float i_out = i_in;
        const float q_out = (q_in - iq->c_phase * i_in) * iq->c_gain;

        i_buf[n] = i_out;
        q_buf[n] = q_out;
    }
}
