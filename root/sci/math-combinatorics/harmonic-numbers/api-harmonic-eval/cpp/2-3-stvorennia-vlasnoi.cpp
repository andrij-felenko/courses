#include <cmath>
#include <expected>
#include <numbers>
#include <string_view>

namespace sys_math {

constexpr double EULER_MASCHERONI = 0.57721566490153286060;

enum class HarmonicError {
    InvalidArgument,
    DomainError,
    Overflow
};

[[nodiscard]] inline std::expected<double, HarmonicError> cpp_harmonic_eval(double x) noexcept {
    if (std::isnan(x) || x < 0.0) {
        return std::unexpected(HarmonicError::InvalidArgument);
    }
    if (x == 0.0) {
        return 0.0;
    }

    const double h = 1e-7;
    const double dig = (std::lgamma(x + 1.0 + h) - std::lgamma(x + 1.0 - h)) / (2.0 * h);

    if (std::isnan(dig) || std::isinf(dig)) {
        return std::unexpected(HarmonicError::DomainError);
    }

    return dig + EULER_MASCHERONI;
}

} // namespace sys_math
