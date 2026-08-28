// Чисельний аналіз кругових відображень та теореми Данжуа (C++20).
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <string_view>
#include <iomanip>

enum class MapError {
    InvalidParam,
    DivergentOrbit
};

class CircleMap {
public:
    constexpr CircleMap(double omega, double k) noexcept
        : omega_{omega}, k_{k} {}

    [[nodiscard]] constexpr double lift(double x) const noexcept {
        return x + omega_ - (k_ / (2.0 * std::numbers::pi)) * std::sin(2.0 * std::numbers::pi * x);
    }

    [[nodiscard]] constexpr double lift_prime(double x) const noexcept {
        return 1.0 - k_ * std::cos(2.0 * std::numbers::pi * x);
    }

    [[nodiscard]] double rotation_number(std::size_t iterations = 1000000) const noexcept {
        double x = 0.0;
        for (std::size_t i = 0; i < iterations; ++i) {
            x = lift(x);
        }
        double rho = std::fmod(x / static_cast<double>(iterations), 1.0);
        return (rho < 0.0) ? rho + 1.0 : rho;
    }

    [[nodiscard]] std::expected<double, MapError>
    derivative_product(double x0, std::size_t q_steps) const noexcept {
        if (q_steps == 0) return std::unexpected(MapError::InvalidParam);

        double prod = 1.0;
        double curr_x = x0;

        for (std::size_t i = 0; i < q_steps; ++i) {
            double mod_x = std::fmod(curr_x, 1.0);
            if (mod_x < 0.0) mod_x += 1.0;

            double prime_val = lift_prime(mod_x);
            if (std::isnan(prime_val) || std::isinf(prime_val)) {
                return std::unexpected(MapError::DivergentOrbit);
            }
            prod *= prime_val;
            curr_x = lift(curr_x);
        }
        return prod;
    }

private:
    double omega_;
    double k_;
};

struct Convergent {
    std::size_t p;
    std::size_t q;
};

[[nodiscard]] std::vector<Convergent>
compute_convergents(double alpha, std::size_t max_depth = 10) {
    std::vector<Convergent> convergents;
    convergents.reserve(max_depth);

    double val = alpha;
    std::size_t p_prev = 1, p_curr = 0;
    std::size_t q_prev = 0, q_curr = 1;

    for (std::size_t i = 0; i < max_depth; ++i) {
        auto a = static_cast<std::size_t>(std::floor(val));
        std::size_t p_next = a * p_curr + p_prev;
        std::size_t q_next = a * q_curr + q_prev;

        convergents.push_back({p_next, q_next});
        p_prev = p_curr; p_curr = p_next;
        q_prev = q_curr; q_curr = q_next;

        double rem = val - static_cast<double>(a);
        if (rem < 1e-12) break;
        val = 1.0 / rem;
    }
    return convergents;
}

int main() {
    constexpr double golden_ratio = (std::numbers::sqrt5 - 1.0) / 2.0;
    const CircleMap map{golden_ratio, 0.5};

    std::cout << std::fixed << std::setprecision(8);
    std::cout << "=== Аналіз кругових відображень у C++20 ===\n";
    std::cout << "Омега = " << golden_ratio << ", K = 0.5\n";

    const double rho = map.rotation_number();
    std::cout << "Число обертання rho(f) = " << rho << "\n\n";

    const auto convergents = compute_convergents(rho, 8);
    std::span<const Convergent> convergents_view{convergents.data() + 2, convergents.size() - 2};

    constexpr double x1 = 0.15;
    constexpr double x2 = 0.72;

    std::cout << "q_k   | log(f^{q_k}')(x1) | log(f^{q_k}')(x2) | Різниця (Denjoy bound)\n";
    std::cout << "---------------------------------------------------------------------\n";

    for (const auto& [p, q] : convergents_view) {
        auto res1 = map.derivative_product(x1, q);
        auto res2 = map.derivative_product(x2, q);

        if (res1 && res2) {
            double log_d1 = std::log(std::abs(*res1));
            double log_d2 = std::log(std::abs(*res2));
            double diff = std::abs(log_d1 - log_d2);

            std::cout << std::setw(5) << q << " | "
                      << std::setw(17) << log_d1 << " | "
                      << std::setw(17) << log_d2 << " | "
                      << diff << "\n";
        }
    }

    return 0;
}
