#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

/*
 * Обчислення добутку Кронекера C = A (x) B.
 * Розмір A: (mA x nA), розмір B: (mB x nB).
 * Розмір C: ((mA * mB) x (nA * nB)).
 */
void kronecker_product_dense(
    const double *A, size_t mA, size_t nA,
    const double *B, size_t mB, size_t nB,
    double *C
) {
    size_t nC = nA * nB;
    for (size_t ia = 0; ia < mA; ++ia) {
        for (size_t ja = 0; ja < nA; ++ja) {
            double a_val = A[ia * nA + ja];
            for (size_t ib = 0; ib < mB; ++ib) {
                size_t row_c = ia * mB + ib;
                for (size_t jb = 0; jb < nB; ++jb) {
                    size_t col_c = ja * nB + jb;
                    C[row_c * nC + col_c] = a_val * B[ib * nB + jb];
                }
            }
        }
    }
}
