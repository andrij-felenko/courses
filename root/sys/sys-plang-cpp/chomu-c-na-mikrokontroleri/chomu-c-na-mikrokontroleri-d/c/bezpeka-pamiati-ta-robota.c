/* Обробка буфера мовою C через сирі покажчики */
#include <stdint.h>
#include <stdbool.h>

bool parse_frame_c(const uint8_t* buffer, uint32_t size, uint16_t* out_crc) {
    if (!buffer || size < 4) {
        return false;
    }
    *out_crc = (uint16_t)((buffer[size - 2] << 8) | buffer[size - 1]);
    return true;
}
