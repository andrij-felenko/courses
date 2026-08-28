#include <cstdint>

/* Розрахунок першого байта для операції запису (R/W = 0) */
constexpr uint8_t i2c_10bit_header_write(uint16_t addr10) noexcept {
    return static_cast<uint8_t>(0xF0 | (((addr10 >> 8) & 0x03) << 1) | 0x00);
}

/* Розрахунок першого байта для операції читання (R/W = 1) */
constexpr uint8_t i2c_10bit_header_read(uint16_t addr10) noexcept {
    return static_cast<uint8_t>(0xF0 | (((addr10 >> 8) & 0x03) << 1) | 0x01);
}

/* Розрахунок другого байта (молодші 8 бітів) */
constexpr uint8_t i2c_10bit_header_low(uint16_t addr10) noexcept {
    return static_cast<uint8_t>(addr10 & 0xFF);
}
