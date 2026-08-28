/* cpp */
#include <cmath>
#include <numbers>
#include <optional>

namespace navigation::compass {

constexpr float kMinHFieldNt = 2000.0f; // Поріг надійності горизонтального поля

struct SensorsInput {
    float bx_nt{0.0f};          // Магнітне поле X (нТл)
    float by_nt{0.0f};          // Магнітне поле Y (нТл)
    float bz_nt{0.0f};          // Магнітне поле Z (нТл)
    float roll_rad{0.0f};       // Крен (рад)
    float pitch_rad{0.0f};      // Тангаж (рад)
    float declination_deg{0.0f};// Схилення D (град)
};

struct HeadingResult {
    float heading_mag_deg{0.0f};  // Курс магнітний [0..360°)
    float heading_true_deg{0.0f}; // Курс істинний [0..360°)
    float h_intensity_nt{0.0f};   // Горизонтальне поле H (нТл)
};

[[nodiscard]] constexpr float normalize360(float angle_deg) noexcept {
    float normalized = std::fmod(angle_deg, 360.0f);
    if (normalized < 0.0f) {
        normalized += 360.0f;
    }
    return normalized;
}

[[nodiscard]] std::optional<HeadingResult> computeHeading(const SensorsInput& in) noexcept {
    const float cos_roll = std::cos(in.roll_rad);
    const float sin_roll = std::sin(in.roll_rad);
    const float cos_pitch = std::cos(in.pitch_rad);
    const float sin_pitch = std::sin(in.pitch_rad);

    // Компенсація нахилу: поворот вектора B у горизонтальну площину
    const float hx = in.bx_nt * cos_pitch +
                     in.by_nt * sin_roll * sin_pitch +
                     in.bz_nt * cos_roll * sin_pitch;

    const float hy = in.by_nt * cos_roll -
                     in.bz_nt * sin_roll;

    const float h_len = std::hypot(hx, hy);
    if (h_len < kMinHFieldNt) {
        return std::nullopt; // Сингулярність поблизу полярних широт
    }

    const float mag_rad = std::atan2(-hy, hx);
    const float mag_deg = normalize360(mag_rad * (180.0f / std::numbers::pi_v<float>));
    const float true_deg = normalize360(mag_deg + in.declination_deg);

    return HeadingResult{
        .heading_mag_deg = mag_deg,
        .heading_true_deg = true_deg,
        .h_intensity_nt = h_len
    };
}

} // namespace navigation::compass
