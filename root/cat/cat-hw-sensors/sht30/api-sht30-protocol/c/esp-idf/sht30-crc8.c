#include <stdint.h>
#include <stdbool.h>

// Обчислення CRC-8 для SHT30 з поліномом 0x31 та ініціалізацією 0xFF
uint8_t sht30_crc8(const uint8_t *data, size_t len) {
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

// Перевірка 6-байтного фрейму даних SHT30
bool sht30_validate_frame(const uint8_t frame[6]) {
    uint8_t temp_crc = sht30_crc8(&frame[0], 2);
    uint8_t hum_crc  = sht30_crc8(&frame[3], 2);
    return (temp_crc == frame[2]) && (hum_crc == frame[5]);
}
