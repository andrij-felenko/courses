#include <iostream>
#include <vector>
#include <string_view>
#include <cmath>
#include <iomanip>
#include <expected>
#include <optional>

namespace quantum {

struct Isotope {
    std::string_view name;
    double nuclear_mass_kg;
    int atomic_number;
};

struct SpectralLine {
    int n1;
    int n2;
    double wavelength_vac_nm;
    double wavelength_air_nm;
    double energy_ev;
};

enum class SpectralError {
    InvalidQuantumNumbers,
    CalculationOverflow
};

class SpectrumCalculator {
public:
    static constexpr double R_INF = 10973731.568160;  // м⁻¹
    static constexpr double MASS_E = 9.1093837015e-31; // кг
    static constexpr double MASS_P = 1.67262192369e-27;// кг
    static constexpr double MASS_D = 3.3435837724e-27; // кг
    static constexpr double ALPHA = 7.2973525693e-3;   // α ≈ 1/137
    static constexpr double SPEED_OF_LIGHT = 299792458.0; // м/с
    static constexpr double EV_TO_JOULE = 1.602176634e-19;
    static constexpr double PLANCK_H = 6.62607015e-34;

    [[nodiscard]] static constexpr double get_reduced_rydberg(const Isotope& iso) noexcept {
        const double mu_ratio = 1.0 / (1.0 + MASS_E / iso.nuclear_mass_kg);
        const double z = static_cast<double>(iso.atomic_number);
        return R_INF * (z * z) * mu_ratio;
    }

    [[nodiscard]] static double calculate_air_refractive_index(double lambda_vac_nm) noexcept {
        if (lambda_vac_nm <= 0.0) return 1.0;
        const double sigma = 1000.0 / lambda_vac_nm;
        const double s2 = sigma * sigma;
        const double n_minus_1 = 1.0e-8 * (8342.54 + 2406147.0 / (130.0 - s2) + 15998.0 / (38.9 - s2));
        return 1.0 + n_minus_1;
    }

    [[nodiscard]] static std::expected<SpectralLine, SpectralError> 
    compute_line(const Isotope& iso, int n1, int n2) noexcept {
        if (n1 <= 0 || n2 <= n1) {
            return std::unexpected(SpectralError::InvalidQuantumNumbers);
        }

        const double r_eff = get_reduced_rydberg(iso);
        const double wavenumber = r_eff * (1.0 / (static_cast<double>(n1 * n1)) - 1.0 / (static_cast<double>(n2 * n2)));

        if (wavenumber <= 0.0) {
            return std::unexpected(SpectralError::CalculationOverflow);
        }

        const double lambda_vac_nm = (1.0 / wavenumber) * 1.0e9;
        const double n_air = calculate_air_refractive_index(lambda_vac_nm);
        const double lambda_air_nm = lambda_vac_nm / n_air;
        const double energy_ev = (wavenumber * PLANCK_H * SPEED_OF_LIGHT) / EV_TO_JOULE;

        return SpectralLine{
            .n1 = n1,
            .n2 = n2,
            .wavelength_vac_nm = lambda_vac_nm,
            .wavelength_air_nm = lambda_air_nm,
            .energy_ev = energy_ev
        };
    }

    [[nodiscard]] static constexpr double 
    fine_structure_shift_ev(int z, int n, double j) noexcept {
        if (n <= 0 || j < 0.5) return 0.0;
        const double z_double = static_cast<double>(z);
        const double z_alpha = z_double * ALPHA;
        const double e_n = -13.605693 * ((z_double * z_double) / static_cast<double>(n * n));
        const double factor = ((z_alpha * z_alpha) / static_cast<double>(n)) * 
                              ((1.0 / (j + 0.5)) - (0.75 / static_cast<double>(n)));
        return e_n * factor;
    }
};

} // namespace quantum

int main() {
    using namespace quantum;

    constexpr Isotope protium{"Протій (1H)", SpectrumCalculator::MASS_P, 1};
    constexpr Isotope deuterium{"Дейтерій (2H)", SpectrumCalculator::MASS_D, 1};

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Спектральні лінії серії Бальмера (C++23) ===\n\n";

    for (int n2 = 3; n2 <= 6; ++n2) {
        auto res_h = SpectrumCalculator::compute_line(protium, 2, n2);
        auto res_d = SpectrumCalculator::compute_line(deuterium, 2, n2);

        if (res_h && res_d) {
            std::cout << protium.name << " " << res_h->n1 << "->" << res_h->n2 
                      << " | λ_vac: " << res_h->wavelength_vac_nm << " нм"
                      << " | λ_air: " << res_h->wavelength_air_nm << " нм\n";
            std::cout << deuterium.name << " " << res_d->n1 << "->" << res_d->n2 
                      << " | λ_vac: " << res_d->wavelength_vac_nm << " нм"
                      << " | λ_air: " << res_d->wavelength_air_nm << " нм\n";
            
            const double shift_pm = (res_h->wavelength_vac_nm - res_d->wavelength_vac_nm) * 1000.0;
            std::cout << "  └─ Ізотопічний зсув H-D: " << shift_pm << " пм\n\n";
        }
    }

    return 0;
}
