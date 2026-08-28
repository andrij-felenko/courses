#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <algorithm>
#include <stdexcept>

namespace color_space {

constexpr int32_t kFixY_R  = 19595;
constexpr int32_t kFixY_G  = 38470;
constexpr int32_t kFixY_B  = 7471;

constexpr int32_t kFixCb_R = -11058;
constexpr int32_t kFixCb_G = -21710;
constexpr int32_t kFixCb_B = 32768;

constexpr int32_t kFixCr_R = 32768;
constexpr int32_t kFixCr_G = -27439;
constexpr int32_t kFixCr_B = -5329;

constexpr int32_t kFixInvCr_R = 91881;
constexpr int32_t kFixInvCb_G = -22554;
constexpr int32_t kFixInvCr_G = -46802;
constexpr int32_t kFixInvCb_B = 116130;

struct YCbCrBufferView {
    std::span<const uint8_t> y_plane;
    std::span<const uint8_t> cb_plane;
    std::span<const uint8_t> cr_plane;
    size_t y_stride{0};
    size_t cb_stride{0};
    size_t cr_stride{0};
    size_t width{0};
    size_t height{0};
};

class ColorConverter {
public:
    static void convert_rgb_to_ycbcr(std::span<const uint8_t> rgb_data, size_t rgb_stride,
                                     std::span<uint8_t> y_plane, size_t y_stride,
                                     std::span<uint8_t> cb_plane, size_t cb_stride,
                                     std::span<uint8_t> cr_plane, size_t cr_stride,
                                     size_t width, size_t height)
    {
        if (width == 0 || height == 0) {
            throw std::invalid_argument("Розміри кадру мають бути більшими за нуль");
        }

        for (size_t y = 0; y < height; ++y) {
            auto rgb_row = rgb_data.subspan(y * rgb_stride, width * 3);
            auto y_row   = y_plane.subspan(y * y_stride, width);
            auto cb_row  = cb_plane.subspan(y * cb_stride, width);
            auto cr_row  = cr_plane.subspan(y * cr_stride, width);

            for (size_t x = 0; x < width; ++x) {
                int32_t r = rgb_row[x * 3 + 0];
                int32_t g = rgb_row[x * 3 + 1];
                int32_t b = rgb_row[x * 3 + 2];

                int32_t luma = (kFixY_R * r + kFixY_G * g + kFixY_B * b) >> 16;
                int32_t cb   = ((kFixCb_R * r + kFixCb_G * g + kFixCb_B * b) >> 16) + 128;
                int32_t cr   = ((kFixCr_R * r + kFixCr_G * g + kFixCr_B * b) >> 16) + 128;

                y_row[x]  = static_cast<uint8_t>(std::clamp(luma, 0, 255));
                cb_row[x] = static_cast<uint8_t>(std::clamp(cb, 0, 255));
                cr_row[x] = static_cast<uint8_t>(std::clamp(cr, 0, 255));
            }
        }
    }

    static void convert_ycbcr_to_rgb(const YCbCrBufferView& view,
                                     std::span<uint8_t> rgb_out, size_t rgb_stride)
    {
        for (size_t y = 0; y < view.height; ++y) {
            auto y_row   = view.y_plane.subspan(y * view.y_stride, view.width);
            auto cb_row  = view.cb_plane.subspan(y * view.cb_stride, view.width);
            auto cr_row  = view.cr_plane.subspan(y * view.cr_stride, view.width);
            auto rgb_row = rgb_out.subspan(y * rgb_stride, view.width * 3);

            for (size_t x = 0; x < view.width; ++x) {
                int32_t luma = y_row[x];
                int32_t cb   = static_cast<int32_t>(cb_row[x]) - 128;
                int32_t cr   = static_cast<int32_t>(cr_row[x]) - 128;

                int32_t r = luma + ((kFixInvCr_R * cr) >> 16);
                int32_t g = luma + ((kFixInvCB_G * cb + kFixInvCr_G * cr) >> 16);
                int32_t b = luma + ((kFixInvCb_B * cb) >> 16);

                rgb_row[x * 3 + 0] = static_cast<uint8_t>(std::clamp(r, 0, 255));
                rgb_row[x * 3 + 1] = static_cast<uint8_t>(std::clamp(g, 0, 255));
                rgb_row[x * 3 + 2] = static_cast<uint8_t>(std::clamp(b, 0, 255));
            }
        }
    }
};

} // namespace color_space
