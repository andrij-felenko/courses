#include <iostream>
#include <vector>
#include <optional>
#include <cstdint>
#include <limits>

namespace math::diophantine {

struct Solution {
    std::uint64_t x{0};
    std::uint64_t y{0};
    std::uint32_t a{0};
    std::uint32_t b{0};
};

class GeronoSolver {
public:
    [[nodiscard]] static constexpr bool safe_mul(std::uint64_t a, std::uint64_t b, std::uint64_t& res) noexcept {
        if (a == 0 || b == 0) {
            res = 0;
            return true;
        }
        if (a > std::numeric_limits<std::uint64_t>::max() / b) {
            return false;
        }
        res = a * b;
        return true;
    }

    [[nodiscard]] static constexpr bool safe_pow(std::uint64_t base, std::uint32_t exp, std::uint64_t& res) noexcept {
        std::uint64_t result = 1;
        std::uint64_t b = base;
        std::uint32_t e = exp;

        while (e > 0) {
            if (e & 1U) {
                if (!safe_mul(result, b, result)) {
                    return false;
                }
            }
            e >>= 1U;
            if (e > 0) {
                if (!safe_mul(b, b, b)) {
                    return false;
                }
            }
        }
        res = result;
        return true;
    }

    [[nodiscard]] static std::optional<std::uint64_t> exact_nth_root(std::uint64_t target, std::uint32_t b) noexcept {
        if (target == 0) return 0;
        if (target == 1) return 1;
        if (b == 0) return std::nullopt;
        if (b == 1) return target;

        std::uint64_t low = 1;
        std::uint64_t high = target;

        if (b == 2) high = 4294967295ULL;
        else if (b == 3) high = 2642245ULL;
        else if (b == 4) high = 65535ULL;
        else if (b >= 5 && b < 64) high = 1024ULL;
        else if (b >= 64) high = 1ULL;

        while (low <= high) {
            std::uint64_t mid = low + (high - low) / 2;
            std::uint64_t p = 0;
            const bool ok = safe_pow(mid, b, p);

            if (ok && p == target) {
                return mid;
            }
            if (!ok || p > target) {
                if (mid == 0) break;
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] std::vector<Solution> solve_quad_base(std::uint64_t max_x, std::uint32_t max_b) const {
        std::vector<Solution> results;
        for (std::uint64_t x = 2; x <= max_x; ++x) {
            const std::uint64_t target = x * x - 1;
            for (std::uint32_t b = 2; b <= max_b; ++b) {
                if (auto y = exact_nth_root(target, b)) {
                    results.push_back(Solution{x, *y, 2, b});
                }
            }
        }
        return results;
    }
};

} // namespace math::diophantine

int main() {
    std::cout << "=== Чисельний пошук розв'язків x² - yᵇ = 1 (C++) ===\n";
    const math::diophantine::GeronoSolver solver;
    
    const auto solutions = solver.solve_quad_base(100000, 10);
    std::cout << "Знайдено розв'язків: " << solutions.size() << "\n";

    for (std::size_t i = 0; i < solutions.size(); ++i) {
        const auto& s = solutions[i];
        std::cout << "Розв'язок #" << (i + 1) << ": "
                  << s.x << "^" << s.a << " - "
                  << s.y << "^" << s.b << " = 1\n";
    }

    return 0;
}
