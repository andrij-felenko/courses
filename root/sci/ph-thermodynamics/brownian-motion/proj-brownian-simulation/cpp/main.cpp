#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numbers>
#include <stdexcept>

struct SimulationConfig {
    double temp{300.0};       // Температура, К
    double gamma{1e-8};       // Коефіцієнт тертя, кг/с
    double mass{1e-14};       // Маса частинки, кг
    double dt{1e-7};          // Крок за часом, с
    std::size_t steps{1000};  // Довжина траєкторії
    std::size_t trials{500};  // Кількість частинок в ансамблі
};

struct SimulationResult {
    std::vector<double> time;
    std::vector<double> msd;
    double estimated_diffusion_coeff{0.0};
    double theoretical_diffusion_coeff{0.0};
};

class BrownianSimulator {
public:
    explicit BrownianSimulator(SimulationConfig config)
        : config_(config), rd_(), gen_(rd_()) {}

    SimulationResult run() {
        if (config_.dt <= 0.0 || config_.steps == 0 || config_.trials == 0) {
            throw std::invalid_argument("Некоректні параметри симуляції");
        }

        constexpr double kB = 1.380649e-23;
        const double noise_scale = std::sqrt(2.0 * config_.gamma * kB * config_.temp * config_.dt) / config_.mass;
        const double damping = 1.0 - (config_.gamma / config_.mass) * config_.dt;
        const double v_thermal = std::sqrt(kB * config_.temp / config_.mass);

        SimulationResult res;
        res.time.resize(config_.steps);
        res.msd.assign(config_.steps, 0.0);
        res.theoretical_diffusion_coeff = (kB * config_.temp) / config_.gamma;

        for (std::size_t i = 0; i < config_.steps; ++i) {
            res.time[i] = static_cast<double>(i) * config_.dt;
        }

        std::normal_distribution<double> dist_norm(0.0, 1.0);

        for (std::size_t trial = 0; trial < config_.trials; ++trial) {
            double x = 0.0;
            double y = 0.0;
            double vx = dist_norm(gen_) * v_thermal;
            double vy = dist_norm(gen_) * v_thermal;

            res.msd[0] += (x * x + y * y);

            for (std::size_t step = 1; step < config_.steps; ++step) {
                vx = vx * damping + noise_scale * dist_norm(gen_);
                vy = vy * damping + noise_scale * dist_norm(gen_);

                x += vx * config_.dt;
                y += vy * config_.dt;

                res.msd[step] += (x * x + y * y);
            }
        }

        for (auto &val : res.msd) {
            val /= static_cast<double>(config_.trials);
        }

        const std::size_t last = config_.steps - 1;
        if (res.time[last] > 0.0) {
            // У 2D просторі: MSD = 4 * D * t
            res.estimated_diffusion_coeff = res.msd[last] / (4.0 * res.time[last]);
        }

        return res;
    }

private:
    SimulationConfig config_;
    std::random_device rd_;
    std::mt19937 gen_;
};

int main() {
    try {
        SimulationConfig cfg{
            .temp = 300.0,
            .gamma = 1e-8,
            .mass = 1e-14,
            .dt = 1e-7,
            .steps = 1000,
            .trials = 500
        };

        BrownianSimulator simulator(cfg);
        auto result = simulator.run();

        std::cout << "Теоретичний D = " << result.theoretical_diffusion_coeff << " м²/с\n";
        std::cout << "Оцінений D    = " << result.estimated_diffusion_coeff << " м²/с\n";
        std::cout << "MSD на фініші (t = " << result.time.back() << " с): " 
                  << result.msd.back() << " м²\n";
    } catch (const std::exception &e) {
        std::cerr << "Помилка симуляції: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
