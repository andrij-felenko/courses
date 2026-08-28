#include <cstdint>
#include <cstdio>

// швидкий детермінований генератор (xorshift128+ із засівом splitmix64):
// мільярди чисел на секунду — рівно те, чого треба гарячому циклу
struct Rng {
    uint64_t s0, s1;
    explicit Rng(uint64_t seed) {
        auto mix = [](uint64_t& x) {
            x += 0x9E3779B97F4A7C15ULL;
            uint64_t z = x;
            z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
            z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
            return z ^ (z >> 31);
        };
        s0 = mix(seed); s1 = mix(seed);
    }
    double next() {                           // рівномірно в [0, 1)
        uint64_t x = s0, y = s1; s0 = y;
        x ^= x << 23;
        s1 = x ^ y ^ (x >> 17) ^ (y >> 26);
        return ((s1 + y) >> 11) * (1.0 / 9007199254740992.0);
    }
};

int main() {
    const double p = 0.001, r = 0.1, eG = 0.0, eB = 0.4;
    const uint64_t N = 2'000'000'000ULL;      // два мільярди бітів — питання секунд
    Rng rng(12345);

    bool bad = rng.next() < p / (p + r);      // старт зі сталого розподілу
    uint64_t hist[64] = {0}, run = 0, errors = 0;
    for (uint64_t i = 0; i < N; ++i) {
        if (rng.next() < (bad ? eB : eG)) ++errors;
        if (bad) ++run;
        else if (run) { ++hist[run < 64 ? run : 63]; run = 0; }
        bad = bad ? (rng.next() >= r) : (rng.next() < p);
    }
    printf("BER=%.6f  пачок(k=10)=%llu\n",
           (double)errors / N, (unsigned long long)hist[10]);
    return 0;
}
