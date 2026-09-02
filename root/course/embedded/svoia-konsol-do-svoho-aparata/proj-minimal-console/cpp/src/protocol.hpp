#pragma once

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "hal.hpp"

namespace console {

// Обидва напрямки — кадр фіксованої довжини 14 байтів. Фіксована довжина
// потрібна не заради краси: у FLRC вона економить заголовок і дає обом
// сторонам однаковий час у ефірі.
inline constexpr std::size_t kFrameLength = 14;
inline constexpr std::byte kUplinkSync{0x5A};
inline constexpr std::byte kDownlinkSync{0xA5};

namespace flag {
inline constexpr std::uint8_t Armed = 0x01;
inline constexpr std::uint8_t RateHigh = 0x02;
inline constexpr std::uint8_t Payload = 0x04;
inline constexpr std::uint8_t Failsafe = 0x08;
}   // namespace flag

using Frame = std::array<std::byte, kFrameLength>;

// CRC-16/CCITT-FALSE півбайтною таблицею: 32 байти флеш замість 512 і
// близько 3 мкс на кадр — у бюджет 15 мкс лягає з запасом.
constexpr std::uint16_t crc16(std::span<const std::byte> data) noexcept
{
    constexpr std::array<std::uint16_t, 16> table{
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
        0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF};

    std::uint16_t crc = 0xFFFF;
    for (std::byte raw : data) {
        const auto value = std::to_integer<std::uint8_t>(raw);
        crc = static_cast<std::uint16_t>((crc << 4) ^ table[((crc >> 12) ^ (value >> 4)) & 0x0F]);
        crc = static_cast<std::uint16_t>((crc << 4) ^ table[((crc >> 12) ^ (value & 0x0F)) & 0x0F]);
    }
    return crc;
}

struct UplinkFrame {
    std::array<std::uint16_t, hal::kAxisCount> axes{};
    std::uint16_t switches{};
    std::uint8_t flags{};
    std::uint8_t aux{};
    std::uint8_t sequence{};

    [[nodiscard]] Frame serialize() const noexcept;
};

enum class ProtoError : std::uint8_t { WrongLength, WrongSync, CrcMismatch };

struct Telemetry {
    std::uint8_t sequence{};
    std::uint16_t vbatMv{};
    std::uint16_t currentDeciAmp{};
    std::int8_t rssiDbm{-127};
    std::uint8_t linkPercent{};
    std::uint8_t mosTempC{};
    std::uint8_t flightMode{};
    std::uint8_t satellites{};
    std::uint8_t status{};

    [[nodiscard]] static std::expected<Telemetry, ProtoError> parse(
        std::span<const std::byte> raw) noexcept;
};

// Ковзне вікно на 64 слоти: скільки відповідей прийшло на останні 64 посилки.
class LinkStats {
public:
    void mark(bool received) noexcept
    {
        window_ = (window_ << 1) | (received ? 1ull : 0ull);
        if (filled_ < 64) {
            ++filled_;
        }
        quality_ = static_cast<std::uint8_t>(std::popcount(window_) * 100u / filled_);
    }

    [[nodiscard]] std::uint8_t quality() const noexcept { return quality_; }

private:
    std::uint64_t window_{};
    std::uint8_t filled_{};
    std::uint8_t quality_{};
};

}   // namespace console
