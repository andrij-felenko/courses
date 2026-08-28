// matrix_simd.c
#include <Python.h>

void fast_matrix_multiply(const float *a, const float *b, float *c, int n) {
    // Відпускаємо GIL: цикл виконуватиметься паралельно з іншими потоками
    Py_BEGIN_ALLOW_THREADS

    #pragma omp parallel for
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            float sum = 0.0f;
            for (int k = 0; k < n; ++k) {
                sum += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = sum;
        }
    }

    // Відновлюємо GIL перед поверненням у простір інтерпретатора
    Py_END_ALLOW_THREADS
}
