#ifndef CHERNOFF_BOUNDS_HPP
#define CHERNOFF_BOUNDS_HPP

#include <cmath>
#include <algorithm>
#include <optional>
#include <cstddef>

namespace algo::chernoff {

struct ConcentrationConfig {
    double mu{0.0};
    double delta{0.0};
};

class BoundCalculator {
public:
    // Точна межа верхнього хвоста у логарифмічно захищеному форматі
    static constexpr double upper_exact(double mu, double delta) noexcept {
        if (mu <= 0.0 || delta <= 0.0) return 1.0;
        const double log_b = mu * (delta - (1.0 + delta) * std::log(1.0 + delta));
        return std::min(1.0, std::exp(log_b));
    }

    // Аппроксимація верхнього хвоста: exp(-mu * delta^2 / 3)
    static constexpr double upper_approx(double mu, double delta) noexcept {
        if (mu <= 0.0 || delta <= 0.0) return 1.0;
        return std::min(1.0, std::exp(-mu * delta * delta / 3.0));
    }

    // Аппроксимація нижнього хвоста: exp(-mu * delta^2 / 2)
    static constexpr double lower_approx(double mu, double delta) noexcept {
        if (mu <= 0.0 || delta <= 0.0 || delta >= 1.0) return 1.0;
        return std::min(1.0, std::exp(-mu * delta * delta / 2.0));
    }

    // Двостороння межа: 2 * exp(-mu * delta^2 / 3)
    static constexpr double two_sided(double mu, double delta) noexcept {
        if (mu <= 0.0 || delta <= 0.0 || delta >= 1.0) return 1.0;
        return std::min(1.0, 2.0 * std::exp(-mu * delta * delta / 3.0));
    }

    // Обчислення необхідної кількості випробувань k для підсилення більшості голосів
    static std::optional<std::size_t> required_trials(double gamma, double target_error) noexcept {
        if (gamma <= 0.0 || target_error <= 0.0 || target_error >= 1.0) {
            return std::nullopt;
        }
        const double k = (3.0 / (2.0 * gamma * gamma)) * std::log(1.0 / target_error);
        return static_cast<std::size_t>(std::ceil(k));
    }
};

} // namespace algo::chernoff

#endif // CHERNOFF_BOUNDS_HPP
