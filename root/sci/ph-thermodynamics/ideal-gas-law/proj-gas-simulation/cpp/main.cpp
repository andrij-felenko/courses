#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <memory>
#include <iomanip>

struct Particle {
    double x{0.0}, y{0.0};
    double vx{0.0}, vy{0.0};
};

class GasSimulator {
public:
    GasSimulator(size_t num_particles, double lx, double ly, double mass, double temp)
        : lx_(lx), ly_(ly), mass_(mass), kb_(1.380649e-23), particles_(num_particles) {
        init_particles(temp);
    }

    double step(double dt) {
        double impulse = 0.0;
        for (auto& p : particles_) {
            p.x += p.vx * dt;
            p.y += p.vy * dt;

            if (p.x <= 0.0) {
                p.x = -p.x;
                impulse += 2.0 * mass_ * std::abs(p.vx);
                p.vx = -p.vx;
            } else if (p.x >= lx_) {
                p.x = 2.0 * lx_ - p.x;
                impulse += 2.0 * mass_ * std::abs(p.vx);
                p.vx = -p.vx;
            }

            if (p.y <= 0.0) {
                p.y = -p.y;
                impulse += 2.0 * mass_ * std::abs(p.vy);
                p.vy = -p.vy;
            } else if (p.y >= ly_) {
                p.y = 2.0 * ly_ - p.y;
                impulse += 2.0 * mass_ * std::abs(p.vy);
                p.vy = -p.vy;
            }
        }
        return impulse;
    }

    double calculate_temperature() const {
        double sum_v_sq = 0.0;
        for (const auto& p : particles_) {
            sum_v_sq += p.vx * p.vx + p.vy * p.vy;
        }
        double mean_v_sq = sum_v_sq / static_cast<double>(particles_.size());
        return (mass_ * mean_v_sq) / (2.0 * kb_);
    }

    double area() const { return lx_ * ly_; }
    double perimeter() const { return 2.0 * (lx_ + ly_); }
    size_t num_particles() const { return particles_.size(); }
    double kb() const { return kb_; }

private:
    void init_particles(double temp) {
        std::mt19937 gen(1337);
        std::uniform_real_distribution<double> dist_x(0.1, lx_ - 0.1);
        std::uniform_real_distribution<double> dist_y(0.1, ly_ - 0.1);
        std::uniform_real_distribution<double> dist_angle(0.0, 2.0 * M_PI);

        double v_rms = std::sqrt(2.0 * kb_ * temp / mass_);

        for (auto& p : particles_) {
            p.x = dist_x(gen);
            p.y = dist_y(gen);
            double angle = dist_angle(gen);
            p.vx = v_rms * std::cos(angle);
            p.vy = v_rms * std::sin(angle);
        }
    }

    double lx_, ly_;
    double mass_;
    double kb_;
    std::vector<Particle> particles_;
};

int main() {
    const size_t n_particles = 1000;
    const double lx = 10.0, ly = 10.0;
    const double mass = 4.0e-26; // Атом гелію
    const double target_temp = 300.0;
    const double dt = 1.0e-5;
    const int total_steps = 100000;

    GasSimulator sim(n_particles, lx, ly, mass, target_temp);

    double accum_impulse = 0.0;
    for (int step = 0; step < total_steps; ++step) {
        accum_impulse += sim.step(dt);
    }

    double t_sim = sim.calculate_temperature();
    double total_time = total_steps * dt;
    double p_sim = accum_impulse / (sim.perimeter() * total_time);
    double z_factor = (p_sim * sim.area()) / (sim.num_particles() * sim.kb() * t_sim);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Симуляція ідеального газу (C++ RAII) ===\n";
    std::cout << "N частинок   : " << sim.num_particles() << "\n";
    std::cout << "Температура  : " << t_sim << " K\n";
    std::cout << "Тиск P       : " << std::scientific << p_sim << " Па·м\n";
    std::cout << std::fixed << "Z = PV/(NkT) : " << z_factor << " (Очікуване: 1.0000)\n";

    return 0;
}
