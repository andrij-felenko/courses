#include <array>
#include <cstdint>

/* Рядки симетричної матриці B (12×12). */
constexpr std::array<uint16_t, 12> B = {
    0xA3B, 0xD1D, 0xE8E, 0xB47, 0xDA3, 0xED1,
    0xF68, 0xBB4, 0x9DA, 0x8ED, 0xC76, 0x7FF,
};

/* m·B над GF(2): XOR тих рядків B, де в m стоїть одиниця. */
constexpr uint16_t times_B(uint16_t m) noexcept {
    uint16_t acc = 0;
    for (size_t i = 0; i < 12; ++i) {
        if (m & (1u << i)) acc ^= B[i];
    }
    return acc;
}

/* Кодування: 12 бітів даних -> 24-бітне слово [дані(12) | перевірка(12)]. */
constexpr uint32_t golay_encode(uint16_t data) noexcept {
    data &= 0x0FFF;
    return static_cast<uint32_t>(data) | (static_cast<uint32_t>(times_B(data)) << 12);
}
