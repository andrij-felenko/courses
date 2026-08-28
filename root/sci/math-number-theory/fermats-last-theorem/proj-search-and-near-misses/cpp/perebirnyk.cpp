#include <cstdio>
#include <cstdint>
using u128 = unsigned __int128;

u128 ipow(uint64_t x, int n) { u128 p = 1; while (n--) p *= x; return p; }

uint64_t iroot(u128 s, int n) {               // ⌊ⁿ√s⌋ — бінарний пошук, лише цілими
    uint64_t lo = 1, hi = 2'000'000'000ull;   // верхня межа з запасом для діапазону
    while (lo < hi) {
        uint64_t mid = lo + (hi - lo + 1) / 2;
        if (ipow(mid, n) <= s) lo = mid; else hi = mid - 1;
    }
    return lo;
}

int main() {
    const int n = 3, N = 1000;
    long double bestRel = 2.0L;
    uint64_t bA = 0, bB = 0, bC = 0; long long bDelta = 0;
    for (uint64_t a = 1; a < (uint64_t)N; ++a)
        for (uint64_t b = a; b < (uint64_t)N; ++b) {
            u128 s = ipow(a, n) + ipow(b, n);
            uint64_t c = iroot(s, n);                    // cⁿ ≤ s < (c+1)ⁿ
            u128 below = ipow(c, n), above = ipow(c + 1, n);
            if (below == s) { printf("РОЗВ'ЯЗОК\n"); return 0; }
            uint64_t cc = (s - below < above - s) ? c : c + 1;
            long long delta = (long long)((__int128)ipow(cc, n) - (__int128)s);
            long double rel = (delta < 0 ? -delta : delta) / (long double)s;
            if (rel < bestRel) { bestRel = rel; bA = a; bB = b; bC = cc; bDelta = delta; }
        }
    printf("немає розв'язку при a, b < %d;  найтісніше:  "
           "%llu^%d + %llu^%d = %llu^%d %c %lld\n", N,
           (unsigned long long)bA, n, (unsigned long long)bB, n,
           (unsigned long long)bC, n, bDelta > 0 ? '-' : '+',
           bDelta > 0 ? bDelta : -bDelta);
    // немає розв'язку при a, b < 1000;  найтісніше:  791^3 + 812^3 = 1010^3 - 1
    return 0;
}
