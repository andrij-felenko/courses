// Запис 48-бітного числа в буфер (little-endian)
static inline void _mav_put_uint48_t(uint8_t *buf, uint64_t val) {
    buf[0] = (uint8_t)(val >> 0);
    buf[1] = (uint8_t)(val >> 8);
    buf[2] = (uint8_t)(val >> 16);
    buf[3] = (uint8_t)(val >> 24);
    buf[4] = (uint8_t)(val >> 32);
    buf[5] = (uint8_t)(val >> 40);
}

// Читання 48-бітного числа з буфера (little-endian)
static inline uint64_t _mav_get_uint48_t(const uint8_t *buf) {
    return ((uint64_t)buf[0])       |
           (((uint64_t)buf[1]) << 8)  |
           (((uint64_t)buf[2]) << 16) |
           (((uint64_t)buf[3]) << 24) |
           (((uint64_t)buf[4]) << 32) |
           (((uint64_t)buf[5]) << 40);
}
