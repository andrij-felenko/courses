#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

uint16_t iso14443a_crc16(const uint8_t *data, size_t len) {
    uint16_t w_crc = 0x6363; // Початкове значення за ISO 14443-A

    for (size_t i = 0; i < len; i++) {
        uint8_t byte = data[i];
        byte ^= (uint8_t)(w_crc & 0x00FF);
        byte ^= (byte << 4);
        w_crc = (w_crc >> 8) ^ ((uint16_t)byte << 8) ^ ((uint16_t)byte << 3) ^ ((uint16_t)byte >> 4);
    }

    return w_crc;
}

void iso14443a_append_crc(uint8_t *buffer, size_t *len) {
    uint16_t crc = iso14443a_crc16(buffer, *len);
    buffer[*len] = (uint8_t)(crc & 0xFF);         // LSB першим
    buffer[*len + 1] = (uint8_t)((crc >> 8) & 0xFF); // MSB другим
    *len += 2;
}

bool iso14443a_check_crc(const uint8_t *buffer, size_t len) {
    if (len < 2) return false;
    uint16_t calc_crc = iso14443a_crc16(buffer, len - 2);
    uint16_t recv_crc = (uint16_t)buffer[len - 2] | ((uint16_t)buffer[len - 1] << 8);
    return calc_crc == recv_crc;
}
