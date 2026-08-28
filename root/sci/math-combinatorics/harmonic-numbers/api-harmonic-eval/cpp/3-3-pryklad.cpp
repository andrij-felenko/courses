#include <iostream>
#include <cmath>
#include <expected>
#include <concepts>
#include <numbers>
#include <boost/math/special_functions/digamma.hpp>
#include <boost/math/special_functions/zeta.hpp>

namespace math_api {

// Використання офіційної математичної константи C++20
constexpr double EULER_GAMMA = 0.57721566490153286060;

enum class EvalError {
    InvalidArgument,
    DomainError,
    Overflow
};

template <std::floating_point T>
class HarmonicEvaluator {
public:
    // Обчислення H[x] для довільного дійсного x >= 0
    [[nodiscard]] static std::expected<T, EvalError> eval(T x) noexcept {
        if (std::isnan(x) || x < static_cast<T>(0)) {
            return std::unexpected(EvalError::InvalidArgument);
        }
        if (x == static_cast<T>(0)) {
            return static_cast<T>(0);
        }

        try {
            // H[x] = digamma(x + 1) + gamma
            T dig = boost::math::digamma(x + static_cast<T>(1));
            return dig + static_cast<T>(EULER_GAMMA);
        } catch (const std::overflow_error&) {
            return std::unexpected(EvalError::Overflow);
        } catch (const std::domain_error&) {
            return std::unexpected(EvalError::DomainError);
        }
    }

    // Узагальнене гармонічне число H[n, m] = sum(1/k^m)
    [[nodiscard]] static std::expected<T, EvalError> eval_generalized(std::size_t n, std::size_t m) noexcept {
        if (n == 0 || m == 0) {
            return std::unexpected(EvalError::InvalidArgument);
        }
        
        T sum = static_cast<T>(0);
        for (std::size_t k = 1; k <= n; ++k) {
            sum += static_cast<T>(1) / std::pow(static_cast<T>(k), static_cast<T>(m));
        }
        return sum;
    }
};

} // namespace math_api

int main() {
    using Evaluator = math_api::HarmonicEvaluator<double>;

    auto r1 = Evaluator::eval(10.0);
    if (r1) {
        std::cout << "H[10] = " << *r1 << "\n";
    }

    auto r2 = Evaluator::eval(2.5); // Неперервний дійсний аргумент!
    if (r2) {
        std::cout << "H[2.5] = " << *r2 << "\n";
    }

    auto r3 = Evaluator::eval_generalized(100, 2); // H[100, 2] -> pi^2 / 6
    if (r3) {
        std::cout << "H[100, 2] = " << *r3 << " (границя pi^2/6 ≈ 1.64493)\n";
    }

    return 0;
}
