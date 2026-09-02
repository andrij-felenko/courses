#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <string_view>

// Ядро радіотракту: діапазони, бітова упаковка, розкладка каналів на осі,
// мертва зона й згладжування.
namespace rc {

inline constexpr std::size_t kChannels    = 16;
inline constexpr std::size_t kPackedBytes = 22;  // 16 * 11 біт = 176 біт

inline constexpr std::uint16_t kUsMin    = 988;
inline constexpr std::uint16_t kUsCenter = 1500;
inline constexpr std::uint16_t kUsMax    = 2012;

inline constexpr std::uint16_t kRawMin    = 172;
inline constexpr std::uint16_t kRawCenter = 992;
inline constexpr std::uint16_t kRawMax    = 1811;

using RawChannels   = std::array<std::uint16_t, kChannels>;
using MicrosChannels = std::array<std::uint16_t, kChannels>;
using PackedPayload = std::array<std::uint8_t, kPackedBytes>;

enum class Axis : std::size_t { Roll = 0, Pitch, Yaw, Throttle };
inline constexpr std::size_t kAxisCount = 4;
using AxisSet = std::array<std::uint16_t, kAxisCount>;

// Порядок каналів на дроті: Betaflight `map`, ArduPilot RCMAP_*
enum class ChannelMap : std::uint8_t { AETR = 0, TAER, RETA, ETAR };

// AUX1 — це CH5, індекс 4
[[nodiscard]] constexpr std::size_t auxIndex(std::size_t aux) noexcept { return aux + 3; }

[[nodiscard]] constexpr std::uint16_t rawToUs(std::uint16_t raw) noexcept
{
    if (raw <= kRawMin) {
        return kUsMin;
    }
    if (raw >= kRawMax) {
        return kUsMax;
    }
    // T_us = 988 + (raw - 172) * 1024 / 1640, з округленням
    const std::uint32_t num = static_cast<std::uint32_t>(raw - kRawMin) * 1024u;
    return static_cast<std::uint16_t>(kUsMin + (num + 820u) / 1640u);
}

[[nodiscard]] constexpr std::uint16_t usToRaw(std::uint16_t us) noexcept
{
    if (us <= kUsMin) {
        return kRawMin;
    }
    if (us >= kUsMax) {
        return kRawMax;
    }
    const std::uint32_t num = static_cast<std::uint32_t>(us - kUsMin) * 1640u;
    return static_cast<std::uint16_t>(kRawMin + (num + 512u) / 1024u);
}

[[nodiscard]] constexpr std::uint16_t applyDeadband(std::uint16_t us,
                                                    std::uint16_t deadbandUs) noexcept
{
    const int delta = static_cast<int>(us) - static_cast<int>(kUsCenter);
    const int db    = static_cast<int>(deadbandUs);

    if (delta > -db && delta < db) {
        return kUsCenter;
    }
    // Зсув, а не обнулення: на межі зони команда не стрибає
    const int shifted = delta + ((delta > 0) ? -db : db);
    return static_cast<std::uint16_t>(static_cast<int>(kUsCenter) + shifted);
}

// Розмір поля перевіряє компілятор: span зі статичною довжиною
[[nodiscard]] RawChannels unpack11Bit(std::span<const std::uint8_t, kPackedBytes> payload) noexcept;
[[nodiscard]] PackedPayload pack11Bit(const RawChannels& raw) noexcept;

[[nodiscard]] MicrosChannels toMicros(const RawChannels& raw) noexcept;

[[nodiscard]] std::size_t channelIndex(ChannelMap map, Axis axis) noexcept;
[[nodiscard]] AxisSet applyMap(ChannelMap map, const MicrosChannels& us) noexcept;
[[nodiscard]] std::string_view mapName(ChannelMap map) noexcept;

// Біквадратний ФНЧ (rc_smoothing_cutoff) — прибирає сходинки квантування
class Biquad {
public:
    Biquad(float cutoffHz, float sampleHz) noexcept;
    float operator()(float x) noexcept;

private:
    float b0_{1.0f}, b1_{0.0f}, b2_{0.0f}, a1_{0.0f}, a2_{0.0f};
    float x1_{0.0f}, x2_{0.0f}, y1_{0.0f}, y2_{0.0f};
    bool  primed_{false};
};

}  // namespace rc
