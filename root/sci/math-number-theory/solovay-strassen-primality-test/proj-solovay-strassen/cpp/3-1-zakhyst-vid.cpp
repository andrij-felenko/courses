// Ідіоматична C++ реалізація безпечного модульного множення без 128-бітних типів
[[nodiscard]] constexpr std::uint64_t mul_mod_safe(std::uint64_t a, std::uint64_t b, std::uint64_t mod) noexcept {
    std::uint64_t res = 0;
    a %= mod;
    while (b > 0) {
        if (b & 1) {
            res = (res >= mod - a) ? (res - (mod - a)) : (res + a);
        }
        a = (a >= mod - a) ? (a - (mod - a)) : (a + a);
        b >>= 1;
    }
    return res;
}
