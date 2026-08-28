#include <cstdint>
#include <cstdio>
#include <cmath>
#include <vector>
#include <algorithm>

struct Rng {
    uint64_t s;
    uint64_t next() {
        uint64_t z = (s += 0x9E3779B97F4A7C15ULL);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
        return z ^ (z >> 31);
    }
    // 53 старші біти → double у [0,1). Зібрано руками навмисно: стандарт фіксує
    // рушії точно, а розподіли — ні, тож std::uniform_real_distribution дає
    // з того самого зерна різні числа під libstdc++ і під libc++.
    double u01() { return (next() >> 11) * (1.0 / 9007199254740992.0); }   // 2⁵³
};

// n точок по d координат в ОДНОМУ суцільному масиві: точка i — це [i·d, i·d + d)
std::vector<double> gen(int n, int d, uint64_t seed) {
    Rng g{seed};
    std::vector<double> p(static_cast<size_t>(n) * d);
    for (double& v : p) v = g.u01();
    return p;
}

static double dist2(const double* a, const double* b, int d) {
    double s = 0.0;
    for (int i = 0; i < d; ++i) { const double t = a[i] - b[i]; s += t * t; }
    return s;
}
