#include <vector>
#include <span>
#include <functional>
#include <cstdint>

class ModularSieve {
public:
    template <typename Fn>
    static bool has_local_solution(Fn&& poly, std::size_t n, int64_t modulus) noexcept {
        if (n > 8) return true; // Пропускаємо для високих розмірностей

        std::vector<int64_t> current(n, 0);
        std::size_t total = 1;
        for (std::size_t i = 0; i < n; ++i) total *= modulus;

        for (std::size_t step = 0; step < total; ++step) {
            std::size_t temp = step;
            for (std::size_t i = 0; i < n; ++i) {
                current[i] = static_cast<int64_t>(temp % modulus);
                temp /= modulus;
            }
            const int64_t val = poly(std::span<const int64_t>(current));
            if ((val % modulus + modulus) % modulus == 0) {
                return true;
            }
        }
        return false;
    }
};
