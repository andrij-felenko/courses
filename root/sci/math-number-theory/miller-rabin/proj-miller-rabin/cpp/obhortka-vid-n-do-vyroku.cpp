#include <cstdint>
using u64  = uint64_t;
using u128 = __uint128_t;

// n − 1 = 2^s · d; повертає d, s віддає через посилання
static u64 factor_out_twos(u64 n, int& s) {
    u64 d = n - 1;
    for (s = 0; (d & 1) == 0; ++s) d >>= 1;
    return d;
}

// true, якщо ЖОДНА основа не свідок (n пройшло весь набір)
static bool passes_all(u64 n, const u64* bases, int cnt) {
    int s; u64 d = factor_out_twos(n, s);
    for (int i = 0; i < cnt; ++i) {
        u64 a = bases[i] % n;
        if (a == 0) continue;                 // основа кратна n — не рахуємо
        if (is_witness(a, d, s, n)) return false;
    }
    return true;
}

bool is_prime(u64 n) {
    if (n < 2) return false;                  // 0, 1 — не прості
    for (u64 sp : {2u,3u,5u,7u,11u,13u,17u,19u,23u,29u,31u,37u,41u,43u,47u,53u}) {
        if (n == sp)     return true;         // сама мала проста
        if (n % sp == 0) return false;        // має дрібний дільник → складене
    }
    // тут n > 53, непарне й взаємно просте з усіма основами нижче
    static const u64 bases64[] = {2,3,5,7,11,13,17,19,23,29,31,37};
    return passes_all(n, bases64, 12);
}
