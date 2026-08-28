#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define EMBED_DIM 128

typedef struct {
    float x;
    float y;
    float z;
} point3d_t;

typedef struct {
    point3d_t pos;
    float cov[3];                   /* діагональні дисперсії за осями X, Y, Z */
    float descriptor[EMBED_DIM];    /* нормалізований вектор ознак Re-ID */
} target_candidate_t;

typedef struct {
    float mahalanobis_threshold;    /* поріг квадрата відстані Махаланобіса */
    float appearance_threshold;     /* поріг косинусної схожості */
    float weight_spatial;           /* вага просторової близькості (0.0..1.0) */
    float weight_appearance;        /* вага візуальної схожості (0.0..1.0) */
} gating_config_t;

/* Обчислення косинусної схожості нормалізованих дескрипторів */
static float appearance_similarity(const float *a, const float *b, uint16_t dim) {
    float dot = 0.0f;
    float norm_a = 0.0f;
    float norm_b = 0.0f;
    for (uint16_t i = 0; i < dim; ++i) {
        dot += a[i] * b[i];
        norm_a += a[i] * a[i];
        norm_b += b[i] * b[i];
    }
    float denom = sqrtf(norm_a) * sqrtf(norm_b);
    return (denom > 1e-6f) ? (dot / denom) : 0.0f;
}

/* Перевірка просторового стробу та обчислення комбінованого скору відповідності */
bool validate_reacquisition_candidate(
    const target_candidate_t *cand,
    const point3d_t *pred_pos,
    const float pred_cov[3],
    const float ref_desc[EMBED_DIM],
    const gating_config_t *cfg,
    float *out_match_score)
{
    float dx = cand->pos.x - pred_pos->x;
    float dy = cand->pos.y - pred_pos->y;
    float dz = cand->pos.z - pred_pos->z;

    /* Сумарна дисперсія інновації S = P_pred + R_meas */
    float var_x = (pred_cov[0] + cand->cov[0] > 1e-4f) ? (pred_cov[0] + cand->cov[0]) : 1e-4f;
    float var_y = (pred_cov[1] + cand->cov[1] > 1e-4f) ? (pred_cov[1] + cand->cov[1]) : 1e-4f;
    float var_z = (pred_cov[2] + cand->cov[2] > 1e-4f) ? (pred_cov[2] + cand->cov[2]) : 1e-4f;

    /* Квадрат відстані Махаланобіса */
    float d_mahalanobis_sq = (dx * dx) / var_x + (dy * dy) / var_y + (dz * dz) / var_z;

    /* Перевірка просторового критерію */
    if (d_mahalanobis_sq > cfg->mahalanobis_threshold) {
        return false;
    }

    /* Перевірка візуального дескриптора */
    float app_sim = appearance_similarity(cand->descriptor, ref_desc, EMBED_DIM);
    if (app_sim < cfg->appearance_threshold) {
        return false;
    }

    /* Нормалізований просторовий скор: 1.0 при d=0, спадає до 0 при межі стробу */
    float spatial_score = 1.0f - (d_mahalanobis_sq / cfg->mahalanobis_threshold);
    if (spatial_score < 0.0f) spatial_score = 0.0f;

    /* Зважений комбінований скор кандидата */
    if (out_match_score != NULL) {
        *out_match_score = cfg->weight_spatial * spatial_score + cfg->weight_appearance * app_sim;
    }

    return true;
}
