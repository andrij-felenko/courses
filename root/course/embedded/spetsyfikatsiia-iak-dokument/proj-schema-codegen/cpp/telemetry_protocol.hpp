#pragma once

// Той самий контракт telemetry_protocol.ksy, але типи навантажень
// живуть у std::variant: невірну гілку тут не прочитаєш навіть помилково,
// на відміну від union у C.

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <type_traits>
#include <variant>

namespace telemetry {

inline constexpr std::uint8_t kSof = 0xAA;
inline constexpr std::uint8_t kEof = 0x55;
inline constexpr std::uint8_t kVersion = 0x01;

inline constexpr std::size_t kHeaderLen = 6;  // sof, version, msg_id, seq_id, len(2)
inline constexpr std::size_t kFooterLen = 3;  // crc16(2), eof
inline constexpr std::size_t kMinFrame = kHeaderLen + kFooterLen;
inline constexpr std::size_t kMaxPayload = 64;
inline constexpr std::size_t kMaxFrame = kHeaderLen + kMaxPayload + kFooterLen;

// Біти поля flags у msg_telemetry
inline constexpr std::uint8_t kFlagAlert = 0x01;
inline constexpr std::uint8_t kFlagSensorFault = 0x02;

enum class MsgType : std::uint8_t {
    Ping = 0x01,
    SetConfig = 0x02,
    TelemetryReport = 0x20,
    Response = 0x80
};

// enums::status_code — код виконання у відповіді
enum class StatusCode : std::uint8_t {
    Ok = 0x00,
    InvalidCrc = 0x01,
    UnknownCmd = 0x02,
    PayloadLengthMismatch = 0x03,
    ParamOutOfRange = 0x04,
    HardwareBusy = 0x05
};

enum class ParseError : std::uint8_t {
    InvalidSof,
    InvalidEof,
    InvalidLen,
    InvalidCrc,
    UnknownMsg,
    UnsupportedVersion,
    BufferTooSmall
};

struct Ping {
    static constexpr MsgType kId = MsgType::Ping;
    static constexpr std::size_t kWireSize = 0;
};

struct SetConfig {
    static constexpr MsgType kId = MsgType::SetConfig;
    static constexpr std::size_t kWireSize = 5;

    std::uint16_t sample_rate_hz{};
    std::int16_t alert_threshold_raw{};
    std::uint8_t flags_enable{};

    // instances зі схеми
    [[nodiscard]] constexpr double alert_threshold_c() const noexcept
    {
        return alert_threshold_raw * 0.01;
    }
};

struct Telemetry {
    static constexpr MsgType kId = MsgType::TelemetryReport;
    static constexpr std::size_t kWireSize = 8;

    std::int16_t temp_raw{};
    std::uint16_t pressure_raw{};
    std::uint16_t voltage_mv{};
    std::uint8_t flags{};
    std::uint8_t reserved{};

    [[nodiscard]] constexpr double temperature_c() const noexcept { return temp_raw * 0.01; }
    [[nodiscard]] constexpr double pressure_hpa() const noexcept { return pressure_raw * 0.1; }
    [[nodiscard]] constexpr bool alert_active() const noexcept { return (flags & kFlagAlert) != 0; }
    [[nodiscard]] constexpr bool sensor_fault() const noexcept
    {
        return (flags & kFlagSensorFault) != 0;
    }
};

struct Ack {
    static constexpr MsgType kId = MsgType::Response;
    static constexpr std::size_t kWireSize = 2;

    std::uint8_t target_seq_id{};
    StatusCode status{StatusCode::Ok};
};

using Payload = std::variant<Ping, SetConfig, Telemetry, Ack>;

struct Frame {
    std::uint8_t seq_id{};
    Payload payload{Ping{}};

    // Тип повідомлення не зберігаємо окремим полем: його однозначно
    // задає альтернатива варіанта, тож розійтися їм ніде.
    [[nodiscard]] MsgType id() const noexcept
    {
        return std::visit([](const auto& p) noexcept { return std::decay_t<decltype(p)>::kId; },
                          payload);
    }
};

// CRC-16/CCITT-FALSE. constexpr — щоб еталонні суми рахувалися ще при збірці.
[[nodiscard]] constexpr std::uint16_t crc16_ccitt(std::span<const std::uint8_t> data) noexcept
{
    std::uint16_t crc = 0xFFFF;
    for (std::uint8_t byte : data) {
        crc ^= static_cast<std::uint16_t>(byte << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

// Помилку віддаємо через expected, а не через -1 і глобальний errno.
[[nodiscard]] std::expected<Frame, ParseError> parse(std::span<const std::uint8_t> frame) noexcept;

// Успіх — це підпростір буфера з готовим кадром, тож довжину нікуди
// передавати окремо не треба.
[[nodiscard]] std::expected<std::span<std::uint8_t>, ParseError> encode(
    const Frame& frame, std::span<std::uint8_t> out) noexcept;

[[nodiscard]] std::string_view to_string(ParseError err) noexcept;
[[nodiscard]] std::string_view to_string(StatusCode code) noexcept;

}  // namespace telemetry
