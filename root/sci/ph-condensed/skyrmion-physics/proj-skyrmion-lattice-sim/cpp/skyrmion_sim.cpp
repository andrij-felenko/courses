// skyrmion_sim.cpp — Чисельне моделювання магнітного скирміона мовою C++
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <memory>

struct Spin3D {
    double x{0.0};
    double y{0.0};
    double z{1.0};

    [[nodiscard]] Spin3D normalized() const noexcept {
        double len = std::sqrt(x * x + y * y + z * z);
        if (len > 1e-12) {
            return {x / len, y / len, z / len};
        }
        return *this;
    }

    [[nodiscard]] static double dot(const Spin3D& a, const Spin3D& b) noexcept {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }

    [[nodiscard]] static Spin3D cross(const Spin3D& a, const Spin3D& b) noexcept {
        return {
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        };
    }
};

class SkyrmionLattice {
public:
    SkyrmionLattice(std::size_t grid_size, double step_meters)
        : size_(grid_size), step_(step_meters), spins_(grid_size * grid_size) {}

    void initialize_neel_skyrmion(double radius_meters) {
        const double center = (static_cast<double>(size_) - 1.0) / 2.0;

        for (std::size_t r = 0; r < size_; ++r) {
            for (std::size_t c = 0; c < size_; ++c) {
                double dx = (static_cast<double>(c) - center) * step_;
                double dy = (static_cast<double>(r) - center) * step_;
                double dist = std::hypot(dx, dy);

                double theta = std::numbers::pi;
                if (dist < radius_meters) {
                    theta = std::numbers::pi * (1.0 - dist / radius_meters);
                } else {
                    theta = 0.0;
                }

                double phi = std::atan2(dy, dx);

                Spin3D s{
                    std::sin(theta) * std::cos(phi),
                    std::sin(theta) * std::sin(phi),
                    std::cos(theta)
                };

                spins_[index(r, c)] = s.normalized();
            }
        }
    }

    [[nodiscard]] double compute_topological_charge() const noexcept {
        double total_q = 0.0;

        for (std::size_t r = 0; r < size_ - 1; ++r) {
            for (std::size_t c = 0; c < size_ - 1; ++c) {
                const auto& m00 = spins_[index(r, c)];
                const auto& m10 = spins_[index(r, c + 1)];
                const auto& m01 = spins_[index(r + 1, c)];
                const auto& m11 = spins_[index(r + 1, c + 1)];

                total_q += solid_angle(m00, m10, m01);
                total_q += solid_angle(m11, m01, m10);
            }
        }

        return total_q / (4.0 * std::numbers::pi);
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }

private:
    std::size_t size_;
    double step_;
    std::vector<Spin3D> spins_;

    [[nodiscard]] std::size_t index(std::size_t r, std::size_t c) const noexcept {
        return r * size_ + c;
    }

    [[nodiscard]] static double solid_angle(const Spin3D& m1, const Spin3D& m2, const Spin3D& m3) noexcept {
        double triple_prod = Spin3D::dot(m1, Spin3D::cross(m2, m3));
        double denom = 1.0 + Spin3D::dot(m1, m2) + Spin3D::dot(m2, m3) + Spin3D::dot(m3, m1);
        return 2.0 * std::atan2(triple_prod, denom);
    }
};

int main() {
    constexpr std::size_t grid_N = 64;
    constexpr double grid_step = 1.0e-9;  // 1 nm
    constexpr double skyrmion_r = 12.0e-9; // 12 nm

    SkyrmionLattice lattice(grid_N, grid_step);
    lattice.initialize_neel_skyrmion(skyrmion_r);

    double charge_Q = lattice.compute_topological_charge();

    std::cout << "Розмір сітки: " << lattice.size() << "x" << lattice.size() << "\n";
    std::cout << "Топологічний заряд Q = " << charge_Q << "\n";

    return 0;
}
