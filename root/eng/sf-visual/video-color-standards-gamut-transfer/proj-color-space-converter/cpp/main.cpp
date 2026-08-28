// cpp
#include <cstdint>
#include <span>
#include <algorithm>
#include <array>
#include <concepts>

namespace video {

// Коефіцієнти матриць перетворення у форматі Q8.8
struct MatrixCoeffs {
    int32_t y_scale;
    int32_t rv_scale;
    int32_t gu_scale;
    int32_t gv_scale;
    int32_t bu_scale;
};

// Стандартні коефіцієнти BT.709 Studio Range
constexpr MatrixCoeffs BT709_STUDIO{298, 459, 55, 136, 541};
// Стандартні коефіцієнти BT.601 Studio Range
constexpr MatrixCoeffs BT601_STUDIO{298, 409, 100, 208, 516};

struct PixelRGBA {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a{255};
};

/**
 * Ідіоматичний C++20 конвертер YUV420p у RGBA з використанням std::span та std::clamp
 */
class ColorSpaceConverter {
public:
    explicit ColorSpaceConverter(MatrixCoeffs coeffs = BT709_STUDIO)
        : coeffs_(coeffs) {}

    void convert_yuv420p(std::span<const uint8_t> y_plane,
                         std::span<const uint8_t> u_plane,
                         std::span<const uint8_t> v_plane,
                         std::span<PixelRGBA> out_pixels,
                         size_t width, size_t height,
                         size_t y_stride, size_t uv_stride) const
    {
        for (size_t y = 0; y < height; ++y) {
            const auto y_line = y_plane.subspan(y * y_stride, width);
            const auto u_line = u_plane.subspan((y / 2) * uv_stride, width / 2);
            const auto v_line = v_plane.subspan((y / 2) * uv_stride, width / 2);
            const auto out_line = out_pixels.subspan(y * width, width);

            for (size_t x = 0; x < width; ++x) {
                const int32_t y_val = std::max(0, static_cast<int32_t>(y_line[x]) - 16);
                const int32_t u_val = static_cast<int32_t>(u_line[x / 2]) - 128;
                const int32_t v_val = static_cast<int32_t>(v_line[x / 2]) - 128;

                const int32_t y_scaled = coeffs_.y_scale * y_val + 128;

                const int32_t r = (y_scaled + coeffs_.rv_scale * v_val) >> 8;
                const int32_t g = (y_scaled - coeffs_.gu_scale * u_val - coeffs_.gv_scale * v_val) >> 8;
                const int32_t b = (y_scaled + coeffs_.bu_scale * u_val) >> 8;

                out_line[x] = PixelRGBA{
                    .r = static_cast<uint8_t>(std::clamp(r, 0, 255)),
                    .g = static_cast<uint8_t>(std::clamp(g, 0, 255)),
                    .b = static_cast<uint8_t>(std::clamp(b, 0, 255)),
                    .a = 255
                };
            }
        }
    }

private:
    MatrixCoeffs coeffs_;
};

} // namespace video
