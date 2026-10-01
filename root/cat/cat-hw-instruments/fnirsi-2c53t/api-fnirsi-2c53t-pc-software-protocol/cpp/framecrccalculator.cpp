#include <cstdint>
#include <cstddef>
#include <vector>

class FrameCrcCalculator {
public:
    static uint16_t calculate(const uint8_t* data, size_t length) {
        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < length; ++i) {
            crc ^= data[i];
            for (int bit = 0; bit < 8; ++bit) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0xA001;
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }
};
