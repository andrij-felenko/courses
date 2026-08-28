#include <iostream>
#include <cstdint>
#include <optional>
#include <limits>

namespace math {

class TriangularChecker {
public:
    // Обчислення цілочисельного квадратного кореня
    static constexpr std::uint64_t integer_sqrt(std::uint64_t n) noexcept {
        if (n == 0) return 0;
        std::uint64_t x = n;
        std::uint64_t y = (x + 1) / 2;
        while (y < x) {
            x = y;
            y = (x + n / x) / 2;
        }
        return x;
    }

    // Перевірка на трикутність з поверненням індексу через std::optional
    static constexpr std::optional<std::uint64_t> get_triangular_index(std::uint64_t m) noexcept {
        if (m == 0) return 0;

        if (m > (std::numeric_limits<std::uint64_t>::max() - 1) / 8) {
            return std::nullopt;
        }

        // Швидкий фільтр за модулем 9
        const std::uint64_t rem9 = m % 9;
        if (rem9 == 2 || rem9 == 4 || rem9 == 5 || rem9 == 7 || rem9 == 8) {
            return std::nullopt;
        }

        const std::uint64_t disc = 8 * m + 1;
        const std::uint64_t s = integer_sqrt(disc);

        if (s * s != disc || (s & 1) == 0) {
            return std::nullopt;
        }

        return (s - 1) / 2;
    }

    static constexpr bool is_triangular(std::uint64_t m) noexcept {
        return get_triangular_index(m).has_value();
    }
};

} // namespace math
