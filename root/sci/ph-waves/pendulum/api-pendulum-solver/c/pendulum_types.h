/* pendulum_types.h - Типи даних та структури конфігурації у мові C */
#ifndef PENDULUM_TYPES_H
#define PENDULUM_TYPES_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PENDULUM_SOLVER_EULER           = 0,
    PENDULUM_SOLVER_VERLET          = 1,
    PENDULUM_SOLVER_RK4             = 2,
    PENDULUM_SOLVER_ADAPTIVE_RK45   = 3
} pendulum_solver_mode_t;

typedef enum {
    PENDULUM_OK                     =  0,
    PENDULUM_ERR_INVALID_PARAM      = -1,
    PENDULUM_ERR_DIVERGENCE         = -2,
    PENDULUM_ERR_ALLOCATION         = -3,
    PENDULUM_ERR_UNSUPPORTED_MODE   = -4
} pendulum_status_t;

typedef struct {
    double length;
    double mass;
    double gravity;
    double damping;
    double inertia;
    double pivot_dist;
    double drive_amplitude;
    double drive_frequency;
} pendulum_config_t;

typedef struct {
    double theta;
    double omega;
    double alpha;
    double time;
    uint64_t step_count;
} pendulum_state_t;

typedef struct {
    double kinetic_energy;
    double potential_energy;
    double total_energy;
    double initial_energy;
    double energy_drift_pct;
} pendulum_metrics_t;

#ifdef __cplusplus
}
#endif

#endif /* PENDULUM_TYPES_H */
