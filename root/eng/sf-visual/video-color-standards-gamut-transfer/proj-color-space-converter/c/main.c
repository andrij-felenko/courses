/* c */
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>

/* Матричні коефіцієнти BT.709 Q8.8 */
#define COEFF_Y  298
#define COEFF_RV 459
#define COEFF_GU 55
#define COEFF_GV 136
#define COEFF_BU 541

/* Допоміжна функція насичення 8-бітного значення */
static inline uint8_t saturate_u8(int32_t val) {
    if (val < 0) return 0;
    if (val > 255) return 255;
    return (uint8_t)val;
}

/**
 * Перетворення площини YUV420p у RGBA32 (8 біт на канал)
 * @param y_plane  Вказівник на площину яркості Y (width x height)
 * @param u_plane  Вказівник на колірну площину Cb/U (width/2 x height/2)
 * @param v_plane  Вказівник на колірну площину Cr/V (width/2 x height/2)
 * @param rgba_out Вихідний буфер RGBA (width * height * 4 байт)
 * @param width    Ширина кадру у пікселях (кратна 2)
 * @param height   Висота кадру у пікселях (кратна 2)
 * @param y_stride Крок рядка яркості (байтів на рядок)
 * @param uv_stride Крок рядка колірності
 */
void yuv420p_to_rgba32_c(const uint8_t *y_plane,
                         const uint8_t *u_plane,
                         const uint8_t *v_plane,
                         uint8_t *rgba_out,
                         size_t width, size_t height,
                         size_t y_stride, size_t uv_stride)
{
    for (size_t y = 0; y < height; ++y) {
        const uint8_t *y_line = y_plane + y * y_stride;
        const uint8_t *u_line = u_plane + (y / 2) * uv_stride;
        const uint8_t *v_line = v_plane + (y / 2) * uv_stride;
        uint8_t *out_line = rgba_out + y * width * 4;

        for (size_t x = 0; x < width; ++x) {
            int32_t y_val = (int32_t)y_line[x] - 16;
            if (y_val < 0) y_val = 0;

            int32_t u_val = (int32_t)u_line[x / 2] - 128;
            int32_t v_val = (int32_t)v_line[x / 2] - 128;

            int32_t y_scaled = COEFF_Y * y_val + 128;

            int32_t r_val = (y_scaled + COEFF_RV * v_val) >> 8;
            int32_t g_val = (y_scaled - COEFF_GU * u_val - COEFF_GV * v_val) >> 8;
            int32_t b_val = (y_scaled + COEFF_BU * u_val) >> 8;

            size_t out_idx = x * 4;
            out_line[out_idx + 0] = saturate_u8(r_val);
            out_line[out_idx + 1] = saturate_u8(g_val);
            out_line[out_idx + 2] = saturate_u8(b_val);
            out_line[out_idx + 3] = 255; /* Непрозорий альфа-канал */
        }
    }
}
