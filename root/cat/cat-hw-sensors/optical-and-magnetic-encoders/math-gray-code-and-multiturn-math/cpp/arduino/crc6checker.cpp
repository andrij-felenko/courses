#include <Arduino.h>

class CRC6Checker {
private:
    static const uint8_t POLY = 0x43; // x^6 + x + 1

public:
    static uint8_t compute(uint32_t data, uint8_t bitLen) {
        uint32_t poly = static_cast<uint32_t>(POLY) << (bitLen - 6);
        uint32_t code = data << 6;
        uint32_t mask = 1U << (bitLen + 5);

        for (uint8_t i = 0; i < bitLen; i++) {
            if (code & mask) {
                code ^= poly;
            }
            poly >>= 1;
            mask >>= 1;
        }
        return static_cast<uint8_t>(code & 0x3F);
    }

    static bool validate(uint32_t data, uint8_t dataBits, uint8_t expectedCRC) {
        return compute(data, dataBits) == expectedCRC;
    }
};
