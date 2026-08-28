#include <immintrin.h>
#include <span>
#include <cstddef>

void transform_axial_vectors_avx2_cpp(std::span<const double> src_x,
                                     std::span<const double> src_y,
                                     std::span<const double> src_z,
                                     std::span<double> dst_x,
                                     std::span<double> dst_y,
                                     std::span<double> dst_z,
                                     const Matrix3x3& mat) {
    const double det = mat.determinant();
    const size_t count = src_x.size();
    
    const __m256d m00 = _mm256_set1_pd(mat.m[0][0] * det);
    const __m256d m01 = _mm256_set1_pd(mat.m[0][1] * det);
    const __m256d m02 = _mm256_set1_pd(mat.m[0][2] * det);
    
    for (size_t i = 0; i < count; i += 4) {
        const __m256d vx = _mm256_loadu_pd(&src_x[i]);
        const __m256d vy = _mm256_loadu_pd(&src_y[i]);
        const __m256d vz = _mm256_loadu_pd(&src_z[i]);
        
        const __m256d rx = _mm256_add_pd(_mm256_mul_pd(m00, vx),
                          _mm256_add_pd(_mm256_mul_pd(m01, vy),
                                        _mm256_mul_pd(m02, vz)));
        
        _mm256_storeu_pd(&dst_x[i], rx);
    }
}
