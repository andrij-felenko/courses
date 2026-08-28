#include <stdio.h>
#include <stddef.h>

#define DIM 3

/*
 * Швидка згортка: res[i][l] = sum_k ( A[i][l][k] * v[k] )
 * Символ Кронекера delta_jl усунув цикл за j, перетворивши його на прямий доступ l.
 */
void tensor_contract_kronecker(
    const double A[DIM][DIM][DIM],
    const double v[DIM],
    double res[DIM][DIM]
) {
    for (size_t i = 0; i < DIM; ++i) {
        for (size_t l = 0; l < DIM; ++l) {
            double sum = 0.0;
            for (size_t k = 0; k < DIM; ++k) {
                sum += A[i][l][k] * v[k];
            }
            res[i][l] = sum;
        }
    }
}

/*
 * Згортка Епсилон-Дельта: обчислення векторного добутку c = a x b.
 * Використовує ненульові індекси символу Леві-Чивіти без повного потрійного циклу 3x3x3.
 */
void cross_product_optimized(const double a[3], const double b[3], double c[3]) {
    c[0] = a[1] * b[2] - a[2] * b[1];
    c[1] = a[2] * b[0] - a[0] * b[2];
    c[2] = a[0] * b[1] - a[1] * b[0];
}
