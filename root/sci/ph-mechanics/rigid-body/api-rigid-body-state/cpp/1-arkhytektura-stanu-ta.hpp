// C++ API: Strongly-Typed Object-Oriented Rigid Body Specification
#ifndef RIGID_BODY_HPP
#define RIGID_BODY_HPP

#include <array>
#include <cmath>
#include <expected>
#include <optional>
#include <span>

namespace physics::api {

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double norm_sq() const noexcept { return x * x + y * y + z * z; }
    [[nodiscard]] double norm() const noexcept { return std::sqrt(norm_sq()); }
};

struct Quat {
    double w{1.0};
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double norm_sq() const noexcept { return w * w + x * x + y * y + z * z; }
    [[nodiscard]] double norm() const noexcept { return std::sqrt(norm_sq()); }
};

using Mat3x3 = std::array<std::array<double, 3>, 3>;

enum class ValidationError {
    InvalidMass,
    InvalidInertiaTensor,
    QuaternionDegenerate,
    ContainsNanOrInf
};

struct RigidBodyState {
    Vec3 position{};
    Vec3 linear_velocity{};
    Quat orientation{};
    Vec3 angular_velocity_body{};
};

struct MassProperties {
    double mass{1.0};
    Vec3 principal_inertia{1.0, 1.0, 1.0};
    Vec3 center_of_mass_offset{};

    [[nodiscard]] std::expected<void, ValidationError> validate() const noexcept {
        if (mass <= 0.0 || std::isnan(mass) || std::isinf(mass)) {
            return std::unexpected(ValidationError::InvalidMass);
        }
        if (principal_inertia.x <= 0.0 || principal_inertia.y <= 0.0 || principal_inertia.z <= 0.0) {
            return std::unexpected(ValidationError::InvalidInertiaTensor);
        }
        return {};
    }
};

struct DerivedState {
    double kinetic_energy_transient{0.0};
    double kinetic_energy_rotational{0.0};
    double kinetic_energy_total{0.0};
    Vec3 linear_momentum_world{};
    Vec3 angular_momentum_world{};
    Mat3x3 inertia_tensor_world{};
};

} // namespace physics::api

#endif // RIGID_BODY_HPP
