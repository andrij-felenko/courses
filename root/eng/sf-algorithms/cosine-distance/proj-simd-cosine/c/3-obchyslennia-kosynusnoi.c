#include <math.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    const size_t *indices;
    const float *values;
    size_t nnz; // кількість ненульових елементів (Number of Non-Zeroes)
} SparseVectorC;

MetricResult cosine_distance_sparse(const SparseVectorC *u, const SparseVectorC *v) {
    MetricResult res = {1.0f, false};
    if (!u || !v || u->nnz == 0 || v->nnz == 0) return res;

    // Обчислюємо норму u заздалегідь або під час проходу
    float sq_u = 0.0f;
    for (size_t i = 0; i < u->nnz; ++i) {
        sq_u += u->values[i] * u->values[i];
    }

    float sq_v = 0.0f;
    for (size_t j = 0; j < v->nnz; ++j) {
        sq_v += v->values[j] * v->values[j];
    }

    float dot = 0.0f;
    size_t i = 0, j = 0;

    // Двопокажчиковий перетин посортованих індексів
    while (i < u->nnz && j < v->nnz) {
        size_t idx_u = u->indices[i];
        size_t idx_v = v->indices[j];

        if (idx_u == idx_v) {
            dot += u->values[i] * v->values[j];
            i++;
            j++;
        } else if (idx_u < idx_v) {
            i++;
        } else {
            j++;
        }
    }

    const float eps = 1e-12f;
    if (sq_u < eps || sq_v < eps) return res;

    float norm_prod = sqrtf(sq_u) * sqrtf(sq_v);
    float cos_sim = dot / norm_prod;

    if (cos_sim > 1.0f) cos_sim = 1.0f;
    if (cos_sim < -1.0f) cos_sim = -1.0f;

    res.distance = 1.0f - cos_sim;
    res.success = true;
    return res;
}
