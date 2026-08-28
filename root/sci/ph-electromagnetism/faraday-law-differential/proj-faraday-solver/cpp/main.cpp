#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <memory>

class FaradayFdtdSolver {
public:
    FaradayFdtdSolver(std::size_t gridSize, double dz)
        : gridSize_(gridSize), dz_(dz), cSpeed_(3.0e8) {
        dt_ = 0.99 * dz_ / cSpeed_;
        ey_.resize(gridSize_, 0.0);
        bx_.resize(gridSize_, 0.0);
    }

    /* Оновлення магнітного поля B з ротора E (диференціальний закон Фарадея) */
    void updateMagneticField() noexcept {
        double coeff = dt_ / dz_;
        for (std::size_t k = 0; k < gridSize_ - 1; ++k) {
            bx_[k] += coeff * (ey_[k + 1] - ey_[k]);
        }
    }

    /* Оновлення електричного поля E з ротора B (закон Ампера-Максвелла) */
    void updateElectricField() noexcept {
        double coeff = (cSpeed_ * cSpeed_) * dt_ / dz_;
        for (std::size_t k = 1; k < gridSize_ - 1; ++k) {
            ey_[k] += coeff * (bx_[k] - bx_[k - 1]);
        }
    }

    void injectGaussianSource(std::size_t location, double timeStep, double width) {
        if (location < gridSize_) {
            ey_[location] += std::exp(-std::pow((timeStep - 40.0) / width, 2.0));
        }
    }

    void step(double timeStep) {
        injectGaussianSource(gridSize_ / 2, timeStep, 12.0);
        updateMagneticField();
        updateElectricField();
    }

    [[nodiscard]] double getEy(std::size_t index) const { return ey_.at(index); }
    [[nodiscard]] double getBx(std::size_t index) const { return bx_.at(index); }
    [[nodiscard]] double getDt() const noexcept { return dt_; }

private:
    std::size_t gridSize_;
    double dz_;
    double cSpeed_;
    double dt_;
    std::vector<double> ey_;
    std::vector<double> bx_;
};

int main() {
    constexpr std::size_t kGridSize = 200;
    constexpr double kDz = 0.001; // 1 мм

    FaradayFdtdSolver solver(kGridSize, kDz);

    std::cout << "Ініціалізація C++20 FDTD розв'язувача laws Faraday...\n";
    std::cout << "Крок часу dt = " << solver.getDt() << " с\n";

    for (int t = 0; t < 300; ++t) {
        solver.step(static_cast<double>(t));
    }

    std::cout << "Розрахунок завершено. Ey[100] = " << solver.getEy(100) << " В/м\n";
    return 0;
}
