// C++ Implementation: Derived Computations using Modern C++ Types
#include <cmath>
#include <expected>

namespace physics::api {

[[nodiscard]] inline DerivedState compute_derived(const RigidBodyState& s, const MassProperties& m) noexcept {
    DerivedState d;

    double v_sq = s.linear_velocity.norm_sq();
    d.kinetic_energy_transient = 0.5 * m.mass * v_sq;

    d.kinetic_energy_rotational = 0.5 * (
        m.principal_inertia.x * s.angular_velocity_body.x * s.angular_velocity_body.x +
        m.principal_inertia.y * s.angular_velocity_body.y * s.angular_velocity_body.y +
        m.principal_inertia.z * s.angular_velocity_body.z * s.angular_velocity_body.z
    );

    d.kinetic_energy_total = d.kinetic_energy_transient + d.kinetic_energy_rotational;

    d.linear_momentum_world = {
        m.mass * s.linear_velocity.x,
        m.mass * s.linear_velocity.y,
        m.mass * s.linear_velocity.z
    };

    Vec3 L_body{
        m.principal_inertia.x * s.angular_velocity_body.x,
        m.principal_inertia.y * s.angular_velocity_body.y,
        m.principal_inertia.z * s.angular_velocity_body.z
    };

    const auto& q = s.orientation;
    double R00 = 1.0 - 2.0 * (q.y * q.y + q.z * q.z);
    double R01 = 2.0 * (q.x * q.y - q.z * q.w);
    double R02 = 2.0 * (q.x * q.z + q.y * q.w);

    double R10 = 2.0 * (q.x * q.y + q.z * q.w);
    double R11 = 1.0 - 2.0 * (q.x * q.x + q.z * q.z);
    double R12 = 2.0 * (q.y * q.z - q.x * q.w);

    double R20 = 2.0 * (q.x * q.z - q.y * q.w);
    double R21 = 2.0 * (q.y * q.z + q.x * q.w);
    double R22 = 1.0 - 2.0 * (q.x * q.x + q.y * q.y);

    d.angular_momentum_world = {
        R00 * L_body.x + R01 * L_body.y + R02 * L_body.z,
        R10 * L_body.x + R11 * L_body.y + R12 * L_body.z,
        R20 * L_body.x + R21 * L_body.y + R22 * L_body.z
    };

    d.inertia_tensor_world = {{
        { R00*R00*m.principal_inertia.x + R01*R01*m.principal_inertia.y + R02*R02*m.principal_inertia.z,
          R00*R10*m.principal_inertia.x + R01*R11*m.principal_inertia.y + R02*R12*m.principal_inertia.z,
          R00*R20*m.principal_inertia.x + R01*R21*m.principal_inertia.y + R02*R22*m.principal_inertia.z },
        { R00*R10*m.principal_inertia.x + R01*R11*m.principal_inertia.y + R02*R12*m.principal_inertia.z,
          R10*R10*m.principal_inertia.x + R11*R11*m.principal_inertia.y + R12*R12*m.principal_inertia.z,
          R10*R20*m.principal_inertia.x + R11*R21*m.principal_inertia.y + R12*R22*m.principal_inertia.z },
        { R00*R20*m.principal_inertia.x + R01*R21*m.principal_inertia.y + R02*R22*m.principal_inertia.z,
          R10*R20*m.principal_inertia.x + R11*R21*m.principal_inertia.y + R12*R22*m.principal_inertia.z,
          R20*R20*m.principal_inertia.x + R21*R21*m.principal_inertia.y + R22*R22*m.principal_inertia.z }
    }};

    return d;
}

} // namespace physics::api
