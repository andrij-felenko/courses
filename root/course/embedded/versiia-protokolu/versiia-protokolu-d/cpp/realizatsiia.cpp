#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <expected>
#include <array>

namespace protocol {

constexpr uint8_t MAGIC_0 = 0xAA;
constexpr uint8_t MAGIC_1 = 0x55;
constexpr uint8_t CURRENT_MAJOR = 1;
constexpr uint8_t SUPPORTED_INCOMPAT_MASK = 0x01;

#pragma pack(push, 1)
struct FrameHeader {
    std::array<uint8_t, 2> magic;
    uint8_t ver_major;
    uint8_t ver_minor;
    uint8_t incompat_flags;
    uint8_t compat_flags;
    uint8_t msg_type;
    uint8_t payload_len;
};
#pragma pack(pop)

enum class ParseError {
    BadMagic,
    UnsupportedMajor,
    UnknownIncompatFlag,
    BufferUnderflow,
    PayloadTruncated
};

struct ParsedTelemetry {
    uint16_t voltage_mv{0};
    int32_t  current_ma{0};
    std::optional<int16_t> temperature_c{std::nullopt};
};

class VersionedMessageParser {
public:
    static std::expected<ParsedTelemetry, ParseError> 
    parse_telemetry(std::span<const uint8_t> frame_bytes) {
        if (frame_bytes.size() < sizeof(FrameHeader)) {
            return std::unexpected(ParseError::BufferUnderflow);
        }

        const auto* hdr = reinterpret_cast<const FrameHeader*>(frame_bytes.data());
        
        if (hdr->magic[0] != MAGIC_0 || hdr->magic[1] != MAGIC_1) {
            return std::unexpected(ParseError::BadMagic);
        }

        if (hdr->ver_major != CURRENT_MAJOR) {
            return std::unexpected(ParseError::UnsupportedMajor);
        }

        if ((hdr->incompat_flags & ~SUPPORTED_INCOMPAT_MASK) != 0) {
            return std::unexpected(ParseError::UnknownIncompatFlag);
        }

        const size_t total_expected = sizeof(FrameHeader) + hdr->payload_len;
        if (frame_bytes.size() < total_expected) {
            return std::unexpected(ParseError::PayloadTruncated);
        }

        auto payload = frame_bytes.subspan(sizeof(FrameHeader), hdr->payload_len);
        
        // Перевірка мінімального розміру v1.0 (6 байтів)
        if (payload.size() < 6) {
            return std::unexpected(ParseError::PayloadTruncated);
        }

        ParsedTelemetry result;
        result.voltage_mv = static_cast<uint16_t>(payload[0] | (payload[1] << 8));
        
        uint32_t raw_curr = static_cast<uint32_t>(payload[2]) |
                            (static_cast<uint32_t>(payload[3]) << 8) |
                            (static_cast<uint32_t>(payload[4]) << 16) |
                            (static_cast<uint32_t>(payload[5]) << 24);
        result.current_ma = static_cast<int32_t>(raw_curr);

        // Перевірка наявності поля v1.1
        if (payload.size() >= 8) {
            uint16_t raw_temp = static_cast<uint16_t>(payload[6] | (payload[7] << 8));
            result.temperature_c = static_cast<int16_t>(raw_temp);
        }

        return result;
    }
};

} // namespace protocol
