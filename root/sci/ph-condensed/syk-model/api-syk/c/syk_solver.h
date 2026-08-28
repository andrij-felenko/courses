/* C API специфікація заголовного файлу syk_solver.h */
#include <complex.h>
#include <stdint.h>

typedef enum {
    SYK_SUCCESS = 0,                  /* Успішне виконання операції */
    SYK_ERROR_INVALID_PARAM = -1,     /* Некоректні параметри конфігурації */
    SYK_ERROR_OUT_OF_MEMORY = -2,     /* Недостатньо оперативної пам'яті */
    SYK_ERROR_CONVERGENCE_FAILED = -3,/* Не вдалося досягти збіжності */
    SYK_ERROR_NULL_POINTER = -4       /* Передано нульовий вказівник */
} syk_status_t;

typedef struct {
    uint32_t N_fermions;
    uint32_t q_body;
    double beta;
    double J_coupling;
    uint32_t grid_points;
    double mix_alpha;
    double tolerance;
    uint32_t max_iters;
} SYKSolverConfig;

typedef struct syk_solver_handle_t syk_solver_handle_t;

syk_status_t syk_solver_create(const SYKSolverConfig* config, syk_solver_handle_t** handle_out);
syk_status_t syk_solver_run(syk_solver_handle_t* handle);
syk_status_t syk_solver_get_g_tau(const syk_solver_handle_t* handle, double* out_tau_grid, double* out_g_tau);
syk_status_t syk_solver_get_sigma_omega(const syk_solver_handle_t* handle, double complex* out_sigma_omega);
void syk_solver_destroy(syk_solver_handle_t* handle);
