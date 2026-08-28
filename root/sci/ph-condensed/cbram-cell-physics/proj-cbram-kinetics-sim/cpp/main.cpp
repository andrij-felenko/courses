#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string_view>
#include <algorithm>

namespace cbram {

constexpr double kElemCharge = 1.602e-19; // Елементарний заряд, Кл
constexpr double kBoltzmann  = 1.381e-23; // Стала Больцмана, Дж/К
constexpr double kTempEnv    = 300.0;     // Кімнатна температура, К

// Структура фізичних параметрів комірки
struct CellParameters {
    double cellGap{10.0e-9};            // Товщина електроліту (м)
    double activationEnergy{0.8 * kElemCharge}; // E_a (Дж)
    double hopDistance{0.4e-9};         // Довжина стрибка іона (м)
    double attemptFrequency{1.0e13};    // Частота спроб (Гц)
    double rHrs{1.0e7};                 // Опір HRS (Ом)
    double rLrs{1000.0};                // Опір LRS (Ом)
    double iCompliance{100.0e-6};       // Обмеження струму I_CC (А)
    double thermalCoeff{5.0e-5};        // Тепловий коефіцієнт (Вт/К)
};

// Точка результату розрахунку ВАХ
struct SimulationPoint {
    double voltage{0.0};
    double current{0.0};
    double filamentHeight{0.0};
    double temperature{kTempEnv};
    bool isLrs{false};
};

class CellSimulator {
public:
    explicit CellSimulator(CellParameters params = {})
        : params_(params), height_(0.0), temp_(kTempEnv), isConnected_(false) {}

    // Виконати один диференціальний крок
    SimulationPoint step(double vApp, double dt) {
        const double rCell = computeResistance();
        double iCell = vApp / rCell;

        // Захист струму комплайєнсом
        if (vApp > 0.0 && std::abs(iCell) > params_.iCompliance) {
            iCell = std::copysign(params_.iCompliance, iCell);
        }

        // Джоулів нагрів у звуженні
        const double pJoule = iCell * iCell * rCell;
        temp_ = kTempEnv + pJoule / params_.thermalCoeff;

        // Поле в зазорі
        const double gapRem = params_.cellGap - height_ + 0.1e-9;
        const double eField = vApp / gapRem;

        if (vApp > 0.0 && !isConnected_) {
            // Динаміка SET
            double arg = (kElemCharge * eField * params_.hopDistance) / (2.0 * kBoltzmann * temp_);
            arg = std::min(arg, 30.0); // Захист від exp-overflow

            const double vDrift = params_.attemptFrequency * params_.hopDistance *
                                  std::exp(-params_.activationEnergy / (kBoltzmann * temp_)) *
                                  std::sinh(arg);

            height_ += vDrift * dt;
            if (height_ >= params_.cellGap * 0.99) {
                height_ = params_.cellGap;
                isConnected_ = true;
            }
        } else if (vApp < 0.0 && isConnected_) {
            // Динаміка RESET
            const double vDissolve = params_.attemptFrequency * params_.hopDistance *
                                     std::exp(-params_.activationEnergy / (kBoltzmann * temp_)) * 2.0;
            height_ -= vDissolve * dt;
            if (height_ < params_.cellGap * 0.95) {
                isConnected_ = false;
            }
            height_ = std::max(0.0, height_);
        }

        return SimulationPoint{vApp, iCell, height_, temp_, isConnected_};
    }

    [[nodiscard]] double height() const noexcept { return height_; }
    [[nodiscard]] bool isLrs() const noexcept { return isConnected_; }

private:
    [[nodiscard]] double computeResistance() const noexcept {
        if (height_ >= params_.cellGap * 0.99) {
            return params_.rLrs;
        }
        const double fraction = height_ / params_.cellGap;
        const double rCurr = params_.rHrs * (1.0 - fraction) + params_.rLrs * fraction;
        return std::max(rCurr, params_.rLrs);
    }

    CellParameters params_;
    double height_;
    double temp_;
    bool isConnected_;
};

} // namespace cbram

int main() {
    using namespace cbram;

    CellParameters params;
    CellSimulator simulator(params);

    constexpr int steps = 200;
    constexpr double dt = 1.0e-5;

    std::cout << "=== CBRAM Simulation Output (C++) ===\n";
    std::cout << std::left 
              << std::setw(8)  << "Step"
              << std::setw(14) << "Voltage (V)"
              << std::setw(16) << "Current (uA)"
              << std::setw(16) << "Filament (nm)"
              << "State\n";

    for (int i = 0; i <= steps; ++i) {
        const double t = static_cast<double>(i) / steps;
        double vApp = 0.0;

        if (t <= 0.25) {
            vApp = (t / 0.25) * 1.5;
        } else if (t <= 0.50) {
            vApp = 1.5 - ((t - 0.25) / 0.25) * 1.5;
        } else if (t <= 0.75) {
            vApp = -((t - 0.50) / 0.25) * 1.0;
        } else {
            vApp = -1.0 + ((t - 0.75) / 0.25) * 1.0;
        }

        const auto pt = simulator.step(vApp, dt);

        if (i % 20 == 0) {
            std::cout << std::left
                      << std::setw(8)  << i
                      << std::setw(14) << std::fixed << std::setprecision(3) << pt.voltage
                      << std::setw(16) << std::fixed << std::setprecision(2) << pt.current * 1e6
                      << std::setw(16) << std::fixed << std::setprecision(2) << pt.filamentHeight * 1e9
                      << (pt.isLrs ? "LRS" : "HRS") << "\n";
        }
    }

    return 0;
}
