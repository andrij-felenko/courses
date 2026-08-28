// electrostatic_energy.cpp — Обчислювальний модуль енергії поля на C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <expected>
#include <numbers>
#include <iomanip>

namespace electrodynamics {

// Фізичні константи
constexpr double epsilon_0 = 8.8541878128e-12; // Ф/м
constexpr double k_coulomb = 1.0 / (4.0 * std::numbers::pi * epsilon_0);
constexpr double min_distance_sq = 1e-24;     // м²

// Структура тривимірного вектора з операторами та методами відстані
struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr double distance_sq(const Vec3& other) const noexcept {
        const double dx = x - other.x;
        const double dy = y - other.y;
        const double dz = z - other.z;
        return dx * dx + dy * dy + dz * dz;
    }

    [[nodiscard]] double distance(const Vec3& other) const noexcept {
        return std::sqrt(distance_sq(other));
    }

    constexpr Vec3 operator+(const Vec3& other) const noexcept {
        return {x + other.x, y + other.y, z + other.z};
    }

    constexpr Vec3 operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
};

// Точковий заряд із позицією, швидкістю та масою
struct Charge {
    Vec3 pos;
    double q{0.0};   // Заряд у кулонах
    Vec3 vel;       // Швидкість у м/с
    double mass{1.0e-12}; // Маса у кг
};

// Типи помилок обчислення
enum class CalculationError {
    TooFewCharges,
    SingularityDetected
};

class SystemEnergySolver {
public:
    // Обчислення повної потенціальної енергії взаємодії пар
    [[nodiscard]] static std::expected<double, CalculationError> 
    compute_interaction_energy(std::span<const Charge> charges) noexcept {
        if (charges.size() < 2) {
            return std::unexpected(CalculationError::TooFewCharges);
        }

        double pairwise_sum = 0.0;
        const size_t n = charges.size();

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                const double r_sq = charges[i].pos.distance_sq(charges[j].pos);
                if (r_sq < min_distance_sq) {
                    return std::unexpected(CalculationError::SingularityDetected);
                }
                pairwise_sum += (charges[i].q * charges[j].q) / std::sqrt(r_sq);
            }
        }

        return k_coulomb * pairwise_sum;
    }

    // Обчислення скалярного потенціалу у довільній точці спостереження
    [[nodiscard]] static double 
    compute_potential_at(std::span<const Charge> charges, const Vec3& point) noexcept {
        double total_potential = 0.0;
        for (const auto& charge : charges) {
            const double r_sq = point.distance_sq(charge.pos);
            if (r_sq >= min_distance_sq) {
                total_potential += charge.q / std::sqrt(r_sq);
            }
        }
        return k_coulomb * total_potential;
    }

    // Обчислення вектора напруженості поля E у точці спостереження
    [[nodiscard]] static Vec3 
    compute_electric_field_at(std::span<const Charge> charges, const Vec3& point) noexcept {
        Vec3 field{0.0, 0.0, 0.0};
        for (const auto& charge : charges) {
            const double dx = point.x - charge.pos.x;
            const double dy = point.y - charge.pos.y;
            const double dz = point.z - charge.pos.z;
            const double r_sq = dx * dx + dy * dy + dz * dz;

            if (r_sq >= min_distance_sq) {
                const double r = std::sqrt(r_sq);
                const double factor = k_coulomb * charge.q / (r_sq * r);
                field.x += factor * dx;
                field.y += factor * dy;
                field.z += factor * dz;
            }
        }
        return field;
    }

    // Інтегрування енергії поля на 3D сітці
    [[nodiscard]] static double 
    integrate_field_energy(std::span<const Charge> charges, 
                           const Vec3& min_bounds, const Vec3& max_bounds, 
                           int grid_steps) noexcept {
        const double dx = (max_bounds.x - min_bounds.x) / grid_steps;
        const double dy = (max_bounds.y - min_bounds.y) / grid_steps;
        const double dz = (max_bounds.z - min_bounds.z) / grid_steps;
        const double dV = dx * dy * dz;

        double integrated_energy = 0.0;

        for (int ix = 0; ix < grid_steps; ++ix) {
            const double x = min_bounds.x + (ix + 0.5) * dx;
            for (int iy = 0; iy < grid_steps; ++iy) {
                const double y = min_bounds.y + (iy + 0.5) * dy;
                for (int iz = 0; iz < grid_steps; ++iz) {
                    const double z = min_bounds.z + (iz + 0.5) * dz;
                    const Vec3 sample_point{x, y, z};

                    const Vec3 E = compute_electric_field_at(charges, sample_point);
                    const double E_sq = E.x * E.x + E.y * E.y + E.z * E.z;
                    const double w = 0.5 * epsilon_0 * E_sq;

                    integrated_energy += w * dV;
                }
            }
        }

        return integrated_energy;
    }
};

} // namespace electrodynamics

int main() {
    using namespace electrodynamics;

    // Конфігурація з 4 зарядів квадруполя
    const std::vector<Charge> system{
        {{{0.00, 0.00, 0.0}},  1.0e-9},
        {{{0.01, 0.00, 0.0}}, -1.0e-9},
        {{{0.01, 0.01, 0.0}},  1.0e-9},
        {{{0.00, 0.01, 0.0}}, -1.0e-9}
    };

    auto energy_result = SystemEnergySolver::compute_interaction_energy(system);

    std::cout << "=== Обчислення на C++20 ===\n";
    if (energy_result) {
        std::cout << "Потенціальна енергія взаємодії: " 
                  << std::scientific << std::setprecision(6) 
                  << *energy_result << " Дж\n";
        
        const Vec3 center_point{0.005, 0.005, 0.0};
        const double phi = SystemEnergySolver::compute_potential_at(system, center_point);
        std::cout << "Скалярний потенціал у центрі: " 
                  << std::fixed << std::setprecision(6) 
                  << phi << " В\n";

        const Vec3 min_b{-0.02, -0.02, -0.02};
        const Vec3 max_b{ 0.03,  0.03,  0.03};
        const double grid_energy = SystemEnergySolver::integrate_field_energy(system, min_b, max_b, 30);
        std::cout << "3D Інтегрована енергія поля: " 
                  << std::scientific << std::setprecision(6) 
                  << grid_energy << " Дж\n";
    } else {
        std::cout << "Не вдалося обчислити енергію системи через помилку!\n";
    }

    return 0;
}
