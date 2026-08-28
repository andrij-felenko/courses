#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>

namespace magnetic {

constexpr double MU_0 = 1.25663706212e-6; // Гн/м

struct SimulationPoint {
    double H;       // Напруженість поля, А/м
    double M;       // Намагніченість, А/м
    double B;       // Магнітна індукція, Тл
    double mu_diff; // Відносна диференціальна проникність (безрозмірна)
};

class JilesAthertonSimulator {
public:
    struct Parameters {
        double M_s{1.6e6};   // Намагніченість насичення, А/м
        double a{1100.0};    // Параметр дисперсії Ланжевена, А/м
        double k{400.0};     // Коефіцієнт піннінгу (коерцитивність), А/м
        double c{0.2};       // Коефіцієнт зворотності (0..1)
        double alpha{1.6e-3};// Міждоменний зв'язок
    };

    explicit JilesAthertonSimulator(Parameters params) : p_(params) {}

    void step(double H_next, double dH) {
        if (std::abs(dH) < 1e-12) return;

        const double delta = (dH > 0.0) ? 1.0 : -1.0;
        const double H_e = H_next + p_.alpha * M_;
        const double M_an = calculateMan(H_e);
        const double dMan_dHe = calculateDManDHe(H_e);

        const double diff = M_an - M_irr_;
        double dMirr_dHe = 0.0;
        if (delta * diff > 0.0) {
            dMirr_dHe = diff / (delta * p_.k);
        }

        const double numerator = (1.0 - p_.c) * dMirr_dHe + p_.c * dMan_dHe;
        const double denominator = 1.0 - p_.alpha * ((1.0 - p_.c) * dMirr_dHe + p_.c * dMan_dHe);
        
        double dM_dH = 0.0;
        if (std::abs(denominator) > 1e-9) {
            dM_dH = std::max(0.0, numerator / denominator);
        }

        M_ += dM_dH * dH;
        if (std::abs(1.0 - p_.c) > 1e-6) {
            M_irr_ = (M_ - p_.c * M_an) / (1.0 - p_.c);
        }
    }

    [[nodiscard]] double magnetization() const noexcept { return M_; }
    [[nodiscard]] double induction(double H) const noexcept { return MU_0 * (H + M_); }

private:
    [[nodiscard]] double calculateMan(double H_e) const noexcept {
        if (std::abs(H_e) < 1e-6) return 0.0;
        const double z = H_e / p_.a;
        if (std::abs(z) > 100.0) return p_.M_s * (z > 0 ? 1.0 : -1.0);
        return p_.M_s * (1.0 / std::tanh(z) - 1.0 / z);
    }

    [[nodiscard]] double calculateDManDHe(double H_e) const noexcept {
        if (std::abs(H_e) < 1e-6) return p_.M_s / (3.0 * p_.a);
        const double z = H_e / p_.a;
        if (std::abs(z) > 100.0) return 0.0;
        const double coth_z = 1.0 / std::tanh(z);
        const double d_coth = 1.0 - coth_z * coth_z;
        const double d_inv_z = -1.0 / (z * z);
        return (p_.M_s / p_.a) * (d_coth - d_inv_z);
    }

    Parameters p_;
    double M_{0.0};
    double M_irr_{0.0};
};

} // namespace magnetic

int main() {
    using namespace magnetic;

    JilesAthertonSimulator::Parameters params{
        .M_s = 1.6e6,
        .a = 1100.0,
        .k = 400.0,
        .c = 0.2,
        .alpha = 1.6e-3
    };

    JilesAthertonSimulator sim(params);

    constexpr int steps_per_cycle = 2000;
    constexpr int total_cycles = 3;
    constexpr double H_peak = 3000.0; // А/м

    std::vector<SimulationPoint> loop_points;
    loop_points.reserve(steps_per_cycle);

    double prev_H = 0.0;
    double prev_B = 0.0;
    double energy_loss = 0.0;

    for (int cycle = 0; cycle < total_cycles; ++cycle) {
        for (int i = 0; i < steps_per_cycle; ++i) {
            const double angle = 2.0 * std::numbers::pi * static_cast<double>(i) / steps_per_cycle;
            const double H = H_peak * std::sin(angle);
            const double dH = H - prev_H;

            sim.step(H, dH);
            const double B = sim.induction(H);

            if (cycle == total_cycles - 1) {
                if (i > 0) {
                    energy_loss += 0.5 * (H + prev_H) * (B - prev_B);
                }
                const double mu_diff = (std::abs(dH) > 1e-6) ? (B - prev_B) / (dH * MU_0) : 1.0;
                loop_points.push_back({H, sim.magnetization(), B, mu_diff});
            }

            prev_H = H;
            prev_B = B;
        }
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "# Результати симуляції гістерезису (C++20)\n";
    std::cout << "# Точок у петлі: " << loop_points.size() << "\n";
    std::cout << "# Втрати енергії на цикл: " << std::abs(energy_loss) << " Дж/м^3\n";
    std::cout << "# Потужність втрат при 50 Гц: " << (std::abs(energy_loss) * 50.0 / 1000.0) << " кВт/м^3\n\n";

    std::cout << "# Зріз даних петлі (H, B, mu_diff):\n";
    for (size_t i = 0; i < loop_points.size(); i += 100) {
        const auto& pt = loop_points[i];
        std::cout << "H = " << std::setw(8) << pt.H << " A/m | "
                  << "B = " << std::setw(6) << std::setprecision(3) << pt.B << " T | "
                  << "mu_diff = " << std::setw(8) << std::setprecision(1) << pt.mu_diff << "\n";
    }

    return 0;
}
