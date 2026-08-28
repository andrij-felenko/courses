#include <array>
#include <cstdint>

constexpr std::array<uint16_t, 256> generate_crc16_table() {
    std::array<uint16_t, 256> table{};
    for (uint16_t i = 0; i < 256; ++i) {
        uint16_t cur = i << 8;
        for (int j = 0; j < 8; ++j) {
            cur = (cur & 0x8000) ? ((cur << 1) ^ 0x1021) : (cur << 1);
        }
        table[i] = cur;
    }
    return table;
}

// Таблиця генерується компілятором і записується у Flash-пам'ять (.rodata)
constexpr auto CRC16_TABLE = generate_crc16_table();
