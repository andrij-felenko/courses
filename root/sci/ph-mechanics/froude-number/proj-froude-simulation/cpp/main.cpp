#include <iostream>
#include <vector>
#include <cmath>
#include <expected>
#include <iomanip>
#include <string>

namespace froude {

constexpr double GRAVITY = 9.80665;
constexpr double WATER_DENSITY = 998.2;
constexpr double WATER_VISCOSITY = 1.004e-6;

struct HydraulicJump {
    double depth_h1;
    double depth_h2;
    double velocity_v1;
    double velocity_v2;
    double froude_Fr1;
    double froude_Fr2;
    double energy_loss_dE;
};

struct ShipScaleResult {
    double model_length_m;
    double model_speed_ms;
    double model_froude;
    double model_reynolds;
    double ship_speed_ms;
    double ship_reynolds;
    double drag_wave_N;
    double drag_total_N;
    double power_kW;
};

enum class HydroError {
    InvalidDepth,
    InvalidDischarge,
    SubcriticalFlow,
    InvalidScale
};

class HydroCalculator {
public:
    static std::expected<HydraulicJump, HydroError> 
    compute_jump(double discharge_q, double h1) noexcept {
        if (h1 <= 0.0) return std::unexpected(HydroError::InvalidDepth);
        if (discharge_q <= 0.0) return std::unexpected(HydroError::InvalidDischarge);

        double v1 = discharge_q / h1;
        double fr1 = v1 / std::sqrt(GRAVITY * h1);

        if (fr1 <= 1.0) {
            return std::unexpected(HydroError::SubcriticalFlow);
        }

        double fr1_sq = fr1 * fr1;
        double h2 = 0.5 * h1 * (std::sqrt(1.0 + 8.0 * fr1_sq) - 1.0);
        double v2 = discharge_q / h2;
        double fr2 = v2 / std::sqrt(GRAVITY * h2);
        double dh = h2 - h1;
        double dE = (dh * dh * dh) / (4.0 * h1 * h2);

        return HydraulicJump{
            .depth_h1 = h1,
            .depth_h2 = h2,
            .velocity_v1 = v1,
            .velocity_v2 = v2,
            .froude_Fr1 = fr1,
            .froude_Fr2 = fr2,
            .energy_loss_dE = dE
        };
    }

    static std::expected<ShipScaleResult, HydroError>
    scale_ship(double L_ship, double L_model, double v_ship_knots, 
               double S_ship, double R_model_N) noexcept {
        if (L_ship <= 0.0 || L_model <= 0.0 || L_model >= L_ship) {
            return std::unexpected(HydroError::InvalidScale);
        }

        double scale = L_ship / L_model;
        double v_ship_ms = v_ship_knots * 0.514444;
        double v_model_ms = v_ship_ms / std::sqrt(scale);

        double fr_m = v_model_ms / std::sqrt(GRAVITY * L_model);
        double re_m = (v_model_ms * L_model) / WATER_VISCOSITY;
        double re_s = (v_ship_ms * L_ship) / WATER_VISCOSITY;

        double S_model = S_ship / (scale * scale);
        double q_m = 0.5 * WATER_DENSITY * v_model_ms * v_model_ms;
        double C_tm = R_model_N / (q_m * S_model);

        double C_fm = ittc_friction(re_m);
        double C_w = std::max(0.0, C_tm - C_fm);
        double C_fs = ittc_friction(re_s);
        double C_ts = C_w + C_fs;

        double q_s = 0.5 * WATER_DENSITY * v_ship_ms * v_ship_ms;
        double R_ts = C_ts * q_s * S_ship;
        double R_ws = C_w * q_s * S_ship;
        double power = (R_ts * v_ship_ms) / 1000.0;

        return ShipScaleResult{
            .model_length_m = L_model,
            .model_speed_ms = v_model_ms,
            .model_froude = fr_m,
            .model_reynolds = re_m,
            .ship_speed_ms = v_ship_ms,
            .ship_reynolds = re_s,
            .drag_wave_N = R_ws,
            .drag_total_N = R_ts,
            .power_kW = power
        };
    }

private:
    static double ittc_friction(double reynolds) noexcept {
        if (reynolds <= 0.0) return 0.0;
        double log_re = std::log10(reynolds);
        double denom = log_re - 2.0;
        return 0.075 / (denom * denom);
    }
};

} // namespace froude

int main() {
    using namespace froude;

    std::cout << "=== C++23 Hydrodynamic Froude Scaling ===\n";

    auto jump_res = HydroCalculator::compute_jump(3.5, 0.4);
    if (jump_res) {
        const auto& j = *jump_res;
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "Fr1: " << j.froude_Fr1 << " -> h1: " << j.depth_h1 << " m, h2: " << j.depth_h2 << " m\n";
        std::cout << "Energy Dissipation dE: " << j.energy_loss_dE << " m\n";
    } else {
        std::cout << "Error computing jump\n";
    }

    auto ship_res = HydroCalculator::scale_ship(120.0, 4.0, 20.0, 2200.0, 25.5);
    if (ship_res) {
        const auto& s = *ship_res;
        std::cout << "\nShip Scaling Results:\n";
        std::cout << "Model speed: " << s.model_speed_ms << " m/s (Fr = " << s.model_froude << ")\n";
        std::cout << "Full scale drag: " << (s.drag_total_N / 1000.0) << " kN\n";
        std::cout << "Effective power: " << s.power_kW << " kW\n";
    }

    return 0;
}
