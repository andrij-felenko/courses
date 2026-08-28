#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>
#include <stdio.h>

#define DRIFT_EPSILON 1e-7f
#define ADWIN_MAX_BUCKETS 64
#define ADWIN_BUCKET_DEGREE 5

/* ── 1. ДЕТЕКТОР CUSUM ─────────────────────────────────────────────────── */

typedef struct {
    float mu_target;
    float slack_delta;
    float threshold_h;
    float s_pos;
    float s_neg;
    uint32_t sample_cnt;
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

void cusum_reset(cusum_detector_t *d) {
    if (!d) return;
    d->s_pos = 0.0f;
    d->s_neg = 0.0f;
    d->sample_cnt = 0;
}

bool cusum_update(cusum_detector_t *d, float x_val, bool *out_pos_alarm, bool *out_neg_alarm) {
    if (!d) return false;
    d->sample_cnt++;

    float diff_pos = x_val - d->mu_target - d->slack_delta;
    float diff_neg = d->mu_target - d->slack_delta - x_val;

    d->s_pos = (d->s_pos + diff_pos > 0.0f) ? (d->s_pos + diff_pos) : 0.0f;
    d->s_neg = (d->s_neg + diff_neg > 0.0f) ? (d->s_neg + diff_neg) : 0.0f;

    bool pos = (d->s_pos >= d->threshold_h);
    bool neg = (d->s_neg >= d->threshold_h);

    if (out_pos_alarm) *out_pos_alarm = pos;
    if (out_neg_alarm) *out_neg_alarm = neg;

    return (pos || neg);
}

/* ── 2. ДЕТЕКТОР ADWIN (АДАПТИВНЕ ВІКНО НА БАКЕТАХ) ─────────────────────── */

typedef struct {
    uint32_t size;  /* Кількість елементів (2^j) */
    float total;    /* Сума елементів у бакеті */
} adwin_bucket_t;

typedef struct {
    adwin_bucket_t buckets[ADWIN_MAX_BUCKETS];
    uint32_t bucket_count;
    uint32_t total_elements;
    float total_sum;
    float confidence_delta; /* Рівень хибної тривоги (наприклад, 0.002) */
} adwin_detector_t;

void adwin_init(adwin_detector_t *ad, float delta) {
    if (!ad) return;
    ad->bucket_count = 0;
    ad->total_elements = 0;
    ad->total_sum = 0.0f;
    ad->confidence_delta = (delta > 0.0f && delta < 1.0f) ? delta : 0.002f;
    memset(ad->buckets, 0, sizeof(ad->buckets));
}

static void adwin_drop_oldest_bucket(adwin_detector_t *ad) {
    if (ad->bucket_count == 0) return;

    ad->total_elements -= ad->buckets[0].size;
    ad->total_sum -= ad->buckets[0].total;

    for (uint32_t i = 0; i < ad->bucket_count - 1; ++i) {
        ad->buckets[i] = ad->buckets[i + 1];
    }
    ad->bucket_count--;
}

static void adwin_compress_buckets(adwin_detector_t *ad) {
    uint32_t cur_size = 1;
    uint32_t i = ad->bucket_count;

    while (i > 0) {
        /* Підрахунок бакетів однакового розміру cur_size */
        uint32_t count_same = 0;
        int32_t idx = (int32_t)i - 1;
        while (idx >= 0 && ad->buckets[idx].size == cur_size) {
            count_same++;
            idx--;
        }

        if (count_same > ADWIN_BUCKET_DEGREE) {
            /* Злиття двох найстаріших бакетів цього розміру */
            uint32_t merge_idx = (uint32_t)(idx + 1);
            ad->buckets[merge_idx].size *= 2;
            ad->buckets[merge_idx].total += ad->buckets[merge_idx + 1].total;

            for (uint32_t k = merge_idx + 1; k < ad->bucket_count - 1; ++k) {
                ad->buckets[k] = ad->buckets[k + 1];
            }
            ad->bucket_count--;
            /* Продовжуємо перевірку без зміни cur_size */
        } else {
            cur_size *= 2;
            i = (uint32_t)(idx + 1);
        }
    }
}

static bool adwin_check_cut(const adwin_detector_t *ad, uint32_t *cut_bucket_idx) {
    if (ad->bucket_count < 2 || ad->total_elements < 10) return false;

    uint32_t n0 = 0;
    float sum0 = 0.0f;

    for (uint32_t i = 0; i < ad->bucket_count - 1; ++i) {
        n0 += ad->buckets[i].size;
        sum0 += ad->buckets[i].total;

        uint32_t n1 = ad->total_elements - n0;
        float sum1 = ad->total_sum - sum0;

        if (n0 >= 4 && n1 >= 4) {
            float mu0 = sum0 / (float)n0;
            float mu1 = sum1 / (float)n1;
            float diff = fabsf(mu0 - mu1);

            float m = 1.0f / ((1.0f / (float)n0) + (1.0f / (float)n1));
            float eps_cut = sqrtf((1.0f / (2.0f * m)) * logf(4.0f / ad->confidence_delta));

            if (diff >= eps_cut) {
                if (cut_bucket_idx) *cut_bucket_idx = i;
                return true;
            }
        }
    }
    return false;
}

bool adwin_update(adwin_detector_t *ad, float x_val) {
    if (!ad) return false;

    /* Додаємо новий бакет одиничного розміру в кінець */
    if (ad->bucket_count >= ADWIN_MAX_BUCKETS) {
        adwin_drop_oldest_bucket(ad);
    }

    uint32_t last = ad->bucket_count++;
    ad->buckets[last].size = 1;
    ad->buckets[last].total = x_val;
    ad->total_elements += 1;
    ad->total_sum += x_val;

    adwin_compress_buckets(ad);

    /* Перевірка статистичного розщеплення */
    bool drift_detected = false;
    uint32_t cut_idx = 0;

    while (adwin_check_cut(ad, &cut_idx)) {
        drift_detected = true;
        /* Видаляємо всі бакети включно до cut_idx */
        for (uint32_t k = 0; k <= cut_idx; ++k) {
            adwin_drop_oldest_bucket(ad);
        }
    }

    return drift_detected;
}

/* ── 3. СТАТИСТИКА ВЕЛФОРДА ТА ЕНТРОПІЯ SOFTMAX ────────────────────────── */

typedef struct {
    uint32_t n;
    float mean;
    float m2;
} welford_stat_t;

void welford_init(welford_stat_t *w) {
    if (!w) return;
    w->n = 0;
    w->mean = 0.0f;
    w->m2 = 0.0f;
}

void welford_update(welford_stat_t *w, float x) {
    if (!w) return;
    w->n++;
    float delta = x - w->mean;
    w->mean += delta / (float)w->n;
    float delta2 = x - w->mean;
    w->m2 += delta * delta2;
}

float welford_variance(const welford_stat_t *w) {
    if (!w || w->n < 2) return 0.0f;
    return w->m2 / (float)(w->n - 1);
}

float compute_softmax_entropy(const float *logits, uint32_t k) {
    if (!logits || k == 0) return 0.0f;

    float max_l = logits[0];
    for (uint32_t i = 1; i < k; ++i) {
        if (logits[i] > max_l) max_l = logits[i];
    }

    float sum_exp = 0.0f;
    for (uint32_t i = 0; i < k; ++i) {
        sum_exp += expf(logits[i] - max_l);
    }

    float entropy = 0.0f;
    for (uint32_t i = 0; i < k; ++i) {
        float p = expf(logits[i] - max_l) / (sum_exp + DRIFT_EPSILON);
        if (p > DRIFT_EPSILON) {
            entropy -= p * logf(p);
        }
    }

    float max_ent = logf((float)k);
    return (max_ent > DRIFT_EPSILON) ? (entropy / max_ent) : 0.0f;
}

float mahalanobis_diag_distance(const float *z, const float *mu, const float *var, uint32_t dim) {
    if (!z || !mu || !var || dim == 0) return 0.0f;

    float d2 = 0.0f;
    for (uint32_t i = 0; i < dim; ++i) {
        float diff = z[i] - mu[i];
        d2 += (diff * diff) / (var[i] + DRIFT_EPSILON);
    }
    return d2;
}

/* ── 4. ЕСКАЛАЦІЙНИЙ МОНІТОР-МЕНЕДЖЕР ───────────────────────────────────── */

typedef enum {
    DRIFT_LEVEL_0_NOMINAL = 0,
    DRIFT_LEVEL_1_WARNING = 1,
    DRIFT_LEVEL_2_CONFIRMED = 2,
    DRIFT_LEVEL_3_FAILSAFE = 3
} drift_level_t;

typedef struct {
    cusum_detector_t entropy_cusum;
    adwin_detector_t entropy_adwin;
    welford_stat_t embedding_stats;
    drift_level_t current_level;
    uint32_t cooldown_timer;
    uint32_t cooldown_target;
    float ood_mahalanobis_threshold;
} drift_monitor_engine_t;

void drift_engine_init(drift_monitor_engine_t *eng, float nom_entropy, float ood_threshold) {
    if (!eng) return;
    cusum_init(&eng->entropy_cusum, nom_entropy, 0.05f, 4.0f);
    adwin_init(&eng->entropy_adwin, 0.002f);
    welford_init(&eng->embedding_stats);
    eng->current_level = DRIFT_LEVEL_0_NOMINAL;
    eng->cooldown_timer = 0;
    eng->cooldown_target = 100;
    eng->ood_mahalanobis_threshold = ood_threshold;
}

drift_level_t drift_engine_step(drift_monitor_engine_t *eng,
                                const float *logits, uint32_t num_classes,
                                const float *embedding, const float *ref_mu,
                                const float *ref_var, uint32_t emb_dim) {
    if (!eng) return DRIFT_LEVEL_3_FAILSAFE;

    float norm_entropy = compute_softmax_entropy(logits, num_classes);
    float d2_mahal = mahalanobis_diag_distance(embedding, ref_mu, ref_var, emb_dim);
    welford_update(&eng->embedding_stats, norm_entropy);

    bool pos_alarm = false, neg_alarm = false;
    cusum_update(&eng->entropy_cusum, norm_entropy, &pos_alarm, &neg_alarm);
    bool adwin_alarm = adwin_update(&eng->entropy_adwin, norm_entropy);

    /* Логіка FSM ескалації */
    if (d2_mahal > eng->ood_mahalanobis_threshold * 2.0f) {
        eng->current_level = DRIFT_LEVEL_3_FAILSAFE;
        eng->cooldown_timer = 0;
    } else if (adwin_alarm || (pos_alarm && d2_mahal > eng->ood_mahalanobis_threshold)) {
        eng->current_level = DRIFT_LEVEL_2_CONFIRMED;
        eng->cooldown_timer = 0;
    } else if (pos_alarm || adwin_alarm) {
        if (eng->current_level < DRIFT_LEVEL_1_WARNING) {
            eng->current_level = DRIFT_LEVEL_1_WARNING;
        }
        eng->cooldown_timer = 0;
    } else {
        /* Механізм відновлення через гістерезис */
        if (eng->current_level > DRIFT_LEVEL_0_NOMINAL) {
            eng->cooldown_timer++;
            if (eng->cooldown_timer >= eng->cooldown_target) {
                eng->current_level = (drift_level_t)(eng->current_level - 1);
                eng->cooldown_timer = 0;
                cusum_reset(&eng->entropy_cusum);
            }
        }
    }

    return eng->current_level;
}

/* ── 5. ТЕСТОВИЙ СТЕНД ─────────────────────────────────────────────────── */

int main(void) {
    printf("=== ТЕСТ БОРТОВОГО МОНІТОРА ДРЕЙФУ (C99) ===\n");

    drift_monitor_engine_t engine;
    drift_engine_init(&engine, 0.15f, 50.0f);

    float ref_mu[4] = {1.0f, 2.0f, -1.0f, 0.5f};
    float ref_var[4] = {0.2f, 0.2f, 0.2f, 0.2f};

    /* Фаза 1: Номінальний режим (100 вибірок) */
    printf("[Фаза 1] Стаціонарний вхід (100 циклів)...\n");
    for (int t = 0; t < 100; ++t) {
        float logits[3] = {4.5f, 0.2f, 0.1f}; /* Гострий розподіл */
        float emb[4] = {1.05f, 1.95f, -0.98f, 0.52f};
        drift_level_t lvl = drift_engine_step(&engine, logits, 3, emb, ref_mu, ref_var, 4);
        if (lvl != DRIFT_LEVEL_0_NOMINAL) {
            printf("ПОМИЛКА: Несподівана тривога на такті %d (Рівень %d)\n", t, lvl);
            return 1;
        }
    }
    printf("  -> Успіх: 0 хибних тривог.\n");

    /* Фаза 2: Стрибок розмиття / засліплення (ентропія зростає) */
    printf("[Фаза 2] Стрибок ентропії (імітація засліплення сонцем)...\n");
    int alarm_tick = -1;
    for (int t = 100; t < 200; ++t) {
        float logits[3] = {1.1f, 1.0f, 0.95f}; /* Майже рівномірний розподіл */
        float emb[4] = {1.1f, 1.9f, -1.1f, 0.4f};
        drift_level_t lvl = drift_engine_step(&engine, logits, 3, emb, ref_mu, ref_var, 4);
        if (lvl >= DRIFT_LEVEL_1_WARNING && alarm_tick == -1) {
            alarm_tick = t;
            printf("  -> Тривогу дрейфу зафіксовано на такті %d (Рівень %d)\n", t, lvl);
        }
    }

    if (alarm_tick != -1 && alarm_tick <= 125) {
        printf("  -> Успіх: Дрейф виявлено за %d тактів після виникнення.\n", alarm_tick - 100);
    } else {
        printf("ПОМИЛКА: Занадто довга затримка детекції (%d)\n", alarm_tick);
        return 1;
    }

    printf("Усі тести пройдено успішно.\n");
    return 0;
}
