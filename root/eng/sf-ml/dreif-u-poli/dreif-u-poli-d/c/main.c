#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define DRIFT_EPSILON 1e-7f

typedef struct {
    float mu_target;     /* Номінальне математичне сподівання сигналу */
    float slack_delta;   /* Люфт для компенсації шуму */
    float threshold_h;   /* Поріг фіксації тривоги */
    float s_pos;         /* Позитивний накопичувач CUSUM */
    float s_neg;         /* Негативний накопичувач CUSUM */
    uint32_t sample_cnt; /* Загальна кількість оброблених вибірок */
} cusum_detector_t;

void cusum_init(cusum_detector_t *d, float mu, float delta, float threshold) {
    if (!d) return;
    d->mu_target = mu;
    d->slack_delta = delta;
    d->threshold_h = threshold;
    d->s_pos = 0.0f;
    d->s_neg = 0.0f;
    d->sample_cnt = 0;
}

bool cusum_update(cusum_detector_t *d, float x_val, bool *out_pos_alarm, bool *out_neg_alarm) {
    if (!d) return false;

    d->sample_cnt++;
    
    /* Оновлення верхнього та нижнього накопичувачів */
    float diff_pos = x_val - d->mu_target - d->slack_delta;
    float diff_neg = d->mu_target - d->slack_delta - x_val;

    d->s_pos = (d->s_pos + diff_pos > 0.0f) ? (d->s_pos + diff_pos) : 0.0f;
    d->s_neg = (d->s_neg + diff_neg > 0.0f) ? (d->s_neg + diff_neg) : 0.0f;

    bool pos_alarm = (d->s_pos >= d->threshold_h);
    bool neg_alarm = (d->s_neg >= d->threshold_h);

    if (out_pos_alarm) *out_pos_alarm = pos_alarm;
    if (out_neg_alarm) *out_neg_alarm = neg_alarm;

    return (pos_alarm || neg_alarm);
}

float compute_softmax_entropy(const float *logits, uint32_t num_classes) {
    if (!logits || num_classes == 0) return 0.0f;

    /* Чисельно стабільний Softmax через віднімання максимуму */
    float max_l = logits[0];
    for (uint32_t i = 1; i < num_classes; ++i) {
        if (logits[i] > max_l) max_l = logits[i];
    }

    float sum_exp = 0.0f;
    for (uint32_t i = 0; i < num_classes; ++i) {
        sum_exp += expf(logits[i] - max_l);
    }

    float entropy = 0.0f;
    for (uint32_t i = 0; i < num_classes; ++i) {
        float p = expf(logits[i] - max_l) / (sum_exp + DRIFT_EPSILON);
        if (p > DRIFT_EPSILON) {
            entropy -= p * logf(p);
        }
    }

    /* Нормування на log(K) */
    float max_entropy = logf((float)num_classes);
    return (max_entropy > DRIFT_EPSILON) ? (entropy / max_entropy) : 0.0f;
}
