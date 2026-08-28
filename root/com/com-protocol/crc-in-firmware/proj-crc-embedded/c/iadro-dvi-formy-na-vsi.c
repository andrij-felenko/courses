#include <stdint.h>
#include <stddef.h>

extern const uint16_t crc16_table[256];   /* CRC-16/CCITT-FALSE, поліном 0x1021 */
extern const uint32_t crc32_table[256];   /* CRC-32/ISO-HDLC, поліном 0xEDB88320 */

/* Невідбита форма: зсув ліворуч, з даними зустрічається СТАРШИЙ байт регістра. */
uint16_t crc16_update(uint16_t crc, const uint8_t *p, size_t n) {
    while (n--) {
        uint8_t idx = (uint8_t)((crc >> 8) ^ *p++);
        crc = (uint16_t)(crc << 8) ^ crc16_table[idx];
    }
    return crc;
}

/* Відбита форма: зсув праворуч, з даними зустрічається МОЛОДШИЙ байт регістра. */
uint32_t crc32_update(uint32_t crc, const uint8_t *p, size_t n) {
    while (n--) {
        uint8_t idx = (uint8_t)(crc ^ *p++);
        crc = (crc >> 8) ^ crc32_table[idx];
    }
    return crc;
}
