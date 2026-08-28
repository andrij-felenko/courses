#include <iostream>
#include <array>
#include <cmath>
#include <optional>
#include <span>
#include <concepts>

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vec3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] constexpr double dot(const Vec3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
    [[nodiscard]] Vec3 clamp_norm(double max_val) const noexcept {
        const double n = norm();
        if (n > max_val && n > 1e-6) {
            return (*this) * (max_val / n);
        }
        return *this;
    }
};

/* Одновимірний фільтр Калмана з постійним прискоренням (Singer модель) */
class AxisKalman {
public:
    explicit AxisKalman(double init_p = 0.0, double q_acc = 1.0, double r_meas = 0.1) noexcept
        : p_{init_p}, q_acc_{q_acc}, r_meas_{r_meas} {
        P_[0][0] = 10.0; P_[1][1] = 10.0; P_[2][2] = 10.0;
    }

    void predict(double dt) noexcept {
        const double dt2 = 0.5 * dt * dt;
        p_ += v_ * dt + a_ * dt2;
        v_ += a_ * dt;

        const double P00 = P_[0][0] + dt * (P_[1][0] + P_[0][1]) + dt2 * (P_[2][0] + P_[0][2])
                         + dt * dt * P_[1][1] + dt * dt2 * (P_[2][1] + P_[1][2]) + dt2 * dt2 * P_[2][2];
        const double P01 = P_[0][1] + dt * P_[1][1] + dt2 * P_[2][1] + dt * P_[0][2] + dt * dt * P_[1][2] + dt * dt2 * P_[2][2];
        const double P02 = P_[0][2] + dt * P_[1][2] + dt2 * P_[2][2];
        const double P11 = P_[1][1] + dt * (P_[2][1] + P_[1][2]) + dt * dt * P_[2][2];
        const double P12 = P_[1][2] + dt * P_[2][2];
        const double P22 = P_[2][2] + q_acc_ * dt;

        P_[0][0] = P00; P_[0][1] = P01; P_[0][2] = P02;
        P_[1][0] = P01; P_[1][1] = P11; P_[1][2] = P12;
        P_[2][0] = P02; P_[2][1] = P12; P_[2][2] = P22;
    }

    void update(double z_meas) noexcept {
        const double inn = z_meas - p_;
        const double s = P_[0][0] + r_meas_;
        if (std::abs(s) < 1e-9) return;

        const double k0 = P_[0][0] / s;
        const double k1 = P_[1][0] / s;
        const double k2 = P_[2][0] / s;

        p_ += k0 * inn;
        v_ += k1 * inn;
        a_ += k2 * inn;

        const double p00 = P_[0][0], p01 = P_[0][1], p02 = P_[0][2];
        P_[0][0] -= k0 * p00; P_[0][1] -= k0 * p01; P_[0][2] -= k0 * p02;
        P_[1][0] -= k1 * p00; P_[1][1] -= k1 * p01; P_[1][2] -= k1 * p02;
        P_[2][0] -= k2 * p00; P_[2][1] -= k2 * p01; P_[2][2] -= k2 * p02;
    }

    [[nodiscard]] constexpr double position() const noexcept { return p_; }
    [[nodiscard]] constexpr double velocity() const noexcept { return v_; }
    [[nodiscard]] constexpr double acceleration() const noexcept { return a_; }

private:
    double p_{0.0};
    double v_{0.0};
    double a_{0.0};
    std::array<std::array<double, 3>, 3> P_{};
    double q_acc_{1.0};
    double r_meas_{0.1};
};

/* 3D Оцінювач стану цілі */
class TargetEstimator3D {
public:
    TargetEstimator3D(Vec3 init_pos, double q_acc = 1.5, double r_meas = 0.05) noexcept
        : kf_x_{init_pos.x, q_acc, r_meas},
          kf_y_{init_pos.y, q_acc, r_meas},
          kf_z_{init_pos.z, q_acc, r_meas} {}

    void step(double dt, std::optional<Vec3> raw_measurement) noexcept {
        kf_x_.predict(dt);
        kf_y_.predict(dt);
        kf_z_.predict(dt);

        if (raw_measurement.has_value()) {
            kf_x_.update(raw_measurement->x);
            kf_y_.update(raw_measurement->y);
            kf_z_.update(raw_measurement->z);
        }
    }

    [[nodiscard]] Vec3 position() const noexcept {
        return {kf_x_.position(), kf_y_.position(), kf_z_.position()};
    }
    [[nodiscard]] Vec3 velocity() const noexcept {
        return {kf_x_.velocity(), kf_y_.velocity(), kf_z_.velocity()};
    }
    [[nodiscard]] Vec3 acceleration() const noexcept {
        return {kf_x_.acceleration(), kf_y_.acceleration(), kf_z_.acceleration()};
    }

private:
    AxisKalman kf_x_, kf_y_, kf_z_;
};

struct GuidanceSettings {
    double navigation_ratio{3.5};
    double max_acceleration{20.0}; // [м/с^2] ~2G
    bool enable_apn{true};
};

/* Контролер пропорційного наведення */
class ProportionalNavigationGuidance {
public:
    explicit ProportionalNavigationGuidance(GuidanceSettings settings = {}) noexcept
        : settings_{settings} {}

    [[nodiscard]] Vec3 compute_command(
        const Vec3& drone_pos,
        const Vec3& drone_vel,
        const TargetEstimator3D& target_est
    ) const noexcept {
        const Vec3 r_target = target_est.position();
        const Vec3 v_target = target_est.velocity();
        const Vec3 a_target = target_est.acceleration();

        const Vec3 R_vec = r_target - drone_pos;
        const double R_norm = R_vec.norm();
        if (R_norm < 0.1) {
            return {0.0, 0.0, 0.0};
        }

        const Vec3 e_los = R_vec * (1.0 / R_norm);
        const Vec3 V_r = v_target - drone_vel;

        double V_c = -e_los.dot(V_r);
        if (V_c < 0.1) {
            V_c = 0.1; // Запобігання інверсії знаку
        }

        const Vec3 cross_rv = R_vec.cross(V_r);
        const Vec3 Omega = cross_rv * (1.0 / (R_norm * R_norm));

        const Vec3 a_pn = Omega.cross(e_los) * (settings_.navigation_ratio * V_c);

        Vec3 a_cmd = a_pn;
        if (settings_.enable_apn) {
            const Vec3 a_t_parallel = e_los * a_target.dot(e_los);
            const Vec3 a_t_perp = a_target - a_t_parallel;
            const Vec3 a_apn = a_t_perp * (settings_.navigation_ratio * 0.5);
            a_cmd = a_cmd + a_apn;
        }

        return a_cmd.clamp_norm(settings_.max_acceleration);
    }

private:
    GuidanceSettings settings_;
};
