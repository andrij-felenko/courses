#include <iostream>
#include <vector>
#include <cmath>
#include <functional>
#include <expected>
#include <string>
#include <iomanip>

namespace quantum {

class NumerovSolver {
public:
    struct Config {
        double x_min{-5.0};
        double x_max{5.0};
        std::size_t steps{1000};
        double tolerance{1e-7};
    };

    enum class ErrorCode {
        InvalidInterval,
        MemoryAllocationFailed,
        ConvergenceFailed
    };

    explicit NumerovSolver(Config config, std::function<double(double)> potential)
        : config_(config), potential_(std::move(potential)) {}

    // Обчислення хвильової функції для фіксованої енергії E
    [[nodiscard]] std::vector<double> integrate(double E) const {
        std::vector<double> psi(config_.steps + 1, 0.0);
        const double h = (config_.x_max - config_.x_min) / static_cast<double>(config_.steps);
        const double h2_12 = (h * h) / 12.0;

        psi[0] = 0.0;
        psi[1] = 1e-7;

        auto k2_val = [this, E](double x) {
            return 2.0 * (E - potential_(x));
        };

        for (std::size_t i = 1; i < config_.steps; ++i) {
            const double x_prev = config_.x_min + static_cast<double>(i - 1) * h;
            const double x_curr = config_.x_min + static_cast<double>(i) * h;
            const double x_next = config_.x_min + static_cast<double>(i + 1) * h;

            const double k2_prev = k2_val(x_prev);
            const double k2_curr = k2_val(x_curr);
            const double k2_next = k2_val(x_next);

            const double term_curr = 2.0 * (1.0 - 5.0 * h2_12 * k2_curr) * psi[i];
            const double term_prev = (1.0 + h2_12 * k2_prev) * psi[i - 1];
            const double denom = 1.0 + h2_12 * k2_next;

            psi[i + 1] = (term_curr - term_prev) / denom;
        }

        return psi;
    }

    // Пошук власного значення на інтервалі [E_low, E_high]
    [[nodiscard]] std::expected<double, ErrorCode> find_eigenvalue(double E_low, double E_high) const {
        auto psi_low = integrate(E_low);
        auto psi_high = integrate(E_high);

        double f_low = psi_low.back();
        double f_high = psi_high.back();

        if (f_low * f_high > 0.0) {
            return std::unexpected(ErrorCode::InvalidInterval);
        }

        double E_mid = E_low;
        while ((E_high - E_low) > config_.tolerance) {
            E_mid = 0.5 * (E_low + E_high);
            auto psi_mid = integrate(E_mid);
            double f_mid = psi_mid.back();

            if (std::abs(f_mid) < 1e-12) {
                break;
            }

            if (f_low * f_mid < 0.0) {
                E_high = E_mid;
                f_high = f_mid;
            } else {
                E_low = E_mid;
                f_low = f_mid;
            }
        }

        return E_mid;
    }

    // Нормування хвильової функції: ∫ |ψ|² dx = 1
    static void normalize(std::vector<double>& psi, double h) {
        double norm_sq = 0.0;
        for (std::size_t i = 0; i < psi.size() - 1; ++i) {
            norm_sq += 0.5 * (psi[i] * psi[i] + psi[i + 1] * psi[i + 1]) * h;
        }
        const double norm = std::sqrt(norm_sq);
        if (norm > 0.0) {
            for (auto& val : psi) {
                val /= norm;
            }
        }
    }

private:
    Config config_;
    std::function<double(double)> potential_;
};

} // namespace quantum

int main() {
    using namespace quantum;

    NumerovSolver::Config cfg{.x_min = -5.0, .x_max = 5.0, .steps = 1000, .tolerance = 1e-7};
    
    // Задаємо потенціал квантового осцилятора через лямбда-вираз
    auto harmonic_potential = [](double x) { return 0.5 * x * x; };
    NumerovSolver solver(cfg, harmonic_potential);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Обчислення власних значень (C++23 std::expected):\n";

    const std::vector<std::pair<double, double>> brackets = {
        {0.1, 0.9}, // E0 = 0.5
        {1.1, 1.9}, // E1 = 1.5
        {2.1, 2.9}  // E2 = 2.5
    };

    for (std::size_t i = 0; i < brackets.size(); ++i) {
        auto res = solver.find_eigenvalue(brackets[i].first, brackets[i].second);
        if (res) {
            std::cout << "Стан E" << i << " = " << *res << " (теоретичне: " << (static_cast<double>(i) + 0.5) << ")\n";
        } else {
            std::cerr << "Помилка обчислення для стану E" << i << "\n";
        }
    }

    return 0;
}
