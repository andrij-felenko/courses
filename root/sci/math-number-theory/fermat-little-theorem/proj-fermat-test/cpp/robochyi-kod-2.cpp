#include <cstdint>

// портативна заміна mulmod через додавання (вимагає m < 2⁶³)
constexpr std::uint64_t mulmod(std::uint64_t a, std::uint64_t b, std::uint64_t m) noexcept {
    std::uint64_t r = 0;
    a %= m;
    while (b > 0) {
        if (b & 1) r = (r + a) % m;   // додати поточну сходинку
        a = (a + a) % m;              // подвоїти
        b >>= 1;
    }
    return r;
}
