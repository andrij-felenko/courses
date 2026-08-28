#include <stdint.h>

// Безпечне складання 16-бітного Big-Endian слова з двох байтів
int16_t parse_be16_signed(const uint8_t bytes[2]) {
    // bytes[0] - старший байт (MSB), bytes[1] - молодший байт (LSB)
    uint16_t raw_unsigned = ((uint16_t)bytes[0] << 8) | (uint16_t)bytes[1];
    return (int16_t)raw_unsigned;
}

// Безпечне складання 16-бітного Little-Endian слова (наприклад, для давачів Bosch)
int16_t parse_le16_signed(const uint8_t bytes[2]) {
    // bytes[0] - молодший байт (LSB), bytes[1] - старший байт (MSB)
    uint16_t raw_unsigned = ((uint16_t)bytes[1] << 8) | (uint16_t)bytes[0];
    return (int16_t)raw_unsigned;
}

// Розпакування 24-бітного Big-Endian знакового числа (прецизійний АЦП)
int32_t parse_be24_signed(const uint8_t bytes[3]) {
    // Збираємо 24 біти у верхні розряди 32-бітного слова, потім арифметично зсуваємо
    uint32_t raw_24 = ((uint32_t)bytes[0] << 24) |
                      ((uint32_t)bytes[1] << 16) |
                      ((uint32_t)bytes[2] << 8);
    return (int32_t)raw_24 >> 8; // Арифметичний зсув автоматично розмножує знак
}

// Розпакування 20-бітного тиску Bosch BMP280 (MSB, LSB, XLSB[7:4])
uint32_t parse_bmp280_pressure_raw(const uint8_t bytes[3]) {
    uint32_t msb = (uint32_t)bytes[0];
    uint32_t lsb = (uint32_t)bytes[1];
    uint32_t xlsb = (uint32_t)bytes[2] >> 4;
    return (msb << 12) | (lsb << 4) | xlsb;
}

// Використання апаратної інструкції перевороту байтів REV16 процесора ARM
int16_t parse_be16_fast(uint16_t raw_from_bus) {
    return (int16_t)__builtin_bswap16(raw_from_bus);
}
