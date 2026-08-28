#include <array>
#include <cstdint>
#include <cstddef>
#include <span>

namespace crc {

inline constexpr uint32_t CRC32_POLYNOMIAL = 0x04C11DB7U;

// Генерація таблиці LUT під час компіляції
constexpr auto generate_crc32_table() {
    std::array<uint32_t, 256> table{};
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t remainder = i << 24;
        for (int bit = 0; bit < 8; ++bit) {
            if ((remainder & 0x80000000U) != 0) {
                remainder = (remainder << 1) ^ CRC32_POLYNOMIAL;
            } else {
                remainder = (remainder << 1);
            }
        }
        table[i] = remainder;
    }
    return table;
}

inline constexpr auto CRC32_LUT = generate_crc32_table();

[[nodiscard]] constexpr uint32_t crc32_table_lookup(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (uint8_t byte : data) {
        uint8_t table_index = static_cast<uint8_t>((crc >> 24) ^ byte);
        crc = (crc << 8) ^ CRC32_LUT[table_index];
    }
    return crc ^ 0xFFFFFFFFU;
}

} // namespace crc
