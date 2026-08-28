#include <cstdint>
#include <numeric>   // std::gcd
#include <utility>   // std::swap
#include <vector>

using u64 = uint64_t;
struct Triple { u64 a, b, c; };

// Усі примітивні трійки з гіпотенузою c ≤ limit.
std::vector<Triple> primitive_triples(u64 limit) {
    std::vector<Triple> out;
    for (u64 m = 2; m * m + 1 <= limit; ++m) {
        for (u64 n = 1; n < m; ++n) {
            u64 c = m * m + n * n;
            if (c > limit) break;                          // більші n лише збільшать c
            if (((m - n) & 1u) && std::gcd(m, n) == 1) {   // різна парність + взаємна простота
                u64 a = m * m - n * n, b = 2 * m * n;
                if (a > b) std::swap(a, b);
                out.push_back({a, b, c});
            }
        }
    }
    return out;
}
