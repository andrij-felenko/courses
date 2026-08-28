#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numeric>
#include <iomanip>

// Структура для опису стану електрона у двовимірній площині
struct Electron {
    double x{0.0};
    double y{0.0};
    double vx{0.0};
    double vy{0.0};
};

class DrudeSimulator {
private:
    std::size_t num_particles;
    double tau;          // Час релаксації (секунди)
    double E_x;          // Напруженість електричного поля (В/м)
    double dt;           // Крок інтегрування за часом (секунди)
    double mass;         // Маса електрона (кг)
    double charge;       // Заряд електрона (Кл)
    double v_thermal;    // Середня теплова швидкість (м/с)

    std::vector<Electron> particles;
    std::mt19937_64 rng;
    std::uniform_real_distribution<double> uniform_dist{0.0, 1.0};
    std::normal_distribution<double> gaussian_dist{0.0, 1.0};

public:
    DrudeSimulator(std::size_t n, double tau_s, double field_v_m, double dt_s, double v_th)
        : num_particles(n), tau(tau_s), E_x(field_v_m), dt(dt_s),
          mass(9.109e-31), charge(1.602e-19), v_thermal(v_th), particles(n)
    {
        std::random_device rd;
        rng.seed(rd());
        reset_velocities();
    }

    void reset_velocities() {
        double sigma = v_thermal / std::sqrt(2.0);
        for (auto& p : particles) {
            p.vx = gaussian_dist(rng) * sigma;
            p.vy = gaussian_dist(rng) * sigma;
        }
    }

    void step() {
        double p_scatter = 1.0 - std::exp(-dt / tau);
        double a_x = -charge * E_x / mass;
        double sigma = v_thermal / std::sqrt(2.0);

        for (auto& p : particles) {
            // 1. Прискорення полем
            p.vx += a_x * dt;

            // 2. Випадкове розсіювання на ґратці
            if (uniform_dist(rng) < p_scatter) {
                p.vx = gaussian_dist(rng) * sigma;
                p.vy = gaussian_dist(rng) * sigma;
            }

            // 3. Зсув координат
            p.x += p.vx * dt;
            p.y += p.vy * dt;
        }
    }

    double get_mean_drift_velocity_x() const {
        double sum_vx = 0.0;
        for (const auto& p : particles) {
            sum_vx += p.vx;
        }
        return sum_vx / static_cast<double>(num_particles);
    }

    double get_mean_squared_displacement() const {
        double sum_r2 = 0.0;
        for (const auto& p : particles) {
            sum_r2 += (p.x * p.x + p.y * p.y);
        }
        return sum_r2 / static_cast<double>(num_particles);
    }
};

int main() {
    const std::size_t N = 100'000;
    const double tau = 2.5e-14;      // 25 фс
    const double E_x = 1.0e4;        // 10 кВ/м
    const double dt = 1.0e-15;       // 1 фс
    const double v_th = 1.0e5;       // Теплова швидкість ~10^5 м/с

    DrudeSimulator sim(N, tau, E_x, dt, v_th);
    double theoretical_v_d = -(1.602e-19 * E_x * tau) / 9.109e-31;

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Теоретична дрейфова швидкість v_d: " << theoretical_v_d << " м/с\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Крок\tЧас (фс)\tСимульована v_d (м/с)\n";

    for (int step = 0; step <= 200; ++step) {
        if (step % 20 == 0) {
            double current_t = step * dt * 1.0e15;
            double sim_v_d = sim.get_mean_drift_velocity_x();
            std::cout << step << "\t" << current_t << " фс\t\t" << sim_v_d << " м/с\n";
        }
        sim.step();
    }

    return 0;
}
