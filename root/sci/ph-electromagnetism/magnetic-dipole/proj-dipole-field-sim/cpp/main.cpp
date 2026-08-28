#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <fstream>
#include <string_view>
#include <memory>
#include <span>

namespace physics {

constexpr double MU0_OVER_4PI = 1.0e-7;
constexpr double PLUMMER_EPS = 1.0e-5;

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vector3D operator+(const Vector3D& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr Vector3D operator-(const Vector3D& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    constexpr Vector3D operator*(double scale) const noexcept {
        return {x * scale, y * scale, z * scale};
    }
    
    [[nodiscard]] double dot(const Vector3D& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }
    [[nodiscard]] Vector3D cross(const Vector3D& rhs) const noexcept {
        return {
            y * rhs.z - z * rhs.y,
            z * rhs.x - x * rhs.z,
            x * rhs.y - y * rhs.x
        };
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
    [[nodiscard]] Vector3D normalized() const noexcept {
        const double len = norm();
        return (len < 1.0e-12) ? Vector3D{0, 0, 0} : (*this) * (1.0 / len);
    }
};

struct MagneticDipole {
    Vector3D position; // Положення r (м)
    Vector3D moment;   // Магнітний момент m (А·м²)
};

class DipoleSimulator {
public:
    explicit DipoleSimulator(std::vector<MagneticDipole> dipoles)
        : dipoles_(std::move(dipoles)) {}

    [[nodiscard]] Vector3D computeField(const Vector3D& point) const noexcept {
        Vector3D total_field{0.0, 0.0, 0.0};
        for (const auto& dipole : dipoles_) {
            const Vector3D R = point - dipole.position;
            const double r2 = R.dot(R) + PLUMMER_EPS * PLUMMER_EPS;
            const double r = std::sqrt(r2);
            const Vector3D R_hat = R * (1.0 / r);
            const double m_dot_rhat = dipole.moment.dot(R_hat);

            const Vector3D B_dip = (R_hat * (3.0 * m_dot_rhat) - dipole.moment) * 
                                  (MU0_OVER_4PI / (r * r * r));
            total_field = total_field + B_dip;
        }
        return total_field;
    }

    struct ForceTorqueResult {
        Vector3D force;
        Vector3D torque;
    };

    [[nodiscard]] ForceTorqueResult computeForceAndTorque(size_t target_idx) const {
        if (target_idx >= dipoles_.size()) {
            throw std::out_of_range("Dipole index out of range");
        }

        Vector3D total_force{0.0, 0.0, 0.0};
        Vector3D ext_field{0.0, 0.0, 0.0};
        const auto& target = dipoles_[target_idx];

        for (size_t j = 0; j < dipoles_.size(); ++j) {
            if (j == target_idx) continue;

            const Vector3D R = target.position - dipoles_[j].position;
            const double r2 = R.dot(R) + PLUMMER_EPS * PLUMMER_EPS;
            const double r = std::sqrt(r2);
            const double r4 = r2 * r2;
            const Vector3D R_hat = R * (1.0 / r);

            const double m1_r = dipoles_[j].moment.dot(R_hat);
            const double m2_r = target.moment.dot(R_hat);
            const double m1_m2 = dipoles_[j].moment.dot(target.moment);

            const Vector3D term1 = target.moment * m1_r;
            const Vector3D term2 = dipoles_[j].moment * m2_r;
            const Vector3D term3 = R_hat * (m1_m2 - 5.0 * m1_r * m2_r);

            const Vector3D F_ij = (term1 + term2 + term3) * (3.0 * MU0_OVER_4PI / r4);
            total_force = total_force + F_ij;

            const Vector3D B_j = (R_hat * (3.0 * m1_r) - dipoles_[j].moment) * 
                                 (MU0_OVER_4PI / (r * r * r));
            ext_field = ext_field + B_j;
        }

        return {total_force, target.moment.cross(ext_field)};
    }

    [[nodiscard]] std::vector<Vector3D> traceFieldLineRK4(
        Vector3D start_point, double step_size, size_t num_steps) const {
        
        std::vector<Vector3D> path;
        path.reserve(num_steps + 1);
        Vector3D current = start_point;
        path.push_back(current);

        for (size_t i = 0; i < num_steps; ++i) {
            const Vector3D k1 = computeField(current).normalized();
            const Vector3D k2 = computeField(current + k1 * (0.5 * step_size)).normalized();
            const Vector3D k3 = computeField(current + k2 * (0.5 * step_size)).normalized();
            const Vector3D k4 = computeField(current + k3 * step_size).normalized();

            const Vector3D dr = (k1 + k2 * 2.0 + k3 * 2.0 + k4) * (step_size / 6.0);
            current = current + dr;
            path.push_back(current);
        }

        return path;
    }

    void exportFieldGridCSV(std::string_view filename, 
                           double bounds, size_t resolution) const {
        std::ofstream file(filename.data());
        if (!file.is_open()) {
            throw std::runtime_error("Failed to open file for writing");
        }

        file << "x,y,z,Bx,By,Bz,B_mag\n";
        const double step = (2.0 * bounds) / static_cast<double>(resolution - 1);

        for (size_t ix = 0; ix < resolution; ++ix) {
            const double x = -bounds + ix * step;
            for (size_t iy = 0; iy < resolution; ++iy) {
                const double y = -bounds + iy * step;
                const Vector3D p{x, y, 0.0};
                const Vector3D B = computeField(p);
                file << x << "," << y << ",0.0," 
                     << B.x << "," << B.y << "," << B.z << "," << B.norm() << "\n";
            }
        }
    }

private:
    std::vector<MagneticDipole> dipoles_;
};

} // namespace physics

int main() {
    using namespace physics;

    std::vector<MagneticDipole> system{
        {{-0.05, 0.0, 0.0}, {0.0, 0.0, 1.0}},
        {{ 0.05, 0.0, 0.0}, {0.0, 0.0, 1.0}}
    };

    DipoleSimulator sim(std::move(system));

    std::cout << "=== СИМУЛЯЦІЯ ДИПОЛЬНИХ ПОЛІВ ТА СИЛ (C++20) ===\n";

    auto [force0, torque0] = sim.computeForceAndTorque(0);
    auto [force1, torque1] = sim.computeForceAndTorque(1);

    std::cout << "Диполь 0: Сила F = (" << force0.x << ", " << force0.y << ", " << force0.z << ") Н\n";
    std::cout << "Диполь 0: Момент τ = (" << torque0.x << ", " << torque0.y << ", " << torque0.z << ") Н·м\n";

    std::cout << "\nТрасування силової лінії (RK4, 10 кроків):\n";
    auto line = sim.traceFieldLineRK4({0.06, 0.0, 0.01}, 0.005, 10);
    for (size_t i = 0; i < line.size(); ++i) {
        const auto B = sim.computeField(line[i]);
        std::cout << "Крок " << i << ": pos = (" << line[i].x << ", " << line[i].y << ", " << line[i].z 
                  << ") м | |B| = " << B.norm() << " Тл\n";
    }

    try {
        sim.exportFieldGridCSV("dipole_field_grid.csv", 0.15, 20);
        std::cout << "\nСітку векторного поля успішно збережено у dipole_field_grid.csv\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка збереження файлу: " << e.what() << "\n";
    }

    return 0;
}
