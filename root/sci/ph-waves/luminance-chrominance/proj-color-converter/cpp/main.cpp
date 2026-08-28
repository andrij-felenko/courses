#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <expected>
#include <algorithm>

namespace color_space {

enum class ConversionError {
    InvalidDimensions,
    NullBuffer,
    BufferSizeMismatch,
    InvalidStride
};

struct FrameMetrics {
    size_t width;
    size_t height;
    size_t stride_rgb = 0;
    size_t stride_y = 0;
    size_t stride_uv = 0;

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return width > 0 && height > 0 && (width % 2 == 0) && (height % 2 == 0);
    }
};

class ColorConverter {
public:
    // Табличні коефіцієнти fixed-point 16.16 у constexpr
    static constexpr int32_t KYR = 16843, KYG = 33030, KYB = 6423;
    static constexpr int32_t KCbR = -9699, KCbG = -19071, KCbB = 28770;
    static constexpr int32_t KCrR = 28770, KCrG = -24117, KCrB = -4653;

    struct NV12Frame {
        std::vector<uint8_t> y_plane;
        std::vector<uint8_t> uv_plane;
        size_t stride_y;
        size_t stride_uv;
    };

    static std::expected<NV12Frame, ConversionError>
    convert_rgb24_to_nv12(std::span<const uint8_t> rgb, FrameMetrics metrics) {
        if (!metrics.is_valid()) {
            return std::unexpected(ConversionError::InvalidDimensions);
        }

        if (metrics.stride_rgb == 0) metrics.stride_rgb = metrics.width * 3;
        if (metrics.stride_y == 0)   metrics.stride_y = metrics.width;
        if (metrics.stride_uv == 0)  metrics.stride_uv = metrics.width;

        const size_t min_rgb_size = metrics.stride_rgb * (metrics.height - 1) + metrics.width * 3;
        if (rgb.size() < min_rgb_size) {
            return std::unexpected(ConversionError::BufferSizeMismatch);
        }

        NV12Frame frame{
            .y_plane = std::vector<uint8_t>(metrics.stride_y * metrics.height),
            .uv_plane = std::vector<uint8_t>(metrics.stride_uv * (metrics.height / 2)),
            .stride_y = metrics.stride_y,
            .stride_uv = metrics.stride_uv
        };

        for (size_t y = 0; y < metrics.height; y += 2) {
            auto row1 = rgb.subspan(y * metrics.stride_rgb, metrics.width * 3);
            auto row2 = rgb.subspan((y + 1) * metrics.stride_rgb, metrics.width * 3);

            auto y_row1 = std::span(frame.y_plane).subspan(y * metrics.stride_y, metrics.width);
            auto y_row2 = std::span(frame.y_plane).subspan((y + 1) * metrics.stride_y, metrics.width);
            auto uv_row = std::span(frame.uv_plane).subspan((y / 2) * metrics.stride_uv, metrics.width);

            size_t uv_col = 0;

            for (size_t x = 0; x < metrics.width; x += 2) {
                const size_t p1 = x * 3;
                const size_t p2 = (x + 1) * 3;

                const int r00 = row1[p1],     g00 = row1[p1 + 1], b00 = row1[p1 + 2];
                const int r01 = row1[p2],     g01 = row1[p2 + 1], b01 = row1[p2 + 2];
                const int r10 = row2[p1],     g10 = row2[p1 + 1], b10 = row2[p1 + 2];
                const int r11 = row2[p2],     g11 = row2[p2 + 1], b11 = row2[p2 + 1];

                y_row1[x]     = clamp(16 + ((KYR * r00 + KYG * g00 + KYB * b00 + 32768) >> 16));
                y_row1[x + 1] = clamp(16 + ((KYR * r01 + KYG * g01 + KYB * b01 + 32768) >> 16));
                y_row2[x]     = clamp(16 + ((KYR * r10 + KYG * g10 + KYB * b10 + 32768) >> 16));
                y_row2[x + 1] = clamp(16 + ((KYR * r11 + KYG * g11 + KYB * b11 + 32768) >> 16));

                const int r_avg = (r00 + r01 + r10 + r11 + 2) >> 2;
                const int g_avg = (g00 + g01 + g10 + g11 + 2) >> 2;
                const int b_avg = (b00 + b01 + b10 + b11 + 2) >> 2;

                uv_row[uv_col++] = clamp(128 + ((KCbR * r_avg + KCbG * g_avg + KCbB * b_avg + 32768) >> 16));
                uv_row[uv_col++] = clamp(128 + ((KCrR * r_avg + KCrG * g_avg + KCrB * b_avg + 32768) >> 16));
            }
        }

        return frame;
    }

private:
    [[nodiscard]] static constexpr uint8_t clamp(int32_t val) noexcept {
        return static_cast<uint8_t>(std::clamp(val, 0, 255));
    }
};

} // namespace color_space
