#ifndef FLOQUET_SOLVER_H
#define FLOQUET_SOLVER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    FLOQUET_SUCCESS                =  0,
    FLOQUET_ERROR_INVALID_PARAM    = -1,
    FLOQUET_ERROR_INTEGRATION_FAIL = -2,
    FLOQUET_ERROR_EIGEN_FAIL       = -3,
    FLOQUET_ERROR_ALLOCATION       = -4
} floquet_status_t;

/* Вказівник на функцію коефіцієнтів A(t): заповнює плоский масив out_matrix (size n*n) */
typedef void (*floquet_rhs_fn)(double t, size_t n, double* out_matrix, void* user_data);

typedef struct {
    size_t dim;               /* Розмірність n */
    double period;            /* Період T */
    size_t steps;             /* Кількість кроків RK4 */
    double tol;               /* Чисельний допуск стійкості */
} floquet_config_t;

typedef struct {
    double* monodromy;        /* Вихідна матриця M розміру n*n (row-major) */
    double* re_multipliers;   /* Дійсна частина мультиплікаторів (розмір n) */
    double* im_multipliers;   /* Уявна частина мультиплікаторів (розмір n) */
    double max_modulus;       /* Максимальний модуль |lambda| */
    double trace;             /* Слід матриці монодромії tr(M) */
    bool is_stable;           /* Прапорець стійкості */
} floquet_result_t;

/* Виділення ресурсів для результату */
floquet_status_t floquet_result_alloc(size_t dim, floquet_result_t* res);

/* Звільнення ресурсів */
void floquet_result_free(floquet_result_t* res);

/* Обчислення матриці монодромії та аналіз мультиплікаторів */
floquet_status_t floquet_solve(
    const floquet_config_t* config,
    floquet_rhs_fn rhs,
    void* user_data,
    floquet_result_t* out_result
);

#ifdef __cplusplus
}
#endif

#endif /* FLOQUET_SOLVER_H */
