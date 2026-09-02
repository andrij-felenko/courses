#include "rc/channels.hpp"

#include <cmath>
#include <numbers>
#include <utility>

namespace rc {
namespace {

// Рядок — розкладка, стовпець — вісь (Roll, Pitch, Yaw, Throttle);
// значення — номер каналу на дроті.
constexpr std::array<std::array<std::size_t, kAxisCount>, 4> kMapTable{{
    {0, 1, 3, 2},  // AETR
    {1, 2, 3, 0},  // TAER
    {3, 1, 0, 2},  // RETA
    {2, 0, 3, 1},  // ETAR
}};

constexpr std::array<std::string_view, 4> kMapNames{"AETR", "TAER", "RETA", "ETAR"};

}  // namespace

RawChannels unpack11Bit(std::span<const std::uint8_t, kPackedBytes> payload) noexcept
{
    RawChannels raw{};

    for (std::size_t i = 0; i < kChannels; ++i) {
        const std::size_t bit   = i * 11;
        const std::size_t byte  = bit / 8;
        const std::size_t shift = bit % 8;

        std::uint32_t acc = static_cast<std::uint32_t>(payload[byte]) |
                            (static_cast<std::uint32_t>(payload[byte + 1]) << 8);
        if (byte + 2 < kPackedBytes) {
            acc |= static_cast<std::uint32_t>(payload[byte + 2]) << 16;
        }
        raw[i] = static_cast<std::uint16_t>((acc >> shift) & 0x07FFu);
    }
    return raw;
}

PackedPayload pack11Bit(const RawChannels& raw) noexcept
{
    PackedPayload payload{};

    for (std::size_t i = 0; i < kChannels; ++i) {
        const std::uint32_t v     = static_cast<std::uint32_t>(raw[i]) & 0x07FFu;
        const std::size_t   bit   = i * 11;
        const std::size_t   byte  = bit / 8;
        const std::size_t   shift = bit % 8;

        payload[byte]     |= static_cast<std::uint8_t>(v << shift);
        payload[byte + 1] |= static_cast<std::uint8_t>(v >> (8 - shift));
        if (shift > 5 && byte + 2 < kPackedBytes) {
            payload[byte + 2] |= static_cast<std::uint8_t>(v >> (16 - shift));
        }
    }
    return payload;
}

MicrosChannels toMicros(const RawChannels& raw) noexcept
{
    MicrosChannels us{};
    for (std::size_t i = 0; i < kChannels; ++i) {
        us[i] = rawToUs(raw[i]);
    }
    return us;
}

std::size_t channelIndex(ChannelMap map, Axis axis) noexcept
{
    return kMapTable[std::to_underlying(map)][std::to_underlying(axis)];
}

AxisSet applyMap(ChannelMap map, const MicrosChannels& us) noexcept
{
    AxisSet axes{};
    const auto& row = kMapTable[std::to_underlying(map)];
    for (std::size_t axis = 0; axis < kAxisCount; ++axis) {
        axes[axis] = us[row[axis]];
    }
    return axes;
}

std::string_view mapName(ChannelMap map) noexcept
{
    return kMapNames[std::to_underlying(map)];
}

Biquad::Biquad(float cutoffHz, float sampleHz) noexcept
{
    // Виродження — фільтр стає прямим проводом, а не джерелом NaN
    if (sampleHz <= 0.0f || cutoffHz <= 0.0f || cutoffHz >= sampleHz * 0.5f) {
        return;
    }

    constexpr float q = 0.70710678f;  // Баттерворт, 2-й порядок
    const float omega = 2.0f * std::numbers::pi_v<float> * cutoffHz / sampleHz;
    const float cs    = std::cos(omega);
    const float alpha = std::sin(omega) / (2.0f * q);
    const float a0    = 1.0f + alpha;

    b0_ = ((1.0f - cs) * 0.5f) / a0;
    b1_ = (1.0f - cs) / a0;
    b2_ = b0_;
    a1_ = (-2.0f * cs) / a0;
    a2_ = (1.0f - alpha) / a0;
}

float Biquad::operator()(float x) noexcept
{
    if (!primed_) {
        // Перший кадр заповнює лінію затримки, інакше вихід «виповзає» з нуля
        x1_ = x2_ = y1_ = y2_ = x;
        primed_ = true;
        return x;
    }

    const float y = b0_ * x + b1_ * x1_ + b2_ * x2_ - a1_ * y1_ - a2_ * y2_;

    x2_ = x1_;
    x1_ = x;
    y2_ = y1_;
    y1_ = y;
    return y;
}

}  // namespace rc
