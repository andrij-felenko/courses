/* pendulum_solver.h - Сигнатури функцій C API */
#ifndef PENDULUM_SOLVER_H
#define PENDULUM_SOLVER_H

#include "pendulum_types.h"

#ifdef __cplusplus
extern "C" {
#endif

pendulum_status_t pendulum_init(const pendulum_config_t *config,
                                double initial_theta,
                                double initial_omega,
                                pendulum_state_t *state);

pendulum_status_t pendulum_step(const pendulum_config_t *config,
                                pendulum_solver_mode_t mode,
                                double dt,
                                pendulum_state_t *state);

pendulum_status_t pendulum_get_metrics(const pendulum_config_t *config,
                                       const pendulum_state_t *state,
                                       double initial_energy,
                                       pendulum_metrics_t *metrics);

pendulum_status_t pendulum_calc_period_theory(const pendulum_config_t *config,
                                              double initial_theta_deg,
                                              double *out_period_sec);

#ifdef __cplusplus
}
#endif

#endif /* PENDULUM_SOLVER_H */
