#include <stdint.h>
#include <stdlib.h>
#include <stddef.h>

/* Функція обмеження діапазону (clamping) у межах [0, 255] */
static inline uint8_t clamp_u8(int32_t val) {
    if (val < 0) return 0;
    if (val > 255) return 255;
    return (uint8_t)val;
}

/* 
 * Перетворення растрового кадру RGB24 у формат NV12 (Y-площина + interleaved UV-площина)
 * Параметри:
 *   rgb        - вхідний масив байтів RGB (3 байти на піксель)
 *   width      - ширина кадру в пікселях (мусить бути парною)
 *   height     - висота кадру в пікселях (мусить бути парною)
 *   y_plane    - вихідна площина Y (розмір width * height байтів)
 *   uv_plane   - вихідна площина UV (розмір width * height / 2 байтів)
 *   stride_rgb - крок рядка вхідного буфера RGB в байтах
 *   stride_y   - крок рядка вихідної площини Y в байтах
 *   stride_uv  - крок рядка вихідної площини UV в байтах
 */
int rgb24_to_nv12_convert(const uint8_t *rgb, size_t width, size_t height,
                          uint8_t *y_plane, uint8_t *uv_plane,
                          size_t stride_rgb, size_t stride_y, size_t stride_uv) {
    /* Перевірка аргументів на нульові покажчики та парність розмірів */
    if (!rgb || !y_plane || !uv_plane) return -1;
    if ((width % 2 != 0) || (height % 2 != 0)) return -2;
    if (stride_rgb < width * 3 || stride_y < width || stride_uv < width) return -3;

    size_t x, y;
    size_t uv_row_idx = 0;

    /* Обробка кадру блоками 2x2 рядки за один крок */
    for (y = 0; y < height; y += 2) {
        const uint8_t *row1 = rgb + y * stride_rgb;
        const uint8_t *row2 = rgb + (y + 1) * stride_rgb;

        uint8_t *y_row1 = y_plane + y * stride_y;
        uint8_t *y_row2 = y_plane + (y + 1) * stride_y;
        uint8_t *uv_row  = uv_plane + (y / 2) * stride_uv;

        size_t uv_col_idx = 0;

        for (x = 0; x < width; x += 2) {
            size_t p1 = x * 3;
            size_t p2 = (x + 1) * 3;

            /* Зчитування 4 пікселів блоку 2x2 */
            int r00 = row1[p1],     g00 = row1[p1 + 1], b00 = row1[p1 + 2];
            int r01 = row1[p2],     g01 = row1[p2 + 1], b01 = row1[p2 + 2];
            int r10 = row2[p1],     g10 = row2[p1 + 1], b10 = row2[p1 + 2];
            int r11 = row2[p2],     g11 = row2[p2 + 1], b11 = row2[p2 + 2];

            /* Обчислення Y для кожного з 4 пікселів */
            int32_t y00 = 16 + (( 16843 * r00 + 33030 * g00 +  6423 * b00 + 32768) >> 16);
            int32_t y01 = 16 + (( 16843 * r01 + 33030 * g01 +  6423 * b01 + 32768) >> 16);
            int32_t y10 = 16 + (( 16843 * r10 + 33030 * g10 +  6423 * b10 + 32768) >> 16);
            int32_t y11 = 16 + (( 16843 * r11 + 33030 * g11 +  6423 * b11 + 32768) >> 16);

            y_row1[x]     = clamp_u8(y00);
            y_row1[x + 1] = clamp_u8(y01);
            y_row2[x]     = clamp_u8(y10);
            y_row2[x + 1] = clamp_u8(y11);

            /* Просторове усереднення RGB для колірності */
            int r_avg = (r00 + r01 + r10 + r11 + 2) >> 2;
            int g_avg = (g00 + g01 + g10 + g11 + 2) >> 2;
            int b_avg = (b00 + b01 + b10 + b11 + 2) >> 2;

            /* Обчислення Cb та Cr */
            int32_t cb = 128 + ((-9699 * r_avg - 19071 * g_avg + 28770 * b_avg + 32768) >> 16);
            int32_t cr = 128 + (( 28770 * r_avg - 24117 * g_avg -  4653 * b_avg + 32768) >> 16);

            /* Запис у черговий порядок NV12: Cb, Cr */
            uv_row[uv_col_idx++] = clamp_u8(cb);
            uv_row[uv_col_idx++] = clamp_u8(cr);
        }
    }

    return 0;
}
