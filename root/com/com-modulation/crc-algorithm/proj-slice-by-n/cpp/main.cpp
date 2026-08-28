#include <array>
#include <cstdint>
#include <cstddef>
#include <span>
#include <bit>

namespace fast_crc {

inline constexpr uint32_t CRC32_POLY_REV = 0xEDB88320U;

// Генерація матриці таблиць Slice-by-8 під час компіляції (constexpr)
constexpr auto make_slice8_tables() {
    std::array<std::array<uint32_t, 256>, 8> tables{};

    // Базова таблиця T0
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t c = i;
        for (int b = 0; b < 8; ++b) {
            c = (c & 1U) ? (c >> 1) ^ CRC32_POLY_REV : (c >> 1);
        }
        tables[0][i] = c;
    }

    // Таблиці T1..T7 для зсувів 1..7 байтів
    for (size_t k = 1; k < 8; ++k) {
        for (size_t i = 0; i < 256; ++i) {
            const uint32_t prev = tables[k - 1][i];
            tables[k][i] = (prev >> 8) ^ tables[0][prev & 0xFFU];
        }
    }
    return tables;
}

inline constexpr auto SLICE8_TABLES = make_slice8_tables();

template <typename ByteType>
[[nodiscard]] constexpr uint32_t crc32_slice8(std::span<const ByteType> buffer) noexcept {
    static_assert(sizeof(ByteType) == 1, "Buffer element must be a 1-byte type");

    uint32_t crc = 0xFFFFFFFFU;
    auto ptr = reinterpret_cast<const uint8_t*>(buffer.data());
    size_t length = buffer.size();

    // 1. Пролог: побайтове вирівнювання адреси до кратності 8 байтам
    while (length > 0 && (reinterpret_cast<uintptr_t>(ptr) & 7U) != 0) {
        crc = (crc >> 8) ^ SLICE8_TABLES[0][(crc ^ *ptr) & 0xFFU];
        ++ptr;
        --length;
    }

    // 2. Паралельний розрахунок 8 байтів за ітерацію
    while (length >= 8) {
        const auto low = *reinterpret_cast<const uint32_t*>(ptr);
        const auto high = *reinterpret_cast<const uint32_t*>(ptr + 4);

        const uint32_t term1 = low ^ crc;
        const uint32_t term2 = high;

        crc = SLICE8_TABLES[7][term1 & 0xFFU]
            ^ SLICE8_TABLES[6][(term1 >> 8) & 0xFFU]
            ^ SLICE8_TABLES[5][(term1 >> 16) & 0xFFU]
            ^ SLICE8_TABLES[4][term1 >> 24]
            ^ SLICE8_TABLES[3][term2 & 0xFFU]
            ^ SLICE8_TABLES[2][(term2 >> 8) & 0xFFU]
            ^ SLICE8_TABLES[1][(term2 >> 16) & 0xFFU]
            ^ SLICE8_TABLES[0][term2 >> 24];

        ptr += 8;
        length -= 8;
    }

    // 3. Епілог: обробка фінального залишку
    while (length > 0) {
        crc = (crc >> 8) ^ SLICE8_TABLES[0][(crc ^ *ptr) & 0xFFU];
        ++ptr;
        --length;
    }

    return crc ^ 0xFFFFFFFFU;
}

} // namespace fast_crc
