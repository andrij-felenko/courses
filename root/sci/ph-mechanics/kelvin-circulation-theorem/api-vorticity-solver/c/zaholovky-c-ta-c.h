#ifndef VORTICITY_SOLVER_H
#define VORTICITY_SOLVER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BC_PERIODIC = 0,
    BC_SLIP_WALL = 1,
    BC_NO_SLIP = 2
} boundary_cond_t;

typedef enum {
    SOLVER_SUCCESS = 0,
    SOLVER_ERR_INVALID_PARAM = -1,
    SOLVER_ERR_NO_MEMORY = -2,
    SOLVER_ERR_CFL_VIOLATION = -3,
    SOLVER_ERR_POISSON_CONVERGENCE = -4
} solver_error_t;

typedef struct {
    size_t nx;
    size_t ny;
    double dx;
    double dy;
    double dt;
    double viscosity;
    boundary_cond_t bc_type;
} solver_config_t;

typedef struct {
    double circulation;
    double vorticity_integral;
    double stokes_error;
    double baroclinic_generation;
    double viscous_dissipation;
} circulation_stats_t;

typedef struct {
    double x;
    double y;
} point2d_t;

typedef struct vorticity_solver_s vorticity_solver_t;

/* Створення та знищення об'єкта соловера */
solver_error_t vorticity_solver_create(const solver_config_t* config, vorticity_solver_t** out_solver);
void vorticity_solver_destroy(vorticity_solver_t* solver);

/* Ініціалізація початкового поля вихровості */
solver_error_t vorticity_solver_set_vorticity(vorticity_solver_t* solver, const double* omega_field);

/* Крок інтегрування по часу */
solver_error_t vorticity_solver_step(vorticity_solver_t* solver);

/* Отримання поточного фізичного часу */
double vorticity_solver_get_time(const vorticity_solver_t* solver);

/* Отримання вказівників на поля швидкостей та вихровості (readonly) */
const double* vorticity_solver_get_omega(const vorticity_solver_t* solver);
const double* vorticity_solver_get_velocity_u(const vorticity_solver_t* solver);
const double* vorticity_solver_get_velocity_v(const vorticity_solver_t* solver);

/* Обчислення циркуляції Кельвіна вздовж довільного замкненого полігонального контуру */
solver_error_t vorticity_solver_compute_circulation(
    const vorticity_solver_t* solver,
    const point2d_t* contour_points,
    size_t num_points,
    circulation_stats_t* out_stats
);

#ifdef __cplusplus
}
#endif

#endif /* VORTICITY_SOLVER_H */
