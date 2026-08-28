#include <math.h>

// softmax із температурою: логіти z[n] → ймовірності p[n]
void softmax_T(const float *z, float *p, int n, float T) {
    float sum = 0.0f;
    for (int i = 0; i < n; ++i) {
        p[i] = expf(z[i] / T);   // ділимо логіт на T, тоді експонента
        sum += p[i];
    }
    for (int i = 0; i < n; ++i)
        p[i] /= sum;             // нормуємо, щоб додавалося в 1
}
