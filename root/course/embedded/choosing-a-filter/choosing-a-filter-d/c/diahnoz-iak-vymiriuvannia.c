#include <stdint.h>
#include <math.h>

// Частка відліків-викидів у буфері: |x − медіана| > k·MAD.
// Проста O(n²) реалізація для короткого діагностичного вікна (n ≤ ~64).
static float med_of(const float *buf, int n, float *scratch) {
    for (int i = 0; i < n; i++) scratch[i] = buf[i];
    // сортування вставками — дешеве й достатнє для малих n
    for (int i = 1; i < n; i++) {
        float v = scratch[i]; int j = i - 1;
        while (j >= 0 && scratch[j] > v) { scratch[j + 1] = scratch[j]; j--; }
        scratch[j + 1] = v;
    }
    return scratch[n / 2];
}

float outlier_fraction(const float *x, int n, float k) {
    float scratch[64];
    float med = med_of(x, n, scratch);
    for (int i = 0; i < n; i++) scratch[i] = fabsf(x[i] - med);  // |відхилення|
    float mad = med_of(scratch, n, scratch);      // медіана абс. відхилень
    if (mad < 1e-6f) mad = 1e-6f;                  // сталий сигнал: уникаємо ділення на 0
    int hits = 0;
    for (int i = 0; i < n; i++)
        if (fabsf(x[i] - med) > k * mad) hits++;
    return (float)hits / n;                        // 0.00 → шум; помітна частка → викиди
}
