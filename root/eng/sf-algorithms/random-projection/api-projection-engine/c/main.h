#ifndef RANDOM_PROJECTION_ENGINE_H
#define RANDOM_PROJECTION_ENGINE_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди результатів виконання операцій рушія */
typedef enum {
    RP_SUCCESS               =  0,  /* Операцію виконано успішно */
    RP_ERROR_INVALID_ARG     = -1,  /* Некоректні аргументи (d == 0 або k == 0) */
    RP_ERROR_OUT_OF_MEMORY   = -2,  /* Помилка виділення пам'яті під матрицю */
    RP_ERROR_NULL_POINTER    = -3,  /* Передано нульовий вказівник на дані */
    RP_ERROR_UNALIGNED_DATA  = -4,  /* Дані не вирівняні по межі 32/64 байт */
    RP_ERROR_DEGENERATE_NORM = -5   /* Норма вихідного вектора нульова при нормуванні */
} rp_status_t;

/* Типи ймовірнісних розподілів матриці проєктування */
typedef enum {
    RP_DIST_GAUSSIAN          = 0,  /* Щільна гаусова матриця N(0, 1) */
    RP_DIST_RADEMACHER        = 1,  /* Знаки {+1, -1} з імовірністю 1/2 */
    RP_DIST_SPARSE_ACHLIOPTAS = 2,  /* Розріджена {+√3, 0, -√3}, 66.7% нулів */
    RP_DIST_VERY_SPARSE       = 3   /* Дуже розріджена з коефіцієнтом s = √d */
} rp_distribution_t;

/* Структура конфігурації генерації проєктора */
typedef struct {
    uint32_t orig_dim;         /* Початкова розмірність d (1 .. 10^7) */
    uint32_t target_dim;       /* Цільова розмірність k (1 .. d) */
    rp_distribution_t dist;    /* Закон розподілу коефіцієнтів */
    uint64_t seed;             /* Зерно для генератора псевдовипадкових чисел */
    bool normalize_output;     /* Чи нормувати вихідний вектор до одиничної довжини */
} rp_config_t;

/* Непрозорий дескриптор екземпляра рушія */
typedef struct rp_engine rp_engine_t;

/* Створення та ініціалізація рушія випадкового проєктування */
rp_status_t rp_create(const rp_config_t *config, rp_engine_t **out_engine);

/* Звільнення ресурсів та очищення виділеної пам'яті */
void rp_destroy(rp_engine_t *engine);

/* Проєктування одного вектора: in_vec (d) -> out_vec (k) */
rp_status_t rp_transform_single(
    const rp_engine_t *engine,
    const float *in_vec,
    float *out_vec
);

/* Пакетне перетворення масиву векторів */
rp_status_t rp_transform_batch(
    const rp_engine_t *engine,
    const float *in_matrix,
    size_t num_vectors,
    size_t in_stride_floats,
    float *out_matrix,
    size_t out_stride_floats
);

#ifdef __cplusplus
}
#endif

#endif /* RANDOM_PROJECTION_ENGINE_H */
