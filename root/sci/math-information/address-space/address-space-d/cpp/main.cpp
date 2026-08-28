#include <cstdint>
#include <cstdio>

// Розмір адресного простору в байтах для N ліній адреси (байтова адресація).
// Для N = 32 результат не влазить у 32-бітне число (це РІВНО 2^32),
// тому рахуємо в 64-бітному типі.
static uint64_t address_space_bytes(unsigned n) {
    return (uint64_t)1 << n;          // 2^N: один зсув ліворуч на N позицій
}

int main() {
    for (unsigned n : { 16u, 32u }) {
        uint64_t bytes = address_space_bytes(n);
        std::printf("%u ліній -> 2^%u = %llu байтів\n",
                    n, n, (unsigned long long)bytes);
    }
    return 0;
}
