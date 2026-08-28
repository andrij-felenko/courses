#include <stdint.h>

#define KR 2   /* радіус ядра: 5 = 2*KR+1 */
static const int32_t W[5] = {1, 4, 6, 4, 1};   /* сума = 16 = 2^4 */

static inline int clampi(int v, int lo, int hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

/* Горизонтальний прохід: src -> dst, кожен рядок згортається з W. */
static void blur_h(const uint8_t *src, uint8_t *dst, int w, int h) {
    for (int y = 0; y < h; ++y) {
        const uint8_t *row = src + (size_t)y * w;
        uint8_t       *out = dst + (size_t)y * w;
        for (int x = 0; x < w; ++x) {
            int32_t acc = 0;
            for (int t = -KR; t <= KR; ++t) {
                int xi = clampi(x + t, 0, w - 1);   /* edge-clamp по краю рядка */
                acc += W[t + KR] * row[xi];
            }
            out[x] = (uint8_t)((acc + 8) >> 4);     /* /16 з округленням */
        }
    }
}

/* Вертикальний прохід: src -> dst, кожен стовпець згортається з W. */
static void blur_v(const uint8_t *src, uint8_t *dst, int w, int h) {
    for (int y = 0; y < h; ++y) {
        uint8_t *out = dst + (size_t)y * w;
        for (int x = 0; x < w; ++x) {
            int32_t acc = 0;
            for (int t = -KR; t <= KR; ++t) {
                int yi = clampi(y + t, 0, h - 1);   /* edge-clamp по краю стовпця */
                acc += W[t + KR] * src[(size_t)yi * w + x];
            }
            out[x] = (uint8_t)((acc + 8) >> 4);
        }
    }
}

/* Повне гаусове розмиття 5x5 двома проходами.
   tmp — проміжний буфер тих самих розмірів, що й кадр (виділяє викликач). */
void gauss5_separable(const uint8_t *src, uint8_t *dst,
                      uint8_t *tmp, int w, int h) {
    blur_h(src, tmp, w, h);   /* спершу рядки  */
    blur_v(tmp, dst, w, h);   /* тоді стовпці  */
}
