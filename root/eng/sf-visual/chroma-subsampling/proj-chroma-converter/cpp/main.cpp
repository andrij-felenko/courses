#include <iostream>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <cmath>

// Клас кадру YUV444 з керуванням пам'яттю через RAII
class Yuv444Frame {
public:
    int width;
    int height;
    std::vector<uint8_t> y;
    std::vector<uint8_t> cb;
    std::vector<uint8_t> cr;

    Yuv444Frame(int w, int h) 
        : width(w), height(h), y(w * h), cb(w * h), cr(w * h) {}
};

// Клас плоского кадру YUV420p (4:2:0)
class Yuv420pFrame {
public:
    int width;
    int height;
    std::vector<uint8_t> y;
    std::vector<uint8_t> cb;
    std::vector<uint8_t> cr;

    Yuv420pFrame(int w, int h) 
        : width(w), height(h), 
          y(w * h), 
          cb((w / 2) * (h / 2)), 
          cr((w / 2) * (h / 2)) {}
};

// Перетворення 4:4:4 у 4:2:0 із 2D ФНЧ антиаліасингом
Yuv420pFrame convert_444_to_420p(const Yuv444Frame& src) {
    const int w = src.width;
    const int h = src.height;
    Yuv420pFrame dst(w, h);

    // 1. Канал Y копіюється без змін
    std::copy(src.y.begin(), src.y.end(), dst.y.begin());

    const int cw = w / 2;
    const int ch = h / 2;

    // 2. Двовимірна фільтрація КІХ 2x2 та субдискретизація Cb/Cr
    for (int cy = 0; cy < ch; ++cy) {
        for (int cx = 0; cx < cw; ++cx) {
            const int x0 = cx * 2;
            const int y0 = cy * 2;
            const int x1 = std::min(x0 + 1, w - 1);
            const int y1 = std::min(y0 + 1, h - 1);

            const uint32_t sum_cb = src.cb[y0 * w + x0] + src.cb[y0 * w + x1] +
                                    src.cb[y1 * w + x0] + src.cb[y1 * w + x1];
            dst.cb[cy * cw + cx] = static_cast<uint8_t>((sum_cb + 2) >> 2);

            const uint32_t sum_cr = src.cr[y0 * w + x0] + src.cr[y0 * w + x1] +
                                    src.cr[y1 * w + x0] + src.cr[y1 * w + x1];
            dst.cr[cy * cw + cx] = static_cast<uint8_t>((sum_cr + 2) >> 2);
        }
    }

    return dst;
}

// Зворотне відновлення 4:2:0 у 4:4:4 через білінійну інтерполяцію
Yuv444Frame convert_420p_to_444(const Yuv420pFrame& src) {
    const int w = src.width;
    const int h = src.height;
    const int cw = w / 2;
    const int ch = h / 2;
    Yuv444Frame dst(w, h);

    std::copy(src.y.begin(), src.y.end(), dst.y.begin());

    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            const float cx_f = std::max(0.0f, static_cast<float>(x) / 2.0f - 0.25f);
            const float cy_f = std::max(0.0f, static_cast<float>(y) / 2.0f - 0.25f);

            const int x0 = static_cast<int>(cx_f);
            const int y0 = static_cast<int>(cy_f);
            const int x1 = std::min(x0 + 1, cw - 1);
            const int y1 = std::min(y0 + 1, ch - 1);

            const float fx = cx_f - static_cast<float>(x0);
            const float fy = cy_f - static_cast<float>(y0);

            const float w00 = (1.0f - fx) * (1.0f - fy);
            const float w10 = fx * (1.0f - fy);
            const float w01 = (1.0f - fx) * fy;
            const float w11 = fx * fy;

            const float val_cb = w00 * src.cb[y0 * cw + x0] + w10 * src.cb[y0 * cw + x1] +
                                 w01 * src.cb[y1 * cw + x0] + w11 * src.cb[y1 * cw + x1];
            const float val_cr = w00 * src.cr[y0 * cw + x0] + w10 * src.cr[y0 * cw + x1] +
                                 w01 * src.cr[y1 * cw + x0] + w11 * src.cr[y1 * cw + x1];

            dst.cb[y * w + x] = static_cast<uint8_t>(std::clamp(val_cb + 0.5f, 0.0f, 255.0f));
            dst.cr[y * w + x] = static_cast<uint8_t>(std::clamp(val_cr + 0.5f, 0.0f, 255.0f));
        }
    }

    return dst;
}
