#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stddef.h>

/* Коефіцієнти BT.601 Full Range у форматі Q16.16 (масштаб 65536) */
#define FIX_Y_R  19595  /*  0.299000 * 65536 */
#define FIX_Y_G  38470  /*  0.587000 * 65536 */
#define FIX_Y_B   7471  /*  0.114000 * 65536 */

#define FIX_CB_R -11058 /* -0.168736 * 65536 */
#define FIX_CB_G -21710 /* -0.331264 * 65536 */
#define FIX_CB_B  32768 /*  0.500000 * 65536 */

#define FIX_CR_R  32768 /*  0.500000 * 65536 */
#define FIX_CR_G -27439 /* -0.418688 * 65536 */
#define FIX_CR_B  -5329 /* -0.081312 * 65536 */

/* Коефіцієнти зворотного перетворення BT.601 Full Range Q16.16 */
#define FIX_INV_CR_R  91881  /*  1.402000 * 65536 */
#define FIX_INV_CB_G -22554  /* -0.344136 * 65536 */
#define FIX_INV_CR_G -46802  /* -0.714136 * 65536 */
#define FIX_INV_CB_B 116130  /*  1.772000 * 65536 */

static inline uint8_t clamp_u8(int32_t val) {
    if (val < 0) return 0;
    if (val > 255) return 255;
    return (uint8_t)val;
}

/* Конверсія упакованого буфера RGB24 -> YCbCr444 з урахуванням кроку stride */
void rgb24_to_ycbcr444_c(const uint8_t* rgb, size_t rgb_stride,
                         uint8_t* y_plane, size_t y_stride,
                         uint8_t* cb_plane, size_t cb_stride,
                         uint8_t* cr_plane, size_t cr_stride,
                         size_t width, size_t height)
{
    for (size_t y = 0; y < height; ++y) {
        const uint8_t* rgb_row = rgb + y * rgb_stride;
        uint8_t* y_row  = y_plane + y * y_stride;
        uint8_t* cb_row = cb_plane + y * cb_stride;
        uint8_t* cr_row = cr_plane + y * cr_stride;

        for (size_t x = 0; x < width; ++x) {
            int32_t r = rgb_row[x * 3 + 0];
            int32_t g = rgb_row[x * 3 + 1];
            int32_t b = rgb_row[x * 3 + 2];

            int32_t luma = (FIX_Y_R * r + FIX_Y_G * g + FIX_Y_B * b) >> 16;
            int32_t cb   = ((FIX_CB_R * r + FIX_CB_G * g + FIX_CB_B * b) >> 16) + 128;
            int32_t cr   = ((FIX_CR_R * r + FIX_CR_G * g + FIX_CR_B * b) >> 16) + 128;

            y_row[x]  = clamp_u8(luma);
            cb_row[x] = clamp_u8(cb);
            cr_row[x] = clamp_u8(cr);
        }
    }
}

/* Конверсія YCbCr444 -> упакований буфер RGB24 */
void ycbcr444_to_rgb24_c(const uint8_t* y_plane, size_t y_stride,
                         const uint8_t* cb_plane, size_t cb_stride,
                         const uint8_t* cr_plane, size_t cr_stride,
                         uint8_t* rgb, size_t rgb_stride,
                         size_t width, size_t height)
{
    for (size_t y = 0; y < height; ++y) {
        const uint8_t* y_row  = y_plane + y * y_stride;
        const uint8_t* cb_row = cb_plane + y * cb_stride;
        const uint8_t* cr_row = cr_plane + y * cr_stride;
        uint8_t* rgb_row = rgb + y * rgb_stride;

        for (size_t x = 0; x < width; ++x) {
            int32_t luma = y_row[x];
            int32_t cb   = (int32_t)cb_row[x] - 128;
            int32_t cr   = (int32_t)cr_row[x] - 128;

            int32_t r = luma + ((FIX_INV_CR_R * cr) >> 16);
            int32_t g = luma + ((FIX_INV_CB_G * cb + FIX_INV_CR_G * cr) >> 16);
            int32_t b = luma + ((FIX_INV_CB_B * cb) >> 16);

            rgb_row[x * 3 + 0] = clamp_u8(r);
            rgb_row[x * 3 + 1] = clamp_u8(g);
            rgb_row[x * 3 + 2] = clamp_u8(b);
        }
    }
}
