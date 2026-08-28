#include <cstdint>
#include <bit>
#include <span>

// Типобезпечний розбір 16-бітного Big-Endian слова через std::span
constexpr int16_t parse_be16_signed(std::span<const uint8_t, 2> bytes) noexcept {
    const auto raw_unsigned = static_cast<uint16_t>((static_cast<uint16_t>(bytes[0]) << 8) |
                                                     static_cast<uint16_t>(bytes[1]));
    return static_cast<int16_t>(raw_unsigned);
}

// Типобезпечний розбір 16-бітного Little-Endian слова
constexpr int16_t parse_le16_signed(std::span<const uint8_t, 2> bytes) noexcept {
    const auto raw_unsigned = static_cast<uint16_t>((static_cast<uint16_t>(bytes[1]) << 8) |
                                                     static_cast<uint16_t>(bytes[0]));
    return static_cast<int16_t>(raw_unsigned);
}

// Розпакування 24-бітного знакового значення через 32-бітний зсув
constexpr int32_t parse_be24_signed(std::span<const uint8_t, 3> bytes) noexcept {
    const auto raw_shifted = (static_cast<uint32_t>(bytes[0]) << 24) |
                             (static_cast<uint32_t>(bytes[1]) << 16) |
                             (static_cast<uint32_t>(bytes[2]) << 8);
    return static_cast<int32_t>(raw_shifted) >> 8;
}

// Розпакування 20-бітного формату BMP280
constexpr uint32_t parse_bmp280_pressure_raw(std::span<const uint8_t, 3> bytes) noexcept {
    const auto msb = static_cast<uint32_t>(bytes[0]);
    const auto lsb = static_cast<uint32_t>(bytes[1]);
    const auto xlsb = static_cast<uint32_t>(bytes[2]) >> 4;
    return (msb << 12) | (lsb << 4) | xlsb;
}

// Сучасний розбір за допомогою std::byteswap (C++23)
template <typename T>
constexpr T from_big_endian(T value) noexcept {
    if constexpr (std::endian::native == std::endian::little) {
        return std::byteswap(value);
    }
    return value;
}
