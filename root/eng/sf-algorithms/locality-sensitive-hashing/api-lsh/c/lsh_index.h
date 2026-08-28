/* --- C-ABI Публічний заголовок lsh_index.h --- */

#ifndef LSH_INDEX_H
#define LSH_INDEX_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    LSH_METRIC_JACCARD   = 1,
    LSH_METRIC_COSINE    = 2,
    LSH_METRIC_EUCLIDEAN = 3
} lsh_metric_type_t;

typedef enum {
    LSH_SUCCESS            =  0,  /* Операція успішно завершена */
    LSH_ERR_INVALID_PARAM  = -1,  /* Некоректні вхідні параметри */
    LSH_ERR_NO_MEMORY      = -2,  /* Помилка виділення пам'яті */
    LSH_ERR_DIM_MISMATCH   = -3,  /* Невідповідність вимірності вектора */
    LSH_ERR_INDEX_EMPTY    = -4   /* Індекс порожній */
} lsh_error_t;

typedef struct {
    lsh_metric_type_t metric;
    size_t dim;
    size_t num_bands;
    size_t rows_per_band;
    float  bin_width;
    size_t initial_capacity;
    uint32_t seed;
} lsh_config_t;

typedef struct {
    uint64_t vector_id;
    float    distance;
} lsh_match_t;

typedef struct lsh_index lsh_index_t;

lsh_error_t lsh_index_create(const lsh_config_t *config, lsh_index_t **out_index);

lsh_error_t lsh_index_insert(lsh_index_t *idx, uint64_t id, const float *data);

lsh_error_t lsh_index_query_knn(
    const lsh_index_t *idx,
    const float *query_vec,
    size_t top_k,
    size_t max_candidates,
    lsh_match_t *out_matches,
    size_t *out_count
);

void lsh_index_destroy(lsh_index_t *idx);

#ifdef __cplusplus
}
#endif

#endif /* LSH_INDEX_H */
