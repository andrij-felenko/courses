#ifndef GEOMETRY_TRANSFORMS_HPP
#define GEOMETRY_TRANSFORMS_HPP

#include <cmath>
#include <algorithm>
#include <array>

namespace nav {

struct EulerAngles {
    float roll{0.0f};   // крен (радіани)
    float pitch{0.0f};  // тангаж (радіани)
    float yaw{0.0f};    // курс (радіани)
};

class Vector3 {
public:
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3() noexcept = default;
    constexpr Vector3(float x_val, float y_val, float z_val) noexcept 
        : x(x_val), y(y_val), z(z_val) {}

    constexpr Vector3 operator+(const Vector3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }

    constexpr Vector3 operator-(const Vector3& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }

    constexpr Vector3 operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    [[nodiscard]] constexpr float dot(const Vector3& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }

    [[nodiscard]] constexpr Vector3 cross(const Vector3& rhs) const noexcept {
        return {
            y * rhs.z - z * rhs.y,
            z * rhs.x - x * rhs.z,
            x * rhs.y - y * rhs.x
        };
    }

    [[nodiscard]] float length() const noexcept {
        return std::sqrt(dot(*this));
    }
};

class Matrix3x3 {
public:
    std::array<std::array<float, 3>, 3> m{};

    constexpr Matrix3x3() noexcept = default;
    constexpr explicit Matrix3x3(const std::array<std::array<float, 3>, 3>& values) noexcept 
        : m(values) {}

    [[nodiscard]] constexpr Vector3 operator*(const Vector3& v) const noexcept {
        return {
            m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z,
            m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z,
            m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z
        };
    }

    [[nodiscard]] static constexpr Matrix3x3 identity() noexcept {
        return Matrix3x3{{{
            {1.0f, 0.0f, 0.0f},
            {0.0f, 1.0f, 0.0f},
            {0.0f, 0.0f, 1.0f}
        }}};
    }
};

class Quaternion {
public:
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Quaternion() noexcept = default;
    constexpr Quaternion(float w_val, float x_val, float y_val, float z_val) noexcept
        : w(w_val), x(x_val), y(y_val), z(z_val) {}

    [[nodiscard]] Quaternion normalized_fast() const noexcept {
        const float sq_norm = w * w + x * x + y * y + z * z;
        if (sq_norm < 1e-6f) {
            return {1.0f, 0.0f, 0.0f, 0.0f};
        }
        const float factor = 1.5f - 0.5f * sq_norm;
        return {w * factor, x * factor, y * factor, z * factor};
    }

    [[nodiscard]] Vector3 rotate(const Vector3& v) const noexcept {
        const Vector3 q_vec{x, y, z};
        const Vector3 t = q_vec.cross(v) + v * w;
        return v + q_vec.cross(t) * 2.0f;
    }

    [[nodiscard]] Quaternion integrate_gyro(const Vector3& omega, float dt) const noexcept {
        const float half_dt = 0.5f * dt;
        const Quaternion delta_q{
            half_dt * (-x * omega.x - y * omega.y - z * omega.z),
            half_dt * ( w * omega.x + y * omega.z - z * omega.y),
            half_dt * ( w * omega.y - x * omega.z + z * omega.x),
            half_dt * ( w * omega.z + x * omega.y - y * omega.x)
        };
        const Quaternion next_q{
            w + delta_q.w,
            x + delta_q.x,
            y + delta_q.y,
            z + delta_q.z
        };
        return next_q.normalized_fast();
    }

    [[nodiscard]] EulerAngles to_euler() const noexcept {
        EulerAngles e{};
        
        // Крен
        const float sinr_cosp = 2.0f * (w * x + y * z);
        const float cosr_cosp = 1.0f - 2.0f * (x * x + y * y);
        e.roll = std::atan2(sinr_cosp, cosr_cosp);

        // Тангаж з безпечним затисканням
        const float sinp = std::clamp(2.0f * (w * y - z * x), -1.0f, 1.0f);
        e.pitch = std::asin(sinp);

        // Рискання
        const float siny_cosp = 2.0f * (w * z + x * y);
        const float cosy_cosp = 1.0f - 2.0f * (y * y + z * z);
        e.yaw = std::atan2(siny_cosp, cosy_cosp);

        return e;
    }
};

// Конвеєр вирівнювання сенсора
[[nodiscard]] inline Vector3 align_sensor_measurement(
    const Vector3& raw,
    const Vector3& bias,
    const Matrix3x3& scale_ortho,
    const Matrix3x3& r_align,
    const Matrix3x3& r_board) noexcept 
{
    const Vector3 unbiased = raw - bias;
    const Vector3 scaled = scale_ortho * unbiased;
    const Vector3 aligned = r_align * scaled;
    return r_board * aligned;
}

} // namespace nav

#endif // GEOMETRY_TRANSFORMS_HPP
