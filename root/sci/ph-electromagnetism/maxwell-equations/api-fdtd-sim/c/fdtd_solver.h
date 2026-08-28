/* FDTD Solver Public C API Header (fdtd_solver.h) */
#ifndef FDTD_SOLVER_H
#define FDTD_SOLVER_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    FDTD_SUCCESS                    =  0,
    FDTD_ERROR_NULL_POINTER         = -1,
    FDTD_ERROR_INVALID_GRID_SIZE    = -2,
    FDTD_ERROR_CFL_VIOLATION        = -3,
    FDTD_ERROR_OUT_OF_MEMORY        = -4,
    FDTD_ERROR_INVALID_MATERIAL     = -5,
    FDTD_ERROR_UNSTABLE_SIMULATION  = -6
} FdtdStatus;

typedef enum {
    FDTD_FIELD_EX = 0, FDTD_FIELD_EY, FDTD_FIELD_EZ,
    FDTD_FIELD_HX, FDTD_FIELD_HY, FDTD_FIELD_HZ
} FdtdFieldComponent;

typedef struct {
    uint32_t dim;
    size_t Nx, Ny, Nz;
    double dx, dy, dz;
    double dt;
    double courant_factor;
} FdtdGridConfig;

typedef struct {
    double eps_r;
    double mu_r;
    double sigma_e;
    double sigma_m;
} MaterialProperties;

typedef struct FdtdSolverOpaque* FdtdSolverHandle;

/* Функції управління життєвим циклом солвера */
FdtdStatus fdtd_solver_create(FdtdSolverHandle* handle, const FdtdGridConfig* cfg);
FdtdStatus fdtd_solver_set_material(FdtdSolverHandle handle, size_t i, size_t j, size_t k, const MaterialProperties* mat);
FdtdStatus fdtd_solver_add_soft_source(FdtdSolverHandle handle, size_t pos_x, double t0, double tau);
FdtdStatus fdtd_solver_step(FdtdSolverHandle handle);
FdtdStatus fdtd_solver_run(FdtdSolverHandle handle, size_t num_steps);
FdtdStatus fdtd_solver_get_field_data(FdtdSolverHandle handle, FdtdFieldComponent comp, double* out_buffer, size_t buffer_size);
void fdtd_solver_destroy(FdtdSolverHandle handle);

#ifdef __cplusplus
}
#endif

#endif /* FDTD_SOLVER_H */
