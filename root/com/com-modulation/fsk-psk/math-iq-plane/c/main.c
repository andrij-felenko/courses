#include <math.h>

typedef struct { float i, q; } iq_t;

// (A, φ у радіанах) → (I, Q)
iq_t to_iq(float A, float phi) {
    iq_t s = { A * cosf(phi), A * sinf(phi) };
    return s;                       // I = A·cos φ,  Q = A·sin φ
}

// φ = 135° = 3π/4:  cos = −0.7071, sin = +0.7071
iq_t s = to_iq(1.0f, 3.0f * (float)M_PI / 4.0f);   // s.i ≈ −0.707, s.q ≈ +0.707

float A   = sqrtf(s.i * s.i + s.q * s.q);          // → 1.000
float phi = atan2f(s.q, s.i) * 180.0f / (float)M_PI; // → 135.0°
