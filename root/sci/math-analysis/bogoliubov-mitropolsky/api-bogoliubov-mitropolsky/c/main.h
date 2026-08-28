#ifndef LIBBM_AVERAGING_H
#define LIBBM_AVERAGING_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BM_SUCCESS = 0,
    BM_ERROR_NULL_POINTER = -1,
    BM_ERROR_INVALID_EPS = -2,
    BM_ERROR_INVALID_ORDER = -3,
    BM_ERROR_ALLOCATION_FAILED = -4,
    BM_ERROR_DIVERGENCE = -5,
    BM_ERROR_QUADRATURE_FAILED = -6
} bm_status_t;

typedef struct {
    double eps;
    double omega0;
    int order;
    size_t quadrature_points;
} bm_config_t;

typedef struct {
    double t;
    double amplitude;
    double phase;
    double x_full;
    double v_full;
} bm_state_t;

/* Вказівник на функцію нелінійного збурення f(x, v) */
typedef double (*bm_perturbation_fn)(double x, double v, void *user_data);

/* Опаковий контекст обчислювача */
typedef struct bm_context bm_context_t;

/**
 * Створення та ініціалізація контексту усереднення Боголюбова — Митропольського.
 */
bm_status_t bm_context_create(const bm_config_t *config,
                              bm_perturbation_fn fn,
                              void *user_data,
                              bm_context_t **out_ctx);

/**
 * Звільнення ресурсів контексту.
 */
bm_status_t bm_context_destroy(bm_context_t *ctx);

/**
 * Встановлення початкового стану осцилятора.
 */
bm_status_t bm_set_initial_state(bm_context_t *ctx, double a0, double psi0);

/**
 * Виконання одного кроку інтегрування усередненої системи на інтервал dt.
 */
bm_status_t bm_step(bm_context_t *ctx, double dt);

/**
 * Отримання поточного відновленого стану осцилятора.
 */
bm_status_t bm_get_state(const bm_context_t *ctx, bm_state_t *out_state);

/**
 * Обчислення першої осцилюючої поправки u1(a, theta) в точці.
 */
bm_status_t bm_compute_u1(const bm_context_t *ctx, double a, double theta, double *out_u1);

#ifdef __cplusplus
}
#endif

#endif /* LIBBM_AVERAGING_H */
