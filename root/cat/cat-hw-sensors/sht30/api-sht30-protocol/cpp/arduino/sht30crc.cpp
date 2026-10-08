#include <Arduino.h>

class SHT30CRC {
public:
    static uint8_t calculate(const uint8_t* data, size_t len) {
        uint8_t crc = 0xFF;
        for (size_t i = 0; i < len; i++) {
            crc ^= data[i];
            for (uint8_t bit = 0; bit < 8; bit++) {
                if (crc & 0x80) {
                    crc = (crc << 1) ^ 0x31;
                } else {
                    crc = (crc << 1);
                }
            }
        }
        return crc;
    }

    static bool verify(const uint8_t frame[6]) {
        return (calculate(&frame[0], 2) == frame[2]) &&
               (calculate(&frame[3], 2) == frame[5]);
    }
};
