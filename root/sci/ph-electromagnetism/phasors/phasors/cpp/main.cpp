#include <math.h>

typedef struct { float re, im; } Phasor;   /* фазор у прямокутній формі */

/* з амплітуди й фази (рад) — у складові */
Phasor phasor_from(float amp, float phase) {
    return (Phasor){ amp * cosf(phase), amp * sinf(phase) };
}

Phasor phasor_add(Phasor a, Phasor b) {
    return (Phasor){ a.re + b.re, a.im + b.im };
}

/* використання: 3∠0° + 4∠90° */
Phasor i1 = phasor_from(3.0f, 0.0f);
Phasor i2 = phasor_from(4.0f, M_PI / 2.0f);
Phasor sum = phasor_add(i1, i2);

float amp   = hypotf(sum.re, sum.im);   /* = 5.0 А     */
float phase = atan2f(sum.im, sum.re);   /* ≈ 0.927 рад ≈ 53.13° */
