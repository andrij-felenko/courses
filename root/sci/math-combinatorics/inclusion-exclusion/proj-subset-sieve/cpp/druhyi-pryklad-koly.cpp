#include <cstdint>
#include <vector>

// Субфакторіали !0 … !n точною цілою рекурентою (жодних дробів і float).
std::vector<int64_t> subfactorials(int n) {
    std::vector<int64_t> d(n + 1);
    d[0] = 1;
    for (int k = 1; k <= n; ++k)
        d[k] = (int64_t)k * d[k - 1] + ((k & 1) ? -1 : +1);   // (−1)ᵏ: −1 для непарних k
    return d;
}
