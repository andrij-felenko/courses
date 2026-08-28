#include <iostream>
#include <cmath>
#include <cstdint>
#include <optional>
#include <utility>
#include <vector>

namespace num_theory {

// Представлення розкладу n = a² + b²
struct SquareDecomposition {
    std::uint64_t a{0};
    std::uint64_t b{0};
};

// Швидке піднесення до степеня за модулем
constexpr std::uint64_t power_mod(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
    std::uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = static_cast<std::uint64_t>((static_cast<unsigned __int128>(result) * base) % mod);
        }
        base = static_cast<std::uint64_t>((static_cast<unsigned __int128>(base) * base) % mod);
        exp >>= 1;
    }
    return result;
}

// Знаходження квадратного кореня з -1 за модулем простого p ≡ 1 (mod 4)
std::optional<std::uint64_t> find_sqrt_minus_one(std::uint64_t p) noexcept {
    if (p % 4 != 1) return std::nullopt;
    const std::uint64_t exp = (p - 1) / 4;
    for (std::uint64_t g = 2; g < p; ++g) {
        const std::uint64_t z = power_mod(g, exp, p);
        if (power_mod(z, 2, p) == p - 1) {
            return (z > p / 2) ? (p - z) : z;
        }
    }
    return std::nullopt;
}

// Алгоритм Корнакк'ї для простого числа p ≡ 1 (mod 4)
std::optional<SquareDecomposition> cornacchia_prime(std::uint64_t p) noexcept {
    if (p == 2) {
        return SquareDecomposition{1, 1};
    }
    if (p % 4 != 1) {
        return std::nullopt;
    }

    const auto z_opt = find_sqrt_minus_one(p);
    if (!z_opt) return std::nullopt;

    const std::uint64_t limit = static_cast<std::uint64_t>(std::sqrt(p));
    std::uint64_t r0 = p;
    std::uint64_t r1 = *z_opt;

    while (r1 > limit) {
        const std::uint64_t rem = r0 % r1;
        r0 = r1;
        r1 = rem;
    }

    const std::uint64_t a = r1;
    const std::uint64_t diff = p - a * a;
    const std::uint64_t b = static_cast<std::uint64_t>(std::sqrt(diff));

    if (b * b == diff) {
        return SquareDecomposition{a, b};
    }
    return std::nullopt;
}

// Повний солвер для довільного цілого натурального числа n
std::optional<SquareDecomposition> solve_sum_of_two_squares(std::uint64_t n) {
    if (n == 0) return SquareDecomposition{0, 0};

    std::uint64_t temp = n;
    std::uint64_t k = 0;
    while (temp % 2 == 0) {
        temp /= 2;
        ++k;
    }

    std::uint64_t multiplier_c = 1;
    std::uint64_t core_m = 1;

    for (std::uint64_t d = 3; d * d <= temp; d += 2) {
        if (temp % d == 0) {
            std::uint64_t count = 0;
            while (temp % d == 0) {
                ++count;
                temp /= d;
            }
            if (d % 4 == 3) {
                if (count % 2 != 0) {
                    // Непарний степінь простого числа 3 mod 4 блокує подання
                    return std::nullopt;
                }
                for (std::uint64_t i = 0; i < count / 2; ++i) multiplier_c *= d;
            } else {
                for (std::uint64_t i = 0; i < count; ++i) core_m *= d;
            }
        }
    }

    if (temp > 1) {
        if (temp % 4 == 3) {
            return std::nullopt;
        }
        core_m *= temp;
    }

    const std::uint64_t pow2_c = k / 2;
    for (std::uint64_t i = 0; i < pow2_c; ++i) multiplier_c *= 2;
    if (k % 2 != 0) core_m *= 2;

    std::uint64_t core_a = 0, core_b = 0;
    for (std::uint64_t x = 0; x * x <= core_m; ++x) {
        const std::uint64_t rem = core_m - x * x;
        const std::uint64_t y = static_cast<std::uint64_t>(std::sqrt(rem));
        if (y * y == rem) {
            core_a = x;
            core_b = y;
            break;
        }
    }

    return SquareDecomposition{multiplier_c * core_a, multiplier_c * core_b};
}

} // namespace num_theory
