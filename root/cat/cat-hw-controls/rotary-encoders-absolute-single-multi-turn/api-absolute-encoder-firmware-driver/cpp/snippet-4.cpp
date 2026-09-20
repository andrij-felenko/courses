template <typename T>
[[nodiscard]] constexpr T grayToBinary(T gray) noexcept {
    for (std::size_t shift = 1; shift < sizeof(T) * 8; shift <<= 1) {
        gray ^= (gray >> shift);
    }
    return gray;
}

// Обчислення CRC-6 BiSS-C
[[nodiscard]] constexpr uint8_t calcCrc6BiSS(uint64_t frame, uint8_t bitLen) noexcept {
    uint8_t crc = 0;
    for (int8_t i = static_cast<int8_t>(bitLen - 1); i >= 0; --i) {
        bool bit = (frame >> i) & 1;
        bool crcMsb = (crc >> 5) & 1;
        crc = (crc << 1) & 0x3F;
        if (bit ^ crcMsb) {
            crc ^= 0x03;
        }
    }
    return crc ^ 0x3F;
}
