#include <immintrin.h>

// Транспонування блоку 8 частинок AoS у формат SoA в регістрах
void transpose_8x8_aos_to_soa(const float *aos_src, float *soa_x, float *soa_y, float *soa_z)
{
    // Завантаження 8 структур AoS по 4 компоненти (x, y, z, w) у 8 векторів YMM
    __m256 r0 = _mm256_loadu_ps(aos_src + 0);
    __m256 r1 = _mm256_loadu_ps(aos_src + 8);
    __m256 r2 = _mm256_loadu_ps(aos_src + 16);
    __m256 r3 = _mm256_loadu_ps(aos_src + 24);

    // Розпакування молодших і старших пар
    __m256 t0 = _mm256_unpacklo_ps(r0, r1);
    __m256 t1 = _mm256_unpackhi_ps(r0, r1);
    __m256 t2 = _mm256_unpacklo_ps(r2, r3);
    __m256 t3 = _mm256_unpackhi_ps(r2, r3);

    // Перестановка 64-бітних блоків
    __m256 v_x = _mm256_shuffle_ps(t0, t2, _MM_SHUFFLE(2, 0, 2, 0));
    __m256 v_y = _mm256_shuffle_ps(t0, t2, _MM_SHUFFLE(3, 1, 3, 1));
    __m256 v_z = _mm256_shuffle_ps(t1, t3, _MM_SHUFFLE(2, 0, 2, 0));

    // Збереження вирівняних SoA векторів
    _mm256_storeu_ps(soa_x, v_x);
    _mm256_storeu_ps(soa_y, v_y);
    _mm256_storeu_ps(soa_z, v_z);
}
