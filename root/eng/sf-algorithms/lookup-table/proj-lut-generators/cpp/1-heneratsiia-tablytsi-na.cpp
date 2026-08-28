#include <cstdint>
#include <array>
#include <span>

/* У C++20 функція consteval гарантує, що вся таблиця на 256 елементів 
   буде порахована виключно компілятором під час збірки. */

consteval auto generate_byte_popcount_table() {
    std::array<uint8_t, 256> table{};
    for (size_t i = 0; i < 256; ++i) {
        uint8_t count = 0;
        /* Алгоритм Браяна Кернігана для точного підрахунку одиничних бітів */
        for (uint8_t val = static_cast<uint8_t>(i); val > 0; val &= static_cast<uint8_t>(val - 1)) {
            ++count;
        }
        table[i] = count;
    }
    return table;
}

/* Статична константна таблиця на 256 байтів, розташована у flash/rodata */
inline constexpr auto BYTE_POPCOUNT_LUT = generate_byte_popcount_table();

[[nodiscard]] constexpr uint32_t popcount_buffer(std::span<const uint8_t> data) noexcept {
    uint32_t total = 0;
    for (const uint8_t byte : data) {
        total += BYTE_POPCOUNT_LUT[byte];
    }
    return total;
}
