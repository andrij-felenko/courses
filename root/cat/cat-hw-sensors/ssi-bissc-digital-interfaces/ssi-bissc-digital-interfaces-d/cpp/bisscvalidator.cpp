// Перевірка CRC-6 стандарту BiSS-C (C++)
#include <cstdint>

class BiSSCValidator {
public:
    static bool verifyCrc6(uint64_t frameData, uint8_t bitCount, uint8_t expectedCrc) noexcept {
        uint8_t crc = 0x00;
        for (int i = static_cast<int>(bitCount) - 1; i >= 0; --i) {
            const uint8_t bit = static_cast<uint8_t>((frameData >> i) & 1U);
            const uint8_t crcMsb = (crc >> 5U) & 1U;
            crc = static_cast<uint8_t>((crc << 1U) & 0x3FU);
            if ((crcMsb ^ bit) != 0U) {
                crc ^= 0x03U;
            }
        }
        return (crc ^ 0x3FU) == expectedCrc;
    }
};
