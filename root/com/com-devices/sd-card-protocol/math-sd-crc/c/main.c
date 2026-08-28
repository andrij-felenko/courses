#include <stdint.h>
#include <stddef.h>

// Розрахунок 7-бітного CRC7 для масиву байтів (поліном x^7 + x^3 + 1)
uint8_t sd_crc7(const uint8_t *data, size_t len) {
    uint8_t crc = 0;
    for (size_t i = 0; i < len; ++i) {
        uint8_t byte = data[i];
        for (int bit = 0; bit < 8; ++bit) {
            crc <<= 1;
            if ((byte ^ crc) & 0x80) {
                crc ^= 0x09; // 0x89 без старшого біта x^7
            }
            byte <<= 1;
        }
    }
    return (crc & 0x7F);
}

// Розрахунок 16-бітного CRC16-CCITT для одиночного бітового потоку
uint16_t sd_crc16_byte_stream(const uint8_t *data, size_t len) {
    uint16_t crc = 0x0000;
    for (size_t i = 0; i < len; ++i) {
        uint8_t byte = data[i];
        for (int bit = 0; bit < 8; ++bit) {
            uint16_t inv = ((byte >> (7 - bit)) & 1) ^ ((crc >> 15) & 1);
            crc <<= 1;
            if (inv) {
                crc ^= 0x1021;
            }
        }
    }
    return crc;
}

// Одночасний розрахунок 4 незалежних CRC16 для ліній DAT0..DAT3
void sd_crc16_4bit_block(const uint8_t *block_512b, uint16_t crc_out[4]) {
    for (int lane = 0; lane < 4; ++lane) {
        crc_out[lane] = 0x0000;
    }

    for (size_t i = 0; i < 512; ++i) {
        uint8_t byte = block_512b[i];
        uint8_t high_nibble = byte >> 4;
        uint8_t low_nibble = byte & 0x0F;

        // Обробка старшого нібла
        for (int lane = 0; lane < 4; ++lane) {
            uint16_t bit = (high_nibble >> lane) & 0x01;
            uint16_t inv = bit ^ ((crc_out[lane] >> 15) & 1);
            crc_out[lane] <<= 1;
            if (inv) {
                crc_out[lane] ^= 0x1021;
            }
        }

        // Обробка молодшого нібла
        for (int lane = 0; lane < 4; ++lane) {
            uint16_t bit = (low_nibble >> lane) & 0x01;
            uint16_t inv = bit ^ ((crc_out[lane] >> 15) & 1);
            crc_out[lane] <<= 1;
            if (inv) {
                crc_out[lane] ^= 0x1021;
            }
        }
    }
}
