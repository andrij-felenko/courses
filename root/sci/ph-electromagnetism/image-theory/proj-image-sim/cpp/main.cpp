#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <numbers>
#include <iomanip>
#include <stdexcept>

// Фізична стала: 1 / (4 * pi * epsilon_0) [Н·м²/Кл²]
constexpr double K_COULOMB = 8.9875517923e9;

// Структура для 3D-вектора
struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] double length_sq() const noexcept {
        return x * x + y * y + z * z;
    }

    [[nodiscard]] double length() const noexcept {
        return std::sqrt(length_sq());
    }

    Vector3D operator-(const Vector3D& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }

    Vector3D operator+(const Vector3D& other) const noexcept {
        return {x + other.x, y + other.y, z + other.z};
    }

    Vector3D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
};

// Точковий заряд (реальний або дзеркальний)
struct PointCharge {
    Vector3D pos;
    double charge{0.0};
    bool is_image{false};
};

// Клас розв'язувача електростатичних полів методом дзеркальних зображень
class ElectrostaticImageSolver {
public:
    enum class GeometryType { Plane, Sphere, CornerReflector90 };

    ElectrostaticImageSolver() = default;

    void add_real_charge(const Vector3D& position, double charge) {
        m_real_charges.push_back({position, charge, false});
    }

    void setup_plane_boundary(double plane_z = 0.0) {
        m_geometry = GeometryType::Plane;
        m_plane_z = plane_z;
        rebuild_image_charges();
    }

    void setup_sphere_boundary(const Vector3D& center, double radius) {
        if (radius <= 0.0) {
            throw std::invalid_argument("Радіус сфери має бути додатним");
        }
        m_geometry = GeometryType::Sphere;
        m_sphere_center = center;
        m_sphere_radius = radius;
        rebuild_image_charges();
    }

    void setup_corner_90_boundary() {
        m_geometry = GeometryType::CornerReflector90;
        rebuild_image_charges();
    }

    // Обчислення потенціалу V у довільній точці P
    [[nodiscard]] double evaluate_potential(const Vector3D& p) const noexcept {
        double v_total = 0.0;

        auto add_contribution = [&](const PointCharge& q) {
            Vector3D r_vec = p - q.pos;
            double dist = r_vec.length();
            if (dist > 1e-12) {
                v_total += K_COULOMB * q.charge / dist;
            }
        };

        for (const auto& q : m_real_charges) add_contribution(q);
        for (const auto& q : m_image_charges) add_contribution(q);

        return v_total;
    }

    // Обчислення вектора напруженості E у довільній точці P
    [[nodiscard]] Vector3D evaluate_field(const Vector3D& p) const noexcept {
        Vector3D e_total{0.0, 0.0, 0.0};

        auto add_contribution = [&](const PointCharge& q) {
            Vector3D r_vec = p - q.pos;
            double dist_sq = r_vec.length_sq();
            double dist = std::sqrt(dist_sq);
            if (dist > 1e-12) {
                double factor = K_COULOMB * q.charge / (dist_sq * dist);
                e_total = e_total + r_vec * factor;
            }
        };

        for (const auto& q : m_real_charges) add_contribution(q);
        for (const auto& q : m_image_charges) add_contribution(q);

        return e_total;
    }

    // Обчислення результуючої кулонівської сили, що діє на реальний заряд з індексом idx
    [[nodiscard]] Vector3D calculate_force_on_charge(size_t idx) const {
        if (idx >= m_real_charges.size()) {
            throw std::out_of_range("Некоректний індекс реального заряду");
        }

        const auto& target = m_real_charges[idx];
        Vector3D e_other{0.0, 0.0, 0.0};

        // Внесок інших реальних зарядів
        for (size_t i = 0; i < m_real_charges.size(); ++i) {
            if (i == idx) continue;
            Vector3D r_vec = target.pos - m_real_charges[i].pos;
            double dist_sq = r_vec.length_sq();
            double dist = std::sqrt(dist_sq);
            if (dist > 1e-12) {
                double factor = K_COULOMB * m_real_charges[i].charge / (dist_sq * dist);
                e_other = e_other + r_vec * factor;
            }
        }

        // Внесок усіх дзеркальних зарядів
        for (const auto& img : m_image_charges) {
            Vector3D r_vec = target.pos - img.pos;
            double dist_sq = r_vec.length_sq();
            double dist = std::sqrt(dist_sq);
            if (dist > 1e-12) {
                double factor = K_COULOMB * img.charge / (dist_sq * dist);
                e_other = e_other + r_vec * factor;
            }
        }

        return e_other * target.charge;
    }

    [[nodiscard]] const std::vector<PointCharge>& get_image_charges() const noexcept {
        return m_image_charges;
    }

private:
    void rebuild_image_charges() {
        m_image_charges.clear();

        for (const auto& real_q : m_real_charges) {
            switch (m_geometry) {
            case GeometryType::Plane: {
                // Дзеркальне відбиття відносно z = m_plane_z
                double z_img = 2.0 * m_plane_z - real_q.pos.z;
                m_image_charges.push_back({
                    {real_q.pos.x, real_q.pos.y, z_img},
                    -real_q.charge,
                    true
                });
                break;
            }
            case GeometryType::Sphere: {
                // Сферична інверсія відносно m_sphere_center
                Vector3D rel_pos = real_q.pos - m_sphere_center;
                double d = rel_pos.length();
                if (d <= m_sphere_radius) {
                    throw std::logic_error("Заряд знаходиться всередині сфери!");
                }
                double d_img = (m_sphere_radius * m_sphere_radius) / d;
                Vector3D img_pos = m_sphere_center + rel_pos * (d_img / d);
                double img_charge = -real_q.charge * (m_sphere_radius / d);

                m_image_charges.push_back({img_pos, img_charge, true});
                break;
            }
            case GeometryType::CornerReflector90: {
                // Три дзеркальні зображення для 90-градусного кута
                m_image_charges.push_back({{-real_q.pos.x, real_q.pos.y, real_q.pos.z}, -real_q.charge, true});
                m_image_charges.push_back({{real_q.pos.x, -real_q.pos.y, real_q.pos.z}, -real_q.charge, true});
                m_image_charges.push_back({{-real_q.pos.x, -real_q.pos.y, real_q.pos.z}, real_q.charge, true});
                break;
            }
            }
        }
    }

    GeometryType m_geometry{GeometryType::Plane};
    std::vector<PointCharge> m_real_charges;
    std::vector<PointCharge> m_image_charges;

    double m_plane_z{0.0};
    Vector3D m_sphere_center{0.0, 0.0, 0.0};
    double m_sphere_radius{1.0};
};

int main() {
    std::cout << "=== Моделювання поля методом дзеркальних зображень (C++) ===\n\n";

    ElectrostaticImageSolver solver;
    // Розмістимо заряд +2 мкКл на висоті z = 0.05 м (5 см)
    solver.add_real_charge({0.0, 0.0, 0.05}, 2.0e-6);
    solver.setup_plane_boundary(0.0);

    Vector3D test_point{0.0, 0.0, 0.02}; // Точка 2 см над площиною
    double v_pot = solver.evaluate_potential(test_point);
    Vector3D e_field = solver.evaluate_field(test_point);
    Vector3D force = solver.calculate_force_on_charge(0);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Потенціал у точці (0, 0, 0.02 м): " << v_pot / 1000.0 << " кВ\n";
    std::cout << "Напруженість E_z: " << e_field.z / 1000.0 << " кВ/м\n";
    std::cout << "Сила притягання до площини: " << force.z << " Н\n";

    return 0;
}
