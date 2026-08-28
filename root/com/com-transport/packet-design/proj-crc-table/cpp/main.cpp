#include <stdint.h>
#include <stddef.h>

uint8_t crc8_table[256];

// Заповнити таблицю один раз на старті (поліном 0x07)
void crc8_init(void) {
    for (int i = 0; i < 256; i++) {
        uint8_t crc = (uint8_t)i;
        for (int b = 0; b < 8; b++)
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x07)
                               : (uint8_t)(crc << 1);
        crc8_table[i] = crc;
    }
}
