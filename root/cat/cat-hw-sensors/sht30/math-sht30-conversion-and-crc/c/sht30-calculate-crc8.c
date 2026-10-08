#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SHT30_CRC8_POLYNOMIAL 0x31
#define SHT30_CRC8_INIT       0xFF

// Обчислення CRC-8 для масиву байтів SHT30
uint8_t sht30_calculate_crc8(const uint8_t *data, size_t length) {
    uint8_t crc = SHT30_CRC8_INIT;
    
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ SHT30_CRC8_POLYNOMIAL;
            } else {
                crc = (crc << 1);
            }
        }
    }
    
    return crc;
}

// Верифікація 2-байтового слова та його контрольної суми
bool sht30_verify_crc8(uint8_t msb, uint8_t lsb, uint8_t checksum) {
    uint8_t buffer[2] = {msb, lsb};
    uint8_t calculated_crc = sht30_calculate_crc8(buffer, 2);
    return (calculated_crc == checksum);
}
