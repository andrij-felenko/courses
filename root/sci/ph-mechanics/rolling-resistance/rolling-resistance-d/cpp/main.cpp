#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <string_view>
#include <span>

constexpr double GRAVITY = 9.81;
constexpr double AIR_DENSITY_STD = 1.225;

struct VehicleParameters {
    double mass_kg{1950.0};
    double cd{0.23};
    double frontal_area_m2{2.25};
    double tire_radius_m{0.33};
    double tire_pressure_bar{2.5};
    double crr_nominal{0.0080};
    double gear_ratio{9.05};
    double gear_efficiency{0.97};
    double rot_inertia_coeff{1.05};
    double aux_power_w{450.0};

    [[nodiscard]] constexpr double aerodynamic_drag_area() const noexcept {
        return cd * frontal_area_m2;
    }
};

struct DynamicState {
    double speed_mps{0.0};
    double accel_mps2{0.0};
    double grade_rad{0.0};
    double headwind_mps{0.0};
    double air_density{AIR_DENSITY_STD};
};

struct TractionAnalysis {
    double f_roll_n{0.0};
    double f_aero_n{0.0};
    double f_grade_n{0.0};
    double f_accel_n{0.0};
    double f_total_wheel_n{0.0};
    double motor_torque_nm{0.0};
    double motor_speed_radps{0.0};
    double motor_power_mech_w{0.0};
    double motor_efficiency{0.0};
    double battery_power_w{0.0};
};

class ElectricPowertrainSimulator {
public:
    explicit ElectricPowertrainSimulator(VehicleParameters params) 
        : params_{params} {}

    [[nodiscard]] double compute_rolling_coeff(double speed_mps) const noexcept {
        const double p_ratio = 2.5 / params_.tire_pressure_bar;
        const double pressure_factor = std::sqrt(p_ratio);
        const double v_norm = (speed_mps * 3.6) / 100.0;
        const double speed_factor = 1.0 + 0.0035 * v_norm + 0.0020 * (v_norm * v_norm);
        return params_.crr_nominal * pressure_factor * speed_factor;
    }

    [[nodiscard]] static double compute_motor_efficiency(double torque_nm, double speed_radps) noexcept {
        const double p_mech = std::abs(torque_nm * speed_radps);
        if (p_mech < 50.0) return 0.65;

        const double loss_copper = 0.0018 * (torque_nm * torque_nm);
        const double loss_iron = 0.00035 * (speed_radps * speed_radps) + 0.08 * speed_radps;
        const double loss_friction = 0.015 * speed_radps + 35.0;
        const double total_loss = loss_copper + loss_iron + loss_friction;

        const double eff = p_mech / (p_mech + total_loss);
        return std::clamp(eff, 0.200, 0.965);
    }

    [[nodiscard]] TractionAnalysis evaluate(const DynamicState& state) const noexcept {
        TractionAnalysis out;
        const double normal_force = params_.mass_kg * GRAVITY * std::cos(state.grade_rad);
        const double crr = compute_rolling_coeff(state.speed_mps);
        out.f_roll_n = crr * normal_force;

        const double air_speed = state.speed_mps + state.headwind_mps;
        const double aero_sign = (air_speed >= 0.0) ? 1.0 : -1.0;
        out.f_aero_n = aero_sign * 0.5 * state.air_density * params_.aerodynamic_drag_area() * (air_speed * air_speed);

        out.f_grade_n = params_.mass_kg * GRAVITY * std::sin(state.grade_rad);
        out.f_accel_n = params_.mass_kg * state.accel_mps2 * params_.rot_inertia_coeff;

        out.f_total_wheel_n = out.f_roll_n + out.f_aero_n + out.f_grade_n + out.f_accel_n;

        const double wheel_speed_radps = state.speed_mps / params_.tire_radius_m;
        out.motor_speed_radps = wheel_speed_radps * params_.gear_ratio;

        if (out.f_total_wheel_n >= 0.0) {
            out.motor_torque_nm = (out.f_total_wheel_n * params_.tire_radius_m) / 
                                  (params_.gear_ratio * params_.gear_efficiency);
            out.motor_power_mech_w = out.motor_torque_nm * out.motor_speed_radps;
            out.motor_efficiency = compute_motor_efficiency(out.motor_torque_nm, out.motor_speed_radps);
            out.battery_power_w = (out.motor_power_mech_w / out.motor_efficiency) + params_.aux_power_w;
        } else {
            out.motor_torque_nm = (out.f_total_wheel_n * params_.tire_radius_m * params_.gear_efficiency) / 
                                  params_.gear_ratio;
            out.motor_power_mech_w = out.motor_torque_nm * out.motor_speed_radps;
            out.motor_efficiency = compute_motor_efficiency(out.motor_torque_nm, out.motor_speed_radps);
            out.battery_power_w = (out.motor_power_mech_w * out.motor_efficiency) + params_.aux_power_w;
        }

        return out;
    }

    [[nodiscard]] const VehicleParameters& parameters() const noexcept { return params_; }

private:
    VehicleParameters params_;
};

void print_table_header() {
    std::cout << std::left 
              << std::setw(10) << "V, км/год" << " | "
              << std::setw(10) << "F_roll, Н" << " | "
              << std::setw(10) << "F_aero, Н" << " | "
              << std::setw(10) << "C_rr" << " | "
              << std::setw(11) << "P_roll, кВт" << " | "
              << std::setw(11) << "P_aero, кВт" << " | "
              << std::setw(14) << "АКБ, кВт·год/100км" << "\n";
    std::cout << std::string(88, '-') << "\n";
}

int main() {
    VehicleParameters ev_params{};
    ElectricPowertrainSimulator sim{ev_params};

    std::cout << "=== МОДЕЛЮВАННЯ ТЯГОВОГО ЕЛЕКТРОПРИВОДУ (C++20) ===\n";
    std::cout << "Маса: " << ev_params.mass_kg << " кг | Cd*A: " 
              << ev_params.aerodynamic_drag_area() << " м² | Crr: " 
              << ev_params.crr_nominal << "\n\n";

    constexpr std::array<double, 5> test_speeds_kmh{30.0, 60.0, 90.0, 120.0, 150.0};
    print_table_header();

    std::cout << std::fixed << std::setprecision(2);
    for (const double v_kmh : test_speeds_kmh) {
        DynamicState st{
            .speed_mps = v_kmh / 3.6,
            .accel_mps2 = 0.0,
            .grade_rad = 0.0,
            .headwind_mps = 0.0,
            .air_density = AIR_DENSITY_STD
        };

        const auto res = sim.evaluate(st);
        const double p_roll_kw = (res.f_roll_n * st.speed_mps) / 1000.0;
        const double p_aero_kw = (res.f_aero_n * st.speed_mps) / 1000.0;
        const double kwh_100km = (res.battery_power_w / 1000.0) / v_kmh * 100.0;
        const double current_crr = sim.compute_rolling_coeff(st.speed_mps);

        std::cout << std::right 
                  << std::setw(10) << v_kmh << " | "
                  << std::setw(10) << res.f_roll_n << " | "
                  << std::setw(10) << res.f_aero_n << " | "
                  << std::setw(10) << std::setprecision(5) << current_crr << " | "
                  << std::setprecision(2)
                  << std::setw(11) << p_roll_kw << " | "
                  << std::setw(11) << p_aero_kw << " | "
                  << std::setw(14) << kwh_100km << "\n";
    }

    return 0;
}
