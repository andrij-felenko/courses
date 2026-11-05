#include <stdint.h>

uint32_t GrayToBinary(uint32_t gray) {
    uint32_t binary = gray;
    while (gray >>= 1) {
        binary ^= gray;
    }
    return binary;
}

uint8_t CalculateCRC8(const uint8_t *data, uint8_t length) {
    uint8_t crc = 0x00; // початкове значення
    for (uint8_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t bit = 8; bit > 0; bit--) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07; // приклад породжувального полінома
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}
