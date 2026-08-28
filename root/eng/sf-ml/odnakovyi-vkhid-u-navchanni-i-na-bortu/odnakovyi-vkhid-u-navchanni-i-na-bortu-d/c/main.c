#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define CLAMP(x, low, high) (((x) < (low)) ? (low) : (((x) > (high)) ? (high) : (x)))

typedef struct {
    int32_t m0_r, m0_g, m0_b;          // Множники комбінованого масштабу (формат Q0.31)
    int32_t shift_r, shift_g, shift_b; // Зсуви вправо
    int32_t z_eff_r, z_eff_g, z_eff_b; // Ефективні нульові точки
} FusedQuantParams;

// Розпакування одного пікселя RGB565 у три 8-бітні значення RGB888 з реплікацією бітів
static inline void unpack_rgb565_exact(uint16_t raw, uint8_t *r, uint8_t *g, uint8_t *b) {
    uint32_t r5 = (raw >> 11) & 0x1F;
    uint32_t g6 = (raw >> 5) & 0x3F;
    uint32_t b5 = raw & 0x1F;
    *r = (uint8_t)((r5 << 3) | (r5 >> 2));
    *g = (uint8_t)((g6 << 2) | (g6 >> 4));
    *b = (uint8_t)((b5 << 3) | (b5 >> 2));
}

// Злите квантування одного 8-бітного пікселя в int8
static inline void quantize_fused_pixel(uint8_t r, uint8_t g, uint8_t b,
                                       const FusedQuantParams *p, int8_t *out) {
    int64_t val_r = ((int64_t)r * p->m0_r + (1LL << (p->shift_r - 1))) >> p->shift_r;
    int64_t val_g = ((int64_t)g * p->m0_g + (1LL << (p->shift_g - 1))) >> p->shift_g;
    int64_t val_b = ((int64_t)b * p->m0_b + (1LL << (p->shift_b - 1))) >> p->shift_b;

    out[0] = (int8_t)CLAMP(val_r + p->z_eff_r, -128, 127);
    out[1] = (int8_t)CLAMP(val_g + p->z_eff_g, -128, 127);
    out[2] = (int8_t)CLAMP(val_b + p->z_eff_b, -128, 127);
}

// Білінійне масштабування рядка з інтерполяцією Q16.16 та формуванням квантованого виходу
void resize_bilinear_row_fused_q16(
    const uint16_t *row0_rgb565,
    const uint16_t *row1_rgb565,
    int in_width,
    int out_width,
    int32_t frac_y, // Дробова частина Y у форматі Q16 (0..65536)
    const FusedQuantParams *params,
    int8_t *out_row_nhwc)
{
    // step_x у форматі Q16.16: (in_width << 16) / out_width
    int32_t step_x = (int32_t)(((int64_t)in_width << 16) / out_width);
    
    // Початкове u_x для режиму half_pixel_centers
    int32_t u_x = ((step_x - (1 << 16)) >> 1);

    for (int ox = 0; ox < out_width; ++ox) {
        int32_t u_clamped = CLAMP(u_x, 0, ((in_width - 1) << 16));
        int x0 = u_clamped >> 16;
        int x1 = (x0 < in_width - 1) ? x0 + 1 : x0;
        int32_t frac_x = u_clamped & 0xFFFF;

        // Розпакування 4 пікселів сітки
        uint8_t r00, g00, b00, r10, g10, b10;
        uint8_t r01, g01, b01, r11, g11, b11;
        unpack_rgb565_exact(row0_rgb565[x0], &r00, &g00, &b00);
        unpack_rgb565_exact(row0_rgb565[x1], &r10, &g10, &b10);
        unpack_rgb565_exact(row1_rgb565[x0], &r01, &g01, &b01);
        unpack_rgb565_exact(row1_rgb565[x1], &r11, &g11, &b11);

        // Обчислення вагових коефіцієнтів Q16.16
        int32_t w00 = ((65536 - frac_x) * (65536 - frac_y)) >> 16;
        int32_t w10 = (frac_x * (65536 - frac_y)) >> 16;
        int32_t w01 = ((65536 - frac_x) * frac_y) >> 16;
        int32_t w11 = (frac_x * frac_y) >> 16;

        // Інтерполяція кожного каналу (з округленням +32768)
        uint8_t r_interp = (uint8_t)((r00 * w00 + r10 * w10 + r01 * w01 + r11 * w11 + 32768) >> 16);
        uint8_t g_interp = (uint8_t)((g00 * w00 + g10 * w10 + g01 * w01 + g11 * w11 + 32768) >> 16);
        uint8_t b_interp = (uint8_t)((b00 * w00 + b10 * w10 + b01 * w01 + b11 * w11 + 32768) >> 16);

        // Квантування та запис в інтерлівед-вихід
        quantize_fused_pixel(r_interp, g_interp, b_interp, params, &out_row_nhwc[ox * 3]);

        u_x += step_x;
    }
}
