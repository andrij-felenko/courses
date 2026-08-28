#include <bit>
#include <cstdint>

// синдром прийнятого слова = word mod g(x); 0 ⇒ помилки не видно
constexpr std::uint16_t syndrome(std::uint16_t word) { return poly_rem(word); }

// вага Геммінга через std::popcount з <bit>
constexpr int weight(std::uint16_t v) { return std::popcount(v); }

// циклічний зсув уліво в N розрядах
constexpr std::uint16_t rotl(std::uint16_t w) {
    uint16_t top = (w >> (N - 1)) & 1;
    return ((w << 1) | top) & ((1u << N) - 1);
}

// циклічний зсув управо в N розрядах
constexpr std::uint16_t rotr(std::uint16_t w) {
    uint16_t bot = w & 1;
    return ((w >> 1) | (bot << (N - 1))) & ((1u << N) - 1);
}
