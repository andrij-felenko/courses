// sine_bsrr.hpp — та сама таблиця, але її будує компілятор (C++17 і новіший).
// std::sin не constexpr, тому чверть періоду рахуємо рядом Тейлора:
// на [0, π/2] шести членів вистачає з запасом (похибка < 1e-9 проти 1/256 у LSB).
#include <array>
#include <cstdint>

inline constexpr int      LEN    = 256;
inline constexpr double   TWO_PI = 6.283185307179586;
inline constexpr uint8_t  PINMAP[8] = {0, 1, 4, 5, 6, 7, 8, 9};   // b0…b7 → виводи

constexpr double sin_quarter(double x) {          // x у [0, π/2]
    double x2 = x * x, term = x, sum = x;
    for (int k = 1; k <= 6; ++k) { term *= -x2 / ((2 * k) * (2 * k + 1)); sum += term; }
    return sum;
}

constexpr double sine(double t) {                 // t — доля періоду, [0, 1)
    if (t < 0.25) return  sin_quarter(TWO_PI * t);
    if (t < 0.50) return  sin_quarter(TWO_PI * (0.5 - t));
    if (t < 0.75) return -sin_quarter(TWO_PI * (t - 0.5));
    return                -sin_quarter(TWO_PI * (1.0 - t));
}

constexpr uint32_t bsrr(unsigned value) {
    uint32_t set_mask = 0, all_mask = 0;
    for (int b = 0; b < 8; ++b) {
        all_mask |= 1u << PINMAP[b];
        if (value & (1u << b)) set_mask |= 1u << PINMAP[b];
    }
    return set_mask | ((all_mask & ~set_mask) << 16);
}

inline constexpr std::array<uint32_t, LEN> sine_bsrr = [] {
    std::array<uint32_t, LEN> t{};
    for (int i = 0; i < LEN; ++i)
        t[i] = bsrr(static_cast<unsigned>(127.5 + 127.5 * sine((i + 0.5) / LEN) + 0.5));
    return t;
}();
