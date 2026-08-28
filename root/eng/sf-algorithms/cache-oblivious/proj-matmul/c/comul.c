// comul.c — кеш-незалежне множення матриць: C += A·B
// Збірка:  cc -O2 -c comul.c
#include <stddef.h>

#define BASE 8      // нижче цього розміру рекурсія вже нічого не дає (див. нижче)

// C += A·B для квадратних блоків n×n.
// lda/ldb/ldc — крок рядка в матриці-власниці: підблок НЕ копіюємо,
// передаємо лише вказівник на його лівий верхній кут.
// ВИМОГА: n — степінь двійки (про це — у пастках).
void comul(const double *A, const double *B, double *C, size_t n,
           size_t lda, size_t ldb, size_t ldc)
{
    if (n <= BASE) {                       // база: звичайний потрійний цикл
        for (size_t i = 0; i < n; i++)
            for (size_t j = 0; j < n; j++) {
                double s = C[i*ldc + j];
                for (size_t k = 0; k < n; k++)
                    s += A[i*lda + k] * B[k*ldb + j];
                C[i*ldc + j] = s;
            }
        return;
    }

    size_t h = n / 2;
    const double *A11 = A,          *A12 = A + h;
    const double *A21 = A + h*lda,  *A22 = A + h*lda + h;
    const double *B11 = B,          *B12 = B + h;
    const double *B21 = B + h*ldb,  *B22 = B + h*ldb + h;
    double       *C11 = C,          *C12 = C + h;
    double       *C21 = C + h*ldc,  *C22 = C + h*ldc + h;

    comul(A11, B11, C11, h, lda, ldb, ldc);   // C11 += A11·B11
    comul(A12, B21, C11, h, lda, ldb, ldc);   // C11 += A12·B21
    comul(A11, B12, C12, h, lda, ldb, ldc);   // C12 += A11·B12
    comul(A12, B22, C12, h, lda, ldb, ldc);   // C12 += A12·B22
    comul(A21, B11, C21, h, lda, ldb, ldc);   // C21 += A21·B11
    comul(A22, B21, C21, h, lda, ldb, ldc);   // C21 += A22·B21
    comul(A21, B12, C22, h, lda, ldb, ldc);   // C22 += A21·B12
    comul(A22, B22, C22, h, lda, ldb, ldc);   // C22 += A22·B22
}
