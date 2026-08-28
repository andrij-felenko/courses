#include <math.h>

// x[]    — буфер відліків (N штук)
// target — шукана частота, Гц;  fs — частота дискретизації, Гц
float goertzel_power(const float *x, int N, float target, float fs)
{
    int   k     = (int)(0.5f + (float)N * target / fs); // найближчий бін
    float w     = 2.0f * (float)M_PI * k / N;
    float coeff = 2.0f * cosf(w);

    float s1 = 0.0f, s2 = 0.0f;
    for (int n = 0; n < N; ++n) {
        float s = x[n] + coeff * s1 - s2;
        s2 = s1;
        s1 = s;
    }
    // квадрат магнітуди біна (без sqrt — для порівняння з порогом досить)
    return s1 * s1 + s2 * s2 - coeff * s1 * s2;
}
