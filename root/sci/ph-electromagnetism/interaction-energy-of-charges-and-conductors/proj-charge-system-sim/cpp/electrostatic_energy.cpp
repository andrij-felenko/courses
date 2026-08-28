// electrostatic_energy.cpp — Ідіоматичний сучасний C++20 варіант
// Компіляція: g++ -O3 -std=c++20 electrostatic_energy.cpp -o electrostatic_energy

#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <expected>
#include <random>
#include <chrono>

namespace electrodynamics {

constexpr double kVacuumEps0 = 8.8541878128e-12;
constexpr double kCoulombK   = 1.0 / (4.0 * std::numbers::pi * kVacuumEps0);

struct Charge3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};
    double q{0.0};
};

enum class ComputeError {
    InvalidSize,
    InvalidSoftening
};

// Обчислення потенціальної енергії системи із використанням std::span та std::expected
[[nodiscard]] std::expected<double, ComputeError>
calculateInteractionEnergy(std::span<const Charge3D> charges, double r_soft = 1e-9) noexcept {
    if (charges.size() < 2) {
        return std::unexpected(ComputeError::InvalidSize);
    }
    if (r_soft < 0.0) {
        return std::unexpected(ComputeError::InvalidSoftening);
    }

    double total_energy = 0.0;
    const double r_soft_sq = r_soft * r_soft;
    const size_t n = charges.size();

    for (size_t i = 0; i < n; ++i) {
        const auto& p1 = charges[i];
        for (size_t j = i + 1; j < n; ++j) {
            const auto& p2 = charges[j];
            const double dx = p1.x - p2.x;
            const double dy = p1.y - p2.y;
            const double dz = p1.z - p2.z;

            const double dist_sq = dx * dx + dy * dy + dz * dz + r_soft_sq;
            total_energy += (p1.q * p2.q) / std::sqrt(dist_sq);
        }
    }

    return kCoulombK * total_energy;
}

// Генерація випадкових зарядів за допомогою <random>
std::vector<Charge3D> generateRandomSystem(size_t n) {
    std::mt19937 rng(12345);
    std::uniform_real_distribution<double> dist_pos(0.0, 1.0);

    std::vector<Charge3D> system;
    system.reserve(n);

    for (size_t i = 0; i < n; ++i) {
        system.push_back({
            .x = dist_pos(rng),
            .y = dist_pos(rng),
            .z = dist_pos(rng),
            .q = (i % 2 == 0) ? 1e-6 : -1e-6
        });
    }

    return system;
}

} // namespace electrodynamics

int main() {
    using namespace electrodynamics;

    constexpr size_t n_charges = 1000;
    const auto system = generateRandomSystem(n_charges);

    const auto start = std::chrono::high_resolution_clock::now();
    const auto result = calculateInteractionEnergy(system);
    const auto end = std::chrono::high_resolution_clock::now();

    const std::chrono::duration<double, std::milli> elapsed = end - start;

    if (result.has_value()) {
        std::cout << "Розмір системи: N = " << n_charges << " зарядів\n";
        std::cout << "Повна енергія системи (C++20): W = " << *result << " Дж\n";
        std::cout << "Час обчислення (C++20): " << elapsed.count() << " мс\n";
    } else {
        std::cerr << "Помилка під час обчислення енергії!\n";
    }

    return 0;
}
