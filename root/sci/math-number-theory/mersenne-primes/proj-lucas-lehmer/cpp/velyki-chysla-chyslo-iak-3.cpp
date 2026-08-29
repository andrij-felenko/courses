#include <algorithm>
#include <cstdint>
#include <span>
#include <vector>

using Limb = std::uint32_t;

// Зовнішні функції модульної арифметики з попередніх модулів
void square(std::span<const Limb> a, std::span<Limb> prod) noexcept;
void reduce_mod_mp(std::span<const Limb> prod, int p, std::span<Limb> r);

// Віднімання двійки за модулем Mp: s = (s − 2) mod Mp
void sub2_mod_mp(std::span<Limb> s, int p) noexcept {
    const int n = static_cast<int>(s.size());
    const int R = p % 32;
    bool above = false;
    for (int i = 1; i < n; ++i) {
        if (s[i] != 0) {
            above = true;
            break;
        }
    }
    if (!(s[0] >= 2 || above)) {
        // s == 0 або s == 1: додаємо Mp перед відніманням
        const Limb d = 2 - s[0];
        std::fill(s.begin(), s.end() - 1, 0xFFFFFFFFU);
        s[n - 1] = (1U << R) - 1;
        Limb b = d;
        for (int i = 0; i < n && b != 0; ++i) {
            const Limb o = s[i];
            s[i] = o - b;
            b = (o < b) ? 1 : 0;
        }
        return;
    }
    Limb b = 2;
    for (int i = 0; i < n && b != 0; ++i) {
        const Limb o = s[i];
        s[i] = o - b;
        b = (o < b) ? 1 : 0;
    }
}

// Головна функція тесту Люка–Лемера для довільного простого p
bool lucas_lehmer(int p) {
    if (p == 2) return true;                   // M₂ = 3 — просте
    if (p < 2) return false;

    const int n = (p + 31) / 32;
    std::vector<Limb> s(n, 0);                 // RAII-буфер поточного стану
    std::vector<Limb> prod(2 * n, 0);          // буфер піднесення до квадрата

    s[0] = 4;                                  // стартове значення S₀ = 4
    for (int k = 0; k < p - 2; ++k) {
        square(s, prod);                       // prod = s²
        reduce_mod_mp(prod, p, s);             // s = prod mod Mp
        sub2_mod_mp(s, p);                     // s = (s − 2) mod Mp
    }

    return std::all_of(s.begin(), s.end(), [](Limb x) { return x == 0; });
}
