#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <numbers>
#include <optional>
#include <span>
#include <iomanip>

enum class EndCorrectionType {
    Unflanged, // 0.6133 * r
    Flanged    // 0.8488 * r
};

struct HelmholtzConfig {
    double cavity_volume_m3{0.001};
    double neck_length_m{0.05};
    double neck_radius_m{0.01};
    double air_density_kg_m3{1.204};
    double sound_speed_m_s{343.2};
    double air_viscosity_pa_s{1.81e-5};
    EndCorrectionType inner_end{EndCorrectionType::Flanged};
    EndCorrectionType outer_end{EndCorrectionType::Unflanged};
};

struct HelmholtzResult {
    double area_m2{0.0};
    double delta_l_in_m{0.0};
    double delta_l_out_m{0.0};
    double effective_length_m{0.0};
    double acoustic_mass{0.0};
    double acoustic_compliance{0.0};
    double resonance_freq_hz{0.0};
    double quality_factor_q{0.0};
};

struct SpectrumPoint {
    double frequency_hz{0.0};
    std::complex<double> acoustic_impedance{0.0, 0.0};
    double absorption_coeff{0.0};
};

class HelmholtzResonator {
public:
    explicit HelmholtzResonator(HelmholtzConfig config)
        : config_(std::move(config)) {
        calculate_parameters();
    }

    [[nodiscard]] const HelmholtzResult& result() const noexcept { return result_; }
    [[nodiscard]] const HelmholtzConfig& config() const noexcept { return config_; }

    [[nodiscard]] SpectrumPoint calculate_at(double frequency_hz) const {
        const double omega = 2.0 * std::numbers::pi * frequency_hz;
        
        // Втрати випромінювання та в'язкого тертя
        const double r_rad = (config_.air_density_kg_m3 * omega * omega) / (2.0 * std::numbers::pi * config_.sound_speed_m_s);
        const double r_visc = (std::sqrt(2.0 * config_.air_density_kg_m3 * config_.air_viscosity_pa_s * omega) / 
                              (std::numbers::pi * std::pow(config_.neck_radius_m, 3))) * result_.effective_length_m;
        const double r_total = r_rad + r_visc;

        const double x_reactance = omega * result_.acoustic_mass - (1.0 / (omega * result_.acoustic_compliance));
        
        const double z_char = (config_.air_density_kg_m3 * config_.sound_speed_m_s) / result_.area_m2;
        const double alpha = (4.0 * r_total * z_char) / 
                       (std::pow(2.0 * r_total + z_char, 2) + x_reactance * x_reactance);

        return SpectrumPoint{
            .frequency_hz = frequency_hz,
            .acoustic_impedance = std::complex<double>(r_total, x_reactance),
            .absorption_coeff = alpha
        };
    }

    [[nodiscard]] std::vector<SpectrumPoint> generate_spectrum(double start_freq_hz, double end_freq_hz, std::size_t points) const {
        std::vector<SpectrumPoint> spectrum;
        spectrum.reserve(points);

        for (std::size_t i = 0; i < points; ++i) {
            const double f = start_freq_hz + (end_freq_hz - start_freq_hz) * (static_cast<double>(i) / static_cast<double>(points - 1));
            spectrum.push_back(calculate_at(f));
        }
        return spectrum;
    }

private:
    static constexpr double end_correction_factor(EndCorrectionType type) noexcept {
        return (type == EndCorrectionType::Flanged) ? 0.848826 : 0.613300;
    }

    void calculate_parameters() {
        result_.area_m2 = std::numbers::pi * config_.neck_radius_m * config_.neck_radius_m;
        result_.delta_l_in_m = end_correction_factor(config_.inner_end) * config_.neck_radius_m;
        result_.delta_l_out_m = end_correction_factor(config_.outer_end) * config_.neck_radius_m;
        result_.effective_length_m = config_.neck_length_m + result_.delta_l_in_m + result_.delta_l_out_m;

        result_.acoustic_mass = (config_.air_density_kg_m3 * result_.effective_length_m) / result_.area_m2;
        result_.acoustic_compliance = config_.cavity_volume_m3 / (config_.air_density_kg_m3 * std::pow(config_.sound_speed_m_s, 2));

        const double omega0 = 1.0 / std::sqrt(result_.acoustic_mass * result_.acoustic_compliance);
        result_.resonance_freq_hz = omega0 / (2.0 * std::numbers::pi);

        const double r_rad = (config_.air_density_kg_m3 * omega0 * omega0) / (2.0 * std::numbers::pi * config_.sound_speed_m_s);
        const double r_visc = (std::sqrt(2.0 * config_.air_density_kg_m3 * config_.air_viscosity_pa_s * omega0) / 
                              (std::numbers::pi * std::pow(config_.neck_radius_m, 3))) * result_.effective_length_m;
        result_.quality_factor_q = (omega0 * result_.acoustic_mass) / (r_rad + r_visc);
    }

    HelmholtzConfig config_;
    HelmholtzResult result_;
};

int main() {
    const HelmholtzConfig config{
        .cavity_volume_m3 = 0.001,
        .neck_length_m = 0.05,
        .neck_radius_m = 0.01
    };

    const HelmholtzResonator resonator(config);
    const auto& res = resonator.result();

    std::cout << "=== C++ акустичний аналіз резонатора ===\n";
    std::cout << "Власна частота f_H: " << std::fixed << std::setprecision(2) << res.resonance_freq_hz << " Гц\n";
    std::cout << "Добротність Q:         " << res.quality_factor_q << "\n\n";

    const auto spectrum = resonator.generate_spectrum(100.0, 300.0, 5);

    std::cout << std::setw(12) << "Частота (Гц)" << " | "
              << std::setw(17) << "Re(Z_A) (Па·с/м³)" << " | "
              << std::setw(17) << "Im(Z_A) (Па·с/м³)" << " | "
              << std::setw(10) << "Поглинання α\n";
    std::cout << std::string(65, '-') << "\n";

    for (const auto& pt : spectrum) {
        std::cout << std::setw(12) << pt.frequency_hz << " | "
                  << std::scientific << std::setprecision(2)
                  << std::setw(17) << pt.acoustic_impedance.real() << " | "
                  << std::setw(17) << pt.acoustic_impedance.imag() << " | "
                  << std::fixed << std::setprecision(4)
                  << std::setw(10) << pt.absorption_coeff << "\n";
    }

    return 0;
}
