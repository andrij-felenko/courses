#include <stdint.h>
#include <stddef.h>

// Побайтовий розрахунок CRC-16-CCITT для перевірки кінцевика CSI-2
uint16_t csi2_crc16_update(uint16_t crc, uint8_t byte) {
    crc ^= (uint16_t)((uint16_t)byte << 8);
    for (int i = 0; i < 8; i++) {
        if (crc & 0x8000) {
            crc = (uint16_t)((crc << 1) ^ 0x1021);
        } else {
            crc = (uint16_t)(crc << 1);
        }
    }
    return crc;
}

// Пакетний розрахунок контрольної суми над усім масивом Payload
uint16_t csi2_calc_payload_crc(const uint8_t *payload, size_t word_count) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < word_count; i++) {
        crc = csi2_crc16_update(crc, payload[i]);
    }
    return crc;
}
