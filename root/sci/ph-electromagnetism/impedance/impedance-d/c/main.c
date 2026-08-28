#include <math.h>

typedef struct { float re, im; } Cplx;   /* комплексне число: re + j*im */

/* імпеданс реальної котушки на частоті f */
Cplx coil_impedance(float R, float L, float f) {
    float w = 2.0f * (float)M_PI * f;     /* кутова частота ω */
    return (Cplx){ R, w * L };            /* Z = R + j*(ω·L) */
}

/* приклад: R=30 Ом, L=10 мГн, f=400 Гц */
Cplx Z = coil_impedance(30.0f, 0.010f, 400.0f);

float mag   = hypotf(Z.re, Z.im);   /* |Z| ≈ 39.1 Ом              */
float phase = atan2f(Z.im, Z.re);   /* φ  ≈ 0.696 рад ≈ 39.9°     */
float I     = 12.0f / mag;          /* амплітуда струму ≈ 0.307 А */
