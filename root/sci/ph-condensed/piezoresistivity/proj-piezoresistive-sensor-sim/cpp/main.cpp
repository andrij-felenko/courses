#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <expected>
#include <string_view>
#include <span>

// Константні фізичні параметри за замовчуванням
struct SensorParameters {
    double membrane_side_um{500.0};   // a, мкм
    double membrane_thick_um{20.0};   // h, мкм
    double r0_300k_ohm{2000.0};       // R0, Ом
    double doping_cm3{3.0e18};        // N, см⁻³
    double v_in_volts{5.0};           // Vin, В
    double pi_l_110{71.8e-11};        // pi_L, 1/Па
    double pi_t_110{-68.7e-11};       // pi_T, 1/Па
    double tcr1{1.2e-3};              // TCR1, 1/K
    double tcr2{2.5e-6};              // TCR2, 1/K²
};

// Результат чисельного моделювання
struct SimulationPoint {
    double pressure_kPa{0.0};
    double temp_K{300.0};
    double sigma_L_MPa{0.0};
    double sigma_T_MPa{0.0};
    double p_factor{1.0};
    double r1_ohm{2000.0};
    double r2_ohm{2000.0};
    double r3_ohm{2000.0};
    double r4_ohm{2000.0};
    double v_out_mV{0.0};
    double sensitivity_mV_V_kPa{0.0};
    double resonant_freq_kHz{0.0};
};

enum class SimulationError {
    InvalidPressure,
    InvalidTemperature,
    ZeroThickness
};

class PiezoresistiveSimulator {
public:
    explicit PiezoresistiveSimulator(SensorParameters params)
        : params_(std::move(params)) {}

    [[nodiscard]] std::expected<SimulationPoint, SimulationError>
    calculate_point(double pressure_kPa, double temp_K) const {
        if (pressure_kPa < 0.0) return std::unexpected(SimulationError::InvalidPressure);
        if (temp_K < 50.0) return std::unexpected(SimulationError::InvalidTemperature);
        if (params_.membrane_thick_um <= 0.0) return std::unexpected(SimulationError::ZeroThickness);

        SimulationPoint pt{};
        pt.pressure_kPa = pressure_kPa;
        pt.temp_K = temp_K;

        const double a_m = params_.membrane_side_um * 1e-6;
        const double h_m = params_.membrane_thick_um * 1e-6;
        const double p_pa = pressure_kPa * 1000.0;

        const double geom_ratio = a_m / h_m;
        const double sigma_L_pa = 0.308 * p_pa * geom_ratio * geom_ratio;
        const double sigma_T_pa = 0.092 * p_pa * geom_ratio * geom_ratio;

        pt.sigma_L_MPa = sigma_L_pa / 1e6;
        pt.sigma_T_MPa = sigma_T_pa / 1e6;

        constexpr double e_mod = 169e9;
        constexpr double rho_m = 2330.0;
        constexpr double nu = 0.06;
        const double fn_hz = (1.654 * h_m / (a_m * a_m)) * std::sqrt(e_mod / (rho_m * (1.0 - nu * nu)));
        pt.resonant_freq_kHz = fn_hz / 1000.0;

        pt.p_factor = calculate_kanda_factor(temp_K);
        const double dt = temp_K - 300.0;
        const double r0_t = params_.r0_300k_ohm * (1.0 + params_.tcr1 * dt + params_.tcr2 * dt * dt);

        const double dr1_r0 = (params_.pi_l_110 * sigma_L_pa + params_.pi_t_110 * sigma_T_pa) * pt.p_factor;
        const double dr2_r0 = (params_.pi_l_110 * sigma_T_pa + params_.pi_t_110 * sigma_L_pa) * pt.p_factor;

        pt.r1_ohm = pt.r3_ohm = r0_t * (1.0 + dr1_r0);
        pt.r2_ohm = pt.r4_ohm = r0_t * (1.0 + dr2_r0);

        const double num = pt.r1_ohm * pt.r3_ohm - pt.r2_ohm * pt.r4_ohm;
        const double den = (pt.r1_ohm + pt.r2_ohm) * (pt.r3_ohm + pt.r4_ohm);
        const double v_out_v = params_.v_in_volts * (num / den);

        pt.v_out_mV = v_out_v * 1000.0;
        pt.sensitivity_mV_V_kPa = (pressure_kPa > 1e-6) ? (pt.v_out_mV / (params_.v_in_volts * pressure_kPa)) : 0.0;

        return pt;
    }

    [[nodiscard]] std::vector<SimulationPoint>
    run_sweep(std::span<const double> pressures_kPa, double temp_K) const {
        std::vector<SimulationPoint> results;
        results.reserve(pressures_kPa.size());
        for (double p : pressures_kPa) {
            if (auto res = calculate_point(p, temp_K); res.has_value()) {
                results.push_back(*res);
            }
        }
        return results;
    }

private:
    [[nodiscard]] double calculate_kanda_factor(double temp_K) const {
        constexpr double n_ref = 1.4e19;
        const double term_n = std::pow(params_.doping_cm3 / n_ref, 0.72);
        const double term_t = std::pow(300.0 / temp_K, 0.85);
        return 1.0 / (1.0 + term_n * term_t);
    }

    SensorParameters params_;
};

int main() {
    const SensorParameters params{};
    const PiezoresistiveSimulator simulator(params);

    const std::vector<double> pressures{0.0, 20.0, 50.0, 100.0};
    const std::vector<double> temperatures{250.0, 300.0, 350.0};

    std::cout << "=== МОДЕЛЮВАННЯ MEMS-ДАТЧИКА ТИСКУ (C++20 Implementation) ===\n";
    std::cout << std::fixed << std::setprecision(2);

    for (double t : temperatures) {
        std::cout << "\n--- Температура: " << t << " K ---\n";
        auto sweep = simulator.run_sweep(pressures, t);
        for (const auto& pt : sweep) {
            std::cout << "Тиск: " << std::setw(6) << pt.pressure_kPa << " кПа | "
                      << "sigma_L: " << std::setw(6) << pt.sigma_L_MPa << " МПа | "
                      << "P_factor: " << std::setw(5) << pt.p_factor << " | "
                      << "V_out: " << std::setw(7) << pt.v_out_mV << " мВ | "
                      << "Чув: " << std::setw(6) << pt.sensitivity_mV_V_kPa << " мВ/В/кПа\n";
        }
    }

    return 0;
}
