#include <iostream>
#include <cmath>
#include <array>
#include <numbers>
#include <stdexcept>
#include <format>

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vector3D operator+(const Vector3D& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }

    constexpr Vector3D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    constexpr double dot(const Vector3D& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }

    constexpr Vector3D cross(const Vector3D& rhs) const noexcept {
        return {
            y * rhs.z - z * rhs.y,
            z * rhs.x - x * rhs.z,
            x * rhs.y - y * rhs.x
        };
    }

    double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
};

class ReciprocalLatticeCPP {
public:
    ReciprocalLatticeCPP(const Vector3D& a1, const Vector3D& a2, const Vector3D& a3)
        : m_a1(a1), m_a2(a2), m_a3(a3) {
        
        Vector3D cross23 = m_a2.cross(m_a3);
        m_v_cell = m_a1.dot(cross23);
        if (std::abs(m_v_cell) < 1e-12) {
            throw std::invalid_argument("Прямі базисні вектори компланарні (V_cell = 0)!");
        }

        const double factor = 2.0 * std::numbers::pi / m_v_cell;
        m_b1 = cross23 * factor;
        m_b2 = m_a3.cross(m_a1) * factor;
        m_b3 = m_a1.cross(m_a2) * factor;
    }

    [[nodiscard]] double unit_cell_volume() const noexcept {
        return m_v_cell;
    }

    [[nodiscard]] Vector3D get_g(int h, int k, int l) const noexcept {
        return m_b1 * h + m_b2 * k + m_b3 * l;
    }

    [[nodiscard]] double interplanar_spacing(int h, int k, int l) const {
        if (h == 0 && k == 0 && l == 0) {
            throw std::invalid_argument("Індекси Міллера не можуть бути одночасно нульовими!");
        }
        const Vector3D g = get_g(h, k, l);
        return 2.0 * std::numbers::pi / g.norm();
    }

    [[nodiscard]] bool is_inside_first_brillouin_zone(const Vector3D& k_vec, int max_index = 2) const noexcept {
        for (int h = -max_index; h <= max_index; ++h) {
            for (int k = -max_index; k <= max_index; ++k) {
                for (int l = -max_index; l <= max_index; ++l) {
                    if (h == 0 && k == 0 && l == 0) continue;
                    const Vector3D g = get_g(h, k, l);
                    const double g_sq = g.dot(g);
                    if (k_vec.dot(g) > 0.5 * g_sq + 1e-9) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    [[nodiscard]] const Vector3D& b1() const noexcept { return m_b1; }
    [[nodiscard]] const Vector3D& b2() const noexcept { return m_b2; }
    [[nodiscard]] const Vector3D& b3() const noexcept { return m_b3; }

private:
    Vector3D m_a1, m_a2, m_a3;
    Vector3D m_b1, m_b2, m_b3;
    double m_v_cell{0.0};
};

int main() {
    constexpr double a = 0.543; // нм
    const Vector3D a1{0.0, a / 2.0, a / 2.0};
    const Vector3D a2{a / 2.0, 0.0, a / 2.0};
    const Vector3D a3{a / 2.0, a / 2.0, 0.0};

    try {
        ReciprocalLatticeCPP lat(a1, a2, a3);
        std::cout << std::format("Об'єм V_cell (C++20): {:.5f} nm^3\n", lat.unit_cell_volume());
        std::cout << std::format("Міжплощинна відстань d(111): {:.5f} nm\n", lat.interplanar_spacing(1, 1, 1));
        std::cout << std::format("Міжплощинна відстань d(220): {:.5f} nm\n", lat.interplanar_spacing(2, 2, 0));

        const Vector3D k_gamma{0.0, 0.0, 0.0};
        const Vector3D k_outside = lat.b1() * 0.8;

        std::cout << std::format("Gamma у ЗБ: {}\n", lat.is_inside_first_brillouin_zone(k_gamma));
        std::cout << std::format("k_outside у ЗБ: {}\n", lat.is_inside_first_brillouin_zone(k_outside));
    } catch (const std::exception& ex) {
        std::cerr << "Помилка розрахунку: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
