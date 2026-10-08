#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t y;
    uint8_t u;
    uint8_t v;
} yuv_pixel_t;

// Обрізання значень у межах [0, 255]
static inline uint8_t clamp_u8(int32_t val) {
    if (val < 0) return 0;
    if (val > 255) return 255;
    return (uint8_t)val;
}

// Перетворення RGB в YUV з фіксованою комою Q0.8
yuv_pixel_t ov2640_rgb_to_yuv(uint8_t r, uint8_t g, uint8_t b) {
    int32_t y_raw = (77 * r + 150 * g + 29 * b) >> 8;
    int32_t u_raw = ((-43 * r - 85 * g + 128 * b) >> 8) + 128;
    int32_t v_raw = ((128 * r - 107 * g - 21 * b) >> 8) + 128;

    yuv_pixel_t out;
    out.y = clamp_u8(y_raw);
    out.u = clamp_u8(u_raw);
    out.v = clamp_u8(v_raw);
    return out;
}
