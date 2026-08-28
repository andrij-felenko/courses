/* modal_solver_c.h — Оголошення типів та С-функцій бібліотеки Modal Solver */
#ifndef MODAL_SOLVER_C_H
#define MODAL_SOLVER_C_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди повернення та помилок виконання */
typedef enum {
    MODAL_SOLVER_SUCCESS = 0,
    MODAL_SOLVER_ERROR_NULL_POINTER = -1,
    MODAL_SOLVER_ERROR_INVALID_DIMENSION = -2,
    MODAL_SOLVER_ERROR_INVALID_MASS = -3,
    MODAL_SOLVER_ERROR_NOT_POSITIVE_DEFINITE = -4,
    MODAL_SOLVER_ERROR_EIGEN_CONVERGENCE_FAILED = -5
} modal_solver_status_t;

/* Структура конфігурації модального розв'язувача */
typedef struct {
    size_t dimension;             /* Кількість ступенів вільності N */
    const double *mass_matrix;    /* Матриця мас M [N * N] у format row-major */
    const double *stiffness_matrix;/* Матриця жорсткості K [N * N] */
    double tolerance;             /* Точність обчислення власних значень (напр. 1e-12) */
} modal_solver_config_t;

/* Структура результатів модального аналізу */
typedef struct {
    size_t dimension;
    double *eigenfrequencies;     /* Власні частоти w_i [N] (у рад/с) */
    double *modal_matrix;         /* Матриця модальних векторів T [N * N] */
    double recommended_max_dt;    /* Максимальний стійкий крок часу */
} modal_analysis_result_t;

/* Ініціалізація та виконання модального аналізу (розв'язання det(K - w^2 M) = 0) */
modal_solver_status_t modal_solver_analyze(
    const modal_solver_config_t *config,
    modal_analysis_result_t *result
);

/* Звільнення пам'яті результату модального аналізу */
void modal_analysis_result_free(modal_analysis_result_t *result);

/* Перетворення фізичних координат x у нормальні координати eta: eta = T^T * M * x */
modal_solver_status_t modal_solver_to_normal_coords(
    const modal_analysis_result_t *analysis,
    const double *physical_coords,
    double *normal_coords
);

/* Перетворення нормальних координат eta у фізичні координати x: x = T * eta */
modal_solver_status_t modal_solver_to_physical_coords(
    const modal_analysis_result_t *analysis,
    const double *normal_coords,
    double *physical_coords
);

#ifdef __cplusplus
}
#endif

#endif /* MODAL_SOLVER_C_H */
