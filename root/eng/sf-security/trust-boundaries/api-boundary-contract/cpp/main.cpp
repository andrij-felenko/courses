#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <expected>
#include <array>
#include <string_view>

namespace security::boundary {

inline constexpr uint16_t kMagic = 0x5345;
inline constexpr uint16_t kVersion = 1;
inline constexpr size_t kMaxPayload = 4096;

enum class GatewayError : uint16_t {
    Ok = 0,
    BadMagic,
    UnsupportedVersion,
    PayloadTooLarge,
    ChecksumMismatch,
    SchemaViolation,
    CanonicalizationFail,
    AccessDenied
};

#pragma pack(push, 1)
struct FrameHeader {
    uint16_t magic{kMagic};
    uint16_t version{kVersion};
    uint16_t opcode{0};
    uint16_t flags{0};
    uint32_t sequence_id{0};
    uint32_t payload_len{0};
};
#pragma pack(pop)

struct ValidatedMessage {
    FrameHeader header{};
    std::array<uint8_t, kMaxPayload> payload{};
    uint32_t checksum{0};
};

class [[nodiscard]] BoundaryValidator {
public:
    static std::expected<ValidatedMessage, GatewayError> validate(std::span<const uint8_t> raw_data) noexcept {
        if (raw_data.size() < sizeof(FrameHeader) + sizeof(uint32_t)) {
            return std::unexpected(GatewayError::SchemaViolation);
        }

        // Атомарне зчитування заголовка
        FrameHeader hdr{};
        std::memcpy(&hdr, raw_data.data(), sizeof(FrameHeader));

        if (hdr.magic != kMagic) {
            return std::unexpected(GatewayError::BadMagic);
        }
        if (hdr.version != kVersion) {
            return std::unexpected(GatewayError::UnsupportedVersion);
        }
        if (hdr.payload_len > kMaxPayload) {
            return std::unexpected(GatewayError::PayloadTooLarge);
        }

        const size_t total_size = sizeof(FrameHeader) + hdr.payload_len + sizeof(uint32_t);
        if (raw_data.size() < total_size) {
            return std::unexpected(GatewayError::SchemaViolation);
        }

        // Перевірка контрольної суми
        const uint32_t computed_crc = calculate_crc32(raw_data.subspan(0, sizeof(FrameHeader) + hdr.payload_len));
        uint32_t packet_crc{0};
        std::memcpy(&packet_crc, raw_data.data() + sizeof(FrameHeader) + hdr.payload_len, sizeof(uint32_t));

        if (computed_crc != packet_crc) {
            return std::unexpected(GatewayError::ChecksumMismatch);
        }

        ValidatedMessage msg{};
        msg.header = hdr;
        std::memcpy(msg.payload.data(), raw_data.data() + sizeof(FrameHeader), hdr.payload_len);
        msg.checksum = packet_crc;

        return msg;
    }

private:
    static uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int i = 0; i < 8; ++i) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
        }
        return ~crc;
    }
};

} // namespace security::boundary
