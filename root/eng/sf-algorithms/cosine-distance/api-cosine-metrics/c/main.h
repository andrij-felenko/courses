#ifndef VECTOR_METRICS_H
#define VECTOR_METRICS_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди результатів виконання операцій векторних метрик.
 */
typedef enum {
    METRICS_SUCCESS              =  0,  /**< Успішне виконання операції */
    METRICS_ERROR_NULL_POINTER    = -1,  /**< Передано нулевий вказівник */
    METRICS_ERROR_INVALID_SIZE   = -2,  /**< Некоректна вимірність (size == 0) */
    METRICS_ERROR_SIZE_MISMATCH  = -3,  /**< Вимірності векторів не збігаються */
    METRICS_ERROR_ZERO_NORM      = -4,  /**< Вектор має нульову норму (||v|| < eps) */
    METRICS_ERROR_UNALIGNED_DATA = -5   /**< Дані не вирівняні під вимоги SIMD */
} MetricsStatus;

/**
 * @brief Структура для представлення розрідженого вектора у форматі Compressed Sparse.
 */
typedef struct {
    const size_t *indices;  /**< Посортований масив індексів ненульових елементів */
    const float  *values;   /**< Масив відповідних ненульових значень */
    size_t        nnz;      /**< Кількість ненульових елементів (Number of Non-Zeroes) */
} SparseVector;

/**
 * @brief Опції для конфігурації векторних обчислень.
 */
typedef struct {
    bool use_simd;          /**< Дозволити апаратне SIMD-прискорення (AVX2/NEON) */
    bool assume_normalized; /**< Прапорець: вважати вектори вже L2-нормалізованими */
    float zero_eps;         /**< Епсілон для перевірки ділення на нуль (за замовчуванням 1e-12f) */
} MetricsOptions;

/**
 * @brief Повертає дефолтні налаштування обчислень.
 */
MetricsOptions metrics_options_default(void);

/**
 * @brief Обчислює косинусну відстань між двома щільними векторами.
 *
 * @param[in]  u        Вказівник на перший вектор
 * @param[in]  v        Вказівник на другий вектор
 * @param[in]  size     Вимірність векторів (кількість елементів float)
 * @param[out] out_dist Вказівник для запису обчисленої відстані d_cos ∈ [0.0, 2.0]
 * @return MetricsStatus Код стану виконання
 */
MetricsStatus metrics_cosine_distance_dense(
    const float *u,
    const float *v,
    size_t size,
    float *out_dist
);

/**
 * @brief Обчислює косинусну відстань із додатковими опціями.
 */
MetricsStatus metrics_cosine_distance_dense_ext(
    const float *u,
    const float *v,
    size_t size,
    const MetricsOptions *opts,
    float *out_dist
);

/**
 * @brief Пакетне обчислення косинусної відстані від один запиту до N векторів матриці.
 *
 * @param[in]  query       Вектор запиту вимірності dim
 * @param[in]  matrix      Матриця векторів розміром [num_vectors x dim] у суцільній пам'яті
 * @param[in]  num_vectors Кількість векторів у матриці
 * @param[in]  dim         Вимірність кожного вектора
 * @param[out] out_dists   Масив розміром num_vectors для запису результатів
 * @return MetricsStatus Код стану виконання
 */
MetricsStatus metrics_cosine_distance_batch(
    const float *query,
    const float *matrix,
    size_t num_vectors,
    size_t dim,
    float *out_dists
);

/**
 * @brief Обчислює косинусну відстань між двома розрідженими векторами.
 */
MetricsStatus metrics_cosine_distance_sparse(
    const SparseVector *u,
    const SparseVector *v,
    float *out_dist
);

/**
 * @brief Виконує L2-нормалізацію вектора inplace: u = u / ||u||.
 *
 * @param[in,out] vector Вказівник на вектор
 * @param[in]     size   Вимірність вектора
 * @return MetricsStatus METRICS_SUCCESS або METRICS_ERROR_ZERO_NORM
 */
MetricsStatus metrics_l2_normalize(
    float *vector,
    size_t size
);

#ifdef __cplusplus
}
#endif

#endif /* VECTOR_METRICS_H */
