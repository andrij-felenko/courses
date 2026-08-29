#pragma once

#include "linalg.hpp"

#include <expected>

namespace nav {

// Кути Тейта-Браяна, радіани, послідовність Z-Y'-X".
struct EulerAngles {
    float roll{};
    float pitch{};
    float yaw{};
};

// Одиничний кватерніон, угода Гамільтона, порядок пам'яті scalar-first.
class Quaternion {
public:
    float w{1.0F};
    float x{};
    float y{};
    float z{};

    constexpr Quaternion() noexcept = default;
    constexpr Quaternion(float w_, float x_, float y_, float z_) noexcept
        : w(w_), x(x_), y(y_), z(z_) {}

    static Quaternion from_axis_angle(const Vector3& axis, float angle_rad) noexcept;
    static Quaternion from_rotation_vector(const Vector3& phi) noexcept;
    static Quaternion from_euler(const EulerAngles& e) noexcept;

    [[nodiscard]] Quaternion operator*(const Quaternion& q) const noexcept;   // добуток Гамільтона
    [[nodiscard]] constexpr Quaternion conjugate() const noexcept { return {w, -x, -y, -z}; }
    [[nodiscard]] float norm() const noexcept;
    [[nodiscard]] bool finite() const noexcept;
    [[nodiscard]] Quaternion normalized() const noexcept;
    [[nodiscard]] Quaternion normalized_fast() const noexcept;
    [[nodiscard]] Vector3 rotate(const Vector3& v) const noexcept;           // тіло -> світ
    [[nodiscard]] Vector3 rotate_inverse(const Vector3& v) const noexcept;   // світ -> тіло
    [[nodiscard]] Quaternion integrate_gyro(const Vector3& omega, float dt) const noexcept;
    [[nodiscard]] Matrix3 to_matrix() const noexcept;
    [[nodiscard]] EulerAngles to_euler() const noexcept;
};

Quaternion slerp(Quaternion a, Quaternion b, float t) noexcept;
Quaternion nlerp(Quaternion a, Quaternion b, float t) noexcept;

enum class KinematicError { GimbalLock, BadInput };

// Похідні кутів Ейлера з гіроскопа. У шарнірному замку множника 1/cos(θ) не існує —
// і функція каже про це типом, а не мовчазною нескінченністю.
[[nodiscard]] std::expected<EulerAngles, KinematicError> euler_rates(const EulerAngles& angles,
                                                                    const Vector3& omega) noexcept;

}  // namespace nav
