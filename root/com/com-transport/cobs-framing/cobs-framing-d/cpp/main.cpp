#include <span>
#include <cstdint>
#include <cstddef>
#include <optional>
#include <expected>

namespace cobs {

enum class DecodeError {
    EmptyBuffer,
    ZeroInsidePayload,
    OffsetOutOfBounds,
    BufferOverflow
};

/**
 * Безпечне кодування COBS із використанням std::span.
 */
[[nodiscard]] size_t encode(std::span<const uint8_t> src, std::span<uint8_t> dst) noexcept {
    if (src.empty() || dst.empty()) return 0;

    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 0x01;

    for (uint8_t byte : src) {
        if (byte == 0) {
            dst[code_idx] = code;
            code_idx = write_idx++;
            code = 0x01;
        } else {
            dst[write_idx++] = byte;
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code_idx = write_idx++;
                code = 0x01;
            }
        }
    }
    dst[code_idx] = code;
    return write_idx;
}

/**
 * Ідіоматичне декодування COBS у C++23 через std::expected.
 */
[[nodiscard]] std::expected<size_t, DecodeError> decode(
    std::span<const uint8_t> src, 
    std::span<uint8_t> dst
) noexcept {
    if (src.empty()) return std::unexpected(DecodeError::EmptyBuffer);

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < src.size()) {
        const uint8_t code = src[read_idx++];
        if (code == 0) return std::unexpected(DecodeError::ZeroInsidePayload);

        const size_t copy_len = code - 1;
        if (read_idx + copy_len > src.size()) {
            return std::unexpected(DecodeError::OffsetOutOfBounds);
        }
        if (write_idx + copy_len > dst.size()) {
            return std::unexpected(DecodeError::BufferOverflow);
        }

        for (size_t i = 0; i < copy_len; ++i) {
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFF && read_idx < src.size()) {
            if (write_idx >= dst.size()) return std::unexpected(DecodeError::BufferOverflow);
            dst[write_idx++] = 0x00;
        }
    }

    return write_idx;
}

} // namespace cobs
