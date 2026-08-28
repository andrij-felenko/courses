#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <string_view>
#include <iomanip>
#include <expected>

namespace OpticalPhysics {

constexpr double PLANCK_H = 6.62607015e-34;
constexpr double SPEED_OF_LIGHT_C = 299792458.0;
constexpr double ELEMENTARY_CHARGE_E = 1.602176634e-19;
constexpr double BOLTZMANN_KB = 1.380649e-23;

struct OpticalComponent {
    std::string_view name;
    double transmittance; // 0.0 .. 1.0
};

struct SystemParameters {
    double wavelength_m{1550e-9};
    double power_tx_w{0.050};
    double distance_m{2000.0};
    double atten_db_per_km{2.5};
    double divergence_rad{0.0015};
    double beam_waist_m{0.005};
    double rx_aperture_m{0.100};
    
    double quantum_efficiency{0.85};
    double dark_current_a{2e-9};
    double load_resistor_ohm{50.0};
    double temperature_k{300.0};
    double bandwidth_hz{125e6};

    std::vector<OpticalComponent> optical_cascade;
};

struct CalculationReport {
    double photon_energy_j;
    double rx_power_w;
    double rx_power_dbm;
    double photoelectrons_per_bit;
    
    double sigma_shot_e;
    double sigma_dark_e;
    double sigma_thermal_e;
    double sigma_total_e;
    
    double snr_linear;
    double snr_db;
    double link_margin_db;
};

enum class CalculationError {
    InvalidWavelength,
    InvalidQuantumEfficiency,
    ZeroBandwidth
};

class PhotonBudgetSolver {
public:
    static std::expected<CalculationReport, CalculationError> 
    compute(const SystemParameters& sys, double required_snr_db) noexcept 
    {
        if (sys.wavelength_m <= 0.0) return std::unexpected(CalculationError::InvalidWavelength);
        if (sys.quantum_efficiency <= 0.0 || sys.quantum_efficiency > 1.0) 
            return std::unexpected(CalculationError::InvalidQuantumEfficiency);
        if (sys.bandwidth_hz <= 0.0) return std::unexpected(CalculationError::ZeroBandwidth);

        CalculationReport r{};
        r.photon_energy_j = (PLANCK_H * SPEED_OF_LIGHT_C) / sys.wavelength_m;
        
        double cascade_eff = 1.0;
        for (const auto& comp : sys.optical_cascade) {
            cascade_eff *= comp.transmittance;
        }

        const double dist_km = sys.distance_m / 1000.0;
        const double channel_loss_db = sys.atten_db_per_km * dist_km;
        const double channel_eff = std::pow(10.0, -channel_loss_db / 10.0);

        const double spot_radius = sys.beam_waist_m + sys.distance_m * std::tan(sys.divergence_rad);
        const double spot_area = std::numbers::pi * spot_radius * spot_radius;
        const double rx_radius = sys.rx_aperture_m / 2.0;
        const double rx_area = std::numbers::pi * rx_radius * rx_radius;
        const double geom_eff = std::min(1.0, rx_area / spot_area);

        r.rx_power_w = sys.power_tx_w * cascade_eff * channel_eff * geom_eff;
        r.rx_power_dbm = 10.0 * std::log10(r.rx_power_w / 1e-3);
        const double rx_photon_rate = r.rx_power_w / r.photon_energy_j;

        const double dt = 1.0 / (2.0 * sys.bandwidth_hz);
        r.photoelectrons_per_bit = sys.quantum_efficiency * rx_photon_rate * dt;

        r.sigma_shot_e = std::sqrt(r.photoelectrons_per_bit);
        const double dark_electrons = (sys.dark_current_a * dt) / ELEMENTARY_CHARGE_E;
        r.sigma_dark_e = std::sqrt(dark_electrons);

        const double thermal_sq = (4.0 * BOLTZMANN_KB * sys.temperature_k * sys.bandwidth_hz) / sys.load_resistor_ohm;
        const double thermal_rms = std::sqrt(thermal_sq);
        r.sigma_thermal_e = (thermal_rms * dt) / ELEMENTARY_CHARGE_E;

        r.sigma_total_e = std::hypot(r.sigma_shot_e, r.sigma_dark_e, r.sigma_thermal_e);
        
        r.snr_linear = r.photoelectrons_per_bit / r.sigma_total_e;
        r.snr_db = 20.0 * std::log10(r.snr_linear);
        r.link_margin_db = r.snr_db - required_snr_db;

        return r;
    }
};

} // namespace OpticalPhysics

int main() {
    using namespace OpticalPhysics;

    SystemParameters params{
        .wavelength_m = 1550e-9,
        .power_tx_w = 0.050,
        .distance_m = 2000.0,
        .atten_db_per_km = 2.5,
        .divergence_rad = 0.0015,
        .beam_waist_m = 0.005,
        .rx_aperture_m = 0.100,
        .quantum_efficiency = 0.85,
        .dark_current_a = 2e-9,
        .load_resistor_ohm = 50.0,
        .temperature_k = 300.0,
        .bandwidth_hz = 125e6,
        .optical_cascade = {
            {"Коліматор AR", 0.98},
            {"Спектральний фільтр", 0.85},
            {"Дихроїчна призма", 0.95}
        }
    };

    auto result = PhotonBudgetSolver::compute(params, 15.6);
    if (result) {
        const auto& r = *result;
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== ФОТОННИЙ БЮДЖЕТ ОПТИЧНОЇ СИСТЕМИ (C++) ===\n";
        std::cout << "Енергія фотона:             " << std::scientific << r.photon_energy_j << " Дж\n" << std::fixed;
        std::cout << "Приймана потужність:        " << (r.rx_power_w * 1e6) << " мкВт (" << r.rx_power_dbm << " дБм)\n";
        std::cout << "Сигнал на біт:              " << r.photoelectrons_per_bit << " e-\n";
        std::cout << "Дробовий шум:               " << r.sigma_shot_e << " e-\n";
        std::cout << "Тепловий шум:               " << r.sigma_thermal_e << " e-\n";
        std::cout << "Сумарний шум:               " << r.sigma_total_e << " e-\n";
        std::cout << "Відношення Сигнал/Шум (SNR): " << r.snr_db << " дБ (лінійне: " << r.snr_linear << ")\n";
        std::cout << "Запас лінії (Link Margin):  " << (r.link_margin_db >= 0 ? "+" : "") << r.link_margin_db << " дБ\n";
    }

    return 0;
}
