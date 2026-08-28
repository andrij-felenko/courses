#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>
#include <string_view>
#include <algorithm>

namespace physics {

constexpr double HBAR_C = 0.19732698; // ҐеВ * фм
constexpr double M_Z = 91.1876;       // ҐеВ
constexpr double ALPHA_S_MZ = 0.1179;

struct InteractionParams {
    double energy_gev;
    double boson_mass_gev;
    double target_mass_gev;
    double coupling;
};

class InteractionCalculator {
public:
    [[nodiscard]] static constexpr std::expected<double, std::string_view> 
    calculate_yukawa_cross_section(const InteractionParams& params, double angle_rad) noexcept {
        if (params.energy_gev <= 0.0 || params.boson_mass_gev < 0.0) {
            return std::unexpected("Некоректні фізичні параметри енергії або маси");
        }
        
        const double k = std::sqrt(params.energy_gev * params.energy_gev);
        const double q_transfer = 2.0 * k * std::sin(angle_rad / 2.0);
        const double denominator = q_transfer * q_transfer + params.boson_mass_gev * params.boson_mass_gev;
        
        if (denominator <= 0.0) {
            return std::unexpected("Нульовий знаменник амплітуди");
        }
        
        const double amplitude_fm = (2.0 * params.target_mass_gev * params.coupling * HBAR_C) / denominator;
        const double cross_section_fm2 = amplitude_fm * amplitude_fm;
        return cross_section_fm2 * 0.01; // Перетворення у барни
    }

    [[nodiscard]] static constexpr double running_coupling_qcd(double q_gev, int n_flavors = 5) noexcept {
        if (q_gev <= 0.3) return 1.0;
        
        const double beta_0 = 11.0 - (2.0 / 3.0) * static_cast<double>(n_flavors);
        const double ln_ratio = std::log((q_gev / M_Z) * (q_gev / M_Z));
        const double denom = 1.0 + (beta_0 * ALPHA_S_MZ / (4.0 * std::numbers::pi)) * ln_ratio;
        
        return ALPHA_S_MZ / std::max(0.01, denom);
    }
};

} // namespace physics

int main() {
    using namespace physics;
    constexpr InteractionParams params{.energy_gev = 0.5, .boson_mass_gev = 0.1395, .target_mass_gev = 0.938, .coupling = 1.0};
    const std::vector<double> angles_deg{10.0, 30.0, 60.0, 90.0, 120.0, 150.0};
    
    std::cout << "=== Modern C++20 Обчислення перерізів розсіяння ===\n";
    std::cout << std::scientific << std::setprecision(6);
    
    for (double deg : angles_deg) {
        const double rad = deg * std::numbers::pi / 180.0;
        auto result = InteractionCalculator::calculate_yukawa_cross_section(params, rad);
        if (result) {
            std::cout << "Кут " << std::setw(3) << static_cast<int>(deg) << " deg: dsigma/dOmega = " << *result << " barn/sr\n";
        }
    }
    
    std::cout << "\nЗалежність α_s(Q) від енергії (QCD):\n" << std::fixed << std::setprecision(4);
    for (double q : {1.0, 5.0, 10.0, 91.2, 500.0, 10000.0}) {
        std::cout << "  Q = " << std::setw(7) << q << " GeV: alpha_s(Q) = " << InteractionCalculator::running_coupling_qcd(q) << "\n";
    }
    return 0;
}
