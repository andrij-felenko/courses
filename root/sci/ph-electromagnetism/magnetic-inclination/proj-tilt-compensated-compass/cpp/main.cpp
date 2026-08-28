/* cpp */
#include <cmath>
#include <numbers>
#include <optional>
#include <span>

namespace navigation {

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float length_sq() const noexcept {
        return x * x + y * y + z * z;
    }

    [[nodiscard]] float length() const noexcept {
        return std::sqrt(length_sq());
    }
};

struct Orientation {
    float heading_deg{0.0f};     // Справжній азимут (0..360°)
    float inclination_deg{0.0f}; // Кут нахилу (-90..+90°)
    float pitch_deg{0.0f};       // Тангаж (-90..+90°)
    float roll_deg{0.0f};        // Крен (-180..+180°)
    float total_field_uT{0.0f};  // Модуль поля
};

class TiltCompensatedCompass {
public:
    explicit TiltCompensatedCompass(float declination_deg = 0.0f) noexcept
        : declination_rad_{declination_deg * std::numbers::pi_v<float> / 180.0f} {}

    [[nodiscard]] std::optional<Orientation> compute(
        const Vector3f& accel,
        const Vector3f& mag
    ) const noexcept {
        if (accel.length_sq() < 1e-4f) {
            return std::nullopt;
        }

        // 1. Оцінка кутів орієнтації
        const float roll  = std::atan2(accel.y, accel.z);
        const float pitch = std::atan2(-accel.x, std::hypot(accel.y, accel.z));

        const float cos_roll  = std::cos(roll);
        const float sin_roll  = std::sin(roll);
        const float cos_pitch = std::cos(pitch);
        const float sin_pitch = std::sin(pitch);

        // 2. Трансформація вектора магнітного поля в горизонт
        const float b_xh = mag.x * cos_pitch + mag.y * sin_roll * sin_pitch + mag.z * cos_roll * sin_pitch;
        const float b_yh = mag.y * cos_roll - mag.z * sin_roll;
        const float b_zh = -mag.x * sin_pitch + mag.y * sin_roll * cos_pitch + mag.z * cos_roll * cos_pitch;

        // 3. Обчислення курсу з урахуванням схилення
        float heading_rad = std::atan2(-b_yh, b_xh) + declination_rad_;
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        
        while (heading_rad < 0.0f)   heading_rad += two_pi;
        while (heading_rad >= two_pi) heading_rad -= two_pi;

        // 4. Повний модуль та кут нахилу
        const float b_total = mag.length();
        float inclination_rad = 0.0f;
        if (b_total > 1e-4f) {
            inclination_rad = std::asin(std::clamp(b_zh / b_total, -1.0f, 1.0f));
        }

        constexpr float rad_to_deg = 180.0f / std::numbers::pi_v<float>;
        return Orientation{
            .heading_deg     = heading_rad * rad_to_deg,
            .inclination_deg = inclination_rad * rad_to_deg,
            .pitch_deg       = pitch * rad_to_deg,
            .roll_deg        = roll * rad_to_deg,
            .total_field_uT  = b_total
        };
    }

    void set_declination(float declination_deg) noexcept {
        declination_rad_ = declination_deg * std::numbers::pi_v<float> / 180.0f;
    }

private:
    float declination_rad_{0.0f};
};

} // namespace navigation
