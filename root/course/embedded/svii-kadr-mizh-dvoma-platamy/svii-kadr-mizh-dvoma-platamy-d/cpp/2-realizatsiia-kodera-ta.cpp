namespace protocol {

enum class CodecError {
    InvalidInput,
    BufferTooSmall,
    CorruptedZeroInside,
    OffsetOutOfBounds
};

// Безпечне кодування COBS у вихідний span
inline std::expected<size_t, CodecError> cobs_encode(
    std::span<const uint8_t> src, 
    std::span<uint8_t> dst) noexcept 
{
    if (src.empty()) return std::unexpected(CodecError::InvalidInput);
    if (dst.size() < src.size() + (src.size() / 254) + 1) {
        return std::unexpected(CodecError::BufferTooSmall);
    }

    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 1;

    while (read_idx < src.size()) {
        if (src[read_idx] == 0x00) {
            dst[code_idx] = code;
            code_idx = write_idx++;
            code = 1;
            read_idx++;
        } else {
            dst[write_idx++] = src[read_idx++];
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code_idx = write_idx++;
                code = 1;
            }
        }
    }
    dst[code_idx] = code;
    return write_idx;
}

// Декодування COBS (підтримує in-place розпакування)
inline std::expected<size_t, CodecError> cobs_decode(
    std::span<const uint8_t> src, 
    std::span<uint8_t> dst) noexcept 
{
    if (src.empty()) return std::unexpected(CodecError::InvalidInput);

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < src.size()) {
        uint8_t code = src[read_idx++];
        if (code == 0) return std::unexpected(CodecError::CorruptedZeroInside);

        for (uint8_t i = 1; i < code; ++i) {
            if (read_idx >= src.size() || write_idx >= dst.size()) {
                return std::unexpected(CodecError::OffsetOutOfBounds);
            }
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFF && read_idx < src.size()) {
            if (write_idx >= dst.size()) return std::unexpected(CodecError::BufferTooSmall);
            dst[write_idx++] = 0x00;
        }
    }
    return write_idx;
}

} // namespace protocol
