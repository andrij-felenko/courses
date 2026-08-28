#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// ============================================================================
// 1. Допоміжні функції виділення пам'яті
// ============================================================================
double* vec_alloc(size_t n, double val) {
    double* data = (double*)malloc(n * sizeof(double));
    if (!data) return NULL;
    for (size_t i = 0; i < n; ++i) data[i] = val;
    return data;
}

// ============================================================================
// 2. Наївний C-підхід з виділенням тимчасових масивів
// ============================================================================
double* vec_scale_naive(const double* a, double alpha, size_t n) {
    double* res = (double*)malloc(n * sizeof(double));
    if (!res) return NULL;
    for (size_t i = 0; i < n; ++i) {
        res[i] = a[i] * alpha;
    }
    return res;
}

double* vec_add_naive(const double* a, const double* b, size_t n) {
    double* res = (double*)malloc(n * sizeof(double));
    if (!res) return NULL;
    for (size_t i = 0; i < n; ++i) {
        res[i] = a[i] + b[i];
    }
    return res;
}

// ============================================================================
// 3. Оптимальний C-підхід: ручно злитий цикл (Fused Kernel)
// restrict гарантує компілятору відсутність перекриття вказівників (аліасингу)
// ============================================================================
void vec_fused_add_scale(double* restrict res, const double* restrict a, 
                        const double* restrict b, const double* restrict c, 
                        double alpha, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        res[i] = a[i] + b[i] * alpha + c[i];
    }
}

int main(void) {
    const size_t N = 10000000;
    double* A = vec_alloc(N, 1.0);
    double* B = vec_alloc(N, 2.0);
    double* C = vec_alloc(N, 3.0);
    double* R = vec_alloc(N, 0.0);

    if (!A || !B || !C || !R) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    // Варіант А: Наївні послідовні виклики (створює 2 тимчасових масиви в купі)
    clock_t t1 = clock();
    double* T1 = vec_scale_naive(B, 2.5, N);     // Alloc 1 + Loop 1
    double* T2 = vec_add_naive(A, T1, N);         // Alloc 2 + Loop 2
    for (size_t i = 0; i < N; ++i) R[i] = T2[i] + C[i]; // Loop 3
    clock_t t2 = clock();
    free(T1);
    free(T2);

    printf("R[0] (наївний C) = %.1f, час: %.2f ms\n", R[0], (double)(t2 - t1) * 1000.0 / CLOCKS_PER_SEC);

    // Варіант Б: Ручний злитий цикл в C (аналог того, що C++ Expression Templates генерують автоматично)
    clock_t t3 = clock();
    vec_fused_add_scale(R, A, B, C, 2.5, N);
    clock_t t4 = clock();

    printf("R[0] (оптимальний злитий C) = %.1f, час: %.2f ms\n", R[0], (double)(t4 - t3) * 1000.0 / CLOCKS_PER_SEC);

    free(A); free(B); free(C); free(R);
    return 0;
}
