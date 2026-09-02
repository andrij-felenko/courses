#include "telemetry_protocol.hpp"

#include <optional>
#include <utility>

namespace telemetry {
namespace {

// Читаємо зсувами: жодного reinterpret_cast на структуру, жодної
// залежності від порядку байтів і вирівнювання самої машини.
[[nodiscard]] std::uint16_t read_u16(std::span<const std::uint8_t> buf, std::size_t at) noexcept
{
    return static_cast<std::uint16_t>(buf[at] | (buf[at + 1] << 8));
}

[[nodiscard]] std::int16_t read_i16(std::span<const std::uint8_t> buf, std::size_t at) noexcept
{
    const std::uint16_t raw = read_u16(buf, at);
    return (raw & 0x8000) ? static_cast<std::int16_t>(static_cast<std::int32_t>(raw) - 0x10000)
                          : static_cast<std::int16_t>(raw);
}

void write_u16(std::span<std::uint8_t> buf, std::size_t at, std::uint16_t value) noexcept
{
    buf[at] = static_cast<std::uint8_t>(value & 0xFF);
    buf[at + 1] = static_cast<std::uint8_t>(value >> 8);
}

[[nodiscard]] constexpr std::optional<std::size_t> wire_size(MsgType type) noexcept
{
    switch (type) {
    case MsgType::Ping: return Ping::kWireSize;
    case MsgType::SetConfig: return SetConfig::kWireSize;
    case MsgType::TelemetryReport: return Telemetry::kWireSize;
    case MsgType::Response: return Ack::kWireSize;
    }
    return std::nullopt;
}

}  // namespace

std::expected<Frame, ParseError> parse(std::span<const std::uint8_t> frame) noexcept
{
    if (frame.size() < kMinFrame) {
        return std::unexpected(ParseError::InvalidLen);
    }
    if (frame.front() != kSof) {
        return std::unexpected(ParseError::InvalidSof);
    }
    if (frame.back() != kEof) {
        return std::unexpected(ParseError::InvalidEof);
    }

    // Заявлена довжина мусить зійтися з реальним розміром span'а — інакше
    // будь-яка наступна subspan різала б за межами кадру.
    const std::size_t declared = read_u16(frame, 4);
    if (declared > kMaxPayload || frame.size() != kHeaderLen + declared + kFooterLen) {
        return std::unexpected(ParseError::InvalidLen);
    }

    const std::uint16_t expected_crc = read_u16(frame, kHeaderLen + declared);
    if (crc16_ccitt(frame.subspan(1, kHeaderLen - 1 + declared)) != expected_crc) {
        return std::unexpected(ParseError::InvalidCrc);
    }

    if (frame[1] != kVersion) {
        return std::unexpected(ParseError::UnsupportedVersion);
    }

    const auto type = static_cast<MsgType>(frame[2]);
    const auto expected_size = wire_size(type);
    if (!expected_size) {
        return std::unexpected(ParseError::UnknownMsg);
    }
    if (*expected_size != declared) {
        // Схема цього не ловить: size: payload_len віддасть підпотік
        // потрібного розміру, а от чи він того розміру, що треба типові,
        // вирішує вже застосунок.
        return std::unexpected(ParseError::InvalidLen);
    }

    const auto body = frame.subspan(kHeaderLen, declared);
    Frame out{.seq_id = frame[3], .payload = Ping{}};

    switch (type) {
    case MsgType::Ping:
        break;
    case MsgType::SetConfig:
        out.payload = SetConfig{.sample_rate_hz = read_u16(body, 0),
                                .alert_threshold_raw = read_i16(body, 2),
                                .flags_enable = body[4]};
        break;
    case MsgType::TelemetryReport:
        out.payload = Telemetry{.temp_raw = read_i16(body, 0),
                                .pressure_raw = read_u16(body, 2),
                                .voltage_mv = read_u16(body, 4),
                                .flags = body[6],
                                .reserved = body[7]};
        break;
    case MsgType::Response:
        // Невідомий код статусу не валимо: сторона могла піти вперед у
        // словнику помилок, і це не привід відкидати кадр.
        out.payload = Ack{.target_seq_id = body[0], .status = static_cast<StatusCode>(body[1])};
        break;
    }

    return out;
}

std::expected<std::span<std::uint8_t>, ParseError> encode(const Frame& frame,
                                                          std::span<std::uint8_t> out) noexcept
{
    const MsgType type = frame.id();
    const std::size_t len = *wire_size(type);  // варіант інших типів не тримає
    const std::size_t total = kHeaderLen + len + kFooterLen;
    if (out.size() < total) {
        return std::unexpected(ParseError::BufferTooSmall);
    }

    out[0] = kSof;
    out[1] = kVersion;
    out[2] = std::to_underlying(type);
    out[3] = frame.seq_id;
    write_u16(out, 4, static_cast<std::uint16_t>(len));

    const auto body = out.subspan(kHeaderLen, len);
    std::visit(
        [body](const auto& payload) noexcept {
            using T = std::decay_t<decltype(payload)>;
            if constexpr (std::is_same_v<T, Telemetry>) {
                write_u16(body, 0, static_cast<std::uint16_t>(payload.temp_raw));
                write_u16(body, 2, payload.pressure_raw);
                write_u16(body, 4, payload.voltage_mv);
                body[6] = payload.flags;
                body[7] = payload.reserved;
            } else if constexpr (std::is_same_v<T, SetConfig>) {
                write_u16(body, 0, payload.sample_rate_hz);
                write_u16(body, 2, static_cast<std::uint16_t>(payload.alert_threshold_raw));
                body[4] = payload.flags_enable;
            } else if constexpr (std::is_same_v<T, Ack>) {
                body[0] = payload.target_seq_id;
                body[1] = std::to_underlying(payload.status);
            }
            // Ping навантаження не має — писати нічого.
        },
        frame.payload);

    write_u16(out, kHeaderLen + len, crc16_ccitt(out.subspan(1, kHeaderLen - 1 + len)));
    out[total - 1] = kEof;
    return out.first(total);
}

std::string_view to_string(ParseError err) noexcept
{
    switch (err) {
    case ParseError::InvalidSof: return "InvalidSof";
    case ParseError::InvalidEof: return "InvalidEof";
    case ParseError::InvalidLen: return "InvalidLen";
    case ParseError::InvalidCrc: return "InvalidCrc";
    case ParseError::UnknownMsg: return "UnknownMsg";
    case ParseError::UnsupportedVersion: return "UnsupportedVersion";
    case ParseError::BufferTooSmall: return "BufferTooSmall";
    }
    return "???";
}

std::string_view to_string(StatusCode code) noexcept
{
    switch (code) {
    case StatusCode::Ok: return "ok";
    case StatusCode::InvalidCrc: return "invalid_crc";
    case StatusCode::UnknownCmd: return "unknown_cmd";
    case StatusCode::PayloadLengthMismatch: return "payload_length_mismatch";
    case StatusCode::ParamOutOfRange: return "param_out_of_range";
    case StatusCode::HardwareBusy: return "hardware_busy";
    }
    return "unknown_status";
}

}  // namespace telemetry
