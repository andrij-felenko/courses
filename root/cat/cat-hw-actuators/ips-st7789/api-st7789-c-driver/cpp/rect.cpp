#include <cstdint>
#include <algorithm>

struct Rect {
    int16_t x;
    int16_t y;
    int16_t w;
    int16_t h;
};

struct ClippedRect {
    uint16_t x_start;
    uint16_t y_start;
    uint16_t x_end;
    uint16_t y_end;
    uint16_t src_x_offset;
    uint16_t src_y_offset;
    uint16_t visible_w;
    uint16_t visible_h;
};

class ST7789Safety {
public:
    static constexpr uint16_t kWidth  = 240;
    static constexpr uint16_t kHeight = 240;

    // Перевірка та розрахунок відсікання меж прямокутника
    static bool clip(const Rect& in, ClippedRect& out) {
        if (in.w <= 0 || in.h <= 0) return false;
        if (in.x >= kWidth || in.y >= kHeight) return false;
        if ((in.x + in.w) <= 0 || (in.y + in.h) <= 0) return false;

        int16_t x0 = in.x;
        int16_t x1 = in.x + in.w - 1;
        out.src_x_offset = (x0 < 0) ? static_cast<uint16_t>(-x0) : 0;
        out.x_start = (x0 < 0) ? 0 : static_cast<uint16_t>(x0);
        out.x_end = (x1 >= kWidth) ? (kWidth - 1) : static_cast<uint16_t>(x1);
        out.visible_w = out.x_end - out.x_start + 1;

        int16_t y0 = in.y;
        int16_t y1 = in.y + in.h - 1;
        out.src_y_offset = (y0 < 0) ? static_cast<uint16_t>(-y0) : 0;
        out.y_start = (y0 < 0) ? 0 : static_cast<uint16_t>(y0);
        out.y_end = (y1 >= kHeight) ? (kHeight - 1) : static_cast<uint16_t>(y1);
        out.visible_h = out.y_end - out.y_start + 1;

        return true;
    }
};
