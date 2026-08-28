#include <cstdint>
#include <cstdio>
#include <functional>
#include <queue>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

constexpr uint64_t K = 5; // скільки різних операцій вкидає клієнт

// SplitMix64: увесь стан — одне 64-бітове число; next() — чиста функція від нього.
struct Rand {
    uint64_t state;
    explicit Rand(uint64_t seed) : state(seed) {}

    uint64_t next() {
        state += 0x9E3779B97F4A7C15ULL;
        uint64_t z = state;
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
        return z ^ (z >> 31);
    }

    uint64_t intn(uint64_t n) { return next() % n; } // рівномірно в [0, n)
    bool chance(uint64_t pct) { return intn(100) < pct; }
};
