#include <math.h>

/* Діюче (RMS) значення блоку з n відліків.
   x[] — виміряні відліки сигналу; n > 0. */
float block_rms(const float x[], int n)
{
    float sum_sq = 0.0f;
    for (int i = 0; i < n; i++) {
        sum_sq += x[i] * x[i];      /* крок 1: квадрат, і одразу в суму */
    }
    float mean_sq = sum_sq / (float)n;  /* крок 2: середнє квадрата */
    return sqrtf(mean_sq);              /* крок 3: корінь повертає одиниці */
}
