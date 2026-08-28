#ifndef HORSESHOE_C_H
#define HORSESHOE_C_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HORSESHOE_SUCCESS = 0,
    HORSESHOE_ERROR_OUT_OF_BOUNDS = -1,
    HORSESHOE_ERROR_ESCAPED_DOMAIN = -2,
    HORSESHOE_ERROR_INVALID_PARAM = -3,
    HORSESHOE_ERROR_NULL_POINTER = -4
} HorseshoeStatus;

typedef struct {
    double x;
    double y;
} HorseshoePoint2D;

typedef struct {
    double alpha;
    double beta;
} HorseshoeConfig;

HorseshoeStatus horseshoe_init_config(double alpha, double beta, HorseshoeConfig* config);

HorseshoeStatus horseshoe_map_forward(const HorseshoePoint2D* in_pt,
                                      HorseshoePoint2D* out_pt,
                                      const HorseshoeConfig* config);

HorseshoeStatus horseshoe_map_inverse(const HorseshoePoint2D* in_pt,
                                      HorseshoePoint2D* out_pt,
                                      const HorseshoeConfig* config);

HorseshoeStatus horseshoe_get_lyapunov(const HorseshoeConfig* config,
                                       double* lyap_x,
                                       double* lyap_y);

HorseshoeStatus horseshoe_reconstruct_orbit(const int* future_code,
                                            size_t future_len,
                                            const int* past_code,
                                            size_t past_len,
                                            const HorseshoeConfig* config,
                                            HorseshoePoint2D* out_pt);

HorseshoeStatus horseshoe_compute_capacity_dim(const HorseshoeConfig* config,
                                               double* out_dim);

#ifdef __cplusplus
}
#endif

#endif /* HORSESHOE_C_H */
