#pragma once

#include "arming_flags.hpp"

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <vector>

namespace msp {

inline constexpr std::uint8_t kStatus = 101;
inline constexpr std::size_t kMaxExtraModeFlags = 15;   // молодші 4 біти заголовка

// Кадр MSP v1:
//   '$' 'M' <напрямок> <size> <code> <payload[size]> <crc>
// напрямок: '<' запит до плати, '>' відповідь плати, '!' відмова.
// crc — XOR по size, code й усьому payload.
//
// Розкладка payload MSP_STATUS у Betaflight 4.x:
//   u16 cycleTime            довжина такту PID, мкс
//   u16 i2cErrorCounter
//   u16 sensors              бітова карта наявних сенсорів
//   u32 flightModeFlags      нижні 32 біти BOX-режимів
//   u8  pidProfileIndex
//   u16 averageSystemLoad    відсотки; той самий лічильник, що піднімає LOAD
//   u16 gyroCycleTime        мкс
//   u8  header               молодші 4 біти: скільки байтів BOX-прапорців далі
//   u8  extra[header & 0x0F]
//   u8  armingDisableFlagCount
//   u32 armingDisableFlags   <- те, заради чого шлють запит
//   u8  configStateFlags     біт 0: потрібне перезавантаження
enum class Error {
    TooShort,
    BadMagic,
    NotAReply,
    LengthMismatch,
    Checksum,
    UnexpectedCode,
    TruncatedPayload
};

[[nodiscard]] std::string_view describe(Error error) noexcept;

struct Status {
    std::uint16_t cycleTimeUs{};
    std::uint16_t i2cErrors{};
    std::uint16_t sensors{};
    std::uint32_t flightModeFlags{};
    std::uint8_t pidProfile{};
    std::uint16_t cpuLoadPercent{};
    std::uint16_t gyroCycleTimeUs{};
    std::vector<std::byte> extraModeFlags;
    std::uint8_t armingFlagCount{};
    bf::Mask armingDisable{};
    std::uint8_t configState{};

    [[nodiscard]] bool rebootRequired() const noexcept { return (configState & 0x01u) != 0u; }
};

[[nodiscard]] std::expected<Status, Error> parseStatus(std::span<const std::byte> frame);

[[nodiscard]] std::vector<std::byte> buildRequest(std::uint8_t code);

// Зворотний бік — потрібен, щоб на стенді мати з чого розбирати
// без підключеної плати.
[[nodiscard]] std::vector<std::byte> encodeStatus(const Status& status);

}  // namespace msp
