#include <cstdint>
#include <optional>
#include <algorithm>

// Опис прямокутної області
struct Rect {
    int16_t x0; // Ліва межа (включно)
    int16_t y0; // Верхня межа (включно)
    int16_t x1; // Права межа (включно)
    int16_t y1; // Нижня межа (включно)

    [[nodiscard]] constexpr int16_t width() const noexcept {
        return static_cast<int16_t>(x1 - x0 + 1);
    }

    [[nodiscard]] constexpr int16_t height() const noexcept {
        return static_cast<int16_t>(y1 - y0 + 1);
    }
};

// Геометричне відсікання прямокутника межами вікна [0, vp_w - 1] × [0, vp_h - 1]
[[nodiscard]] constexpr std::optional<Rect> clip_rect(const Rect& src, int16_t vp_w, int16_t vp_h) noexcept {
    // Умова повного відкидання (trivial rejection)
    if (src.x1 < 0 || src.x0 >= vp_w || src.y1 < 0 || src.y0 >= vp_h) {
        return std::nullopt;
    }

    return Rect{
        .x0 = std::max<int16_t>(0, src.x0),
        .y0 = std::max<int16_t>(0, src.y0),
        .x1 = std::min<int16_t>(static_cast<int16_t>(vp_w - 1), src.x1),
        .y1 = std::min<int16_t>(static_cast<int16_t>(vp_h - 1), src.y1)
    };
}

// Виведення растрового зображення з урахуванням відсікання та кроку пам'яті
void draw_bitmap_clipped(
    int16_t x, int16_t y,
    int16_t w, int16_t h,
    const uint16_t* bitmap,
    int16_t stride,
    int16_t vp_w, int16_t vp_h,
    uint16_t col_offset, uint16_t row_offset
) {
    if (w <= 0 || h <= 0 || bitmap == nullptr) {
        return;
    }

    const Rect src_rect{
        .x0 = x,
        .y0 = y,
        .x1 = static_cast<int16_t>(x + w - 1),
        .y1 = static_cast<int16_t>(y + h - 1)
    };

    const auto clipped = clip_rect(src_rect, vp_w, vp_h);
    if (!clipped.has_value()) {
        return; // Повне відкидання: ранній вихід без транзакцій SPI
    }

    // Обчислення зсувів у буфері джерела
    const int16_t delta_x = clipped->x0 - src_rect.x0;
    const int16_t delta_y = clipped->y0 - src_rect.y0;

    // Фізичні координати GRAM з урахуванням апаратних зміщень
    const auto gram_col_start = static_cast<uint16_t>(clipped->x0 + col_offset);
    const auto gram_col_end   = static_cast<uint16_t>(clipped->x1 + col_offset);
    const auto gram_row_start = static_cast<uint16_t>(clipped->y0 + row_offset);
    const auto gram_row_end   = static_cast<uint16_t>(clipped->y1 + row_offset);

    st7789_set_address_window(gram_col_start, gram_col_end, gram_row_start, gram_row_end);
    st7789_write_command(0x2C); // RAMWR: старт передачі піксельних слів

    const uint16_t* row_ptr = bitmap + (delta_y * stride) + delta_x;
    const int16_t visible_w = clipped->width();
    const int16_t visible_h = clipped->height();

    for (int16_t r = 0; r < visible_h; ++r) {
        st7789_write_pixels(row_ptr, visible_w);
        row_ptr += stride;
    }
}
