#include <immintrin.h>

void transform_axial_vectors_avx2(const double* restrict src_x,
                                 const double* restrict src_y,
                                 const double* restrict src_z,
                                 double* restrict dst_x,
                                 double* restrict dst_y,
                                 double* restrict dst_z,
                                 size_t count,
                                 const Matrix3x3* mat) {
    double det = matrix3x3_determinant(mat);
    
    // Матричні елементи, помножені на det
    __m256d m00 = _mm256_set1_pd(mat->m[0][0] * det);
    __m256d m01 = _mm256_set1_pd(mat->m[0][1] * det);
    __m256d m02 = _mm256_set1_pd(mat->m[0][2] * det);
    
    for (size_t i = 0; i < count; i += 4) {
        __m256d vx = _mm256_loadu_pd(&src_x[i]);
        __m256d vy = _mm256_loadu_pd(&src_y[i]);
        __m256d vz = _mm256_loadu_pd(&src_z[i]);
        
        __m256d rx = _mm256_add_pd(_mm256_mul_pd(m00, vx),
                     _mm256_add_pd(_mm256_mul_pd(m01, vy),
                                   _mm256_mul_pd(m02, vz)));
        
        _mm256_storeu_pd(&dst_x[i], rx);
    }
}
