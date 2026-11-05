#include <cstdint>

class EncoderDecoder {
public:
    static uint32_t grayToBinary(uint32_t gray) {
        uint32_t mask = gray >> 1;
        while (mask != 0) {
            gray ^= mask;
            mask >>= 1;
        }
        return gray;
    }

    static bool verifyCRC(const uint8_t* frame, uint8_t length, uint8_t expected_crc) {
        uint8_t calculated = 0;
        // Спрощена реалізація перевірки CRC-8 для кадру даних
        for (uint8_t i = 0; i < length; ++i) {
            calculated ^= frame[i];
            for (uint8_t j = 0; j < 8; ++j) {
                if (calculated & 0x80) {
                    calculated = (calculated << 1) ^ 0x1D;
                } else {
                    calculated <<= 1;
                }
            }
        }
        return calculated == expected_crc;
    }
};
