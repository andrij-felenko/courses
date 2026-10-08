#include <cstdint>
#include <cstddef>
#include <array>

class SHT30Checksum {
public:
    static constexpr uint8_t POLYNOMIAL = 0x31;
    static constexpr uint8_t INIT_VALUE = 0xFF;

    // Обчислення CRC-8 для двох байтів даних SHT30
    static uint8_t calculate(uint8_t msb, uint8_t lsb) noexcept {
        const std::array<uint8_t, 2> bytes{msb, lsb};
        uint8_t crc = INIT_VALUE;

        for (const uint8_t byte : bytes) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if ((crc & 0x80) != 0) {
                    crc = static_cast<uint8_t>((crc << 1) ^ POLYNOMIAL);
                } else {
                    crc = static_cast<uint8_t>(crc << 1);
                }
            }
        }
        return crc;
    }

    // Перевірка відповідності прийнятої контрольної суми
    static bool verify(uint8_t msb, uint8_t lsb, uint8_t expected_crc) noexcept {
        return calculate(msb, lsb) == expected_crc;
    }
};
