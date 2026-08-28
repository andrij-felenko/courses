#include <stdint.h>
#include <string.h>

// Безпечне вилучення 8-бітного беззнакового цілого
uint8_t unpack_u8(const uint8_t *buf, size_t offset) {
    return buf[offset];
}

// Безпечне вилучення 16-бітного цілого у форматі little-endian
uint16_t unpack_u16_le(const uint8_t *buf, size_t offset) {
    uint16_t val;
    memcpy(&val, &buf[offset], sizeof(uint16_t));
    return val;
}

// Безпечне вилучення 32-бітного цілого у форматі little-endian
uint32_t unpack_u32_le(const uint8_t *buf, size_t offset) {
    uint32_t val;
    memcpy(&val, &buf[offset], sizeof(uint32_t));
    return val;
}

// Безпечне вилучення 32-бітного дробового числа IEEE 754 float
float unpack_f32_le(const uint8_t *buf, size_t offset) {
    float val;
    memcpy(&val, &buf[offset], sizeof(float));
    return val;
}

// Безпечне вилучення 64-бітного цілого у форматі little-endian
uint64_t unpack_u64_le(const uint8_t *buf, size_t offset) {
    uint64_t val;
    memcpy(&val, &buf[offset], sizeof(uint64_t));
    return val;
}
