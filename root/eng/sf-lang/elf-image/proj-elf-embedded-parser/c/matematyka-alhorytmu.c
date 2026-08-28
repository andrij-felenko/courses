#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

uint64_t decode_uleb128_c(const uint8_t* data, size_t max_len, size_t* out_bytes_read) {
    uint64_t result = 0;
    uint32_t shift = 0;
    size_t count = 0;

    while (count < max_len) {
        uint8_t byte = data[count++];
        result |= ((uint64_t)(byte & 0x7F)) << shift;
        if ((byte & 0x80) == 0) {
            break;
        }
        shift += 7;
        if (shift >= 64) {
            /* Захист від нескінченного циклу при пошкоджених даних */
            break;
        }
    }

    if (out_bytes_read) *out_bytes_read = count;
    return result;
}
