#include <cstdio>
#include <cstdint>

uint64_t modpow(uint64_t x, uint64_t n, uint64_t m) {   // xⁿ mod m — швидке піднесення
    uint64_t r = 1 % m; x %= m;
    while (n) { if (n & 1) r = r * x % m; x = x * x % m; n >>= 1; }
    return r;
}

// Модуль, за яким aⁿ+bⁿ=cⁿ не тримається (0 — жоден із проби не викрив).
uint64_t refuted_by(uint64_t a, uint64_t b, uint64_t c, uint64_t n) {
    for (uint64_t m : {2ull, 9ull, 7ull, 13ull})
        if ((modpow(a, n, m) + modpow(b, n, m) + m - modpow(c, n, m)) % m) return m;
    return 0;
}

int main() {
    printf("%llu\n", (unsigned long long)refuted_by(1782, 1841, 1922, 12)); // 2
    printf("%llu\n", (unsigned long long)refuted_by(3987, 4365, 4472, 12)); // 9
}
