#include <array>
#include <cstdint>

// Генерація таблиці CRC-6 (поліном 0x43, P(x) = x⁶ + x¹ + 1) на етапі компіляції
constexpr auto generate_crc6_table() {
    std::array<uint8_t, 256> table{};
    for (size_t i = 0; i < 256; ++i) {
        uint8_t crc = static_cast<uint8_t>(i);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ 0x43) : static_cast<uint8_t>(crc << 1);
        }
        table[i] = crc & 0x3F; // Маскування 6-бітного результату
    }
    return table;
}

// Константний масив у flash-пам'яті (.rodata), розрахований компілятором
constexpr auto crc6_table = generate_crc6_table();
