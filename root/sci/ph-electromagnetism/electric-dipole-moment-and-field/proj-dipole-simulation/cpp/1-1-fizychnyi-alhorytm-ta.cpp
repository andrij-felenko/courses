#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <numbers>

// Структура для 3D вектора дійсної точності
struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr Vector3D operator+(const Vector3D& other) const noexcept {
        return {x + other.x, y + other.y, z + other.z};
    }

    constexpr Vector3D operator-(const Vector3D& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }

    constexpr Vector3D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    [[nodiscard]] double dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
};

// Фізичні константи в системі SI
constexpr double EPSILON_0 = 8.8541878128e-12; // Ф/м
constexpr double K_COULOMB = 1.0 / (4.0 * std::numbers::pi * EPSILON_0);

// Результат обчислення поля в точці
struct FieldPoint {
    Vector3D position;
    double potential{0.0};
    Vector3D electric_field;
};

// Обчислення дипольного потенціалу та поля у точці observation_point (r > 0)
FieldPoint calculate_dipole_field(const Vector3D& dipole_center,
                                 const Vector3D& dipole_moment,
                                 const Vector3D& observation_point) {
    const Vector3D r_vec = observation_point - dipole_center;
    const double r = r_vec.norm();

    if (r < 1e-12) {
        // Уникнення сингулярності в самому центрі диполя
        return {observation_point, 0.0, {0.0, 0.0, 0.0}};
    }

    const Vector3D r_hat = r_vec * (1.0 / r);
    const double p_dot_rhat = dipole_moment.dot(r_hat);

    // Потенціал Phi = (1 / 4pi eps0) * (p . rhat) / r^2
    const double potential = K_COULOMB * p_dot_rhat / (r * r);

    // Поле E = (1 / 4pi eps0) * (3 * (p . rhat) * rhat - p) / r^3
    const Vector3D field_vec = (r_hat * (3.0 * p_dot_rhat) - dipole_moment) * (K_COULOMB / (r * r * r));

    return {observation_point, potential, field_vec};
}

int main() {
    // Диполь з моментом p = 1.85 Debye (молекула води H2O) уздовж осі Z
    const double debye_unit = 3.33564e-30; // C*m
    const Vector3D dipole_center{0.0, 0.0, 0.0};
    const Vector3D dipole_moment{0.0, 0.0, 1.85 * debye_unit};

    std::cout << "--- Розрахунок поля диполя H2O (p = 1.85 D) ---\n";

    // Скануємо точки вздовж осі Z (θ = 0) та осі X (θ = 90 deg) на відстані 1 нм
    const double dist = 1e-9; // 1 нм
    const Vector3D point_z{0.0, 0.0, dist};
    const Vector3D point_x{dist, 0.0, 0.0};

    const auto res_z = calculate_dipole_field(dipole_center, dipole_moment, point_z);
    const auto res_x = calculate_dipole_field(dipole_center, dipole_moment, point_x);

    std::cout << "Точка на осі Z (1 нм): Phi = " << res_z.potential 
              << " В, |E| = " << res_z.electric_field.norm() << " В/м\n";
    std::cout << "Точка на осі X (1 нм): Phi = " << res_x.potential 
              << " В, |E| = " << res_x.electric_field.norm() << " В/м\n";
    std::cout << "Співвідношення полів E_z / E_x: " 
              << res_z.electric_field.norm() / res_x.electric_field.norm() 
              << " (теоретично має бути 2.0)\n";

    return 0;
}
