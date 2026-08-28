#ifndef POISSON_BOUNDARY_CONDITIONS_API_H
#define POISSON_BOUNDARY_CONDITIONS_API_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Перелічуваний тип видів граничних умов */
typedef enum {
    BC_TYPE_DIRICHLET = 0,
    BC_TYPE_NEUMANN   = 1,
    BC_TYPE_ROBIN     = 2,
    BC_TYPE_FLOATING  = 3,
    BC_TYPE_PERIODIC  = 4
} BoundaryConditionType;

/* Перелічуваний тип ітераційних алгоритмів */
typedef enum {
    SOLVER_JACOBI       = 0,
    SOLVER_GAUSS_SEIDEL = 1,
    SOLVER_SOR          = 2,
    SOLVER_PCG_ICCG     = 3,
    SOLVER_MULTIGRID    = 4
} SolverAlgorithm;

/* Описовий вузол граничної умови */
typedef struct {
    BoundaryConditionType type;
    double v_value;        /* Значення для Dirichlet (В) */
    double flux_value;     /* Значення для Neumann (В/м) */
    double alpha_coeff;    /* Коефіцієнт a для Robin */
    double beta_coeff;     /* Коефіцієнт b для Robin */
    double gamma_target;   /* Цільове значення c для Robin */
    double q_total;        /* Сумарний заряд для Floating (Кл) */
} BoundarySpec;

/* Опис конфігурації прямокутної сітки */
typedef struct {
    uint32_t dim;          /* 2 або 3 */
    size_t nx;
    size_t ny;
    size_t nz;
    double dx;
    double dy;
    double dz;
    double origin_x;
    double origin_y;
    double origin_z;
    double eps_r_default;
} GridGeometrySpec;

/* Параметри конфігурації розв'язувача */
typedef struct {
    SolverAlgorithm algorithm;
    double tolerance;
    size_t max_iterations;
    double omega_override;
    uint32_t residual_metric;
} SolverConfigSpec;

/* Результат обчислення */
typedef struct {
    uint32_t status_code;
    size_t iterations_spent;
    double final_residual;
    double execution_time_ms;
    double total_energy_joules;
    double max_electric_field;
} SolverExecutionSummary;

/* Сигнатури фундаментальних викликів API */

/**
 * @brief Перевіряє коректність конфігурації сітки та параметрів
 * @return 0 при успіху, або код помилки ERR_*
 */
int poisson_api_validate_config(const GridGeometrySpec *grid, const SolverConfigSpec *config);

/**
 * @brief Розраховує оптимальний параметр релаксації SOR для заданої сітки
 */
double poisson_api_calculate_optimal_omega(size_t nx, size_t ny, size_t nz);

/**
 * @brief Виконує чисельний розв'язок крайової задачі Пуассона 2D/3D
 */
int poisson_api_solve(
    const GridGeometrySpec *grid_spec,
    const SolverConfigSpec *config_spec,
    const BoundarySpec *boundary_map,
    const double *charge_density_array,
    double *potential_output_array,
    SolverExecutionSummary *execution_summary
);

#ifdef __cplusplus
}
#endif

#endif /* POISSON_BOUNDARY_CONDITIONS_API_H */
