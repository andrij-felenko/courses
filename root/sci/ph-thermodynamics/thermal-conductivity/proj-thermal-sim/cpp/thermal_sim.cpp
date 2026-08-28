// thermal_sim.cpp — Симуляція 1D теплопровідності методом FTCS мовою C++
#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <stdexcept>
#include <span>

struct Material {
    double lambda; // Вт/(м·К)
    double rho;    // кг/м³
    double cp;     // Дж/(кг·К)

    [[nodiscard]] constexpr double alpha() const noexcept {
        return lambda / (rho * cp);
    }
};

class ThermalSimulator1D {
private:
    double length_;
    size_t nodes_;
    double dx_;
    std::vector<double> T_;
    std::vector<double> alpha_grid_;

public:
    ThermalSimulator1D(double length, size_t nodes, const Material& mat_left, const Material& mat_right)
        : length_(length), nodes_(nodes), dx_(length / (nodes - 1)), T_(nodes, 20.0), alpha_grid_(nodes) {
        if (nodes < 3) {
            throw std::invalid_argument("Кількість вузлів сітки має бути не менше 3");
        }
        
        size_t mid = nodes / 2;
        for (size_t i = 0; i < nodes; ++i) {
            alpha_grid_[i] = (i < mid) ? mat_left.alpha() : mat_right.alpha();
        }
    }

    void set_boundary_conditions(double t_left, double t_right) noexcept {
        T_.front() = t_left;
        T_.back() = t_right;
    }

    void run(double total_time) {
        double max_alpha = *std::max_element(alpha_grid_.begin(), alpha_grid_.end());
        double dt = 0.45 * (dx_ * dx_) / max_alpha; // Захисний запас стійкості CFL
        size_t steps = static_cast<size_t>(total_time / dt);

        std::vector<double> T_next = T_;

        for (size_t step = 0; step < steps; ++step) {
            T_next.front() = T_.front();
            T_next.back() = T_.back();

            for (size_t i = 1; i < nodes_ - 1; ++i) {
                double fo = alpha_grid_[i] * dt / (dx_ * dx_);
                T_next[i] = T_[i] + fo * (T_[i + 1] - 2.0 * T_[i] + T_[i - 1]);
            }
            T_ = T_next;
        }
    }

    [[nodiscard]] std::span<const double> temperature_profile() const noexcept {
        return T_;
    }
};

int main() {
    try {
        constexpr Material copper{390.0, 8960.0, 385.0};
        constexpr Material steel{15.0, 7900.0, 500.0};

        constexpr double bar_length = 0.10;
        constexpr size_t grid_nodes = 100;
        constexpr double simulation_time = 5.0;

        ThermalSimulator1D sim(bar_length, grid_nodes, copper, steel);
        sim.set_boundary_conditions(100.0, 20.0);
        sim.run(simulation_time);

        auto profile = sim.temperature_profile();

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Профіль температури (C++) через " << simulation_time << " с ===\n";
        std::cout << "x = 0.00 м (Вхід Cu):     " << profile[0] << " °C\n";
        std::cout << "x = 0.025 м (Середина Cu):   " << profile[grid_nodes / 4] << " °C\n";
        std::cout << "x = 0.050 м (Стик Cu-Steel): " << profile[grid_nodes / 2] << " °C\n";
        std::cout << "x = 0.075 м (Середина Steel): " << profile[3 * grid_nodes / 4] << " °C\n";
        std::cout << "x = 0.100 м (Вихід Steel):   " << profile.back() << " °C\n";

    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
