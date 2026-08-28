// cpp — Ідіоматична симуляція розділення ізотопів на C++20
#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <vector>
#include <iomanip>

namespace IsotopePhysics {

constexpr double kElemCharge = 1.602'176'634e-19; // Кл
constexpr double kAmuToKg    = 1.660'539'066e-27; // кг
constexpr double kGasConst   = 8.314'462'618;     // Дж/(моль·К)

enum class SimulationError {
    InvalidParameter,
    NonPhysicalValues
};

struct EMSeparatorParams {
    double massAmu1{235.0439};
    double massAmu2{238.0507};
    double voltageV{10000.0};
    double magneticBT{0.5};
};

struct EMSeparatorResult {
    double radiusM1{0.0};
    double radiusM2{0.0};
    double separationMm{0.0};
    double resolution{0.0};
};

struct CascadeParams {
    double deltaMkg{0.003};
    double rotorRadiusM{0.15};
    double rpm{90000.0};
    double tempKelvin{320.0};
    double feedFraction{0.0072};
    double prodFraction{0.045};
    double tailFraction{0.002};
};

struct CascadeResult {
    double vPeripheral{0.0};
    double alphaFactor{0.0};
    double minStages{0.0};
    double productFlowRatio{0.0};
};

class IsotopeSeparatorSimulator {
public:
    [[nodiscard]] static std::expected<EMSeparatorResult, SimulationError> 
    simulateEM(const EMSeparatorParams& p) noexcept {
        if (p.magneticBT <= 0.0 || p.voltageV <= 0.0 || p.massAmu1 <= 0.0 || p.massAmu2 <= 0.0) {
            return std::unexpected(SimulationError::InvalidParameter);
        }

        const double m1Kg = p.massAmu1 * kAmuToKg;
        const double m2Kg = p.massAmu2 * kAmuToKg;

        EMSeparatorResult res;
        res.radiusM1 = (1.0 / p.magneticBT) * std::sqrt((2.0 * m1Kg * p.voltageV) / kElemCharge);
        res.radiusM2 = (1.0 / p.magneticBT) * std::sqrt((2.0 * m2Kg * p.voltageV) / kElemCharge);
        res.separationMm = 2.0 * std::abs(res.radiusM2 - res.radiusM1) * 1000.0;
        res.resolution = (p.massAmu1 + p.massAmu2) / (2.0 * std::abs(p.massAmu2 - p.massAmu1));

        return res;
    }

    [[nodiscard]] static std::expected<CascadeResult, SimulationError> 
    simulateCascade(const CascadeParams& p) noexcept {
        if (p.rpm <= 0.0 || p.rotorRadiusM <= 0.0 || p.tempKelvin <= 0.0 ||
            p.prodFraction <= p.feedFraction || p.feedFraction <= p.tailFraction) {
            return std::unexpected(SimulationError::InvalidParameter);
        }

        const double omega = (p.rpm * 2.0 * std::numbers::pi) / 60.0;
        CascadeResult res;
        res.vPeripheral = omega * p.rotorRadiusM;

        const double exponent = (p.deltaMkg * res.vPeripheral * res.vPeripheral) / (2.0 * kGasConst * p.tempKelvin);
        res.alphaFactor = std::exp(exponent);

        const double FenskeRatio = (p.prodFraction / (1.0 - p.prodFraction)) / 
                                   (p.tailFraction / (1.0 - p.tailFraction));
        res.minStages = std::log(FenskeRatio) / std::log(res.alphaFactor);
        res.productFlowRatio = (p.feedFraction - p.tailFraction) / (p.prodFraction - p.tailFraction);

        return res;
    }
};

} // namespace IsotopePhysics

int main() {
    using namespace IsotopePhysics;

    std::cout << "=== СИМУЛЯЦІЯ РОЗДІЛЕННЯ ІЗОТОПІВ (C++20) ===\n\n";

    // 1. Електромагнітне розділення
    EMSeparatorParams emParams{.massAmu1 = 235.0439, .massAmu2 = 238.0507, .voltageV = 10000.0, .magneticBT = 0.5};
    if (auto res = IsotopeSeparatorSimulator::simulateEM(emParams); res.has_value()) {
        std::cout << "--- Електромагнітний розділювач ---\n"
                  << std::fixed << std::setprecision(4)
                  << "Радіус 235U: " << res->radiusM1 << " м\n"
                  << "Радіус 238U: " << res->radiusM2 << " м\n"
                  << std::setprecision(2)
                  << "Просторове розділення: " << res->separationMm << " мм\n"
                  << "Роздільна здатність m/Δm: " << res->resolution << "\n\n";
    }

    // 2. Центрифужний каскад
    CascadeParams cascadeParams{
        .deltaMkg = 0.003,
        .rotorRadiusM = 0.15,
        .rpm = 90000.0,
        .tempKelvin = 320.0,
        .feedFraction = 0.0072,
        .prodFraction = 0.045,
        .tailFraction = 0.002
    };

    if (auto res = IsotopeSeparatorSimulator::simulateCascade(cascadeParams); res.has_value()) {
        std::cout << "--- Збагачувальний каскад (UF6) ---\n"
                  << std::fixed << std::setprecision(1)
                  << "Периферійна швидкість ротора: " << res->vPeripheral << " м/с\n"
                  << std::setprecision(5)
                  << "Фактор збагачення α: " << res->alphaFactor << "\n"
                  << std::setprecision(1)
                  << "Необхідно ступенів N_min: " << res->minStages << "\n"
                  << std::setprecision(4)
                  << "Вихід продукту P/F: " << res->productFlowRatio 
                  << " (" << res->productFlowRatio * 100.0 << "%)\n";
    }

    return 0;
}
