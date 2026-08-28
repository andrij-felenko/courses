#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <numbers>
#include <span>

class EddyCurrentSimulator {
public:
    struct Params {
        double sigma = 5.8e7;       // Провідність (См/м)
        double mu_r = 1.0;          // Відносна проникність
        double thickness = 0.002;   // Товщина (м)
        double frequency = 1000.0;  // Частота (Гц)
        double B_0 = 0.1;           // Амплітуда поля (Тл)
        size_t spatial_nodes = 101;
    };

    explicit EddyCurrentSimulator(Params params)
        : p_(params),
          mu_(p_.mu_r * 4.0 * std::numbers::pi * 1e-7),
          dx_(p_.thickness / static_cast<double>(p_.spatial_nodes - 1)),
          D_m_(1.0 / (mu_ * p_.sigma)) 
    {
        B_.resize(p_.spatial_nodes, 0.0);
        j_y_.resize(p_.spatial_nodes, 0.0);
    }

    void run() {
        const double omega = 2.0 * std::numbers::pi * p_.frequency;
        const double dt = 0.45 * (dx_ * dx_) / D_m_;
        const double alpha = D_m_ * dt / (dx_ * dx_);

        const double period = 1.0 / p_.frequency;
        const double total_time = 5.0 * period;
        const auto num_steps = static_cast<size_t>(total_time / dt);

        std::vector<double> B_next(p_.spatial_nodes, 0.0);

        double t = 0.0;
        for (size_t step = 0; step < num_steps; ++step) {
            t += dt;
            const double B_ext = p_.B_0 * std::sin(omega * t);

            for (size_t i = 1; i < p_.spatial_nodes - 1; ++i) {
                B_next[i] = B_[i] + alpha * (B_[i + 1] - 2.0 * B_[i] + B_[i - 1]);
            }
            B_next[0] = B_ext;
            B_next[p_.spatial_nodes - 1] = B_ext;

            B_ = B_next;
        }

        // Обчислення струмів за допомогою різницевих похідних
        for (size_t i = 1; i < p_.spatial_nodes - 1; ++i) {
            j_y_[i] = -(1.0 / mu_) * (B_[i + 1] - B_[i - 1]) / (2.0 * dx_);
        }
        j_y_[0] = -(1.0 / mu_) * (B_[1] - B_[0]) / dx_;
        j_y_[p_.spatial_nodes - 1] = -(1.0 / mu_) * (B_[p_.spatial_nodes - 1] - B_[p_.spatial_nodes - 2]) / dx_;
    }

    [[nodiscard]] double calculate_average_power_density() const {
        double integrated_power = 0.0;
        for (size_t i = 0; i < p_.spatial_nodes; ++i) {
            const double p_local = (j_y_[i] * j_y_[i]) / p_.sigma;
            const double weight = (i == 0 || i == p_.spatial_nodes - 1) ? 0.5 : 1.0;
            integrated_power += p_local * weight * dx_;
        }
        return integrated_power / p_.thickness;
    }

    [[nodiscard]] double skin_depth() const {
        const double omega = 2.0 * std::numbers::pi * p_.frequency;
        return std::sqrt(2.0 / (omega * mu_ * p_.sigma));
    }

private:
    Params p_;
    double mu_;
    double dx_;
    double D_m_;
    std::vector<double> B_;
    std::vector<double> j_y_;
};

int main() {
    EddyCurrentSimulator::Params params{
        .sigma = 5.8e7,
        .mu_r = 1.0,
        .thickness = 0.002,
        .frequency = 1000.0,
        .B_0 = 0.1,
        .spatial_nodes = 101
    };

    EddyCurrentSimulator sim(params);
    std::cout << "Скін-шар δ: " << sim.skin_depth() * 1e3 << " мм\n";
    
    sim.run();
    
    const double P_sim = sim.calculate_average_power_density();
    std::cout << "Чисельні втрати P_e: " << P_sim * 1e-3 << " кВт/м³\n";

    return 0;
}
