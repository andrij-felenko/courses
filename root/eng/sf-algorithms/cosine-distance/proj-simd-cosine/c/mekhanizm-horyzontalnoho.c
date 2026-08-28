#include <immintrin.h>
#include <math.h>
#include <stddef.h>
#include <stdbool.h>

// Внутрішня функція горизонтального сумування 8 елементів YMM-регістра
static inline float hsum256_ps(__m256 v) {
    __m128 vlow  = _mm256_castps256_ps128(v);
    __m128 vhigh = _mm256_extractf128_ps(v, 1);
    vlow  = _mm_add_ps(vlow, vhigh);
    __m128 shuf = _mm_movehdup_ps(vlow);
    vlow  = _mm_add_ps(vlow, shuf);
    shuf  = _mm_movehl_ps(shuf, vlow);
    vlow  = _mm_add_ss(vlow, shuf);
    return _mm_cvtss_f32(vlow);
}

MetricResult cosine_distance_avx2(const float *u, const float *v, size_t size) {
    MetricResult res = {1.0f, false};
    if (!u || !v || size == 0) return res;

    __m256 v_dot  = _mm256_setzero_ps();
    __m256 v_sq_u = _mm256_setzero_ps();
    __m256 v_sq_v = _mm256_setzero_ps();

    size_t i = 0;
    // Основний векторний цикл (обробка по 8 float за такт)
    for (; i + 7 < size; i += 8) {
        __m256 u_vec = _mm256_loadu_ps(u + i);
        __m256 v_vec = _mm256_loadu_ps(v + i);

        v_dot  = _mm256_fmadd_ps(u_vec, v_vec, v_dot);
        v_sq_u = _mm256_fmadd_ps(u_vec, u_vec, v_sq_u);
        v_sq_v = _mm256_fmadd_ps(v_vec, v_vec, v_sq_v);
    }

    // Горизонтальне сумування векторних акумуляторів
    float dot  = hsum256_ps(v_dot);
    float sq_u = hsum256_ps(v_sq_u);
    float sq_v = hsum256_ps(v_sq_v);

    // Обробка скалярного залишку
    for (; i < size; ++i) {
        float ui = u[i];
        float vi = v[i];
        dot  += ui * vi;
        sq_u += ui * ui;
        sq_v += vi * vi;
    }

    const float eps = 1e-12f;
    if (sq_u < eps || sq_v < eps) return res;

    float norm_product = sqrtf(sq_u) * sqrtf(sq_v);
    float cos_sim = dot / norm_product;

    if (cos_sim > 1.0f) cos_sim = 1.0f;
    if (cos_sim < -1.0f) cos_sim = -1.0f;

    res.distance = 1.0f - cos_sim;
    res.success = true;
    return res;
}
