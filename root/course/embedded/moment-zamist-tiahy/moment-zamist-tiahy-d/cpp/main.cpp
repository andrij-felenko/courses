#include <iostream>
#include <iomanip>
#include <numbers>
#include <cmath>
#include <string_view>

namespace rover {

inline constexpr double Gravity = 9.80665;

struct ChassisSpec {
    double mass_kg{16.0};
    double wheel_radius_m{0.075};
    int    drive_wheels{4};
    double crr{0.08};
    double mu_friction{0.55};
    double slope_degrees{20.0};
    double target_speed_mps{1.5};
    double target_accel_mps2{0.75};
    double safety_factor{1.30};
};

struct PowertrainSpec {
    double gear_ratio{36.0};
    double gearbox_efficiency{0.80};
    double kv_rating{520.0};
    double phase_resistance{0.32};
    double rated_torque_nm{0.10};
    double stall_torque_nm{0.42};
};

struct SizingSummary {
    double total_traction_n{0.0};
    double wheel_torque_nm{0.0};
    double wheel_rpm{0.0};
    double motor_torque_nm{0.0};
    double motor_rpm{0.0};
    double motor_current_a{0.0};
    double mech_power_total_w{0.0};
    bool   traction_ok{false};
    bool   torque_ok{false};
};

class PowertrainEvaluator {
public:
    [[nodiscard]] static constexpr SizingSummary compute(
        const ChassisSpec& ch, 
        const PowertrainSpec& pt) noexcept 
    {
        SizingSummary res{};
        const double theta = ch.slope_degrees * (std::numbers::pi / 180.0);
        
        const double f_rr    = ch.crr * ch.mass_kg * Gravity * std::cos(theta);
        const double f_slope = ch.mass_kg * Gravity * std::sin(theta);
        const double f_acc   = ch.mass_kg * 1.20 * ch.target_accel_mps2;
        res.total_traction_n = f_rr + f_slope + f_acc;
        
        const double force_per_wheel = res.total_traction_n / ch.drive_wheels;
        res.wheel_torque_nm    = force_per_wheel * ch.wheel_radius_m * ch.safety_factor;
        const double omega_wheel = ch.target_speed_mps / ch.wheel_radius_m;
        res.wheel_rpm          = (omega_wheel * 60.0) / (2.0 * std::numbers::pi);
        
        res.motor_torque_nm = res.wheel_torque_nm / (pt.gear_ratio * pt.gearbox_efficiency);
        res.motor_rpm       = res.wheel_rpm * pt.gear_ratio;
        
        const double kt = 60.0 / (pt.kv_rating * 2.0 * std::numbers::pi);
        res.motor_current_a = res.motor_torque_nm / kt;
        
        const double omega_motor = omega_wheel * pt.gear_ratio;
        res.mech_power_total_w = (res.motor_torque_nm * omega_motor) * ch.drive_wheels;
        
        const double max_grip = ch.mu_friction * (ch.mass_kg * Gravity * std::cos(theta) / ch.drive_wheels);
        res.traction_ok = (force_per_wheel <= max_grip);
        res.torque_ok   = (res.motor_torque_nm <= pt.rated_torque_nm);
        
        return res;
    }
};

} // namespace rover

int main() {
    constexpr rover::ChassisSpec chassis{};
    constexpr rover::PowertrainSpec powertrain{};
    
    const auto s = rover::PowertrainEvaluator::compute(chassis, powertrain);
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Тяга: " << s.total_traction_n << " Н | Момент колеса: " 
              << s.wheel_torque_nm << " Нм (" << s.wheel_rpm << " RPM)\n";
    std::cout << "Мотор: " << std::setprecision(4) << s.motor_torque_nm 
              << " Нм (" << std::setprecision(0) << s.motor_rpm << " RPM) | Струм: " 
              << std::setprecision(2) << s.motor_current_a << " А | Потужність: " 
              << s.mech_power_total_w << " Вт\n";
    std::cout << "Статус: Зчеплення: " << (s.traction_ok ? "OK" : "БУКСУВАННЯ")
              << " | Навантаження: " << (s.torque_ok ? "OK" : "ПЕРЕВАНТАЖЕННЯ") << "\n";
              
    return 0;
}
