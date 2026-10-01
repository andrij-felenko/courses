#include <stdio.h>
#include <math.h>

#define PT100_R0 100.0f
#define PT100_A  3.9083e-3f
#define PT100_B  -5.775e-7f

typedef enum {
    PT100_OK = 0,
    PT100_ERR_OPEN_CIRCUIT,
    PT100_ERR_SHORT_CIRCUIT
} pt100_status_t;

pt100_status_t pt100_calculate_temperature(float r_measured, float *temp_out) {
    if (r_measured > 400.0f) {
        return PT100_ERR_OPEN_CIRCUIT;
    }
    if (r_measured < 18.0f) {
        return PT100_ERR_SHORT_CIRCUIT;
    }

    float poly_c = 1.0f - (r_measured / PT100_R0);
    float discriminant = (PT100_A * PT100_A) - (4.0f * PT100_B * poly_c);
    if (discriminant < 0.0f) {
        return PT100_ERR_SHORT_CIRCUIT;
    }
    *temp_out = (-PT100_A + sqrtf(discriminant)) / (2.0f * PT100_B);
    return PT100_OK;
}
