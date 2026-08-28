#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <iomanip>
#include <algorithm>

namespace RayleighSim {

constexpr double PI = 3.14159265358979323846;
constexpr double ATM_SCALE_HEIGHT_M = 8500.0;
constexpr double MOLECULAR_DENSITY = 2.547e25; // м^-3
constexpr double CABANNES_FACTOR = 1.061;

struct ColorRGB {
    double r{0.0}, g{0.0}, b{0.0};
};

struct SpectralBand {
    double wavelength_nm;
    double beta_scattering_m1;
    double optical_depth;
    double transmittance;
};

class AtmosphereModel {
public:
    static double air_refractive_index(double wl_nm) noexcept {
        const double wl_um = wl_nm / 1000.0;
        const double sigma2 = 1.0 / (wl_um * wl_um);
        const double n_minus_1 = 8342.54 + 2406147.0 / (130.0 - sigma2) + 15998.0 / (38.9 - sigma2);
        return 1.0 + n_minus_1 * 1e-8;
    }

    static double calculate_rayleigh_beta(double wl_nm) noexcept {
        const double lambda_m = wl_nm * 1e-9;
        const double n = air_refractive_index(wl_nm);
        const double n2_minus_1 = n * n - 1.0;
        
        return (8.0 * std::pow(PI, 3.0) * std::pow(n2_minus_1, 2.0)) /
               (3.0 * MOLECULAR_DENSITY * std::pow(lambda_m, 4.0)) * CABANNES_FACTOR;
    }

    static std::array<double, 3> get_cie_xyz(double wl_nm) noexcept {
        const double w = wl_nm;
        const double x = 1.056 * std::exp(-0.5 * std::pow((w - 595.0) / 42.0, 2.0)) +
                         0.362 * std::exp(-0.5 * std::pow((w - 442.0) / 22.0, 2.0));
        const double y = 1.011 * std::exp(-0.5 * std::pow((w - 556.0) / 48.0, 2.0));
        const double z = 2.065 * std::exp(-0.5 * std::pow((w - 447.0) / 21.0, 2.0));
        return {x, y, z};
    }
};

class RayleighSpectrumSimulator {
private:
    double air_mass_;
    double start_wl_;
    double end_wl_;
    double step_wl_;

public:
    explicit RayleighSpectrumSimulator(double air_mass = 1.5,
                                       double start_wl = 380.0,
                                       double end_wl = 780.0,
                                       double step_wl = 5.0)
        : air_mass_(air_mass), start_wl_(start_wl), end_wl_(end_wl), step_wl_(step_wl) {}

    [[nodiscard]] std::vector<SpectralBand> compute_spectrum() const {
        std::vector<SpectralBand> spectrum;
        const size_t count = static_cast<size_t>((end_wl_ - start_wl_) / step_wl_) + 1;
        spectrum.reserve(count);

        for (size_t i = 0; i < count; ++i) {
            const double wl = start_wl_ + i * step_wl_;
            const double beta = AtmosphereModel::calculate_rayleigh_beta(wl);
            const double tau = beta * ATM_SCALE_HEIGHT_M;
            const double T = std::exp(-tau * air_mass_);

            spectrum.push_back({wl, beta, tau, T});
        }
        return spectrum;
    }

    [[nodiscard]] ColorRGB compute_sky_color(const std::vector<SpectralBand>& spectrum) const {
        double X = 0.0, Y = 0.0, Z = 0.0;

        for (const auto& band : spectrum) {
            auto [cx, cy, cz] = AtmosphereModel::get_cie_xyz(band.wavelength_nm);
            X += band.transmittance * cx * step_wl_;
            Y += band.transmittance * cy * step_wl_;
            Z += band.transmittance * cz * step_wl_;
        }

        const double max_val = std::max({X, Y, Z});
        if (max_val > 0.0) { X /= max_val; Y /= max_val; Z /= max_val; }

        auto gamma_correct = [](double v) {
            return (v <= 0.0031308) ? 12.92 * v : 1.055 * std::pow(v, 1.0 / 2.4) - 0.055;
        };

        ColorRGB rgb;
        rgb.r = std::clamp(gamma_correct( 3.2406 * X - 1.5372 * Y - 0.4986 * Z), 0.0, 1.0);
        rgb.g = std::clamp(gamma_correct(-0.9689 * X + 1.8758 * Y + 0.0415 * Z), 0.0, 1.0);
        rgb.b = std::clamp(gamma_correct( 0.0557 * X - 0.2040 * Y + 1.0570 * Z), 0.0, 1.0);

        return rgb;
    }
};

} // namespace RayleighSim

int main() {
    using namespace RayleighSim;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Atmospheric Rayleigh Scattering Simulator (C++20) ===\n\n";

    for (double am : {1.0, 1.5, 5.0, 15.0, 30.0}) {
        RayleighSpectrumSimulator sim(am);
        auto spectrum = sim.compute_spectrum();
        ColorRGB color = sim.compute_sky_color(spectrum);

        std::cout << "Air Mass m = " << std::setw(4) << am 
                  << " | Direct Light RGB: ("
                  << color.r << ", " << color.g << ", " << color.b << ")\n";
    }

    return 0;
}
