#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <format>
#include <span>
#include <vector>

namespace pcb::em {

constexpr double Epsilon0 = 8.854187817e-12;
constexpr double Mu0 = 4.0 * std::numbers::pi * 1e-7;
constexpr double CopperResistivity = 1.72e-8;

struct MicrostripConfig {
    double dielectricHeightMm{0.12};
    double relativePermittivity{4.3};
    double traceWidthMm{0.22};
    double traceThicknessUm{35.0};
    double traceLengthMm{60.0};
};

struct GroundSlotConfig {
    double slotLengthMm{12.0};
    double slotWidthMm{0.5};
};

[[nodiscard]] constexpr double currentDensity(double xMm, double hMm, double currentA) noexcept {
    const double h = hMm * 1e-3;
    const double x = xMm * 1e-3;
    const double peakDensity = currentA / (std::numbers::pi * h);
    return peakDensity / (1.0 + (x / h) * (x / h));
}

[[nodiscard]] inline double currentFractionInBand(double xBoundaryMm, double hMm) noexcept {
    return (2.0 / std::numbers::pi) * std::atan(xBoundaryMm / hMm);
}

[[nodiscard]] double crossoverFrequency(const MicrostripConfig& cfg) noexcept {
    const double wM = cfg.traceWidthMm * 1e-3;
    const double tM = cfg.traceThicknessUm * 1e-6;
    const double lM = cfg.traceLengthMm * 1e-3;
    const double hM = cfg.dielectricHeightMm * 1e-3;

    const double areaM2 = wM * tM;
    const double rDc = CopperResistivity * lM / areaM2;

    const double z0 = (87.0 / std::sqrt(cfg.relativePermittivity + 1.41)) *
                      std::log(5.98 * hM / (0.8 * wM + tM));
    const double vProp = 3e8 / std::sqrt(cfg.relativePermittivity);
    const double lLoop = (z0 / vProp) * lM;

    return rDc / (2.0 * std::numbers::pi * lLoop);
}

[[nodiscard]] double slotInductance(const GroundSlotConfig& slot) noexcept {
    const double lM = slot.slotLengthMm * 1e-3;
    const double wM = slot.slotWidthMm * 1e-3;
    if (wM <= 0.0 || lM <= wM) return 0.0;
    return Mu0 * lM * std::log(lM / wM);
}

[[nodiscard]] constexpr double radiatedEmissions(double freqHz, double currentA, double loopAreaM2, double distM) noexcept {
    return 1.316e-14 * (freqHz * freqHz * currentA * loopAreaM2) / distM;
}

[[nodiscard]] constexpr double planeCapacitance(double areaCm2, double thicknessUm, double epsR) noexcept {
    const double areaM2 = areaCm2 * 1e-4;
    const double dM = thicknessUm * 1e-6;
    return (Epsilon0 * epsR * areaM2) / dM;
}

} // namespace pcb::em

int main() {
    using namespace pcb::em;

    constexpr MicrostripConfig trace{
        .dielectricHeightMm = 0.12,
        .relativePermittivity = 4.3,
        .traceWidthMm = 0.22,
        .traceThicknessUm = 35.0,
        .traceLengthMm = 60.0
    };

    std::cout << "=== АНАЛІЗ ОПОРНОГО ШАРУ ЗЕМЛІ (C++20) ===\n\n";

    std::cout << "1. Розподіл густини зворотного струму під доріжкою (h = "
              << trace.dielectricHeightMm << " мм, I = 1.0 A):\n";
    std::cout << "   x = 0.00 мм (пік):     J = "
              << currentDensity(0.0, trace.dielectricHeightMm, 1.0) << " А/м\n";
    std::cout << "   x = ±h (±0.12 мм):     J = "
              << currentDensity(trace.dielectricHeightMm, trace.dielectricHeightMm, 1.0)
              << " А/м  (частка: " << currentFractionInBand(trace.dielectricHeightMm, trace.dielectricHeightMm) * 100.0 << "%)\n";
    std::cout << "   x = ±3h (±0.36 мм):    J = "
              << currentDensity(3.0 * trace.dielectricHeightMm, trace.dielectricHeightMm, 1.0)
              << " А/м  (частка: " << currentFractionInBand(3.0 * trace.dielectricHeightMm, trace.dielectricHeightMm) * 100.0 << "%)\n";
    std::cout << "   x = ±10h (±1.20 мм):   J = "
              << currentDensity(10.0 * trace.dielectricHeightMm, trace.dielectricHeightMm, 1.0)
              << " А/м  (частка: " << currentFractionInBand(10.0 * trace.dielectricHeightMm, trace.dielectricHeightMm) * 100.0 << "%)\n\n";

    const double fc = crossoverFrequency(trace);
    std::cout << "2. Частота кросоверу: f_c = " << (fc / 1000.0) << " кГц\n\n";

    constexpr GroundSlotConfig slot{.slotLengthMm = 12.0, .slotWidthMm = 0.5};
    const double lSlot = slotInductance(slot);
    constexpr double diDt = 0.025 / 0.6e-9;
    const double vBounce = lSlot * diDt;

    std::cout << "3. Паразитна індуктивність розрізу землі: L_slot = "
              << (lSlot * 1e9) << " нГн\n";
    std::cout << "   Стрибок Ground Bounce: V_bounce = " << vBounce << " В\n\n";

    constexpr double areaContinuous = (trace.traceLengthMm * 1e-3) * (trace.dielectricHeightMm * 1e-3);
    constexpr double areaSlotted = areaContinuous + (slot.slotLengthMm * 1e-3) * 0.015;
    const double eClean = radiatedEmissions(200e6, 0.025, areaContinuous, 3.0);
    const double eSlotted = radiatedEmissions(200e6, 0.025, areaSlotted, 3.0);

    std::cout << "4. Випромінювання на 200 МГц:\n";
    std::cout << "   Нерозривний GND: E = " << (eClean * 1e6) << " мкВ/м ("
              << (20.0 * std::log10(eClean * 1e6)) << " дБмкВ/м)\n";
    std::cout << "   Розріз у GND:   E = " << (eSlotted * 1e6) << " мкВ/м ("
              << (20.0 * std::log10(eSlotted * 1e6)) << " дБмкВ/м)\n";
    std::cout << "   Перевищення:    Δ = +" << (20.0 * std::log10(eSlotted / eClean)) << " дБ\n\n";

    const double cPdn = planeCapacitance(60.0, 75.0, 4.3);
    std::cout << "5. Міжшарова ємність живлення-земля: C = " << (cPdn * 1e9) << " нФ\n";

    return 0;
}
