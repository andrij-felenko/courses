#include <immintrin.h>

void cantor_scan_avx512(const double* in_pts, uint8_t* out_res, size_t count, int depth) {
    size_t i = 0;
    __m512d v_three = _mm512_set1_pd(3.0);
    __m512d v_two   = _mm512_set1_pd(2.0);
    __m512d v_one   = _mm512_set1_pd(1.0);

    for (; i + 8 <= count; i += 8) {
        __m512d v_curr = _mm512_loadu_pd(&in_pts[i]);
        __m512i v_mask_active = _mm512_set1_epi64(-1);

        for (int d = 0; d < depth; d++) {
            v_curr = _mm512_mul_pd(v_curr, v_three);
            __m512d v_floor = _mm512_floor_pd(v_curr);
            
            // Маска точок, де потрійна цифра дорівнює 1
            __mmask8 m_is_one = _mm512_cmpeq_pd_mask(v_floor, v_one);
            if (m_is_one) {
                // Відмічаємо вилучені точки
            }
        }
    }
}
