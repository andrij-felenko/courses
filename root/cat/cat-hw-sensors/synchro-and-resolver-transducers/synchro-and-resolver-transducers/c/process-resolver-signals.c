#include <math.h>
#include <stdbool.h>

typedef struct {
    float angle_rad;
    bool fault;
} resolver_result_t;

resolver_result_t process_resolver_signals(float u_sin, float u_cos, float ref_amplitude, float tolerance) {
    resolver_result_t res;
    float magnitude_sq = u_sin * u_sin + u_cos * u_cos;
    float expected_sq = ref_amplitude * ref_amplitude;
    
    if (fabsf(magnitude_sq - expected_sq) > tolerance) {
        res.fault = true;
        res.angle_rad = 0.0f;
    } else {
        res.fault = false;
        res.angle_rad = atan2f(u_sin, u_cos);
        if (res.angle_rad < 0.0f) {
            res.angle_rad += 2.0f * (float)M_PI;
        }
    }
    return res;
}
