// C++ Implementation: Object-Oriented 3D Rigid Body Simulator
#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>

namespace physics {

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vec3 operator+(const Vec3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(double s) const { return {x * s, y * s, z * s}; }

    constexpr Vec3 cross(const Vec3& o) const {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
};

struct Quat {
    double w{1.0}, x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] Quat normalized() const {
        double len = std::sqrt(w * w + x * x + y * y + z * z);
        if (len < 1e-12) return {1.0, 0.0, 0.0, 0.0};
        return {w / len, x / len, y / len, z / len};
    }

    [[nodiscard]] Quat derivative(const Vec3& w_vec) const {
        return {
            0.5 * (-x * w_vec.x - y * w_vec.y - z * w_vec.z),
            0.5 * ( w * w_vec.x + y * w_vec.z - z * w_vec.y),
            0.5 * ( w * w_vec.y + z * w_vec.x - x * w_vec.z),
            0.5 * ( w * w_vec.z + x * w_vec.y - y * w_vec.x)
        };
    }
};

struct RigidBodyState {
    Vec3 pos{};
    Vec3 vel{};
    Quat quat{};
    Vec3 omega{};

    RigidBodyState operator+(const RigidBodyState& d) const {
        return {
            pos + d.pos,
            vel + d.vel,
            {quat.w + d.quat.w, quat.x + d.quat.x, quat.y + d.quat.y, quat.z + d.quat.z},
            omega + d.omega
        };
    }

    RigidBodyState scale(double dt) const {
        return {
            pos * dt,
            vel * dt,
            {quat.w * dt, quat.x * dt, quat.y * dt, quat.z * dt},
            omega * dt
        };
    }
};

struct MassProperties {
    double mass{1.0};
    Vec3 inertia_diag{1.0, 1.0, 1.0};
};

class RigidBody {
public:
    RigidBody(MassProperties props, RigidBodyState initial_state)
        : props_(props), state_(initial_state) {}

    void step_rk4(Vec3 force_world, Vec3 torque_body, double dt) {
        auto compute_deriv = [this, &force_world, &torque_body](const RigidBodyState& s) -> RigidBodyState {
            Vec3 d_pos = s.vel;
            Vec3 d_vel = force_world * (1.0 / props_.mass);
            Quat d_quat = s.quat.derivative(s.omega);

            Vec3 Iw{
                props_.inertia_diag.x * s.omega.x,
                props_.inertia_diag.y * s.omega.y,
                props_.inertia_diag.z * s.omega.z
            };
            Vec3 gyro = s.omega.cross(Iw);
            Vec3 net_torque = torque_body - gyro;

            Vec3 d_omega{
                net_torque.x / props_.inertia_diag.x,
                net_torque.y / props_.inertia_diag.y,
                net_torque.z / props_.inertia_diag.z
            };
            return {d_pos, d_vel, d_quat, d_omega};
        };

        RigidBodyState k1 = compute_deriv(state_);

        RigidBodyState s2 = state_ + k1.scale(dt * 0.5);
        s2.quat = s2.quat.normalized();
        RigidBodyState k2 = compute_deriv(s2);

        RigidBodyState s3 = state_ + k2.scale(dt * 0.5);
        s3.quat = s3.quat.normalized();
        RigidBodyState k3 = compute_deriv(s3);

        RigidBodyState s4 = state_ + k3.scale(dt);
        s4.quat = s4.quat.normalized();
        RigidBodyState k4 = compute_deriv(s4);

        RigidBodyState step_change = (k1 + (k2.scale(2.0)) + (k3.scale(2.0)) + k4).scale(dt / 6.0);
        state_ = state_ + step_change;
        state_.quat = state_.quat.normalized();
    }

    [[nodiscard]] const RigidBodyState& state() const { return state_; }

private:
    MassProperties props_;
    RigidBodyState state_;
};

} // namespace physics

int main() {
    using namespace physics;

    MassProperties props{
        .mass = 2.0,
        .inertia_diag = {1.0, 2.0, 3.0}
    };

    RigidBodyState init_state{
        .pos = {0.0, 0.0, 10.0},
        .vel = {0.0, 0.0, 0.0},
        .quat = {1.0, 0.0, 0.0, 0.0},
        .omega = {1.0, 20.0, 0.1}
    };

    RigidBody body(props, init_state);
    Vec3 gravity{0.0, 0.0, -9.81 * 2.0};
    Vec3 zero_torque{0.0, 0.0, 0.0};
    double dt = 0.001;

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Time(s)\t Z-Pos\t\t Omega_X\t Omega_Y\t Omega_Z\n";

    for (int step = 0; step <= 2000; ++step) {
        if (step % 200 == 0) {
            const auto& s = body.state();
            std::cout << step * dt << "\t " << s.pos.z << "\t\t "
                      << s.omega.x << "\t " << s.omega.y << "\t " << s.omega.z << "\n";
        }
        body.step_rk4(gravity, zero_torque, dt);
    }
    return 0;
}
