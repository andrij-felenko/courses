#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    constexpr Vec3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    Vec3& operator+=(const Vec3& o) noexcept {
        x += o.x; y += o.y; z += o.z;
        return *this;
    }
};

class CircularCurrentLoop {
public:
    constexpr CircularCurrentLoop(double radius, double current, std::size_t segments = 1000) noexcept
        : radius_(radius), current_(current), segments_(segments) {}

    [[nodiscard]] Vec3 vectorPotential(const Vec3& r) const noexcept {
        Vec3 a{};
        const double d_theta = (2.0 * std::numbers::pi) / static_cast<double>(segments_);

        for (std::size_t k = 0; k < segments_; ++k) {
            const double theta = static_cast<double>(k) * d_theta;
            const double rk_x = radius_ * std::cos(theta);
            const double rk_y = radius_ * std::sin(theta);

            const double dl_x = -radius_ * std::sin(theta) * d_theta;
            const double dl_y =  radius_ * std::cos(theta) * d_theta;

            const double dx = r.x - rk_x;
            const double dy = r.y - rk_y;
            const double dz = r.z;
            const double dist = std::sqrt(dx * dx + dy * dy + dz * dz);

            if (dist > 1e-12) {
                a.x += dl_x / dist;
                a.y += dl_y / dist;
            }
        }

        constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;
        const double factor = (mu_0 * current_) / (4.0 * std::numbers::pi);
        return a * factor;
    }

    [[nodiscard]] Vec3 magneticFieldCurl(const Vec3& r, double h = 1e-4) const noexcept {
        const auto a_yp = vectorPotential({r.x, r.y + h, r.z});
        const auto a_ym = vectorPotential({r.x, r.y - h, r.z});
        const auto a_zp = vectorPotential({r.x, r.y, r.z + h});
        const auto a_zm = vectorPotential({r.x, r.y, r.z - h});
        const auto a_xp = vectorPotential({r.x + h, r.y, r.z});
        const auto a_xm = vectorPotential({r.x - h, r.y, r.z});

        const double dAz_dy = (a_yp.z - a_ym.z) / (2.0 * h);
        const double dAy_dz = (a_zp.y - a_zm.y) / (2.0 * h);

        const double dAx_dz = (a_zp.x - a_zm.x) / (2.0 * h);
        const double dAz_dx = (a_xp.z - a_xm.z) / (2.0 * h);

        const double dAy_dx = (a_xp.y - a_xm.y) / (2.0 * h);
        const double dAx_dy = (a_yp.x - a_ym.x) / (2.0 * h);

        return {
            dAz_dy - dAy_dz,
            dAx_dz - dAz_dx,
            dAy_dx - dAx_dy
        };
    }

    [[nodiscard]] double exactOnAxisFieldZ(double z) const noexcept {
        constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;
        return (mu_0 * current_ * radius_ * radius_) /
               (2.0 * std::pow(radius_ * radius_ + z * z, 1.5));
    }

private:
    double radius_;
    double current_;
    std::size_t segments_;
};

int main() {
    const CircularCurrentLoop loop(0.1, 10.0, 1000);
    constexpr double h = 1e-4;

    std::cout << "Порівняння чисельного B = rot A з аналітичною формулою на осі Z:\n";
    std::cout << std::setw(8) << "z, м" << " | "
              << std::setw(14) << "B_num (T)" << " | "
              << std::setw(14) << "B_exact (T)" << " | "
              << std::setw(12) << "Похибка (%)" << "\n";
    std::cout << std::string(58, '-') << "\n";

    for (double z = 0.02; z <= 0.20; z += 0.02) {
        const Vec3 r{0.0, 0.0, z};
        const Vec3 b_num = loop.magneticFieldCurl(r, h);
        const double b_exact = loop.exactOnAxisFieldZ(z);
        const double err = std::abs(b_num.z - b_exact) / b_exact * 100.0;

        std::cout << std::fixed << std::setprecision(2) << std::setw(8) << z << " | "
                  << std::scientific << std::setprecision(6) << std::setw(14) << b_num.z << " | "
                  << std::setw(14) << b_exact << " | "
                  << std::fixed << std::setprecision(4) << std::setw(11) << err << "%\n";
    }

    return 0;
}
