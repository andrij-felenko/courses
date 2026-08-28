#include <math.h>

typedef struct { float b0, b1, b2, a1, a2; } biquad_coef;

biquad_coef design_hpf(float f0, float fs, float Q) {
    float w0    = 2.0f * 3.14159265f * f0 / fs;
    float cosw  = cosf(w0);
    float sinw  = sinf(w0);
    float alpha = sinw / (2.0f * Q);
    float a0    = 1.0f + alpha;
    biquad_coef c;
    c.b0 =  (1.0f + cosw) / 2.0f / a0;
    c.b1 = -(1.0f + cosw)        / a0;
    c.b2 =  (1.0f + cosw) / 2.0f / a0;
    c.a1 = -2.0f * cosw          / a0;
    c.a2 =  (1.0f - alpha)       / a0;
    return c;
}
