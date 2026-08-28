// Симулятор релаксації швидкостей молекул (C++17)
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <algorithm>
#include <memory>

struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
    [[nodiscard]] double norm_sq() const noexcept {
        return x * x + y * y + z * z;
    }
};

class GasSimulation {
public:
    GasSimulation(std::size_t count, double target_temp, double mass)
        : num_particles_(count),
          temp_(target_temp),
          mass_(mass),
          rng_(std::random_device{}()) {
        particles_.resize(num_particles_);
        initialize_monoenergetic();
    }

    void run_collisions(std::size_t num_collisions) {
        std::uniform_int_distribution<std::size_t> dist_particle(0, num_particles_ - 1);
        std::uniform_real_distribution<double> dist_cos(-1.0, 1.0);
        std::uniform_real_distribution<double> dist_phi(0.0, 2.0 * M_PI);

        for (std::size_t step = 0; step < num_collisions; ++step) {
            std::size_t i = dist_particle(rng_);
            std::size_t j = dist_particle(rng_);
            if (i == j) continue;

            // Швидкість центру мас
            Vector3D v_cm{
                0.5 * (particles_[i].x + particles_[j].x),
                0.5 * (particles_[i].y + particles_[j].y),
                0.5 * (particles_[i].z + particles_[j].z)
            };

            // Відносна швидкість
            Vector3D v_rel{
                particles_[i].x - particles_[j].x,
                particles_[i].y - particles_[j].y,
                particles_[i].z - particles_[j].z
            };
            double v_rel_mag = v_rel.norm();

            // Випадковий розсіювальний напрямок
            double cos_theta = dist_cos(rng_);
            double sin_theta = std::sqrt(std::max(0.0, 1.0 - cos_theta * cos_theta));
            double phi = dist_phi(rng_);

            Vector3D new_v_rel{
                v_rel_mag * sin_theta * std::cos(phi),
                v_rel_mag * sin_theta * std::sin(phi),
                v_rel_mag * cos_theta
            };

            // Перерахунок швидкостей
            particles_[i] = Vector3D{
                v_cm.x + 0.5 * new_v_rel.x,
                v_cm.y + 0.5 * new_v_rel.y,
                v_cm.z + 0.5 * new_v_rel.z
            };
            particles_[j] = Vector3D{
                v_cm.x - 0.5 * new_v_rel.x,
                v_cm.y - 0.5 * new_v_rel.y,
                v_cm.z - 0.5 * new_v_rel.z
            };
        }
    }

    void print_statistics() const {
        double sum_v = 0.0;
        double sum_v2 = 0.0;

        for (const auto& p : particles_) {
            double v = p.norm();
            sum_v += v;
            sum_v2 += v * v;
        }

        double v_avg_sim = sum_v / num_particles_;
        double v_rms_sim = std::sqrt(sum_v2 / num_particles_);

        constexpr double kB = 1.380649e-23;
        double v_p_theory = std::sqrt(2.0 * kB * temp_ / mass_);
        double v_avg_theory = std::sqrt(8.0 * kB * temp_ / (M_PI * mass_));
        double v_rms_theory = std::sqrt(3.0 * kB * temp_ / mass_);

        std::cout << std::fixed << std::setprecision(1);
        std::cout << "=== Статистика моделювання (C++17) ===\n";
        std::cout << "v_сер (модель): " << std::setw(6) << v_avg_sim << " м/с | v_сер (теорія): " << v_avg_theory << " м/с\n";
        std::cout << "v_кв  (модель): " << std::setw(6) << v_rms_sim << " м/с | v_кв  (теорія): " << v_rms_theory << " м/с\n";
        std::cout << "v_p   (теорія): " << std::setw(6) << v_p_theory << " м/с\n";
    }

private:
    void initialize_monoenergetic() {
        constexpr double kB = 1.380649e-23;
        double v0 = std::sqrt(3.0 * kB * temp_ / mass_);

        std::uniform_real_distribution<double> dist_cos(-1.0, 1.0);
        std::uniform_real_distribution<double> dist_phi(0.0, 2.0 * M_PI);

        for (auto& p : particles_) {
            double cos_t = dist_cos(rng_);
            double sin_t = std::sqrt(std::max(0.0, 1.0 - cos_t * cos_t));
            double phi = dist_phi(rng_);

            p.x = v0 * sin_t * std::cos(phi);
            p.y = v0 * sin_t * std::sin(phi);
            p.z = v0 * cos_t;
        }
    }

    std::size_t num_particles_;
    double temp_;
    double mass_;
    std::vector<Vector3D> particles_;
    mutable std::mt19937 rng_;
};

int main() {
    constexpr std::size_t N = 100'000;
    constexpr std::size_t COLLISIONS = 2'000'000;
    constexpr double MASS_N2 = 4.65e-26; // кг
    constexpr double TEMP = 300.0;       // К

    GasSimulation sim(N, TEMP, MASS_N2);
    sim.run_collisions(COLLISIONS);
    sim.print_statistics();

    return 0;
}
