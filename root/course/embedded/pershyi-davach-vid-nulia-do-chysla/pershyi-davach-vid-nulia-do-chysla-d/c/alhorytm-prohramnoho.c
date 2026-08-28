#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SHT3X_CRC8_POLYNOMIAL  0x31
#define SHT3X_CRC8_INIT        0xFF

uint8_t sht3x_calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = SHT3X_CRC8_INIT;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ SHT3X_CRC8_POLYNOMIAL);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

bool sht3x_validate_crc(const uint8_t *data_2bytes, uint8_t expected_crc) {
    return sht3x_calculate_crc8(data_2bytes, 2) == expected_crc;
}
