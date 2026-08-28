#include <cmath>
#include <numbers>
#include <array>
#include <string_view>
#include <expected>

namespace drone_propulsion {

inline constexpr double Gravity = 9.80665;
inline constexpr double AirDensitySeaLevel = 1.225;

struct MissionRequirements {
    double mass_kg{2.5};
    double frontal_area_m2{0.065};
    double drag_coefficient{0.45};
    double max_wind_speed_ms{15.0};
    double target_tilt_deg{45.0};
    double min_climb_accel_ms2{3.0};
    double pid_reserve_factor{1.4};
    double battery_voltage_v{22.2};
    double pwm_frequency_hz{48000.0};
    double mosfet_switch_time_s{45e-9};
};

enum class AnalysisWarning {
    None,
    SaturationRisk,
    ExcessiveTwrThermalRisk
};

struct TwrAnalysisReport {
    double optimal_twr{0.0};
    double max_thrust_n{0.0};
    double max_thrust_kgf{0.0};
    double hover_throttle_pct{0.0};
    double duty_cycle{0.0};
    double ripple_current_factor{0.0};
    double mosfet_switch_loss_w{0.0};
    AnalysisWarning warning{AnalysisWarning::None};

    [[nodiscard]] constexpr bool is_balanced() const noexcept {
        return warning == AnalysisWarning::None;
    }
};

class TwrOptimizer {
public:
    [[nodiscard]] static constexpr auto evaluate(
        const MissionRequirements& req,
        double motor_hover_current_a
    ) noexcept -> TwrAnalysisReport 
    {
        TwrAnalysisReport report{};

        // 1. Аеродинамічний опір
        const double drag_force = 0.5 * AirDensitySeaLevel * req.drag_coefficient *
                                  req.frontal_area_m2 * (req.max_wind_speed_ms * req.max_wind_speed_ms);

        // 2. Силовий баланс
        const double weight_n = req.mass_kg * Gravity;
        const double req_vertical_n = req.mass_kg * (Gravity + req.min_climb_accel_ms2);
        const double req_horizontal_n = drag_force;

        // 3. Векторна сума навантажень
        const double vector_thrust_n = std::hypot(req_vertical_n, req_horizontal_n);

        // 4. Оптимальна тяга з запасом авторитету
        report.max_thrust_n = vector_thrust_n * req.pid_reserve_factor;
        report.max_thrust_kgf = report.max_thrust_n / Gravity;
        report.optimal_twr = report.max_thrust_n / weight_n;

        // 5. Відсоток висіння
        report.hover_throttle_pct = (weight_n / report.max_thrust_n) * 100.0;
        report.duty_cycle = report.hover_throttle_pct / 100.0;

        // 6. Пульсації струму на конденсаторах фільтра
        if (report.duty_cycle > 0.0 && report.duty_cycle < 1.0) {
            report.ripple_current_factor = std::sqrt(report.duty_cycle * (1.0 - report.duty_cycle));
        }

        // 7. Динамічні комутаційні втрати ключа
        report.mosfet_switch_loss_w = req.pwm_frequency_hz * req.battery_voltage_v *
                                      motor_hover_current_a * (req.mosfet_switch_time_s / 2.0);

        // 8. Оцінка ризиків
        if (report.hover_throttle_pct > 60.0 || report.optimal_twr < 1.8) {
            report.warning = AnalysisWarning::SaturationRisk;
        } else if (report.hover_throttle_pct < 18.0 || report.optimal_twr > 6.0) {
            report.warning = AnalysisWarning::ExcessiveTwrThermalRisk;
        }

        return report;
    }
};

} // namespace drone_propulsion
