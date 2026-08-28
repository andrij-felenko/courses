#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <span>
#include <numbers>

class QuantumDotSimulator {
public:
    struct Params {
        double r_mean_nm{3.5};
        double sigma_r_nm{0.2};
        double e_g0_ev{1.74};
    };

    explicit QuantumDotSimulator(Params params) : params_(params) {}

    [[nodiscard]] double calculate_brus_gap(double r_nm) const noexcept {
        if (r_nm <= 0.2) return params_.e_g0_ev;
        const double conf = 3.73 / (r_nm * r_nm);
        const double coul = 0.276 / r_nm;
        return params_.e_g0_ev + conf - coul;
    }

    struct SpectrumData {
        std::vector<double> wavelengths;
        std::vector<double> intensities;
    };

    [[nodiscard]] SpectrumData generate_spectrum(std::size_t n_points) const {
        SpectrumData result;
        result.wavelengths.reserve(n_points);
        result.intensities.reserve(n_points);

        constexpr double wl_min = 400.0;
        constexpr double wl_max = 750.0;
        const double step = (wl_max - wl_min) / static_cast<double>(n_points - 1);

        for (std::size_t i = 0; i < n_points; ++i) {
            const double wl = wl_min + static_cast<double>(i) * step;
            const double energy_ev = 1239.84 / wl;
            double total_intensity = 0.0;

            for (int j = -30; j <= 30; ++j) {
                const double r = params_.r_mean_nm + static_cast<double>(j) * 0.01;
                if (r <= 0.3) continue;

                const double e_g = calculate_brus_gap(r);
                const double prob = (1.0 / (params_.sigma_r_nm * std::sqrt(2.0 * std::numbers::pi))) *
                              std::exp(-0.5 * std::pow((r - params_.r_mean_nm) / params_.sigma_r_nm, 2.0));

                constexpr double gamma = 0.03;
                const double lorentzian = (gamma / (2.0 * std::numbers::pi)) /
                                          (std::pow(energy_ev - e_g, 2.0) + std::pow(gamma / 2.0, 2.0));
                total_intensity += prob * lorentzian;
            }
            result.wavelengths.push_back(wl);
            result.intensities.push_back(total_intensity);
        }

        return result;
    }

private:
    Params params_;
};

int main() {
    auto sim = std::make_unique<QuantumDotSimulator>(QuantumDotSimulator::Params{.r_mean_nm = 3.0, .sigma_r_nm = 0.15});
    auto [wavelengths, intensities] = sim->generate_spectrum(5);

    std::cout << "Обчислення спектра квантової точки (C++20 RAII):\n";
    for (std::size_t i = 0; i < wavelengths.size(); ++i) {
        std::cout << "λ = " << wavelengths[i] << " нм -> I = " << intensities[i] << '\n';
    }

    return 0;
}
