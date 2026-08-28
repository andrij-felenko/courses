#include <cstdint>
#include <cstddef>
#include <span>
#include <algorithm>
#include <array>

namespace embedded_ml {

struct FusedQuantParams {
    int32_t m0_r{}, m0_g{}, m0_b{};
    int32_t shift_r{}, shift_g{}, shift_b{};
    int32_t z_eff_r{}, z_eff_g{}, z_eff_b{};
};

struct Rgb888 {
    uint8_t r;
    uint8_t g;
    uint8_t b;
};

// Строго типізоване розпакування RGB565 з реплікацією розрядів
[[nodiscard]] constexpr Rgb888 unpack_rgb565(uint16_t raw) noexcept {
    const uint32_t r5 = (raw >> 11) & 0x1F;
    const uint32_t g6 = (raw >> 5) & 0x3F;
    const uint32_t b5 = raw & 0x1F;
    return {
        .r = static_cast<uint8_t>((r5 << 3) | (r5 >> 2)),
        .g = static_cast<uint8_t>((g6 << 2) | (g6 >> 4)),
        .b = static_cast<uint8_t>((b5 << 3) | (b5 >> 2))
    };
}

class PreprocessingPipeline {
public:
    explicit constexpr PreprocessingPipeline(const FusedQuantParams& params) noexcept
        : params_(params) {}

    void process_row(
        std::span<const uint16_t> row0_rgb565,
        std::span<const uint16_t> row1_rgb565,
        int out_width,
        int32_t frac_y_q16,
        std::span<int8_t> out_row_nhwc) const noexcept
    {
        const int in_width = static_cast<int>(row0_rgb565.size());
        const int32_t step_x = static_cast<int32_t>(((int64_t)in_width << 16) / out_width);
        int32_t u_x = (step_x - (1 << 16)) >> 1;

        for (int ox = 0; ox < out_width; ++ox) {
            const int32_t u_clamped = std::clamp(u_x, 0, (in_width - 1) << 16);
            const int x0 = u_clamped >> 16;
            const int x1 = (x0 < in_width - 1) ? x0 + 1 : x0;
            const int32_t frac_x = u_clamped & 0xFFFF;

            const auto p00 = unpack_rgb565(row0_rgb565[x0]);
            const auto p10 = unpack_rgb565(row0_rgb565[x1]);
            const auto p01 = unpack_rgb565(row0_rgb565[x0]);
            const auto p11 = unpack_rgb565(row0_rgb565[x1]);

            const int32_t w00 = ((65536 - frac_x) * (65536 - frac_y_q16)) >> 16;
            const int32_t w10 = (frac_x * (65536 - frac_y_q16)) >> 16;
            const int32_t w01 = ((65536 - frac_x) * frac_y_q16) >> 16;
            const int32_t w11 = (frac_x * frac_y_q16) >> 16;

            const uint8_t r = static_cast<uint8_t>((p00.r * w00 + p10.r * w10 + p01.r * w01 + p11.r * w11 + 32768) >> 16);
            const uint8_t g = static_cast<uint8_t>((p00.g * w00 + p10.g * w10 + p01.g * w01 + p11.g * w11 + 32768) >> 16);
            const uint8_t b = static_cast<uint8_t>((p00.b * w00 + p10.b * w10 + p01.b * w01 + p11.b * w11 + 32768) >> 16);

            const int dst_idx = ox * 3;
            out_row_nhwc[dst_idx + 0] = quantize_channel(r, params_.m0_r, params_.shift_r, params_.z_eff_r);
            out_row_nhwc[dst_idx + 1] = quantize_channel(g, params_.m0_g, params_.shift_g, params_.z_eff_g);
            out_row_nhwc[dst_idx + 2] = quantize_channel(b, params_.m0_b, params_.shift_b, params_.z_eff_b);

            u_x += step_x;
        }
    }

private:
    [[nodiscard]] static inline int8_t quantize_channel(
        uint8_t val, int32_t m0, int32_t shift, int32_t z_eff) noexcept
    {
        const int64_t scaled = ((static_cast<int64_t>(val) * m0) + (1LL << (shift - 1))) >> shift;
        return static_cast<int8_t>(std::clamp<int64_t>(scaled + z_eff, -128, 127));
    }

    FusedQuantParams params_;
};

} // namespace embedded_ml
