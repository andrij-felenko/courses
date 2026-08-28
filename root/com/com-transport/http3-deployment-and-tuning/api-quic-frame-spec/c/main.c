#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Кодування цілого числа у формат QUIC Varint */
size_t quic_varint_encode(uint64_t val, uint8_t *out) {
    if (val <= 63) {
        out[0] = (uint8_t)(val & 0x3F);
        return 1;
    } else if (val <= 16383) {
        out[0] = (uint8_t)(((val >> 8) & 0x3F) | 0x40);
        out[1] = (uint8_t)(val & 0xFF);
        return 2;
    } else if (val <= 1073741823) {
        out[0] = (uint8_t)(((val >> 24) & 0x3F) | 0x80);
        out[1] = (uint8_t)((val >> 16) & 0xFF);
        out[2] = (uint8_t)((val >> 8) & 0xFF);
        out[3] = (uint8_t)(val & 0xFF);
        return 4;
    } else if (val <= 4611686018427387903ULL) {
        out[0] = (uint8_t)(((val >> 56) & 0x3F) | 0xC0);
        out[1] = (uint8_t)((val >> 48) & 0xFF);
        out[2] = (uint8_t)((val >> 40) & 0xFF);
        out[3] = (uint8_t)((val >> 32) & 0xFF);
        out[4] = (uint8_t)((val >> 24) & 0xFF);
        out[5] = (uint8_t)((val >> 16) & 0xFF);
        out[6] = (uint8_t)((val >> 8) & 0xFF);
        out[7] = (uint8_t)(val & 0xFF);
        return 8;
    }
    return 0; /* Число перевищує 62 біти */
}

/* Декодування QUIC Varint з бувера */
bool quic_varint_decode(const uint8_t *in, size_t in_len, uint64_t *val, size_t *read_bytes) {
    if (in_len == 0) return false;

    uint8_t prefix = (in[0] >> 6) & 0x03;
    size_t len = 1ULL << prefix;

    if (in_len < len) return false;

    uint64_t result = in[0] & 0x3F;
    for (size_t i = 1; i < len; i++) {
        result = (result << 8) | in[i];
    }

    *val = result;
    *read_bytes = len;
    return true;
}
