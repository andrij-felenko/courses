#include <stdint.h>
#include <stddef.h>

static inline uint8_t clamp_u8(int32_t v) {
    return v < 0 ? 0 : (v > 255 ? 255 : (uint8_t)v);
}

// Зчитати піксель (x,y) з YUYV-буфера й повернути RGB888 (BT.601, limited range).
static void yuyv_pixel_to_rgb(const uint8_t *base, size_t stride,
                              int x, int y,
                              uint8_t *r, uint8_t *g, uint8_t *b) {
    const uint8_t *row  = base + (size_t)y * stride;
    const uint8_t *pair = row + (size_t)(x & ~1) * 2;   // початок пари пікселів
    int Y  = (x & 1) ? pair[2] : pair[0];               // свій Y на піксель
    int Cb = pair[1];                                   // спільні на пару
    int Cr = pair[3];

    int32_t c = 298 * (Y  - 16);     // та сама цілочисельна BT.601-матриця
    int32_t d = Cb - 128;
    int32_t e = Cr - 128;
    *r = clamp_u8((c + 409 * e           + 128) >> 8);
    *g = clamp_u8((c - 100 * d - 208 * e + 128) >> 8);
    *b = clamp_u8((c + 516 * d           + 128) >> 8);
}
