#include <math.h>

// softmax із температурою: логіти z[n] → ймовірності p[n].
// T — температура (T=1 звичайний softmax; T>1 м'якший).
// СПЕРШУ віднімаємо max(z/T) — інакше exp() переповнюється й дає NaN.
static void softmax_T(const float *z, float *p, int n, float T) {
    float zmax = z[0] / T;
    for (int i = 1; i < n; ++i) {
        float zt = z[i] / T;
        if (zt > zmax) zmax = zt;           // max уже поділеного на T логіта
    }
    float sum = 0.0f;
    for (int i = 0; i < n; ++i) {
        p[i] = expf(z[i] / T - zmax);       // зсув на max: найбільший показник = 0
        sum += p[i];
    }
    float inv = 1.0f / sum;
    for (int i = 0; i < n; ++i)
        p[i] *= inv;                        // нормуємо, щоб додавалося в 1
}
