[[nodiscard]] constexpr uint32_t crc32_bitwise(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (const uint8_t byte : data) {
        crc ^= static_cast<uint32_t>(byte);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 1U) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
        }
    }
    return crc ^ 0xFFFFFFFFU;
}
