#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>

typedef struct {
    int id;
    float *vector;
} ivf_entry_t;

typedef struct {
    float *centroid;
    ivf_entry_t *entries;
    size_t count;
    size_t capacity;
} ivf_cluster_t;

typedef struct {
    ivf_cluster_t *clusters;
    size_t num_clusters;
    int dim;
} ivf_index_t;

/* Обчислення квадрата евклідової відстані */
static inline float l2_sq(const float *a, const float *b, int dim) {
    float sum = 0.0f;
    for (int i = 0; i < dim; ++i) {
        float diff = a[i] - b[i];
        sum += diff * diff;
    }
    return sum;
}

/* Пошук найближчого сусіда через опитування n_probe найближчих центроїдів */
int ivf_search_nearest(const ivf_index_t *index, const float *query,
                       size_t n_probe, float *out_dist) {
    if (!index || index->num_clusters == 0) return -1;
    if (n_probe > index->num_clusters) n_probe = index->num_clusters;

    /* 1. Знаходимо відстані до всіх центроїдів кластерів */
    float *c_dists = (float *)malloc(index->num_clusters * sizeof(float));
    size_t *c_indices = (size_t *)malloc(index->num_clusters * sizeof(size_t));

    for (size_t i = 0; i < index->num_clusters; ++i) {
        c_dists[i] = l2_sq(query, index->clusters[i].centroid, index->dim);
        c_indices[i] = i;
    }

    /* 2. Простий вибір n_probe найменших центроїдів (часткове сортування вибором) */
    for (size_t i = 0; i < n_probe; ++i) {
        size_t min_idx = i;
        for (size_t j = i + 1; j < index->num_clusters; ++j) {
            if (c_dists[j] < c_dists[min_idx]) min_idx = j;
        }
        float tmp_d = c_dists[i]; c_dists[i] = c_dists[min_idx]; c_dists[min_idx] = tmp_d;
        size_t tmp_i = c_indices[i]; c_indices[i] = c_indices[min_idx]; c_indices[min_idx] = tmp_i;
    }

    /* 3. Скануємо вектори лише всередині відібраних n_probe кластерів */
    int best_id = -1;
    float best_dist_sq = FLT_MAX;

    for (size_t p = 0; p < n_probe; ++p) {
        const ivf_cluster_t *cl = &index->clusters[c_indices[p]];
        for (size_t j = 0; j < cl->count; ++j) {
            float d = l2_sq(query, cl->entries[j].vector, index->dim);
            if (d < best_dist_sq) {
                best_dist_sq = d;
                best_id = cl->entries[j].id;
            }
        }
    }

    free(c_dists);
    free(c_indices);

    if (out_dist) *out_dist = sqrtf(best_dist_sq);
    return best_id;
}
