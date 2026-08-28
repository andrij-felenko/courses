#include <iostream>
#include <vector>
#include <span>
#include <iomanip>
#include <stdexcept>
#include <string>

struct ThermalConfig {
    double length{0.5};         // Довжина стрижня [м]
    std::size_t num_points{51}; // Кількість вузлів сітки
    double alpha{9.7e-5};       // Температуропровідність [м²/с]
    double t_left{100.0};       // Гранична температура зліва [°C]
    double t_right{20.0};       // Гранична температура справа [°C]
    double t_initial{20.0};     // Початкова температура [°C]
};

class HeatSolver1D {
public:
    explicit HeatSolver1D(ThermalConfig config)
        : config_(config), dx_(config.length / static_cast<double>(config.num_points - 1))
    {
        if (config_.num_points < 3 || config_.length <= 0.0) {
            throw std::invalid_argument("Некоректна геометрія чисельної сітки.");
        }
        grid_.resize(config_.num_points, config_.t_initial);
        grid_.front() = config_.t_left;
        grid_.back() = config_.t_right;
    }

    void step(double dt) {
        const double r = config_.alpha * dt / (dx_ * dx_);
        if (r > 0.5) {
            throw std::runtime_error("Порушення умови стійкості CFL: r = " + std::to_string(r));
        }

        std::vector<double> next_grid = grid_;
        for (std::size_t i = 1; i < grid_.size() - 1; ++i) {
            next_grid[i] = grid_[i] + r * (grid_[i + 1] - 2.0 * grid_[i] + grid_[i - 1]);
        }
        grid_ = std::move(next_grid);
    }

    void simulate(double total_time, double dt) {
        const std::size_t steps = static_cast<std::size_t>(total_time / dt);
        for (std::size_t n = 0; n < steps; ++n) {
            step(dt);
        }
    }

    [[nodiscard]] std::span<const double> grid() const noexcept {
        return grid_;
    }

    [[nodiscard]] double dx() const noexcept {
        return dx_;
    }

private:
    ThermalConfig config_;
    double dx_;
    std::vector<double> grid_;
};

int main() {
    try {
        ThermalConfig cfg{
            .length = 0.5,
            .num_points = 51,
            .alpha = 9.7e-5,
            .t_left = 100.0,
            .t_right = 20.0,
            .t_initial = 20.0
        };

        const double dt = 0.0005;
        const double total_time = 10.0;

        HeatSolver1D solver(cfg);
        solver.simulate(total_time, dt);

        std::cout << "=== Профіль температури (t = " << total_time << " с) ===\n";
        const auto result = solver.grid();
        const double dx = solver.dx();

        for (std::size_t i = 0; i < result.size(); i += result.size() / 5) {
            std::cout << "x = " << std::fixed << std::setprecision(3) << i * dx
                      << " м : T = " << std::setprecision(2) << result[i] << " °C\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка розв'язувача: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
