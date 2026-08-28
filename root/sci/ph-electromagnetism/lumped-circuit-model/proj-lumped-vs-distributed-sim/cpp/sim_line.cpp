// sim_line.cpp — Симуляція зосередженої та розподіленої лінії мовою C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <stdexcept>

class LumpedTransmissionLine {
private:
    std::size_t num_cells_;
    double l_total_;
    double c_total_;
    double r_load_;
    std::vector<double> v_nodes_;
    std::vector<double> i_branches_;

public:
    LumpedTransmissionLine(std::size_t num_cells, double l_total, double c_total, double r_load)
        : num_cells_(num_cells), l_total_(l_total), c_total_(c_total), r_load_(r_load),
          v_nodes_(num_cells + 1, 0.0), i_branches_(num_cells, 0.0) {
        if (num_cells == 0) {
            throw std::invalid_argument("Кількість осередків повинна бути більше 0");
        }
    }

    void step(double v_in, double dt) {
        const double l_cell = l_total_ / static_cast<double>(num_cells_);
        const double c_cell = c_total_ / static_cast<double>(num_cells_);

        v_nodes_[0] = v_in;

        // Оновлення струмів індуктивностей
        for (std::size_t k = 0; k < num_cells_ - 1; ++k) {
            const double v_diff = v_nodes_[k] - v_nodes_[k + 1];
            i_branches_[k] += (v_diff / l_cell) * dt;
        }

        const double v_last = v_nodes_[num_cells_ - 1];
        const double v_out = v_nodes_[num_cells_];
        i_branches_[num_cells_ - 1] += ((v_last - v_out) / l_cell) * dt;

        // Оновлення напруг ємностей
        for (std::size_t k = 1; k < num_cells_; ++k) {
            const double i_diff = i_branches_[k - 1] - i_branches_[k];
            v_nodes_[k] += (i_diff / c_cell) * dt;
        }

        const double i_load = v_out / r_load_;
        v_nodes_[num_cells_] += ((i_branches_[num_cells_ - 1] - i_load) / c_cell) * dt;
    }

    [[nodiscard]] double output_voltage() const noexcept {
        return v_nodes_[num_cells_];
    }
};

int main() {
    constexpr double l_total = 100e-9; // 100 нГн
    constexpr double c_total = 40e-12;  // 40 пФ
    constexpr double z0 = std::sqrt(l_total / c_total); // 50 Ом
    constexpr double r_load = 50.0;     // Узгоджене навантаження
    constexpr double t_prop = std::sqrt(l_total * c_total); // ≈ 2.0 нс

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++20 Моделювання зосередженої LC-апроксимації ===\n";
    std::cout << "Імпеданс Z0 = " << z0 << " Ом | Ідеальна затримка = " << t_prop * 1e9 << " нс\n\n";

    const std::vector<std::size_t> cell_counts = {1, 2, 4, 8, 16, 64};
    constexpr double dt = 1e-12; // 1 пс
    constexpr double t_sim = 6e-9;

    for (const auto cells : cell_counts) {
        LumpedTransmissionLine line(cells, l_total, c_total, r_load);
        double t_50percent = -1.0;

        for (double t = 0.0; t <= t_sim; t += dt) {
            const double v_in = (t < 0.2e-9) ? (t / 0.2e-9) : 1.0;
            line.step(v_in, dt);

            if (line.output_voltage() >= 0.5 && t_50percent < 0.0) {
                t_50percent = t;
            }
        }

        std::cout << "Комірок N = " << std::setw(2) << cells 
                  << " | Затримка фронту: " << t_50percent * 1e9 << " нс\n";
    }

    return 0;
}
