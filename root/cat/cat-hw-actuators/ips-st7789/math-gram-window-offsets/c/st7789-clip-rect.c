#include <stdint.h>
#include <stdbool.h>

// Опис прямокутної області в цілочисельних координатах
typedef struct {
    int16_t x0; // Ліва межа (включно)
    int16_t y0; // Верхня межа (включно)
    int16_t x1; // Права межа (включно)
    int16_t y1; // Нижня межа (включно)
} st7789_rect_t;

// Геометричне відсікання прямокутника межами видимого вікна [0, vp_w - 1] × [0, vp_h - 1].
// Повертає true, якщо є видима область, або false при повному відкиданні (trivial rejection).
bool st7789_clip_rect(const st7789_rect_t *src, st7789_rect_t *dst, int16_t vp_w, int16_t vp_h) {
    // Умова тривіального відкидання: прямокутник повністю за межами екрана
    if (src->x1 < 0 || src->x0 >= vp_w || src->y1 < 0 || src->y0 >= vp_h) {
        return false;
    }

    // Аналітичне обрізання координат до діапазону [0, vp_w - 1] та [0, vp_h - 1]
    dst->x0 = (src->x0 < 0) ? 0 : src->x0;
    dst->y0 = (src->y0 < 0) ? 0 : src->y0;
    dst->x1 = (src->x1 >= vp_w) ? (int16_t)(vp_w - 1) : src->x1;
    dst->y1 = (src->y1 >= vp_h) ? (int16_t)(vp_h - 1) : src->y1;

    return true;
}

// Виведення растрового зображення формату RGB565 з урахуванням прямокутного відсікання
void st7789_draw_bitmap_clipped(
    int16_t x, int16_t y,
    int16_t w, int16_t h,
    const uint16_t *bitmap,
    int16_t stride,
    int16_t vp_w, int16_t vp_h,
    uint16_t col_offset, uint16_t row_offset
) {
    if (w <= 0 || h <= 0 || bitmap == (void*)0) {
        return;
    }

    st7789_rect_t src_rect = {
        .x0 = x,
        .y0 = y,
        .x1 = (int16_t)(x + w - 1),
        .y1 = (int16_t)(y + h - 1)
    };
    st7789_rect_t clipped_rect;

    // Спроба відсікання: при повному знаходженні поза вікном негайно виходимо
    if (!st7789_clip_rect(&src_rect, &clipped_rect, vp_w, vp_h)) {
        return;
    }

    // Розрахунок зсувів у масиві джерела через обрізання верхнього та лівого країв
    int16_t delta_x = (int16_t)(clipped_rect.x0 - src_rect.x0);
    int16_t delta_y = (int16_t)(clipped_rect.y0 - src_rect.y0);

    int16_t clipped_w = (int16_t)(clipped_rect.x1 - clipped_rect.x0 + 1);
    int16_t clipped_h = (int16_t)(clipped_rect.y1 - clipped_rect.y0 + 1);

    // Додавання апаратних зміщень кристала ST7789 для відповідного кута повороту
    uint16_t gram_col_start = (uint16_t)(clipped_rect.x0 + col_offset);
    uint16_t gram_col_end   = (uint16_t)(clipped_rect.x1 + col_offset);
    uint16_t gram_row_start = (uint16_t)(clipped_rect.y0 + row_offset);
    uint16_t gram_row_end   = (uint16_t)(clipped_rect.y1 + row_offset);

    // Налаштування вікна адресації командами CASET (0x2A) та RASET (0x2B)
    st7789_set_address_window(gram_col_start, gram_col_end, gram_row_start, gram_row_end);

    // Запуск потокового запису у відеопам'ять командою RAMWR (0x2C)
    st7789_write_command(0x2C);

    // Передача видимих пікселів із урахуванням кроку пам'яті (stride)
    const uint16_t *row_ptr = bitmap + (delta_y * stride) + delta_x;
    for (int16_t r = 0; r < clipped_h; ++r) {
        st7789_write_pixels(row_ptr, clipped_w);
        row_ptr += stride;
    }
}
