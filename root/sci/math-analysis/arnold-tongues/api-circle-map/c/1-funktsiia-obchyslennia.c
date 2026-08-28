#include <stddef.h>
#include <stdbool.h>

typedef enum {
    CIRCLE_MAP_SUCCESS = 0,
    CIRCLE_MAP_ERROR_NULL_POINTER = -1,
    CIRCLE_MAP_ERROR_INVALID_PARAM = -2,
    CIRCLE_MAP_ERROR_CONVERGENCE = -3,
    CIRCLE_MAP_ERROR_OUT_OF_MEMORY = -4
} circle_map_status_t;

typedef struct {
    double omega;
    double k;
    size_t transient_steps;
    size_t measure_steps;
    double initial_x;
} circle_map_config_t;

typedef struct {
    double rotation_number;
    int numerator;
    int denominator;
    bool is_locked;
    double lyapunov_exponent;
} circle_map_result_t;

/**
 * @brief Обчислює число обертання та режим захоплення фази.
 * @param[in] cfg Вказівник на конфігурацію параметрів.
 * @param[in] max_q Максимальний розглядний знаменник резонансу.
 * @param[in] tol Допустиме відхилення для фіксації фазового захоплення.
 * @param[out] out_result Вказівник на структуру для запису результатів.
 * @return Код статусу виконання circle_map_status_t.
 */
circle_map_status_t circle_map_solve(
    const circle_map_config_t *cfg,
    int max_q,
    double tol,
    circle_map_result_t *out_result
);
