// matrix_simd.cpp
#include <Python.h>
#include <vector>
#include <span>
#include <omp.h>

namespace linalg {

void fast_matrix_multiply(std::span<const float> a, std::span<const float> b, 
                          std::span<float> c, int n) noexcept {
    // Звільняємо GIL на час обчислень
    Py_BEGIN_ALLOW_THREADS

    #pragma omp parallel for collapse(2)
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            float sum = 0.0f;
            for (int k = 0; k < n; ++k) {
                sum += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = sum;
        }
    }

    Py_END_ALLOW_THREADS
}

} // namespace linalg
