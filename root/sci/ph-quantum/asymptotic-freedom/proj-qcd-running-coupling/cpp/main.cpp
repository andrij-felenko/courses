#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <span>
#include <expected>
#include <string>

namespace qcd {

/* Опорні фізичні параметри Стандартної Моделі */
struct StandardModelParameters {
    static constexpr double mass_charm  = 1.27;    // Маса c-кварка (ГеВ)
    static constexpr double mass_bottom = 4.18;    // Маса b-кварка (ГеВ)
    static constexpr double mass_top    = 172.5;   // Маса t-кварка (ГеВ)
    static constexpr double mass_z_boson = 91.1876; // Маса Z-бозона (ГеВ)
    static constexpr double alpha_s_mz_ref = 0.1179; // Експериментальне alpha_s(m_Z)
};

/* Результат розрахунку для конкретної енергетичної точки Q */
struct PointResult {
    double q_scale;
    int n_f;
    double lambda_qcd;
    double alpha_s_1loop;
    double alpha_s_2loop;
};

/* Клас для розрахунку еволюційного каскаду константи зв'язку */
class EvolutionCalculator {
public:
    static constexpr double get_beta0(int n_f) noexcept {
        return 11.0 - (2.0 / 3.0) * static_cast<double>(n_f);
    }

    static constexpr double get_beta1(int n_f) noexcept {
        return 102.0 - (38.0 / 3.0) * static_cast<double>(n_f);
    }

    static int get_active_flavors(double q) noexcept {
        if (q < StandardModelParameters::mass_charm)  return 3;
        if (q < StandardModelParameters::mass_bottom) return 4;
        if (q < StandardModelParameters::mass_top)    return 5;
        return 6;
    }

    static double compute_lambda_1loop(double alpha_ref, double q_ref, int n_f) noexcept {
        const double b0 = get_beta0(n_f);
        const double denom = (b0 / (4.0 * std::numbers::pi)) * alpha_ref;
        return q_ref * std::exp(-1.0 / (2.0 * denom));
    }

    static double compute_alpha_1loop(double q, double lambda, int n_f) noexcept {
        if (q <= lambda) {
            return 1.0;
        }
        const double b0 = get_beta0(n_f);
        const double t = std::log((q * q) / (lambda * lambda));
        return (4.0 * std::numbers::pi) / (b0 * t);
    }

    static double compute_alpha_2loop(double q, double lambda, int n_f) noexcept {
        if (q <= lambda) {
            return 1.0;
        }
        const double b0 = get_beta0(n_f);
        const double b1 = get_beta1(n_f);
        const double t = std::log((q * q) / (lambda * lambda));
        if (t <= 0.1) {
            return 1.0;
        }
        const double a1 = (4.0 * std::numbers::pi) / (b0 * t);
        const double corr = 1.0 - (b1 / (b0 * b0)) * (std::log(t) / t);
        return a1 * corr;
    }

    /* Безпечний метод обчислення для довільного набору енергетичних точок */
    static std::expected<std::vector<PointResult>, std::string> calculate(std::span<const double> q_scales) {
        if (q_scales.empty()) {
            return std::unexpected("Масив енергетичних масштабів Q не може бути порожнім.");
        }

        /* Каскадне узгодження порогових мас */
        const double lambda5 = compute_lambda_1loop(StandardModelParameters::alpha_s_mz_ref, StandardModelParameters::mass_z_boson, 5);

        const double alpha_b = compute_alpha_1loop(StandardModelParameters::mass_bottom, lambda5, 5);
        const double lambda4 = compute_lambda_1loop(alpha_b, StandardModelParameters::mass_bottom, 4);

        const double alpha_c = compute_alpha_1loop(StandardModelParameters::mass_charm, lambda4, 4);
        const double lambda3 = compute_lambda_1loop(alpha_c, StandardModelParameters::mass_charm, 3);

        const double alpha_t = compute_alpha_1loop(StandardModelParameters::mass_top, lambda5, 5);
        const double lambda6 = compute_lambda_1loop(alpha_t, StandardModelParameters::mass_top, 6);

        std::vector<PointResult> results;
        results.reserve(q_scales.size());

        for (double q : q_scales) {
            const int nf = get_active_flavors(q);
            double current_lambda = lambda5;

            switch (nf) {
                case 3: current_lambda = lambda3; break;
                case 4: current_lambda = lambda4; break;
                case 5: current_lambda = lambda5; break;
                case 6: current_lambda = lambda6; break;
                default: current_lambda = lambda5; break;
            }

            results.push_back(PointResult{
                .q_scale = q,
                .n_f = nf,
                .lambda_qcd = current_lambda,
                .alpha_s_1loop = compute_alpha_1loop(q, current_lambda, nf),
                .alpha_s_2loop = compute_alpha_2loop(q, current_lambda, nf)
            });
        }

        return results;
    }
};

} // namespace qcd

int main() {
    const std::vector<double> test_scales = { 0.5, 0.7, 1.0, 1.27, 2.0, 4.18, 10.0, 91.1876, 172.5, 500.0, 1000.0 };

    auto results_or_error = qcd::EvolutionCalculator::calculate(test_scales);
    if (!results_or_error) {
        std::cerr << "Помилка виконання: " << results_or_error.error() << '\n';
        return 1;
    }

    std::cout << "===================================================================================\n";
    std::cout << "         ЕВОЛЮЦІЯ ЕФЕКТИВНОЇ КОНСТАНТИ ЗВ'ЯЗКУ КХД alpha_s(Q²) (C++23)\n";
    std::cout << "===================================================================================\n";
    std::cout << std::left << std::setw(10) << "Q (ГеВ)"
              << std::setw(6)  << "n_f"
              << std::setw(14) << "Lambda (ГеВ)"
              << std::setw(16) << "alpha_s (1-loop)"
              << std::setw(16) << "alpha_s (2-loop)" << '\n';
    std::cout << std::string(83, '-') << '\n';

    for (const auto& item : *results_or_error) {
        std::cout << std::left << std::setw(10) << std::fixed << std::setprecision(2) << item.q_scale
                  << std::setw(6)  << item.n_f
                  << std::setw(14) << std::setprecision(4) << item.lambda_qcd
                  << std::setw(16) << std::setprecision(5) << item.alpha_s_1loop
                  << std::setw(16) << std::setprecision(5) << item.alpha_s_2loop << '\n';
    }
    std::cout << std::string(83, '-') << '\n';

    return 0;
}
