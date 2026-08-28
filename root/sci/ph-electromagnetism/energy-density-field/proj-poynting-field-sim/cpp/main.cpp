#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

class FdtdSim1D {
public:
    static constexpr double eps0 = 8.8541878128e-12;
    static constexpr double mu0  = 1.2566370614e-6;
    static constexpr double c0   = 299792458.0;

    explicit FdtdSim1D(std::size_t num_cells, double dz, double courant_factor = 0.5)
        : nz_(num_cells), dz_(dz), dt_(courant_factor * dz / c0),
          e_(num_cells, 0.0), h_(num_cells, 0.0),
          w_e_(num_cells, 0.0), w_m_(num_cells, 0.0), s_(num_cells, 0.0) {}

    void step(std::size_t time_step) {
        const double ch = dt_ / (mu0 * dz_);
        const double ce = dt_ / (eps0 * dz_);

        // 1. Оновлення магнітного поля H
        for (std::size_t i = 0; i < nz_ - 1; ++i) {
            h_[i] -= ch * (e_[i + 1] - e_[i]);
        }

        // 2. Оновлення електричного поля E
        for (std::size_t i = 1; i < nz_; ++i) {
            e_[i] -= ce * (h_[i] - h_[i - 1]);
        }

        // 3. Гаусів імпульс джерела
        constexpr double t0 = 40.0;
        constexpr double spread = 12.0;
        const double pulse = std::exp(-0.5 * std::pow((static_cast<double>(time_step) - t0) / spread, 2.0));
        e_[nz_ / 2] += pulse;

        // 4. Обчислення енергетичних характеристик
        for (std::size_t i = 1; i < nz_ - 1; ++i) {
            const double h_avg = 0.5 * (h_[i] + h_[i - 1]);
            w_e_[i] = 0.5 * eps0 * e_[i] * e_[i];
            w_m_[i] = 0.5 * mu0 * h_avg * h_avg;
            s_[i]   = e_[i] * h_avg;
        }
    }

    [[nodiscard]] double get_e(std::size_t idx) const { return e_.at(idx); }
    [[nodiscard]] double get_w_total(std::size_t idx) const { return w_e_.at(idx) + w_m_.at(idx); }
    [[nodiscard]] double get_s(std::size_t idx) const { return s_.at(idx); }

private:
    std::size_t nz_;
    double dz_;
    double dt_;
    std::vector<double> e_;
    std::vector<double> h_;
    std::vector<double> w_e_;
    std::vector<double> w_m_;
    std::vector<double> s_;
};

int main() {
    constexpr std::size_t grid_size = 200;
    constexpr double dz = 1e-3;

    FdtdSim1D sim(grid_size, dz);

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Крок | Вузол 100 E | Густина w_total (Дж/м³) | Потік S (Вт/м²)\n";
    std::cout << "--------------------------------------------------------------\n";

    for (std::size_t t = 0; t < 300; ++t) {
        sim.step(t);
        if (t % 50 == 0) {
            std::cout << std::setw(4) << t << " | "
                      << std::setw(11) << sim.get_e(100) << " | "
                      << std::setw(23) << sim.get_w_total(100) << " | "
                      << std::setw(16) << sim.get_s(100) << "\n";
        }
    }

    return 0;
}
