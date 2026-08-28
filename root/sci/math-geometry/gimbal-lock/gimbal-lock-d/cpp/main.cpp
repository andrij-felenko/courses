#include <cmath>
#include <algorithm>
#include <numbers>

struct Quaternion {
    double w{1.0};
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

struct EulerAngles {
    double roll{0.0};   // крен φ навколо осі X, радіани
    double pitch{0.0};  // тангаж θ навколо осі Y, радіани
    double yaw{0.0};    // рискання ψ навколо осі Z, радіани
};

[[nodiscard]] constexpr EulerAngles quaternion_to_euler_safe(const Quaternion& q) noexcept {
    EulerAngles angles;
    constexpr double epsilon = 1e-6;
    constexpr double half_pi = std::numbers::pi / 2.0;

    // Захищене обчислення аргументу тангажу
    const double sin_pitch_raw = 2.0 * (q.w * q.y - q.x * q.z);
    const double sin_pitch = std::clamp(sin_pitch_raw, -1.0, 1.0);

    // Ізоляція сингулярності складання рамок
    if (sin_pitch >= 1.0 - epsilon) {
        // Тангаж +90° (зеніт)
        angles.pitch = half_pi;
        angles.roll = 0.0;
        angles.yaw = -2.0 * std::atan2(q.x, q.w);
    } else if (sin_pitch <= -1.0 + epsilon) {
        // Тангаж -90° (надир)
        angles.pitch = -half_pi;
        angles.roll = 0.0;
        angles.yaw = 2.0 * std::atan2(q.x, q.w);
    } else {
        // Регулярна область без виродження
        angles.pitch = std::asin(sin_pitch);

        const double sin_roll = 2.0 * (q.w * q.x + q.y * q.z);
        const double cos_roll = 1.0 - 2.0 * (q.x * q.x + q.y * q.y);
        angles.roll = std::atan2(sin_roll, cos_roll);

        const double sin_yaw = 2.0 * (q.w * q.z + q.x * q.y);
        const double cos_yaw = 1.0 - 2.0 * (q.y * q.y + q.z * q.z);
        angles.yaw = std::atan2(sin_yaw, cos_yaw);
    }

    return angles;
}
