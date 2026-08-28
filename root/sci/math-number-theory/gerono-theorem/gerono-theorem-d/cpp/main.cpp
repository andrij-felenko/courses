#include <iostream>
#include <vector>
#include <optional>
#include <cstdint>
#include <limits>

namespace math::diophantine {

class GeronoVerifier {
public:
    [[nodiscard]] static constexpr bool safe_mul(std::uint64_t a, std::uint64_t b, std::uint64_t& res) noexcept {
        if (a == 0 || b == 0) { res = 0; return true; }
        if (a > std::numeric_limits<std::uint64_t>::max() / b) return false;
        res = a * b;
        return true;
    }

    [[nodiscard]] static constexpr bool safe_pow(std::uint64_t base, std::uint32_t exp, std::uint64_t& res) noexcept {
        std::uint64_t r = 1, b = base;
        while (exp > 0) {
            if (exp & 1U) { if (!safe_mul(r, b, r)) return false; }
            exp >>= 1U;
            if (exp > 0) { if (!safe_mul(b, b, b)) return false; }
        }
        res = r;
        return true;
    }

    void verify(std::uint64_t max_x, std::uint32_t max_b) const {
        for (std::uint64_t x = 2; x <= max_x; ++x) {
            const std::uint64_t target = x * x - 1;
            for (std::uint32_t b = 2; b <= max_b; ++b) {
                std::uint64_t low = 1, high = target;
                if (b == 2) high = 4294967295ULL;
                else if (b == 3) high = 2642245ULL;
                else if (b >= 4) high = 65535ULL;

                while (low <= high) {
                    std::uint64_t mid = low + (high - low) / 2;
                    std::uint64_t p = 0;
                    const bool ok = safe_pow(mid, b, p);
                    if (ok && p == target) {
                        std::cout << "Знайдено розв'язок: " << x << "^2 - " << mid << "^" << b << " = 1\n";
                        break;
                    }
                    if (!ok || p > target) { if (mid == 0) break; high = mid - 1; }
                    else { low = mid + 1; }
                }
            }
        }
    }
};

} // namespace math::diophantine
