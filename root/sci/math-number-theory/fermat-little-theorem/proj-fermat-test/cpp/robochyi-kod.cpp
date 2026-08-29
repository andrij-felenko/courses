#include <cstdint>
#include <span>

// a·b mod m без переповнення через 128-бітне ціле
constexpr std::uint64_t mulmod(std::uint64_t a, std::uint64_t b, std::uint64_t m) noexcept {
    return static_cast<std::uint64_t>(static_cast<unsigned __int128>(a) * b % m);
}

constexpr std::uint64_t powmod(std::uint64_t base, std::uint64_t exp, std::uint64_t m) noexcept {
    std::uint64_t result = 1;
    base %= m;
    while (exp > 0) {
        if (exp & 1) result = mulmod(result, base, m);  // домножити сходинку
        base = mulmod(base, base, m);                   // наступний квадрат
        exp >>= 1;
    }
    return result;
}

bool is_probable_prime(std::uint64_t n, std::span<const std::uint64_t> bases) noexcept {
    if (n < 4)      return n == 2 || n == 3;
    if (n % 2 == 0) return false;
    for (std::uint64_t base : bases) {
        std::uint64_t a = base % n;
        if (a < 2) continue;                 // основи 0 та 1 нічого не кажуть
        if (powmod(a, n - 1, n) != 1)        // свідок складеності
            return false;                    // n напевно складене
    }
    return true;                             // імовірно просте
}
