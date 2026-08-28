// C++17: Обчислення коефіцієнта відбиття та КСХ
#include <iostream>
#include <complex>
#include <cmath>
#include <iomanip>
#include <numbers>

struct SmithPoint {
    std::complex<double> gamma;
    double vswr;
    double return_loss_db;
};

class SmithAnalyzer {
public:
    static SmithPoint analyze(std::complex<double> z_load, double z0 = 50.0) {
        const std::complex<double> z_norm = z_load / z0;
        const std::complex<double> gamma = (z_norm - 1.0) / (z_norm + 1.0);
        const double g_abs = std::abs(gamma);

        if (g_abs >= 0.9999) {
            return {gamma, 999.0, 0.0};
        }

        const double vswr = (1.0 + g_abs) / (1.0 - g_abs);
        const double rl_db = -20.0 * std::log10(g_abs);
        return {gamma, vswr, rl_db};
    }

    static void print_summary(std::complex<double> z_load, double z0 = 50.0) {
        const auto pt = analyze(z_load, z0);
        const double angle_deg = std::arg(pt.gamma) * 180.0 / std::numbers::pi;

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Z = " << z_load.real() << " + j" << z_load.imag() << " Ом"
                  << " | Γ = " << std::abs(pt.gamma) << " ∠" << angle_deg << "°"
                  << " | КСХ = " << pt.vswr << ":1"
                  << " | RL = " << pt.return_loss_db << " дБ\n";
    }
};
