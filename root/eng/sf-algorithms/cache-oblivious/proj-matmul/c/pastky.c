// C += A·B для довільних m×n на n×p: ділимо найбільший вимір навпіл.
// Залишок (m - h) забирає непарність на себе — жоден рядок не губиться.
void comul_rect(const double *A, const double *B, double *C,
                size_t m, size_t n, size_t p,
                size_t lda, size_t ldb, size_t ldc)
{
    if (m <= BASE && n <= BASE && p <= BASE) {
        for (size_t i = 0; i < m; i++)
            for (size_t j = 0; j < p; j++) {
                double s = C[i*ldc + j];
                for (size_t k = 0; k < n; k++)
                    s += A[i*lda + k] * B[k*ldb + j];
                C[i*ldc + j] = s;
            }
        return;
    }
    if (m >= n && m >= p) {                 // A ріжемо горизонтально
        size_t h = m / 2;
        comul_rect(A,         B, C,         h,     n, p, lda, ldb, ldc);
        comul_rect(A + h*lda, B, C + h*ldc, m - h, n, p, lda, ldb, ldc);
    } else if (n >= m && n >= p) {          // ріжемо спільний вимір
        size_t h = n / 2;
        comul_rect(A,     B,         C, m, h,     p, lda, ldb, ldc);
        comul_rect(A + h, B + h*ldb, C, m, n - h, p, lda, ldb, ldc);
    } else {                                // B ріжемо вертикально
        size_t h = p / 2;
        comul_rect(A, B,     C,     m, n, h,     lda, ldb, ldc);
        comul_rect(A, B + h, C + h, m, n, p - h, lda, ldb, ldc);
    }
}
