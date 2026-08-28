#include <array>
#include <cstdint>

// Три канали по 16–17 бітів дають динамічний діапазон 48 бітів:
// 65535 · 65536 · 65537 = 281474976645120 ≈ 2⁴⁸
constexpr std::array<uint32_t, 3> M{65535u, 65536u, 65537u};

struct Rns { std::array<uint32_t, 3> c; };

Rns to_rns(uint64_t x) {
    return {{ uint32_t(x % M[0]), uint32_t(x % M[1]), uint32_t(x % M[2]) }};
}

Rns add(const Rns &a, const Rns &b) {
    Rns r{};
    for (int i = 0; i < 3; ++i) {
        uint32_t s = a.c[i] + b.c[i];            // < 2·65537 — уміщається легко
        r.c[i] = (s >= M[i]) ? s - M[i] : s;     // жодного переносу до сусіднього каналу
    }
    return r;
}

Rns mul(const Rns &a, const Rns &b) {
    Rns r{};
    for (int i = 0; i < 3; ++i)
        r.c[i] = uint32_t((uint64_t)a.c[i] * b.c[i] % M[i]);   // ⚠️ зняти uint64_t — і див. нижче
    return r;
}
