typedef enum {
    FLOQUET_SUCCESS               =  0,
    FLOQUET_ERROR_INVALID_PARAM   = -1,
    FLOQUET_ERROR_INTEGRATION_FAIL= -2,
    FLOQUET_ERROR_EIGEN_FAIL      = -3,
    FLOQUET_ERROR_ALLOCATION      = -4
} floquet_status_t;

typedef struct {
    size_t dim;               /* Розмірність n (dim >= 1) */
    double period;            /* Фізичний період T (period > 0) */
    size_t steps;             /* Кількість кроків сітки RK4 (steps >= 10) */
    double tol;               /* Допуск чистової стійкості (наприклад, 1e-5) */
} floquet_config_t;
