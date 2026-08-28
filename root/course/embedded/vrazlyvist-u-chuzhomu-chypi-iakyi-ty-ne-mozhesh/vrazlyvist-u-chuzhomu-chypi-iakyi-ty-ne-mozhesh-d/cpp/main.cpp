#include <cstdint>
#include <span>
#include <expected>
#include <array>
#include <algorithm>

namespace embedded::protocol {

inline constexpr uint8_t  MAGIC_BYTE        = 0x5AU;
inline constexpr size_t   MAX_PAYLOAD_SIZE  = 128U;

enum class ParseError : uint8_t {
    InvalidHeader,
    BufferOverflow,
    ChecksumMismatch
};

#pragma pack(push, 1)
struct SecureFrameHeader {
    uint8_t  magic;
    uint8_t  sequence;
    uint16_t length;
};
#pragma pack(pop)

uint32_t compute_crc32(std::span<const uint8_t> data) noexcept;

class SafeFrameParser {
public:
    static std::expected<std::span<const uint8_t>, ParseError> parse(
        std::span<const uint8_t> raw_stream) noexcept {
        
        constexpr size_t min_header_size = sizeof(SecureFrameHeader) + sizeof(uint32_t);
        if (raw_stream.size() < min_header_size) {
            return std::unexpected(ParseError::InvalidHeader);
        }

        const auto* header = reinterpret_cast<const SecureFrameHeader*>(raw_stream.data());
        if (header->magic != MAGIC_BYTE) {
            return std::unexpected(ParseError::InvalidHeader);
        }

        if (header->length > MAX_PAYLOAD_SIZE || 
            header->length > (raw_stream.size() - min_header_size)) {
            return std::unexpected(ParseError::BufferOverflow);
        }

        const size_t total_frame_len = sizeof(SecureFrameHeader) + header->length + sizeof(uint32_t);
        if (raw_stream.size() < total_frame_len) {
            return std::unexpected(ParseError::InvalidHeader);
        }

        auto body_span = raw_stream.subspan(0, total_frame_len - sizeof(uint32_t));
        uint32_t expected_crc = compute_crc32(body_span);

        uint32_t received_crc = 0;
        std::copy_n(raw_stream.data() + total_frame_len - sizeof(uint32_t), sizeof(uint32_t),
                    reinterpret_cast<uint8_t*>(&received_crc));

        if (received_crc != expected_crc) {
            return std::unexpected(ParseError::ChecksumMismatch);
        }

        return raw_stream.subspan(sizeof(SecureFrameHeader), header->length);
    }
};

} // namespace embedded::protocol
