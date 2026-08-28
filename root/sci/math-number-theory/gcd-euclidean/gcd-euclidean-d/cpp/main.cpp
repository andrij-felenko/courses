#include <cstdint>
#include <numeric>   // std::gcd — від C++17

std::int64_t gcd(std::int64_t a, std::int64_t b) {
    while (b != 0) {
        std::int64_t r = a % b;
        a = b;
        b = r;
    }
    return a < 0 ? -a : a;      // НСД завжди невід'ємний
}

// gcd(1071, 462) → 21
// У бойовому коді пишуть просто std::gcd(1071, 462).
