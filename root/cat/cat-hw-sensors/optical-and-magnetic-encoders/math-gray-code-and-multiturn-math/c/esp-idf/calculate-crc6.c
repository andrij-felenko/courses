#include <stdint.h>
#include <stdbool.h>

// Твірний поліном CRC-6: x^6 + x + 1 (0x43)
#define CRC6_POLY 0x43

uint8_t calculate_crc6(uint32_t data, uint8_t bit_len) {
    uint32_t poly = (uint32_t)CRC6_POLY << (bit_len - 6);
    uint32_t code = data << 6;
    uint32_t mask = 1U << (bit_len + 5);

    for (int i = 0; i < bit_len; i++) {
        if (code & mask) {
            code ^= poly;
        }
        poly >>= 1;
        mask >>= 1;
    }
    return (uint8_t)(code & 0x3F);
}

bool verify_encoder_frame(uint32_t frame_data, uint8_t data_bits, uint8_t received_crc) {
    uint8_t computed_crc = calculate_crc6(frame_data, data_bits);
    return computed_crc == received_crc;
}
