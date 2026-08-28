#include <iostream>
#include <cmath>
#include <vector>
#include <span>
#include <expected>
#include <string_view>
#include <iomanip>

namespace math_algo {

constexpr double EULER_MASCHERONI = 0.57721566490153286060;

enum class HarmonicError {
    ZeroArgument,
    Overflow
};

class HarmonicCalculator {
public:
    // Повертає H[n] або помилку через std::expected
    [[nodiscard]] static std::expected<double, HarmonicError> compute(std::uint64_t n) noexcept {
        if (n == 0) {
            return std::unexpected(HarmonicError::ZeroArgument);
        }

        if (n <= 1000) {
            return compute_kahan(n);
        }
        return compute_asymptotic(n);
    }

    // Зворотне сумування для масиву доданків через std::span
    [[nodiscard]] static double sum_backward(std::span<const double> terms) noexcept {
        double total = 0.0;
        for (auto it = terms.rbegin(); it != terms.rend(); ++it) {
            total += *it;
        }
        return total;
    }

private:
    [[nodiscard]] static double compute_kahan(std::uint64_t n) noexcept {
        double sum = 0.0;
        double compensation = 0.0;
        for (std::uint64_t k = 1; k <= n; ++k) {
            const double y = (1.0 / static_cast<double>(k)) - compensation;
            const double t = sum + y;
            compensation = (t - sum) - y;
            sum = t;
        }
        return sum;
    }

    [[nodiscard]] static double compute_asymptotic(std::uint64_t n) noexcept {
        const double nd = static_cast<double>(n);
        const double n2 = nd * nd;
        const double n4 = n2 * n2;
        const double n6 = n4 * n2;

        return std::log(nd) + EULER_MASCHERONI 
               + (1.0 / (2.0 * nd)) 
               - (1.0 / (12.0 * n2)) 
               + (1.0 / (120.0 * n4)) 
               - (1.0 / (252.0 * n6));
    }
};

} // namespace math_algo

int main() {
    const std::vector<std::uint64_t> test_cases = {1, 5, 10, 1000, 1000000};

    std::cout << std::setprecision(15);
    for (const auto n : test_cases) {
        auto res = math_algo::HarmonicCalculator::compute(n);
        if (res) {
            std::cout << "H[" << n << "] = " << *res << "\n";
        } else {
            std::cerr << "Помилка обчислення для n = " << n << "\n";
        }
    }
    return 0;
}
