/* C: Поліфазний інтерполятор сигналів для форматів float та Q15 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/* Структура поліфазного інтерполятора float */
typedef struct {
    size_t factor_L;      /* Коефіцієнт інтерполяції */
    size_t taps_per_phase;/* Довжина кожної поліфазної філії */
    float **phase_taps;   /* Таблиця коефіцієнтів [L][taps_per_phase] */
    float *state;         /* Кільцевий буфер вхідних відліків */
    size_t state_head;    /* Вказівник голови буфера */
} polyphase_interp_f32_t;

polyphase_interp_f32_t* polyphase_interp_f32_create(
    size_t factor_L,
    const float *taps,
    size_t total_taps
) {
    if (factor_L == 0 || total_taps == 0) return NULL;

    polyphase_interp_f32_t *it = (polyphase_interp_f32_t*)malloc(sizeof(polyphase_interp_f32_t));
    if (!it) return NULL;

    it->factor_L = factor_L;
    it->taps_per_phase = (total_taps + factor_L - 1) / factor_L;

    it->phase_taps = (float**)malloc(factor_L * sizeof(float*));
    for (size_t p = 0; p < factor_L; ++p) {
        it->phase_taps[p] = (float*)calloc(it->taps_per_phase, sizeof(float));
    }

    /* Декомпозиція коефіцієнтів: e_p[n] = h[n*L + p] */
    for (size_t i = 0; i < total_taps; ++i) {
        size_t p = i % factor_L;
        size_t n = i / factor_L;
        it->phase_taps[p][n] = taps[i];
    }

    it->state = (float*)calloc(it->taps_per_phase, sizeof(float));
    it->state_head = 0;

    return it;
}

void polyphase_interp_f32_destroy(polyphase_interp_f32_t *it) {
    if (!it) return;
    for (size_t p = 0; p < it->factor_L; ++p) {
        free(it->phase_taps[p]);
    }
    free(it->phase_taps);
    free(it->state);
    free(it);
}

/* Приймає 1 вхідний відлік, ґенерує L вихідних відліків у out_samples */
void polyphase_interp_f32_process_sample(
    polyphase_interp_f32_t *it,
    float in_sample,
    float *out_samples
) {
    /* Додаємо новий відлік у зсувний буфер на низькій частоті fs */
    it->state[it->state_head] = in_sample;

    for (size_t p = 0; p < it->factor_L; ++p) {
        float acc = 0.0f;
        size_t taps_count = it->taps_per_phase;
        const float *phase_h = it->phase_taps[p];

        for (size_t i = 0; i < taps_count; ++i) {
            size_t idx = (it->state_head + taps_count - i) % taps_count;
            acc += phase_h[i] * it->state[idx];
        }
        out_samples[p] = acc;
    }

    it->state_head = (it->state_head + 1) % it->taps_per_phase;
}
