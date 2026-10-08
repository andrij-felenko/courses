// Перевірка CRC-6 стандарту BiSS-C (C)
#include <stdbool.h>
#include <stdint.h>

bool bissc_verify_crc6(uint64_t frame_data, uint8_t bit_count, uint8_t expected_crc) {
    uint8_t crc = 0x00;
    for (int i = (int)bit_count - 1; i >= 0; i--) {
        uint8_t bit = (uint8_t)((frame_data >> i) & 1U);
        uint8_t crc_msb = (crc >> 5) & 1U;
        crc = (uint8_t)((crc << 1) & 0x3FU);
        if (crc_msb ^ bit) {
            crc ^= 0x03U; // Поліном x^6 + x + 1
        }
    }
    return (crc ^ 0x3FU) == expected_crc;
}
