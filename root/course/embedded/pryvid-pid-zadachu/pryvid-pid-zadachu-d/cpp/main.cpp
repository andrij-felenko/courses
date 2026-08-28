#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>

enum class MotorType {
    BDC,
    Stepper,
    BLDC,
    Servo
};

struct MotorSpecs {
    MotorType type;
    double max_torque_nm;      // Максимальний крутний момент (Н·м)
    double max_speed_rpm;      // Максимальна швидкість (об/хв)
    double rated_current_a;    // Номінальний струм (А)
    double resistance_ohm;     // Опір фази (Ом)
    double thermal_r_c_per_w;  // Тепловий опір (°C/Вт)
};

struct MotionTask {
    double load_torque_nm;     // Момент навантаження (Н·м)
    double load_inertia_kgm2;  // Момент інерції (кг·м²)
    double target_speed_rpm;   // Цільова швидкість (об/хв)
    double accel_time_s;       // Час розгону (с)
    double ambient_temp_c{25.0};
};

struct AnalysisResult {
    double peak_torque_nm;
    double steady_temperature_c;
};

enum class SizingError {
    InsufficientTorque,
    SpeedExceeded,
    ThermalOverheat
};

[[nodiscard]] constexpr std::expected<AnalysisResult, SizingError> evaluateMotor(
    const MotorSpecs& motor,
    const MotionTask& task
) noexcept {
    const double rad_per_s = task->target_speed_rpm * (2.0 * std::numbers::pi / 60.0);
    const double alpha = rad_per_s / task->accel_time_s;
    const double t_dynamic = task->load_torque_nm + (task->load_inertia_kgm2 * alpha);

    const double safety_margin = (motor.type == MotorType::Stepper) ? 2.0 : 1.3;
    if (t_dynamic * safety_margin > motor.max_torque_nm) {
        return std::unexpected(SizingError::InsufficientTorque);
    }

    if (task->target_speed_rpm > motor.max_speed_rpm) {
        return std::unexpected(SizingError::SpeedExceeded);
    }

    double i_eff = motor.rated_current_a;
    if (motor.type == MotorType::BDC) {
        i_eff *= (t_dynamic / motor.max_torque_nm);
    }

    double p_loss = i_eff * i_eff * motor.resistance_ohm;
    if (motor.type == MotorType::Stepper) {
        p_loss *= 2.0;
    } else if (motor.type == MotorType::BLDC) {
        p_loss *= 1.5;
    }

    const double final_temp = task->ambient_temp_c + (p_loss * motor.thermal_r_c_per_w);
    if (final_temp >= 105.0) {
        return std::unexpected(SizingError::ThermalOverheat);
    }

    return AnalysisResult{
        .peak_torque_nm = t_dynamic,
        .steady_temperature_c = final_temp
    };
}
