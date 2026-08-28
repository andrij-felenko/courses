#include <stdint.h>
#define KR 2                                   /* радіус: 5 = 2*KR+1 */
static const int32_t W[5] = {1, 4, 6, 4, 1};   /* сума 16 = 2^4 */
static inline int clampi(int v, int lo, int hi){
    return v < lo ? lo : (v > hi ? hi : v);
}
/* горизонтальний прохід: кожен рядок згортаємо з W */
static void blur_h(const uint8_t *s, uint8_t *d, int w, int h){
    for (int y = 0; y < h; ++y)
        for (int x = 0; x < w; ++x){
            int32_t a = 0;
            for (int t = -KR; t <= KR; ++t)
                a += W[t+KR] * s[(size_t)y*w + clampi(x+t,0,w-1)];
            d[(size_t)y*w + x] = (uint8_t)((a + 8) >> 4);   /* /16 з округленням */
        }
}
/* вертикальний прохід: кожен стовпець згортаємо з тим самим W */
static void blur_v(const uint8_t *s, uint8_t *d, int w, int h){
    for (int y = 0; y < h; ++y)
        for (int x = 0; x < w; ++x){
            int32_t a = 0;
            for (int t = -KR; t <= KR; ++t)
                a += W[t+KR] * s[(size_t)clampi(y+t,0,h-1)*w + x];
            d[(size_t)y*w + x] = (uint8_t)((a + 8) >> 4);
        }
}
void gauss5(const uint8_t *src, uint8_t *dst, uint8_t *tmp, int w, int h){
    blur_h(src, tmp, w, h);   /* спершу рядки */
    blur_v(tmp, dst, w, h);   /* тоді стовпці */
}
