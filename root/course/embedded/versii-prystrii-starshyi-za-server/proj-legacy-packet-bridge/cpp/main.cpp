#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>

namespace legacy_v1 {

constexpr uint8_t FRAME_MAGIC   = 0xAA;
constexpr uint8_t FRAME_VERSION = 0x01;
constexpr size_t  FRAME_SIZE    = 16;

constexpr uint8_t CMD_MAGIC     = 0x55;
constexpr size_t  CMD_SIZE      = 6;

struct TelemetryData {
    uint32_t device_id{};
    uint16_t seq_num{};
    uint32_t raw_pulses{};
    uint8_t  battery_raw{};
    bool     tamper_alarm{};
    bool     reverse_flow{};
};

enum class ParseError {
    BufferTooSmall,
    InvalidMagic,
    UnsupportedVersion,
    CrcMismatch
};

/* Обчислення CRC-16-CCITT під час компіляції (constexpr) або у рантаймі */
constexpr uint16_t crc16_ccitt(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

static inline uint16_t read_be16(std::span<const uint8_t, 2> p) noexcept {
    return static_cast<uint16_t>((p[0] << 8) | p[1]);
}

static inline uint32_t read_be32(std::span<const uint8_t, 4> p) noexcept {
    return (static_cast<uint32_t>(p[0]) << 24) |
           (static_cast<uint32_t>(p[1]) << 16) |
           (static_cast<uint32_t>(p[2]) << 8)  |
           (static_cast<uint32_t>(p[3]));
}

static inline void write_be16(std::span<uint8_t, 2> p, uint16_t val) noexcept {
    p[0] = static_cast<uint8_t>(val >> 8);
    p[1] = static_cast<uint8_t>(val & 0xFF);
}

std::expected<TelemetryData, ParseError> parse_telemetry(std::span<const uint8_t> frame) noexcept {
    if (frame.size() < FRAME_SIZE) {
        return std::unexpected(ParseError::BufferTooSmall);
    }

    if (frame[0] != FRAME_MAGIC) {
        return std::unexpected(ParseError::InvalidMagic);
    }

    if (frame[1] != FRAME_VERSION) {
        return std::unexpected(ParseError::UnsupportedVersion);
    }

    auto payload = frame.subspan(0, 14);
    uint16_t expected_crc = read_be16(std::span<const uint8_t, 2>(&frame[14], 2));
    uint16_t actual_crc = crc16_ccitt(payload);

    if (expected_crc != actual_crc) {
        return std::unexpected(ParseError::CrcMismatch);
    }

    TelemetryData res{};
    res.device_id    = read_be32(std::span<const uint8_t, 4>(&frame[2], 4));
    res.seq_num      = read_be16(std::span<const uint8_t, 2>(&frame[6], 2));
    res.raw_pulses   = read_be32(std::span<const uint8_t, 4>(&frame[8], 4));
    res.battery_raw  = frame[12];

    uint8_t flags    = frame[13];
    res.tamper_alarm = (flags & 0x01) != 0;
    res.reverse_flow = (flags & 0x02) != 0;

    return res;
}

std::expected<std::array<uint8_t, CMD_SIZE>, bool> build_command(uint8_t cmd_type, uint16_t param) noexcept {
    std::array<uint8_t, CMD_SIZE> out{};
    out[0] = CMD_MAGIC;
    out[1] = cmd_type;
    write_be16(std::span<uint8_t, 2>(&out[2], 2), param);

    uint16_t crc = crc16_ccitt(std::span<const uint8_t>(out.data(), 4));
    write_be16(std::span<uint8_t, 2>(&out[4], 2), crc);

    return out;
}

} // namespace legacy_v1
