#include <stddef.h>
#include <stdbool.h>

/**
 * @brief Структура конфігурації алгебри Вірасоро.
 */
typedef struct {
    double central_charge; /* Центральний заряд c */
    int max_level;         /* Максимальний рівень зрізання N у модулі Верма */
    bool use_ghost_sector; /* Включення духового сектора c_ghost = -26 */
} virasoro_config_t;

/**
 * @brief Структура результату аналізу визначника Каца.
 */
typedef struct {
    double c;               /* Обчислений центральний заряд */
    double h;               /* Конформна вага первинного стану */
    int level;              /* Рівень підпростору N */
    size_t dim;             /* Вимірність базису p(N) */
    double determinant;     /* Обчислене значення визначника Каца */
    bool is_unitary;        /* Прапор унітарності (відсутність духів) */
} virasoro_kac_result_t;

/* Обчислення комутатора: [L_n, L_m] = (n - m) L_{n+m} + (c/12)(n^3 - n) delta_{n+m, 0} */
int virasoro_commutator(
    const virasoro_config_t *cfg,
    int n,
    int m,
    int *out_target_mode,
    double *out_linear_coeff,
    double *out_central_term
);

/* Розрахунок визначника Каца та матриці Грама для заданого рівня N */
int virasoro_eval_kac_det(
    const virasoro_config_t *cfg,
    double conformal_weight_h,
    int level,
    virasoro_kac_result_t *out_res
);

/* Аудит повної конформної аномалії для з'єднаних векторних секторів */
double virasoro_total_central_charge(
    int num_bosons,
    int num_fermions,
    bool include_brst_ghosts
);
