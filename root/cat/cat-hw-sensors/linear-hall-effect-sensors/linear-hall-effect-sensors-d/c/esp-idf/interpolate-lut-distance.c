#include <stdio.h>
#include <math.h>

// Struct for Look-Up Table calibration point
typedef struct {
    float field_mt;
    float distance_mm;
} lut_point_t;

#define LUT_SIZE 5

static const lut_point_t calib_lut[LUT_SIZE] = {
    {100.0f,  1.0f},
    { 60.0f,  3.0f},
    { 35.0f,  6.0f},
    { 20.0f, 10.0f},
    { 10.0f, 15.0f}
};

// Polynomial coefficients: d(B) = c0 + c1*B + c2*B^2
static const float c0 = 22.45f;
static const float c1 = -0.385f;
static const float c2 = 0.0017f;

float interpolate_lut_distance(float field_mt) {
    // Clamping limits
    if (field_mt >= calib_lut[0].field_mt) return calib_lut[0].distance_mm;
    if (field_mt <= calib_lut[LUT_SIZE - 1].field_mt) return calib_lut[LUT_SIZE - 1].distance_mm;

    // Search interval
    for (int i = 0; i < LUT_SIZE - 1; i++) {
        if (field_mt <= calib_lut[i].field_mt && field_mt >= calib_lut[i + 1].field_mt) {
            float b1 = calib_lut[i].field_mt;
            float b2 = calib_lut[i + 1].field_mt;
            float d1 = calib_lut[i].distance_mm;
            float d2 = calib_lut[i + 1].distance_mm;
            // Linear interpolation formula
            return d1 + (field_mt - b1) * (d2 - d1) / (b2 - b1);
        }
    }
    return 0.0f;
}

float polynomial_distance(float field_mt) {
    return c0 + (c1 * field_mt) + (c2 * field_mt * field_mt);
}
