#include <array>
#include <cstddef>
#include <cstdint>

// B(2,6), укладена так, що вгорі стоїть її вікно з шести нулів.
// Стала не єдина можлива: таких є 2²⁶ · 2. Ця — найменша лексикографічно.
inline constexpr std::uint64_t DEBRUIJN = 0x0218a392cd3d5dbfULL;

// Таблицю будує компілятор ще до запуску — тим самим виразом, що й гарячий код.
consteval std::array<std::uint8_t, 64> make_table() {
    std::array<std::uint8_t, 64> t{};
    for (std::uint64_t k = 0; k < 64; ++k) {
        const std::uint64_t hash = ((std::uint64_t{1} << k) * DEBRUIJN) >> 58;
        t[static_cast<std::size_t>(hash)] = static_cast<std::uint8_t>(k);
    }
    return t;
}
inline constexpr auto TAB = make_table();

// ⌊log₂n⌋ для n > 0. На нулі НЕ визначено — див. «Пастки».
constexpr int floor_log2_debruijn(std::uint64_t n) {
    n |= n >> 1;   n |= n >> 2;    n |= n >> 4;    // розмазали старший біт донизу:
    n |= n >> 8;   n |= n >> 16;   n |= n >> 32;   // n стало 2ᵏ⁺¹ − 1
    const std::uint64_t msb = n - (n >> 1);        // лишили сам старший біт: 2ᵏ
    return TAB[static_cast<std::size_t>((msb * DEBRUIJN) >> 58)];
}
