// Сучасна реалізація на C++20: нульовий оверхед і статичне розміщення
#include <array>
#include <cstdint>
#include <span>

namespace crc32 {

inline constexpr uint32_t POLYNOMIAL = 0xEDB88320u;

constexpr auto make_table() noexcept {
    std::array<uint32_t, 256> table{};
    for (size_t i = 0; i < 256; ++i) {
        uint32_t crc = static_cast<uint32_t>(i);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 1u) ? ((crc >> 1) ^ POLYNOMIAL) : (crc >> 1);
        }
        table[i] = crc;
    }
    return table;
}

inline constexpr auto TABLE = make_table();

constexpr uint32_t calculate(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFu;
    for (uint8_t byte : data) {
        const uint8_t index = static_cast<uint8_t>(crc ^ byte);
        crc = (crc >> 8) ^ TABLE[index];
    }
    return crc ^ 0xFFFFFFFFu;
}

} // namespace crc32
