#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>

enum class AnisotropySymmetry {
    Uniaxial,
    Cubic
};

struct MagneticParameters {
    double Ms{1.4e6};              // A/m
    double K1{4.1e5};              // J/m^3
    double K2{1.0e5};              // J/m^3
    AnisotropySymmetry symmetry{AnisotropySymmetry::Uniaxial};
};

class MagnetizationSimulator {
public:
    static constexpr double Mu0 = 1.2566370614359173e-6;

    explicit MagnetizationSimulator(MagneticParameters params) 
        : params_(params) {}

    [[nodiscard]] double anisotropyEnergy(double theta, double phi = 0.0) const noexcept {
        if (params_.symmetry == AnisotropySymmetry::Uniaxial) {
            const double sinT = std::sin(theta);
            const double sin2T = sinT * sinT;
            return params_.K1 * sin2T + params_.K2 * sin2T * sin2T;
        } else {
            const double a1 = std::sin(theta) * std::cos(phi);
            const double a2 = std::sin(theta) * std::sin(phi);
            const double a3 = std::cos(theta);
            const double a1_2 = a1 * a1, a2_2 = a2 * a2, a3_2 = a3 * a3;
            return params_.K1 * (a1_2 * a2_2 + a2_2 * a3_2 + a3_2 * a1_2) 
                 + params_.K2 * (a1_2 * a2_2 * a3_2);
        }
    }

    [[nodiscard]] double totalEnergy(double H, double psi, double theta) const noexcept {
        const double E_A = anisotropyEnergy(theta);
        const double E_Z = -Mu0 * params_.Ms * H * std::cos(psi - theta);
        return E_A + E_Z;
    }

    struct SimulationPoint {
        double H_field;
        double m_normalized;
        double theta_rad;
    };

    [[nodiscard]] std::vector<SimulationPoint> runHysteresisLoop(
        double psiDegrees, double maxHField, std::size_t steps) const 
    {
        std::vector<SimulationPoint> curve;
        curve.reserve(steps + 1);

        const double psi = psiDegrees * std::numbers::pi / 180.0;
        double thetaCurrent = (std::cos(psi) >= 0.0) ? 0.0 : std::numbers::pi;
        const double stepH = 2.0 * maxHField / static_cast<double>(steps);

        for (std::size_t i = 0; i <= steps; ++i) {
            const double H = -maxHField + static_cast<double>(i) * stepH;
            thetaCurrent = minimizeEnergy1D(H, psi, thetaCurrent);
            const double mParallel = std::cos(psi - thetaCurrent);
            curve.push_back({H, mParallel, thetaCurrent});
        }
        return curve;
    }

private:
    MagneticParameters params_;

    [[nodiscard]] double minimizeEnergy1D(double H, double psi, double thetaGuess) const {
        double a = thetaGuess - std::numbers::pi / 4.0;
        double b = thetaGuess + std::numbers::pi / 4.0;
        constexpr double GoldenRatio = 1.618033988749895;
        constexpr double ResPhi = 2.0 - GoldenRatio;

        double x1 = a + ResPhi * (b - a);
        double x2 = b - ResPhi * (b - a);
        double f1 = totalEnergy(H, psi, x1);
        double f2 = totalEnergy(H, psi, x2);

        for (int iter = 0; iter < 80; ++iter) {
            if (f1 < f2) {
                b = x2;
                x2 = x1;
                f2 = f1;
                x1 = a + ResPhi * (b - a);
                f1 = totalEnergy(H, psi, x1);
            } else {
                a = x1;
                x1 = x2;
                f1 = f2;
                x2 = b - ResPhi * (b - a);
                f2 = totalEnergy(H, psi, x2);
            }
            if (std::abs(b - a) < 1e-8) break;
        }
        return (a + b) / 2.0;
    }
};

int main() {
    MagneticParameters feParams{
        .Ms = 1.71e6,
        .K1 = 4.8e4,
        .K2 = 0.5e4,
        .symmetry = AnisotropySymmetry::Uniaxial
    };

    MagnetizationSimulator simulator(feParams);
    auto results = simulator.runHysteresisLoop(45.0, 5e5, 20);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "H (A/m)\t\tM / Ms\t\tTheta (rad)\n";
    for (const auto& point : results) {
        std::cout << point.H_field << "\t\t" 
                  << point.m_normalized << "\t\t" 
                  << point.theta_rad << "\n";
    }
    return 0;
}
