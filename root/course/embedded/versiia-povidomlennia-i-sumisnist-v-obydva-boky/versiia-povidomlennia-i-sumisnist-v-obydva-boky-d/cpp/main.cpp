#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <optional>
#include <bitset>

namespace iot_protocol {

inline constexpr uint8_t PROTO_MAGIC_BYTE0     = 0xAA;
inline constexpr uint8_t PROTO_MAGIC_BYTE1     = 0x55;
inline constexpr uint8_t PROTO_SUPPORTED_MAJOR = 1;
inline constexpr uint8_t TAG_CRITICAL_FLAG     = 0x80;

enum class Tag : uint8_t {
    NodeId      = 0x01,  // uint32_t (4 байти)
    Temperature = 0x02,  // int32_t  (4 байти, міліградуси)
    Humidity    = 0x03,  // uint16_t (2 байти, 0.01 %)
    Voltage     = 0x04,  // uint16_t (2 байти, мВ)
    SoilEc      = 0x05,  // uint16_t (2 байти, мкСм/см)
    GpsPos      = 0x06   // int32_t lat, int32_t lon (8 байтів)
};

enum class ParseError {
    BufferTooSmall,
    InvalidMagic,
    UnsupportedMajorVersion,
    HeaderCrcMismatch,
    PayloadTruncated,
    TagLengthOverflow,
    TagValueMalformed,
    UnknownCriticalTag,
    MandatoryFieldMissing
};

struct GpsCoordinates {
    int32_t latitude_1e7{0};
    int32_t longitude_1e7{0};
};

struct TelemetryMessage {
    uint32_t node_id{0};
    std::optional<int32_t>        temperature_mc{};
    std::optional<uint16_t>       humidity_cpercent{};
    std::optional<uint16_t>       battery_mv{};
    std::optional<uint16_t>       soil_ec_us_cm{};
    std::optional<GpsCoordinates> gps_position{};

    uint16_t unknown_tags_skipped{0};
};

// Обчислення контрольної суми CRC-8
[[nodiscard]] constexpr uint8_t crc8(std::span<const uint8_t> data) noexcept {
    uint8_t crc = 0x00;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ 0x07) : static_cast<uint8_t>(crc << 1);
        }
    }
    return crc;
}

// Безпечне читання Little-Endian без невирівняного доступу до пам'яті
[[nodiscard]] constexpr uint16_t read_u16_le(const uint8_t* p) noexcept {
    return static_cast<uint16_t>(p[0] | (static_cast<uint16_t>(p[1]) << 8));
}

[[nodiscard]] constexpr uint32_t read_u32_le(const uint8_t* p) noexcept {
    return static_cast<uint32_t>(p[0])
         | (static_cast<uint32_t>(p[1]) << 8)
         | (static_cast<uint32_t>(p[2]) << 16)
         | (static_cast<uint32_t>(p[3]) << 24);
}

[[nodiscard]] constexpr int32_t read_i32_le(const uint8_t* p) noexcept {
    return static_cast<int32_t>(read_u32_le(p));
}

// Головна функція декодера у стилі сучасного C++20
[[nodiscard]] std::expected<TelemetryMessage, ParseError> parse_telemetry(
    std::span<const uint8_t> packet
) noexcept {
    constexpr size_t HEADER_SIZE = 8;
    if (packet.size() < HEADER_SIZE) {
        return std::unexpected(ParseError::BufferTooSmall);
    }

    // 1. Валідація магічних байтів
    if (packet[0] != PROTO_MAGIC_BYTE0 || packet[1] != PROTO_MAGIC_BYTE1) {
        return std::unexpected(ParseError::InvalidMagic);
    }

    // 2. Звірка контрольної суми заголовка
    const uint8_t expected_crc = packet[7];
    if (crc8(packet.subspan(0, 7)) != expected_crc) {
        return std::unexpected(ParseError::HeaderCrcMismatch);
    }

    // 3. Перевірка мажорної версії
    const uint8_t major_version = (packet[2] >> 4) & 0x0F;
    if (major_version != PROTO_SUPPORTED_MAJOR) {
        return std::unexpected(ParseError::UnsupportedMajorVersion);
    }

    // 4. Валідація довжини навантаження
    const uint16_t payload_len = read_u16_le(&packet[5]);
    if (packet.size() < (HEADER_SIZE + payload_len)) {
        return std::unexpected(ParseError::PayloadTruncated);
    }

    TelemetryMessage msg{};
    bool has_node_id = false;

    // Зріз виключно корисного навантаження (без копіювання байтів)
    auto payload = packet.subspan(HEADER_SIZE, payload_len);
    size_t cursor = 0;

    while (cursor < payload.size()) {
        if ((payload.size() - cursor) < 2) {
            return std::unexpected(ParseError::TagLengthOverflow);
        }

        const uint8_t raw_tag = payload[cursor++];
        const uint8_t tag_len = payload[cursor++];

        if (tag_len > (payload.size() - cursor)) {
            return std::unexpected(ParseError::TagLengthOverflow);
        }

        const uint8_t* val = &payload[cursor];
        const bool is_critical = (raw_tag & TAG_CRITICAL_FLAG) != 0;
        const auto clean_tag = static_cast<Tag>(raw_tag & ~TAG_CRITICAL_FLAG);

        switch (clean_tag) {
            case Tag::NodeId:
                if (tag_len != 4) return std::unexpected(ParseError::TagValueMalformed);
                msg.node_id = read_u32_le(val);
                has_node_id = true;
                break;

            case Tag::Temperature:
                if (tag_len != 4) return std::unexpected(ParseError::TagValueMalformed);
                msg.temperature_mc = read_i32_le(val);
                break;

            case Tag::Humidity:
                if (tag_len != 2) return std::unexpected(ParseError::TagValueMalformed);
                msg.humidity_cpercent = read_u16_le(val);
                break;

            case Tag::Voltage:
                if (tag_len != 2) return std::unexpected(ParseError::TagValueMalformed);
                msg.battery_mv = read_u16_le(val);
                break;

            case Tag::SoilEc:
                if (tag_len != 2) return std::unexpected(ParseError::TagValueMalformed);
                msg.soil_ec_us_cm = read_u16_le(val);
                break;

            case Tag::GpsPos:
                if (tag_len != 8) return std::unexpected(ParseError::TagValueMalformed);
                msg.gps_position = GpsCoordinates{
                    .latitude_1e7 = read_i32_le(val),
                    .longitude_1e7 = read_i32_le(val + 4)
                };
                break;

            default:
                if (is_critical) {
                    return std::unexpected(ParseError::UnknownCriticalTag);
                }
                msg.unknown_tags_skipped++;
                break;
        }

        cursor += tag_len;
    }

    if (!has_node_id) {
        return std::unexpected(ParseError::MandatoryFieldMissing);
    }

    return msg;
}

} // namespace iot_protocol
