#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <memory>
#include <span >

namespace physics {

constexpr double PLANCK_H = 6.62607015e-34;
constexpr double SPEED_LIGHT = 299792458.0;
constexpr double ELEC_CHARGE = 1.602176634e-19;

struct SpectrumPoint {
    double energy_kev{0.0};
    double wavelength_nm{0.0};
    double raw_intensity{0.0};
    double filtered_intensity{0.0};
};

class XRaySpectrumSimulator {
public:
    struct Configuration {
        double voltage_kv{40.0};
        double current_ma{10.0};
        double target_z{74.0}; /* Вольфрам */
        double al_filter_mm{1.0};
        std::size_t num_bins{100};
    };

    explicit XRaySpectrumSimulator(Configuration config) : config_(config) {}

    [[nodiscard]] double duane_hunt_limit_nm() const noexcept {
        if (config_.voltage_kv <= 0.0) return 0.0;
        const double voltage_volts = config_.voltage_kv * 1000.0;
        return ((PLANCK_H * SPEED_LIGHT) / (ELEC_CHARGE * voltage_volts)) * 1e9;
    }

    [[nodiscard]] std::vector<SpectrumPoint> compute_spectrum() const {
        std::vector<SpectrumPoint> spectrum;
        spectrum.reserve(config_.num_bins);

        const double max_energy = config_.voltage_kv;
        const double step_kev = max_energy / static_cast<double>(config_.num_bins);
        const double filter_cm = config_.al_filter_mm / 10.0;
        constexpr double k_cramers = 1e-9;

        for (std::size_t i = 0; i < config_.num_bins; ++i) {
            const double energy = (i + 0.5) * step_kev;
            const double wavelength = 1239.84 / energy;

            const double raw_i = (energy <= max_energy)
                ? k_cramers * config_.target_z * (config_.current_ma * 1e-3) * (max_energy - energy)
                : 0.0;

            const double mu = attenuation_coefficient(energy);
            const double transmission = std::exp(-mu * filter_cm);
            const double filtered_i = raw_i * transmission;

            spectrum.push_back({energy, wavelength, raw_i, filtered_i});
        }

        return spectrum;
    }

    [[nodiscard]] static double total_power(std::span<const SpectrumPoint> points, double step_kev) noexcept {
        double power = 0.0;
        for (const auto& pt : points) {
            power += pt.filtered_intensity * step_kev;
        }
        return power;
    }

private:
    Configuration config_;

    [[nodiscard]] static double attenuation_coefficient(double energy_kev) noexcept {
        if (energy_kev <= 0.1) return 1000.0;
        return 500.0 * std::pow(10.0 / energy_kev, 2.8);
    }
};

} // namespace physics

int main() {
    using namespace physics;

    XRaySpectrumSimulator::Configuration config{
        .voltage_kv = 50.0,
        .current_ma = 10.0,
        .target_z = 74.0,
        .al_filter_mm = 1.5,
        .num_bins = 10
    };

    XRaySpectrumSimulator sim(config);
    const auto spectrum = sim.compute_spectrum();
    const double step_kev = config.voltage_kv / static_cast<double>(config.num_bins);
    const double power = XRaySpectrumSimulator::total_power(spectrum, step_kev);

    std::cout << "=== Спектр гальмівного випромінювання (C++20) ===\n";
    std::cout << "Напруга: " << config.voltage_kv << " кВ, Анод: Z=" << config.target_z << "\n";
    std::cout << "Межа Дуана — Ганта: " << std::fixed << std::setprecision(4)
              << sim.duane_hunt_limit_nm() << " нм\n\n";

    std::cout << std::left << std::setw(14) << "Енергія(кеВ)"
              << std::setw(14) << "Довжина(нм)"
              << std::setw(20) << "Первинна(Вт/кеВ)"
              << std::setw(20) << "Фільтрована(Вт/кеВ)" << "\n";

    for (const auto& pt : spectrum) {
        std::cout << std::left << std::setw(14) << std::setprecision(2) << pt.energy_kev
                  << std::setw(14) << std::setprecision(4) << pt.wavelength_nm
                  << std::scientific << std::setprecision(6)
                  << std::setw(20) << pt.raw_intensity
                  << std::setw(20) << pt.filtered_intensity << "\n";
    }

    std::cout << "\nЗагальна випромінена потужність: " << std::fixed << std::setprecision(6)
              << power << " Вт\n";

    return 0;
}
