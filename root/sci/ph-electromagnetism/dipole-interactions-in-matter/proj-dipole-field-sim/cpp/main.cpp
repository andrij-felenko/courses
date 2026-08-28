#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <stdexcept>
#include <span>

namespace physics {

constexpr double vacuum_epsilon0 = 8.8541878128e-12;
constexpr double default_cutoff = 1e-9;

struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr Vector3 operator+(const Vector3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    constexpr Vector3 operator-(const Vector3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    constexpr Vector3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    constexpr double dot(const Vector3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
    constexpr Vector3 cross(const Vector3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
    [[nodiscard]] Vector3 normalized() const noexcept {
        double len = norm();
        if (len < 1e-18) return {0.0, 0.0, 0.0};
        return *this * (1.0 / len);
    }
};

class Dipole {
private:
    Vector3 position_{};
    Vector3 moment_{};

public:
    constexpr Dipole(Vector3 pos, Vector3 p) noexcept : position_(pos), moment_(p) {}

    [[nodiscard]] constexpr Vector3 position() const noexcept { return position_; }
    [[nodiscard]] constexpr Vector3 moment() const noexcept { return moment_; }

    [[nodiscard]] double potential(Vector3 point, double cutoff = default_cutoff) const noexcept {
        Vector3 R = point - position_;
        double r_sq = R.dot(R) + cutoff * cutoff;
        double r_len = std::sqrt(r_sq);
        double k_e = 1.0 / (4.0 * std::numbers::pi * vacuum_epsilon0);
        return k_e * moment_.dot(R) / (r_len * r_len * r_len);
    }

    [[nodiscard]] Vector3 electric_field(Vector3 point, double cutoff = default_cutoff) const noexcept {
        Vector3 R = point - position_;
        double r_sq = R.dot(R) + cutoff * cutoff;
        double r_len = std::sqrt(r_sq);
        double r_pow3 = r_len * r_len * r_len;
        double r_pow5 = r_pow3 * r_sq;
        double k_e = 1.0 / (4.0 * std::numbers::pi * vacuum_epsilon0);

        double dot_pR = moment_.dot(R);
        Vector3 term1 = R * (3.0 * dot_pR / r_pow5);
        Vector3 term2 = moment_ * (1.0 / r_pow3);
        return (term1 - term2) * k_e;
    }

    [[nodiscard]] constexpr Vector3 torque(Vector3 ext_field) const noexcept {
        return moment_.cross(ext_field);
    }

    [[nodiscard]] constexpr double potential_energy(Vector3 ext_field) const noexcept {
        return -moment_.dot(ext_field);
    }
};

class FieldLineTracerRK4 {
private:
    Dipole dipole_;
    double step_size_{1e-10};

public:
    explicit FieldLineTracerRK4(Dipole d, double step_size = 1e-10)
        : dipole_(d), step_size_(step_size) {}

    [[nodiscard]] std::vector<Vector3> trace(Vector3 start_point, std::size_t max_steps = 500) const {
        std::vector<Vector3> path;
        path.reserve(max_steps);
        path.push_back(start_point);

        for (std::size_t i = 1; i < max_steps; ++i) {
            Vector3 curr = path.back();

            Vector3 k1 = dipole_.electric_field(curr).normalized() * step_size_;
            Vector3 k2 = dipole_.electric_field(curr + k1 * 0.5).normalized() * step_size_;
            Vector3 k3 = dipole_.electric_field(curr + k2 * 0.5).normalized() * step_size_;
            Vector3 k4 = dipole_.electric_field(curr + k3).normalized() * step_size_;

            Vector3 step = (k1 + k2 * 2.0 + k3 * 2.0 + k4) * (1.0 / 6.0);
            Vector3 next_pt = curr + step;

            path.push_back(next_pt);

            if ((next_pt - dipole_.position()).norm() > 1e-7) {
                break; // Траєкторія вийшла за межі розгляду
            }
        }
        return path;
    }
};

} // namespace physics

int main() {
    using namespace physics;

    Dipole d({0.0, 0.0, 0.0}, {0.0, 0.0, 1e-29});
    Vector3 eval_pt{0.0, 0.0, 1e-9};

    std::cout << "=== Симуляція диполя (C++20 API) ===\n";
    std::cout << "Потенціал phi(1nm) = " << d.potential(eval_pt) << " V\n";

    Vector3 E = d.electric_field(eval_pt);
    std::cout << "Поле E(1nm) = (" << E.x << ", " << E.y << ", " << E.z << ") V/m\n";

    Vector3 ext_E{1e5, 0.0, 0.0};
    Vector3 torque = d.torque(ext_E);
    std::cout << "Момент torque = (" << torque.x << ", " << torque.y << ", " << torque.z << ") N·m\n";

    FieldLineTracerRK4 tracer(d, 1e-10);
    auto path = tracer.trace(eval_pt, 100);
    std::cout << "Успішно побудовано силову лінію RK4 з " << path.size() << " точок.\n";

    return 0;
}
