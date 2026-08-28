#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

class DislocationSimulation {
private:
    double G;         // Модуль зсуву (Па)
    double nu;        // Коефіцієнт Пуассона
    double b;         // Вектор Бюргерса (м)
    double B_visc;    // В'язке гальмування (Па·с)
    double C_force;   // Множник сили
    double r0_core;   // Радіус згладжування ядра (м)

public:
    DislocationSimulation(double shearG = 40e9, double poissonNu = 0.3, 
                          double burgersB = 2.86e-10, double viscB = 1e-4)
        : G(shearG), nu(poissonNu), b(burgersB), B_visc(viscB) {
        C_force = (G * b * b) / (2.0 * M_PI * (1.0 - nu));
        r0_core = 2.0 * b;
    }

    double calculateForceX(double x, double y) const {
        double r2 = x * x + y * y + r0_core * r0_core;
        return C_force * (x * (x * x - y * y)) / (r2 * r2);
    }

    void runTrajectory(double x0, double y0, double dt = 1e-13, size_t maxSteps = 20000) const {
        double x = x0;
        double y = y0;
        size_t steps = 0;

        for (size_t i = 0; i < maxSteps; ++i) {
            double fx = calculateForceX(x, y);
            double vx = fx / B_visc;
            double xNext = x + vx * dt;

            if (std::abs(vx) < 1e-3 || std::abs(xNext - x) < 1e-15) {
                break;
            }
            x = xNext;
            steps = i + 1;
        }

        std::cout << "Старт x0 = " << std::setw(6) << x0 * 1e9 << " нм, y0 = " << y0 * 1e9 
                  << " нм -> Рівновага x_eq = " << std::setw(8) << x * 1e9 
                  << " нм (кроків: " << steps << ")\n";
    }
};

int main() {
    DislocationSimulation sim;
    std::cout << "=== Симуляція ковзання дислокацій (C++) ===\n";
    sim.runTrajectory(2.0e-9, 1.0e-9);
    sim.runTrajectory(0.5e-9, 1.0e-9);
    sim.runTrajectory(-1.5e-9, 1.0e-9);
    return 0;
}
