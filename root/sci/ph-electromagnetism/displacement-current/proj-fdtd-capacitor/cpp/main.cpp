#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>

class Fdtd1DSimulator {
public:
    Fdtd1DSimulator(std::size_t nx, double dx)
        : nx_(nx), dx_(dx),
          c0_(299792458.0),
          eps0_(8.854187817e-12),
          mu0_(4.0 * M_PI * 1e-7),
          dt_(dx / (2.0 * c0_)),
          Ez_(nx, 0.0),
          Hy_(nx - 1, 0.0),
          eps_r_(nx, 1.0)
    {
        // Встановлюємо діелектричний шар конденсатора (вузли 80..120)
        for (std::size_t i = 80; i < 120 && i < nx_; ++i) {
            eps_r_[i] = 4.0;
        }
    }

    void step(std::size_t t_step) {
        const double ch = dt_ / (mu0_ * dx_);

        // 1. Оновлення магнітного поля Hy
        for (std::size_t k = 0; k < nx_ - 1; ++k) {
            Hy_[k] += ch * (Ez_[k + 1] - Ez_[k]);
        }

        // 2. Оновлення електричного поля Ez (враховуючи струм зміщення)
        for (std::size_t k = 1; k < nx_ - 1; ++k) {
            double ce = dt_ / (eps0_ * eps_r_[k] * dx_);
            Ez_[k] += ce * (Hy_[k] - Hy_[k - 1]);
        }

        // 3. Джерело гауссового імпульсу у вузлі 30
        double pulse = std::exp(-std::pow((static_cast<double>(t_step) - 40.0) / 12.0, 2));
        Ez_[30] += pulse;
    }

    double getMaxEzInCapacitor() const {
        double max_val = 0.0;
        for (std::size_t i = 80; i < 120 && i < nx_; ++i) {
            max_val = std::max(max_val, std::abs(Ez_[i]));
        }
        return max_val;
    }

    double getDt() const { return dt_; }

private:
    std::size_t nx_;
    double dx_;
    double c0_;
    double eps0_;
    double mu0_;
    double dt_;
    std::vector<double> Ez_;
    std::vector<double> Hy_;
    std::vector<double> eps_r_;
};

int main() {
    constexpr std::size_t NX = 200;
    constexpr std::size_t STEPS = 400;
    constexpr double DX = 1e-3;

    Fdtd1DSimulator solver(NX, DX);
    std::cout << "Запуск симулятора FDTD (C++): dt = " << solver.getDt() * 1e12 << " пс\n";

    for (std::size_t t = 0; t < STEPS; ++t) {
        solver.step(t);
    }

    std::cout << "Макс. амплітуда Ez у конденсаторі: " << solver.getMaxEzInCapacitor() << " В/м\n";
    return 0;
}
