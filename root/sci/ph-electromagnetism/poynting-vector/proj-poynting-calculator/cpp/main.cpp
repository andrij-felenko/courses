#include <iostream>
#include <cmath>
#include <numbers>
#include <array>
#include <vector>

namespace em::poynting {

struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Vector3D cross(const Vector3D& other) const noexcept {
        return Vector3D{
            y * other.z - z * other.y,
            z * other.x - x * other.z,
            x * other.y - y * other.x
        };
    }

    [[nodiscard]] constexpr double dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] double magnitude() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
};

struct FieldPair {
    Vector3D E;
    Vector3D H;
};

class CoaxialLineSolver {
public:
    constexpr CoaxialLineSolver(double v_volts, double i_amps, double inner_r, double outer_r) noexcept
        : m_v(v_volts), m_i(i_amps), m_a(inner_r), m_b(outer_r), m_ln_ba(std::log(outer_r / inner_r)) {}

    [[nodiscard]] FieldPair compute_fields(double r, double phi) const noexcept {
        const double e_mag = m_v / (r * m_ln_ba);
        const double h_mag = m_i / (2.0 * std::numbers::pi * r);

        return FieldPair{
            .E = Vector3D{e_mag * std::cos(phi), e_mag * std::sin(phi), 0.0},
            .H = Vector3D{-h_mag * std::sin(phi), h_mag * std::cos(phi), 0.0}
        };
    }

    [[nodiscard]] double integrate_power_flux(std::size_t n_r = 200, std::size_t n_phi = 360) const {
        const double dr = (m_b - m_a) / static_cast<double>(n_r);
        const double dphi = (2.0 * std::numbers::pi) / static_cast<double>(n_phi);
        double total_power = 0.0;

        constexpr Vector3D normal_z{0.0, 0.0, 1.0};

        for (std::size_t ir = 0; ir < n_r; ++ir) {
            const double r_mid = m_a + (static_cast<double>(ir) + 0.5) * dr;
            const double da = r_mid * dr * dphi;
            for (std::size_t ip = 0; ip < n_phi; ++ip) {
                const double phi_mid = (static_cast<double>(ip) + 0.5) * dphi;
                const auto [E, H] = compute_fields(r_mid, phi_mid);
                const Vector3D S = E.cross(H);
                total_power += S.dot(normal_z) * da;
            }
        }
        return total_power;
    }

private:
    double m_v;
    double m_i;
    double m_a;
    double m_b;
    double m_ln_ba;
};

} // namespace em::poynting

int main() {
    using namespace em::poynting;

    constexpr double voltage = 100.0;
    constexpr double current = 2.0;
    constexpr double inner_radius = 0.002;  // 2 мм
    constexpr double outer_radius = 0.007;  // 7 мм

    const CoaxialLineSolver solver(voltage, current, inner_radius, outer_radius);
    const double calc_power = solver.integrate_power_flux(200, 360);
    const double theory_power = voltage * current;

    std::cout << "Обчислена потужність C++: " << calc_power << " Вт\n";
    std::cout << "Теоретична потужність (V*I): " << theory_power << " Вт\n";
    return 0;
}
