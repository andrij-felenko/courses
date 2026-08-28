#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>

class MachZehnderInterferometer {
public:
    struct Measurement {
        double i1{0.0};
        double i2{0.0};
        double diff_signal{0.0};
    };

    explicit MachZehnderInterferometer(double wavelength_nm = 632.8, double arm_length_mm = 100.0)
        : wavelength_{wavelength_nm * 1e-9},
          arm_length_{arm_length_mm * 1e-3},
          k_{2.0 * std::numbers::pi / wavelength_} {}

    [[nodiscard]] Measurement simulate(double delta_n) const {
        const double phi_a = k_ * (1.0 + delta_n) * arm_length_;
        const double phi_b = k_ * 1.0 * arm_length_;

        constexpr double inv_sqrt2 = 1.0 / std::numbers::sqrt2;
        constexpr std::complex<double> e_in{1.0, 0.0};
        constexpr std::complex<double> i_unit{0.0, 1.0};

        // BS1: розділення променя
        const std::complex<double> e1_bs1 = e_in * inv_sqrt2;
        const std::complex<double> e2_bs1 = e_in * (i_unit * inv_sqrt2);

        // Фазовий набіг у плечах
        const std::complex<double> e1_arm = e1_bs1 * std::exp(i_unit * phi_a);
        const std::complex<double> e2_arm = e2_bs1 * std::exp(i_unit * phi_b);

        // BS2: зведення хвиль
        const std::complex<double> e_out1 = inv_sqrt2 * (e1_arm * i_unit + e2_arm);
        const std::complex<double> e_out2 = inv_sqrt2 * (e1_arm + e2_arm * i_unit);

        const double i1 = std::norm(e_out1);
        const double i2 = std::norm(e_out2);

        return Measurement{.i1 = i1, .i2 = i2, .diff_signal = i1 - i2};
    }

    [[nodiscard]] std::vector<Measurement> simulate_sweep(std::span<const double> delta_n_values) const {
        std::vector<Measurement> results;
        results.reserve(delta_n_values.size());
        for (const double dn : delta_n_values) {
            results.push_back(simulate(dn));
        }
        return results;
    }

private:
    double wavelength_;
    double arm_length_;
    double k_;
};

int main() {
    const MachZehnderInterferometer mzi{632.8, 100.0};
    const std::vector<double> dn_steps = {0.0, 1e-6, 2e-6, 3e-6, 4e-6, 5e-6, 6e-6, 7e-6, 8e-6, 9e-6, 10e-6};

    const auto results = mzi.simulate_sweep(dn_steps);

    std::cout << "Чисельне моделювання інтерферометра (C++20 RAII):\n";
    std::cout << std::setw(12) << "delta_n" << " | "
              << std::setw(8) << "I1" << " | "
              << std::setw(8) << "I2" << " | "
              << std::setw(12) << "Diff Signal" << "\n";
    std::cout << std::string(48, '-') << "\n";

    for (size_t idx = 0; idx < dn_steps.size(); ++idx) {
        std::cout << std::scientific << std::setprecision(4) << std::setw(12) << dn_steps[idx] << " | "
                  << std::fixed << std::setprecision(4) << std::setw(8) << results[idx].i1 << " | "
                  << std::setw(8) << results[idx].diff_signal << "\n";
    }

    return 0;
}
