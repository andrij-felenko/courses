#ifndef FEIGENBAUM_H
#define FEIGENBAUM_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    FEIGENBAUM_SUCCESS               =  0,
    FEIGENBAUM_ERR_INVALID_PARAM     = -1,
    FEIGENBAUM_ERR_MAX_ITERS_REACHED = -2,
    FEIGENBAUM_ERR_DERIVATIVE_ZERO   = -3,
    FEIGENBAUM_ERR_OUT_OF_MEMORY     = -4,
    FEIGENBAUM_ERR_NUMERICAL_OVERFLOW= -5
} FeigenbaumStatus;

typedef struct {
    double r_min;
    double r_max;
    size_t r_steps;
    size_t transient_iters;
    size_t orbit_iters;
} BifurcationConfig;

typedef struct {
    double r_superstable;
    double f_val;
    size_t iterations_used;
    double lyapunov_exp;
} SuperstableResult;

typedef struct {
    double delta;
    double alpha;
    double delta_error;
    double alpha_error;
} FeigenbaumConstants;

/* Публічні функції C API */

FeigenbaumStatus feigenbaum_compute_diagram(
    const BifurcationConfig* config,
    double* out_orbit_buffer
);

FeigenbaumStatus feigenbaum_find_superstable(
    int period_power,
    double r_guess,
    double tolerance,
    size_t max_iters,
    SuperstableResult* out_result
);

FeigenbaumStatus feigenbaum_estimate_constants(
    const double* r_superstable_array,
    size_t array_length,
    FeigenbaumConstants* out_constants
);

FeigenbaumStatus feigenbaum_compute_lyapunov(
    double r,
    size_t num_iters,
    double* out_lyapunov
);

#ifdef __cplusplus
}
#endif

#endif /* FEIGENBAUM_H */
