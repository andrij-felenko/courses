/* Бітовий покроковий розрахунок CRC-16-CCITT мовою C++ */
constexpr std::uint16_t crc16_bitwise(std::uint16_t crc, std::uint8_t byte) noexcept {
    crc ^= static_cast<std::uint16_t>(byte) << 8;
    for (int i = 0; i < 8; ++i) {
        if (crc & 0x8000U) {
            crc = (crc << 1) ^ 0x1021U;
        } else {
            crc = crc << 1;
        }
    }
    return crc;
}
