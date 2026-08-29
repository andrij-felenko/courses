#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <numbers>
#include <span>

#include "admittance.hpp"

namespace robot::arm {

inline constexpr std::size_t kJoints = 6;

using Vec3 = std::array<float, 3>;
using Mat3 = std::array<float, 9>; // РЯДКАМИ: r[0..2] — перший рядок
using JointVector = std::array<float, kJoints>;
using compliance::Vector6;

// Ланка у стандартній нотації Денавіта — Гартенберга.
struct Link {
    float a{};            // зміщення вздовж x_i, м
    float alpha{};        // поворот навколо x_i, рад
    float d{};            // зміщення вздовж z_{i−1}, м
    float theta_offset{}; // сталий доданок до кута суглоба, рад
};

// Демонстраційна антропоморфна рука: плече, лікоть, сферичне зап'ястя.
inline constexpr std::array<Link, kJoints> kDemoArm{{
    {0.000f, std::numbers::pi_v<float> / 2.0f, 0.330f, 0.0f},
    {0.340f, 0.0f, 0.000f, 0.0f},
    {0.040f, std::numbers::pi_v<float> / 2.0f, 0.000f, 0.0f},
    {0.000f, -std::numbers::pi_v<float> / 2.0f, 0.320f, 0.0f},
    {0.000f, std::numbers::pi_v<float> / 2.0f, 0.000f, 0.0f},
    {0.000f, 0.0f, 0.090f, 0.0f},
}};

inline constexpr float kMaxJointRate = 2.0f; // рад/с — межа приводу

// Робочий орган на зап'ястку: маса й центр мас у системі давача.
struct ToolInertia {
    float mass{};
    Vec3 com{};
    float g{9.81f};
};

// Внесок ваги у покази давача: сила Rᵀ·[0,0,−m·g] і момент com × сила.
[[nodiscard]] Vector6 tool_gravity_wrench(const ToolInertia& tool, const Mat3& r_sensor) noexcept;

// F_ext = F_raw − Rᵀ·[0,0,−m·g] (і те саме для моментів).
[[nodiscard]] Vector6 compensate_tool_gravity(const ToolInertia& tool, const Mat3& r_sensor,
                                              const Vector6& raw) noexcept;

// Поворот шістки «трійка + трійка» з системи фланця в базову: годиться
// і для сил із моментами, і для лінійної та кутової швидкості.
[[nodiscard]] Vector6 rotate_to_base(const Mat3& r, const Vector6& body) noexcept;
[[nodiscard]] Vec3 rotate(const Mat3& r, const Vec3& v) noexcept;
[[nodiscard]] Vec3 rotate_inverse(const Mat3& r, const Vec3& v) noexcept;

enum class KinematicFault : std::uint8_t {
    Singular, // якобіан не розкладається навіть із демпфуванням
};

// Пряма кінематика, геометричний якобіан і згасаюча псевдоінверсія.
class Model {
public:
    struct JointMotion {
        JointVector q_dot{};
        float lambda{}; // фактично вжите демпфування
    };

    explicit Model(std::span<const Link, kJoints> links = kDemoArm) noexcept;

    void update(std::span<const float, kJoints> q) noexcept;

    [[nodiscard]] const Mat3& orientation() const noexcept { return r_flange_; }
    [[nodiscard]] const Vec3& position() const noexcept { return p_flange_; }
    [[nodiscard]] float manipulability() const noexcept { return manipulability_; }
    [[nodiscard]] Vec3 tool_point(const Vec3& offset_in_flange) const noexcept;

    // q' = Jᵀ·(J·Jᵀ + lambda²·I)⁻¹·v; lambda росте від нуля при
    // w < w_threshold до lambda_max у сингулярності.
    [[nodiscard]] std::expected<JointMotion, KinematicFault> joint_velocity(
        const Vector6& twist_base, float lambda_max, float w_threshold) const noexcept;

private:
    std::array<Link, kJoints> links_{};
    Mat3 r_flange_{1.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 0.0f, 1.0f};
    Vec3 p_flange_{};
    std::array<JointVector, compliance::kDof> jacobian_{};
    float manipulability_{0.0f};
};

} // namespace robot::arm
