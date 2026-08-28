#include <cmath>
#include <cstdint>

enum class CrashFault {
    None,
    ActuatorSaturation,
    MagFieldDistortion,
    BatteryCollapse
};

// Аналіз кадру польотних даних у C++
constexpr CrashFault evaluate_frame(float roll_err_deg, float m1_cmd, float m2_cmd,
                                   float mag_innov, float current_a, float voltage_v) noexcept {
    // 1. Просадка батареї нижче критичної відсічки
    if (voltage_v < 13.0f && current_a > 30.0f) {
        return CrashFault::BatteryCollapse;
    }
    // 2. Втрата мотора: максимальна асиметрія при зростанні помилки
    if (m1_cmd > 0.98f && m2_cmd < 0.05f && std::abs(roll_err_deg) > 20.0f) {
        return CrashFault::ActuatorSaturation;
    }
    // 3. Магнітна завада: стрибок нев'язки пропорційно до струму
    if (mag_innov > 0.5f && current_a > 35.0f) {
        return CrashFault::MagFieldDistortion;
    }
    return CrashFault::None;
}
