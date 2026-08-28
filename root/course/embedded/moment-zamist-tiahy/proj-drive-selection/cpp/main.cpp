#include <iostream>
#include <iomanip>
#include <numbers>
#include <cmath>
#include <string_view>

namespace rover {

inline constexpr double Gravity = 9.80665;

struct ChassisConfig {
    double mass_kg{16.0};
    double wheel_radius_m{0.075};
    int    total_wheels{4};
    int    drive_wheels{4};
    double c_rr{0.08};
    double mu_traction{0.55};
    double slope_deg{20.0};
    double target_speed_mps{1.5};
    double target_accel_mps2{0.75};
    double safety_factor{1.25};
};

struct DrivetrainConfig {
    double gear_ratio{36.0};
    double gearbox_efficiency{0.80};
    double kv_rpm_per_volt{520.0};
    double phase_resistance_ohm{0.28};
    double rated_torque_nm{0.12};
    double stall_torque_nm{0.45};
    double thermal_res_c_per_w{2.4};
    double max_winding_temp_c{130.0};
    double ambient_temp_c{25.0};
};

struct CalculationResult {
    double f_rr_n{0.0};
    double f_slope_n{0.0};
    double f_accel_n{0.0};
    double f_total_n{0.0};
    double t_wheel_nm{0.0};
    double t_motor_nm{0.0};
    double wheel_rpm{0.0};
    double motor_rpm{0.0};
    double p_mech_per_motor_w{0.0};
    double p_mech_total_w{0.0};
    double est_current_a{0.0};
    double copper_loss_w{0.0};
    double steady_temp_c{0.0};
    double max_grip_force_n{0.0};
    bool   torque_ok{false};
    bool   stall_margin_ok{false};
    bool   traction_ok{false};
    bool   thermal_ok{false};
};

class DriveSizingCalculator {
public:
    [[nodiscard]] static constexpr CalculationResult evaluate(
        const ChassisConfig& chassis,
        const DrivetrainConfig& drive) noexcept 
    {
        CalculationResult res{};
        
        const double theta_rad = chassis.slope_deg * (std::numbers::pi / 180.0);
        const double cos_theta = std::cos(theta_rad);
        const double sin_theta = std::sin(theta_rad);
        
        res.f_rr_n    = chassis.c_rr * chassis.mass_kg * Gravity * cos_theta;
        res.f_slope_n = chassis.mass_kg * Gravity * sin_theta;
        
        constexpr double rot_factor = 1.20;
        res.f_accel_n = chassis.mass_kg * rot_factor * chassis.target_accel_mps2;
        res.f_total_n = res.f_rr_n + res.f_slope_n + res.f_accel_n;
        
        const double force_per_wheel = res.f_total_n / chassis.drive_wheels;
        res.t_wheel_nm = force_per_wheel * chassis.wheel_radius_m * chassis.safety_factor;
        
        const double omega_wheel = chassis.target_speed_mps / chassis.wheel_radius_m;
        res.wheel_rpm = (omega_wheel * 60.0) / (2.0 * std::numbers::pi);
        
        res.t_motor_nm = res.t_wheel_nm / (drive.gear_ratio * drive.gearbox_efficiency);
        res.motor_rpm  = res.wheel_rpm * drive.gear_ratio;
        const double omega_motor = omega_wheel * drive.gear_ratio;
        
        res.p_mech_per_motor_w = res.t_motor_nm * omega_motor;
        res.p_mech_total_w     = res.p_mech_per_motor_w * chassis.drive_wheels;
        
        const double kt = 60.0 / (drive.kv_rpm_per_volt * 2.0 * std::numbers::pi);
        res.est_current_a = res.t_motor_nm / kt;
        
        res.copper_loss_w  = res.est_current_a * res.est_current_a * drive.phase_resistance_ohm;
        res.steady_temp_c  = drive.ambient_temp_c + (res.copper_loss_w * drive.thermal_res_c_per_w);
        
        const double normal_per_wheel = (chassis.mass_kg * Gravity * cos_theta) / chassis.total_wheels;
        res.max_grip_force_n    = chassis.mu_traction * normal_per_wheel;
        
        res.torque_ok       = (res.t_motor_nm <= drive.rated_torque_nm);
        res.stall_margin_ok = (res.t_motor_nm <= 0.70 * drive.stall_torque_nm);
        res.traction_ok     = (force_per_wheel <= res.max_grip_force_n);
        res.thermal_ok      = (res.steady_temp_c < drive.max_winding_temp_c);
        
        return res;
    }
};

void print_report(const CalculationResult& r) {
    auto status_str = [](bool ok, std::string_view fail_msg) -> std::string_view {
        return ok ? "OK" : fail_msg;
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "============================================================\n"
              << "         ЗВІТ РОЗРАХУНКУ ПРИВОДУ РОВЕРА (C++20)             \n"
              << "============================================================\n"
              << "Сила опору коченню F_rr:      " << std::setw(7) << r.f_rr_n << " Н\n"
              << "Сила подолання схилу F_slope:  " << std::setw(7) << r.f_slope_n << " Н\n"
              << "Динамічна сила розгону F_acc: " << std::setw(7) << r.f_accel_n << " Н\n"
              << "СУМАРНА ПОТРІБНА ТЯГА:        " << std::setw(7) << r.f_total_n << " Н\n"
              << "------------------------------------------------------------\n"
              << "Момент на 1 колесі:           " << std::setw(7) << r.t_wheel_nm << " Н·м  (" << r.wheel_rpm << " RPM)\n"
              << "Потрібний момент мотора:      " << std::setw(7) << r.t_motor_nm << " Н·м  (" << r.motor_rpm << " RPM)\n"
              << "Механічна потужність (1 двиг):" << std::setw(7) << r.p_mech_per_motor_w << " Вт\n"
              << "Механічна потужність (сумарна):" << std::setw(6) << r.p_mech_total_w << " Вт\n"
              << "------------------------------------------------------------\n"
              << "Оціночний струм фази:         " << std::setw(7) << r.est_current_a << " А\n"
              << "Теплові втрати в міді I²·R:   " << std::setw(7) << r.copper_loss_w << " Вт\n"
              << "Стала температура обмотки:    " << std::setw(7) << r.steady_temp_c << " °C\n"
              << "------------------------------------------------------------\n"
              << "ПЕРЕВІРКИ БЕЗПЕКИ ТА ПРАЦЕЗДАТНОСТІ:\n"
              << " [ " << status_str(r.torque_ok, "ПЕРЕВАНТАЖЕННЯ") << " ] Номінальний момент мотора\n"
              << " [ " << status_str(r.stall_margin_ok, "НЕБЕЗПЕКА СТОПОРА") << " ] Запас до стопора (>30%)\n"
              << " [ " << status_str(r.traction_ok, "ПРОБУКСОВУВАННЯ") << " ] Зчеплення з ґрунтом\n"
              << " [ " << status_str(r.thermal_ok, "ПЕРЕГРІВ") << " ] Тепловий режим обмотки\n"
              << "============================================================\n";
}

} // namespace rover

int main() {
    rover::ChassisConfig chassis{};
    rover::DrivetrainConfig drive{};
    
    const auto result = rover::DriveSizingCalculator::evaluate(chassis, drive);
    rover::print_report(result);
    
    return 0;
}
