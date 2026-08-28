#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace legacy_ingress {

constexpr uint8_t MAGIC_BYTE   = 0xAA;
constexpr uint8_t PROTOCOL_VER = 0x01;
constexpr size_t  FRAME_LENGTH = 16;

struct MeterTelemetry {
    uint32_t device_id{};
    uint16_t sequence_id{};
    uint32_t pulse_count{};
    uint8_t  battery_code{};
    bool     tamper_triggered{};
    bool     reverse_flow_flag{};
};

enum class DecodeError {
    FrameTooShort,
    BadMagicPreamble,
    VersionMismatch,
    ChecksumMismatch
};

/* Обчислення CRC-16 під час компіляції або виконання */
constexpr uint16_t compute_crc16(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

std::expected<MeterTelemetry, DecodeError> decode_frame(std::span<const uint8_t> frame) noexcept {
    if (frame.size() < FRAME_LENGTH) {
        return std::unexpected(DecodeError::FrameTooShort);
    }

    if (frame[0] != MAGIC_BYTE) {
        return std::unexpected(DecodeError::BadMagicPreamble);
    }

    if (frame[1] != PROTOCOL_VER) {
        return std::unexpected(DecodeError::VersionMismatch);
    }

    uint16_t received_crc = static_cast<uint16_t>((frame[14] << 8) | frame[15]);
    uint16_t computed_crc = compute_crc16(frame.subspan(0, 14));

    if (received_crc != computed_crc) {
        return std::unexpected(DecodeError::ChecksumMismatch);
    }

    MeterTelemetry record{};
    record.device_id = (static_cast<uint32_t>(frame[2]) << 24) |
                       (static_cast<uint32_t>(frame[3]) << 16) |
                       (static_cast<uint32_t>(frame[4]) << 8)  |
                       (static_cast<uint32_t>(frame[5]));

    record.sequence_id = static_cast<uint16_t>((frame[6] << 8) | frame[7]);

    record.pulse_count = (static_cast<uint32_t>(frame[8]) << 24) |
                         (static_cast<uint32_t>(frame[9]) << 16) |
                         (static_cast<uint32_t>(frame[10]) << 8) |
                         (static_cast<uint32_t>(frame[11]));

    record.battery_code = frame[12];
    
    uint8_t flags = frame[13];
    record.tamper_triggered  = (flags & 0x01) != 0;
    record.reverse_flow_flag = (flags & 0x02) != 0;

    return record;
}

} // namespace legacy_ingress
