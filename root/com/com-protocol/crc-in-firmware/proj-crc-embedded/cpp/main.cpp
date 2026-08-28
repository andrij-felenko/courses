// crc32_table.hpp — ту саму таблицю рахує компілятор; скрипт збірки не потрібен (C++17)
#include <array>
#include <cstdint>

inline constexpr std::uint32_t kPoly = 0xEDB88320U;   // CRC-32/ISO-HDLC, відбитий запис

constexpr std::array<std::uint32_t, 256> make_table() {
    std::array<std::uint32_t, 256> t{};
    for (std::uint32_t i = 0; i < 256; ++i) {
        std::uint32_t c = i;
        for (int k = 0; k < 8; ++k)               // ті самі вісім кроків зсув-XOR
            c = (c & 1U) ? (c >> 1) ^ kPoly : (c >> 1);
        t[i] = c;
    }
    return t;
}

inline constexpr auto kCrc32Table = make_table();  // ← лягає в .rodata, а не в RAM

constexpr std::uint32_t crc32(const char* s) {     // той самий запобіжник, але в компіляторі
    std::uint32_t crc = 0xFFFFFFFFU;
    for (; *s; ++s)
        crc = (crc >> 8) ^ kCrc32Table[(crc ^ static_cast<std::uint8_t>(*s)) & 0xFFU];
    return crc ^ 0xFFFFFFFFU;
}

static_assert(crc32("123456789") == 0xCBF43926U, "профіль CRC-32 розійшовся");
