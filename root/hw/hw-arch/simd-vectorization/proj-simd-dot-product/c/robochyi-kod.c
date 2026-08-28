/* 3. AVX2 вручну: вісім незалежних акумуляторів, FMA, хвіст, зведення.
      Потребує -mavx2 -mfma (входять у -march=native на Haswell і новіших). */
float dot_avx2(const float *a, const float *b, size_t n)
{
    __m256 acc[8];
    for (int k = 0; k < 8; k++)
        acc[k] = _mm256_setzero_ps();

    size_t i = 0;

    /* Основне тіло: 8 акумуляторів × 8 доріжок = 64 елементи за прохід. */
    for (; i + 64 <= n; i += 64)
        for (int k = 0; k < 8; k++) {
            __m256 x = _mm256_loadu_ps(a + i + 8 * k);
            __m256 y = _mm256_loadu_ps(b + i + 8 * k);
            acc[k] = _mm256_fmadd_ps(x, y, acc[k]);   /* acc += x·y */
        }

    /* Догортання по вісім елементів — усе в нульовий ланцюжок.        */
    for (; i + 8 <= n; i += 8) {
        __m256 x = _mm256_loadu_ps(a + i);
        __m256 y = _mm256_loadu_ps(b + i);
        acc[0] = _mm256_fmadd_ps(x, y, acc[0]);
    }

    /* Крок 1: вісім регістрів у один, дерево 8 → 4 → 2 → 1.           */
    for (int step = 4; step >= 1; step >>= 1)
        for (int k = 0; k < step; k++)
            acc[k] = _mm256_add_ps(acc[k], acc[k + step]);

    /* Крок 2: вісім доріжок одного регістра в одне число.             */
    __m128 lo = _mm256_castps256_ps128(acc[0]);        /* доріжки 0..3 */
    __m128 hi = _mm256_extractf128_ps(acc[0], 1);      /* доріжки 4..7 */
    lo = _mm_add_ps(lo, hi);                                  /* 8 → 4 */
    lo = _mm_add_ps(lo, _mm_movehl_ps(lo, lo));               /* 4 → 2 */
    lo = _mm_add_ss(lo, _mm_shuffle_ps(lo, lo, 0x55));        /* 2 → 1 */
    float s = _mm_cvtss_f32(lo);

    /* Хвіст: менше за вісім елементів, скалярно.                      */
    for (; i < n; i++)
        s += a[i] * b[i];

    return s;
}
