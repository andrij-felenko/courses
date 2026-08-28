#include <array>
#include <span>
#include <cstdint>

namespace sensirion {

// Генерація таблиці CRC-8 під час компіляції (constexpr)
constexpr auto generate_crc8_table() {
    std::array<uint8_t, 256> table{};
    for (size_t i = 0; i < 256; ++i) {
        uint8_t curr = static_cast<uint8_t>(i);
        for (int b = 0; b < 8; ++b) {
            if (curr & 0x80) {
                curr = static_cast<uint8_t>((curr << 1) ^ 0x31);
            } else {
                curr = static_cast<uint8_t>(curr << 1);
            }
        }
        table[i] = curr;
    }
    return table;
}

inline constexpr auto crc8_table = generate_crc8_table();

[[nodiscard]] constexpr uint8_t crc8_fast(std::span<const uint8_t> data) noexcept {
    uint8_t crc = 0xFF;
    for (const uint8_t byte : data) {
        crc = crc8_table[crc ^ byte];
    }
    return crc;
}

} // namespace sensirion
