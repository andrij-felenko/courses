#include <iostream>
#include <cmath>
#include <array>
#include <optional>
#include <algorithm>

struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Vector3D operator+(const Vector3D& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3D operator-(const Vector3D& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vector3D operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] constexpr double dot(const Vector3D& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
    [[nodiscard]] constexpr Vector3D cross(const Vector3D& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
    [[nodiscard]] Vector3D clamp_magnitude(double max_val) const noexcept {
        const double n = norm();
        if (n > max_val && n > 1e-6) {
            return (*this) * (max_val / n);
        }
        return *this;
    }
};

struct GuidanceParameters {
    double navigation_ratio{3.5};
    double max_acceleration{25.0}; // [м/с^2]
    double min_distance{0.2};       // [м]
    double min_closing_velocity{0.1}; // [м/с]
    bool enable_augmented_pn{true};
};

class ProportionalNavigationSolver {
public:
    explicit ProportionalNavigationSolver(GuidanceParameters params = {}) noexcept
        : params_{params} {}

    [[nodiscard]] Vector3D compute_acceleration(
        const Vector3D& drone_pos,
        const Vector3D& drone_vel,
        const Vector3D& target_pos,
        const Vector3D& target_vel,
        const Vector3D& target_acc
    ) const noexcept {
        const Vector3D R_vec = target_pos - drone_pos;
        const double R = R_vec.norm();

        if (R < params_.min_distance) {
            return {0.0, 0.0, 0.0};
        }

        const Vector3D e_los = R_vec * (1.0 / R);
        const Vector3D V_r = target_vel - drone_vel;

        double V_c = -e_los.dot(V_r);
        if (V_c < params_.min_closing_velocity) {
            V_c = params_.min_closing_velocity;
        }

        const Vector3D cross_rv = R_vec.cross(V_r);
        const Vector3D Omega = cross_rv * (1.0 / (R * R));

        const Vector3D a_pn = Omega.cross(e_los) * (params_.navigation_ratio * V_c);

        Vector3D a_total = a_pn;
        if (params_.enable_augmented_pn) {
            const Vector3D a_t_parallel = e_los * target_acc.dot(e_los);
            const Vector3D a_t_perp = target_acc - a_t_parallel;
            const Vector3D a_apn = a_t_perp * (params_.navigation_ratio * 0.5);
            a_total = a_total + a_apn;
        }

        return a_total.clamp_magnitude(params_.max_acceleration);
    }

private:
    GuidanceParameters params_;
};
