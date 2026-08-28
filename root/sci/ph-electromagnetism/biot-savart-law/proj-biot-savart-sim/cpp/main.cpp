#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

// Структура для роботи з тривимірними векторами в просторі
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
};

// Векторний добуток двох 3D-векторів
constexpr Vector3 cross(const Vector3& a, const Vector3& b) noexcept {
    return {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

// Довжина (модуль) вектора
constexpr double length(const Vector3& v) noexcept {
    return std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

// Обчислення вектора магнітної індукції B методом Біо-Савара
Vector3 compute_biot_savart(const std::vector<Vector3>& nodes, double current, const Vector3& point) {
    constexpr double mu0 = 4.0 * std::numbers::pi * 1e-7;
    const double factor = (mu0 * current) / (4.0 * std::numbers::pi);
    Vector3 B{0.0, 0.0, 0.0};

    for (size_t i = 0; i < nodes.size() - 1; ++i) {
        Vector3 dl = nodes[i + 1] - nodes[i];
        Vector3 r_mid = (nodes[i] + nodes[i + 1]) * 0.5;
        Vector3 R = point - r_mid;
        double dist = length(R);

        // Регуляризація для захисту від ділення на нуль
        if (dist < 1e-9) continue;

        double dist3 = dist * dist * dist;
        Vector3 dB = cross(dl, R) * (factor / dist3);
        B = B + dB;
    }
    return B;
}

int main() {
    // Параметри витка та струму
    constexpr double radius = 0.1;       // 10 см
    constexpr int segments = 2000;       // Кількість відрізків дискретизації
    constexpr double current = 10.0;      // 10 Ампер

    std::vector<Vector3> loop;
    loop.reserve(segments + 1);

    // Генерація вузлів колового контуру в площині XY
    for (int i = 0; i <= segments; ++i) {
        double phi = 2.0 * std::numbers::pi * i / segments;
        loop.push_back({radius * std::cos(phi), radius * std::sin(phi), 0.0});
    }

    // Точка спостереження на осі Z: (0, 0, 0.05 м)
    Vector3 point{0.0, 0.0, 0.05};
    Vector3 B = compute_biot_savart(loop, current, point);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "--- Результати чисельного розрахунку (C++) ---\n";
    std::cout << "B_x: " << B.x * 1e6 << " uT\n";
    std::cout << "B_y: " << B.y * 1e6 << " uT\n";
    std::cout << "B_z: " << B.z * 1e6 << " uT (Очікуване: ~44.9639 uT)\n";

    return 0;
}
