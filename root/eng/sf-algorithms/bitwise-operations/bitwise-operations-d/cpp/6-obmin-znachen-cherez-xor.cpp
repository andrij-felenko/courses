#include <utility>
#include <concepts>

// В ідіоматичному C++ використовується std::swap
// std::swap(x, y);

// Безпечна реалізація через XOR (з перевіркою аліасингу):
template <std::integral T>
constexpr void xor_swap(T& a, T& b) noexcept {
    if (&a != &b) {
        a ^= b;
        b ^= a;
        a ^= b;
    }
}
