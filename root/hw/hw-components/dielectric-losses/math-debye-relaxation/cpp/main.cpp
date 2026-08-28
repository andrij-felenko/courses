#include <iostream>
#include <iomanip>
#include <vector>
#include <numbers>
#include <cmath>

struct DielectricModel {
    double eps_s{2200.0};      // Статична проникність
    double eps_inf{120.0};     // Оптична проникність
    double tau{1.5e-8};        // Час релаксації (с)
    double c_nom{100e-9};      // Номінальна ємність (Ф)
    double r_dc{0.012};        // Омічний опір металу на DC (Ом)
    double k_skin{1.2e-6};     // Коефіцієнт скін-ефекту (Ом/sqrt(Гц))
};

struct CapacitorMetrics {
    double f{};
    double eps_real{};
    double eps_imag{};
    double tan_delta{};
    double r_di{};
    double r_ohm{};
    double esr{};
    double q_factor{};
};

class DebyeLossCalculator {
public:
    explicit DebyeLossCalculator(DielectricModel model) : model_{model} {}

    [[nodiscard]] CapacitorMetrics compute(double freq_hz) const noexcept {
        CapacitorMetrics res{};
        res.f = freq_hz;

        const double omega = 2.0 * std::numbers::pi * freq_hz;
        const double wt = omega * model_.tau;
        const double wt_sq = wt * wt;

        // Формули Дебая
        res.eps_real = model_.eps_inf + (model_.eps_s - model_.eps_inf) / (1.0 + wt_sq);
        res.eps_imag = (model_.eps_s - model_.eps_inf) * wt / (1.0 + wt_sq);
        res.tan_delta = res.eps_imag / res.eps_real;

        // Розрахунок опорів
        res.r_di = res.tan_delta / (omega * model_.c_nom);
        res.r_ohm = model_.r_dc + model_.k_skin * std::sqrt(freq_hz);
        res.esr = res.r_di + res.r_ohm;
        res.q_factor = 1.0 / res.tan_delta;

        return res;
    }

private:
    DielectricModel model_;
};

int main() {
    const DielectricModel x7r_model{
        .eps_s = 2200.0,
        .eps_inf = 120.0,
        .tau = 1.5e-8,
        .c_nom = 100e-9,
        .r_dc = 0.012,
        .k_skin = 1.2e-6
    };

    const DebyeLossCalculator calc{x7r_model};
    const std::vector<double> test_freqs{1e2, 1e3, 1e4, 1e5, 1e6, 1e7};

    std::cout << std::left
              << std::setw(14) << "Частота (Гц)"
              << std::setw(10) << "eps'"
              << std::setw(10) << "eps''"
              << std::setw(13) << "tan(delta)"
              << std::setw(13) << "R_di (Ом)"
              << std::setw(13) << "ESR (Ом)"
              << "Q\n";
    std::cout << std::string(80, '-') << "\n";

    for (const double f : test_freqs) {
        const auto m = calc.compute(f);
        std::cout << std::left << std::fixed
                  << std::setw(14) << std::setprecision(0) << m.f
                  << std::setw(10) << std::setprecision(1) << m.eps_real
                  << std::setw(10) << std::setprecision(2) << m.eps_imag
                  << std::setw(13) << std::setprecision(5) << m.tan_delta
                  << std::setw(13) << std::setprecision(5) << m.r_di
                  << std::setw(13) << std::setprecision(5) << m.esr
                  << std::setprecision(1) << m.q_factor << "\n";
    }

    return 0;
}
