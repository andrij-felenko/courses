// ParityPipeline.hpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <algorithm>
#include <array>

namespace embedded_ml {

struct QuantizationChannel {
    int32_t m0{0};
    int32_t shift{31};
    int32_t z_eff{0};
};

struct PipelineConfig {
    int in_width{320};
    int in_height{240};
    int out_width{224};
    int out_height{224};
    std::array<QuantizationChannel, 3> channels{};
};

struct RgbPixel {
    uint8_t r;
    uint8_t g;
    uint8_t b;
};

class PreprocessingEngine {
public:
    explicit constexpr PreprocessingEngine(const PipelineConfig& config) noexcept
        : cfg_(config),
          step_x_q16_(static_cast<int32_t>(((static_cast<int64_t>(config.in_width) << 16) / config.out_width))),
          step_y_q16_(static_cast<int32_t>(((static_cast<int64_t>(config.in_height) << 16) / config.out_height))) {}

    [[nodiscard]] static constexpr RgbPixel unpack_rgb565(uint16_t raw) noexcept {
        const uint32_t r5 = (raw >> 11) & 0x1F;
        const uint32_t g6 = (raw >> 5) & 0x3F;
        const uint32_t b5 = raw & 0x1F;
        return {
            .r = static_cast<uint8_t>((r5 << 3) | (r5 >> 2)),
            .g = static_cast<uint8_t>((g6 << 2) | (g6 >> 4)),
            .b = static_cast<uint8_t>((b5 << 3) | (b5 >> 2))
        };
    }

    void process_row(
        std::span<const uint16_t> row0,
        std::span<const uint16_t> row1,
        int out_row_idx,
        std::span<int8_t> out_tensor_row) const noexcept
    {
        const int32_t v_y = (static_cast<int32_t>(((static_cast<int64_t>(out_row_idx * 2 + 1) * step_y_q16_) - (1 << 16))) >> 1);
        const int32_t v_clamped = std::clamp(v_y, 0, (cfg_.in_height - 1) << 16);
        const int32_t frac_y = v_clamped & 0xFFFF;

        int32_t u_x = (step_x_q16_ - (1 << 16)) >> 1;

        for (int ox = 0; ox < cfg_.out_width; ++ox) {
            const int32_t u_clamped = std::clamp(u_x, 0, (cfg_.in_width - 1) << 16);
            const int x0 = u_clamped >> 16;
            const int x1 = (x0 < cfg_.in_width - 1) ? x0 + 1 : x0;
            const int32_t frac_x = u_clamped & 0xFFFF;

            const auto p00 = unpack_rgb565(row0[x0]);
            const auto p10 = unpack_rgb565(row0[x1]);
            const auto p01 = unpack_rgb565(row0[x0]);
            const auto p11 = unpack_rgb565(row1[x1]);

            const int32_t w00 = ((65536 - frac_x) * (65536 - frac_y)) >> 16;
            const int32_t w10 = (frac_x * (65536 - frac_y)) >> 16;
            const int32_t w01 = ((65536 - frac_x) * frac_y) >> 16;
            const int32_t w11 = (frac_x * frac_y) >> 16;

            const uint8_t r = static_cast<uint8_t>((p00.r * w00 + p10.r * w10 + p01.r * w01 + p11.r * w11 + 32768) >> 16);
            const uint8_t g = static_cast<uint8_t>((p00.g * w00 + p10.g * w10 + p01.g * w01 + p11.g * w11 + 32768) >> 16);
            const uint8_t b = static_cast<uint8_t>((p00.b * w00 + p10.b * w10 + p01.b * w01 + p11.b * w11 + 32768) >> 16);

            const size_t dst_idx = static_cast<size_t>(ox) * 3;
            out_tensor_row[dst_idx + 0] = quantize_channel(r, cfg_.channels[0]);
            out_tensor_row[dst_idx + 1] = quantize_channel(g, cfg_.channels[1]);
            out_tensor_row[dst_idx + 2] = quantize_channel(b, cfg_.channels[2]);

            u_x += step_x_q16_;
        }
    }

    void process_frame(
        std::span<const uint16_t> src_frame,
        std::span<int8_t> dst_tensor) const noexcept
    {
        for (int oy = 0; oy < cfg_.out_height; ++oy) {
            const int32_t v_y = (static_cast<int32_t>(((static_cast<int64_t>(oy * 2 + 1) * step_y_q16_) - (1 << 16))) >> 1);
            const int32_t v_clamped = std::clamp(v_y, 0, (cfg_.in_height - 1) << 16);
            const int y0 = v_clamped >> 16;
            const int y1 = (y0 < cfg_.in_height - 1) ? y0 + 1 : y0;

            const auto row0 = src_frame.subspan(static_cast<size_t>(y0) * cfg_.in_width, cfg_.in_width);
            const auto row1 = src_frame.subspan(static_cast<size_t>(y1) * cfg_.in_width, cfg_.in_width);
            const auto out_row = dst_tensor.subspan(static_cast<size_t>(oy) * cfg_.out_width * 3, cfg_.out_width * 3);

            process_row(row0, row1, oy, out_row);
        }
    }

private:
    [[nodiscard]] static inline int8_t quantize_channel(uint8_t val, const QuantizationChannel& q) noexcept {
        const int64_t prod = static_cast<int64_t>(val) * q.m0;
        const int64_t rounded = (prod + (1LL << (q.shift - 1))) >> q.shift;
        const int32_t clamped = std::clamp<int32_t>(static_cast<int32_t>(rounded) + q.z_eff, -128, 127);
        return static_cast<int8_t>(clamped);
    }

    PipelineConfig cfg_;
    int32_t step_x_q16_{0};
    int32_t step_y_q16_{0};
};

} // namespace embedded_ml
