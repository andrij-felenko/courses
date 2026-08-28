#include <stdint.h>
#include <stdbool.h>

// Розрахунок CRC-8 з поліномом 0x31 (x^8 + x^5 + x^4 + 1), типовим для давачів Sensirion
uint8_t calculate_crc8_sensirion(const uint8_t *data, uint8_t len) {
    uint8_t crc = 0xFF; // Початкове значення
    for (uint8_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x31);
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

// Перевірка цілісності пакета температури й вологості (2 байти даних + 1 байт CRC)
bool parse_sensirion_word(const uint8_t packet[3], uint16_t *out_val) {
    if (calculate_crc8_sensirion(packet, 2) != packet[2]) {
        return false; // Пакет спотворений завадою на шині!
    }
    *out_val = ((uint16_t)packet[0] << 8) | packet[1];
    return true;
}
