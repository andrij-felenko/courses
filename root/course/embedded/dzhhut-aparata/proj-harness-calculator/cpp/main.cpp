#include <iostream>
#include <iomanip>
#include <cmath>
#include <expected>
#include <string_view>

namespace harness {

constexpr double CopperRho20 = 1.724e-8; // Питомий опір міді за 20 °C, Ом * м
constexpr double CopperAlpha = 0.00393;  // Температурний коефіцієнт, 1 / K

enum class CalcError {
    InvalidCrossSection,
    InvalidLength,
    InvalidCurrent
};

struct Spec {
    double awg{24.0};
    double crossSectionMm2{0.205};     // 24 AWG
    double lengthM{1.8};               // 1.8 м
    double currentA{1.5};              // 1.5 А
    double ambientTempC{50.0};         // 50 °C
    double contactResistanceMohm{15.0};// 15 мОм
    int    loadedWiresCount{6};
    double logicVIlMax{0.80};          // 3.3V CMOS V_IL max
    double logicVOlMax{0.20};          // 3.3V CMOS V_OL max
    double outerDiameterMm{7.5};
};

struct Result {
    double wireResistanceOhm{0.0};
    double totalLoopDropV{0.0};
    double groundShiftV{0.0};
    double actualVIlAtReceiver{0.0};
    double noiseMarginV{0.0};
    bool   isLogicSafe{false};
    double bundleDeratingFactor{1.0};
    double minBendRadiusStaticMm{0.0};
    double minBendRadiusDynamicMm{0.0};
};

[[nodiscard]] constexpr std::expected<Result, CalcError> evaluate(const Spec& spec) noexcept {
    if (spec.crossSectionMm2 <= 0.0) {
        return std::unexpected(CalcError::InvalidCrossSection);
    }
    if (spec.lengthM <= 0.0) {
        return std::unexpected(CalcError::InvalidLength);
    }
    if (spec.currentA < 0.0) {
        return std::unexpected(CalcError::InvalidCurrent);
    }

    const double areaM2 = spec.crossSectionMm2 * 1e-6;
    const double r20 = (CopperRho20 * spec.lengthM) / areaM2;
    const double deltaT = spec.ambientTempC - 20.0;
    const double rWire = r20 * (1.0 + CopperAlpha * deltaT);
    const double rContact = spec.contactResistanceMohm * 1e-3;

    Result res{};
    res.wireResistanceOhm = rWire;
    res.totalLoopDropV = spec.currentA * (2.0 * rWire + 2.0 * rContact);
    res.groundShiftV = spec.currentA * (rWire + rContact);

    res.actualVIlAtReceiver = spec.logicVOlMax + res.groundShiftV;
    res.noiseMarginV = spec.logicVIlMax - res.actualVIlAtReceiver;
    res.isLogicSafe = (res.noiseMarginV >= 0.15); // Мінімальний запас 150 мВ

    if (spec.loadedWiresCount <= 1) {
        res.bundleDeratingFactor = 1.0;
    } else if (spec.loadedWiresCount == 2) {
        res.bundleDeratingFactor = 0.88;
    } else {
        const double k = 1.0 / std::sqrt(static_cast<double>(spec.loadedWiresCount));
        res.bundleDeratingFactor = (k < 0.40) ? 0.40 : k;
    }

    res.minBendRadiusStaticMm = 6.0 * spec.outerDiameterMm;
    res.minBendRadiusDynamicMm = 12.0 * spec.outerDiameterMm;

    return res;
}

} // namespace harness

int main() {
    constexpr harness::Spec spec{};
    const auto outcome = harness::evaluate(spec);

    if (!outcome) {
        std::cerr << "Помилка розрахунку джгута: некоректні геометричні параметри.\n";
        return 1;
    }

    const auto& res = *outcome;

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== РЕЗУЛЬТАТИ РОЗРАХУНКУ КАБЕЛЬНОГО ДЖГУТА (C++) ===\n";
    std::cout << "Опір жили за " << spec.ambientTempC << " °C:       " << res.wireResistanceOhm << " Ом\n";
    std::cout << "Сумарне падіння в петлі (±V):   " << res.totalLoopDropV << " В\n";
    std::cout << "Перекіс потенціалу землі (GND):  " << res.groundShiftV << " В\n";
    std::cout << "Рівень нуля на вході приймача:  " << res.actualVIlAtReceiver
              << " В (поріг: " << spec.logicVIlMax << " В)\n";
    std::cout << "Запас завадостійкості:           " << res.noiseMarginV
              << " В [" << (res.isLogicSafe ? "БЕЗПЕЧНО" : "НЕБЕЗПЕЧНИЙ ЗБІЙ") << "]\n";
    std::cout << "Делейтинг пучка провідників:     " << res.bundleDeratingFactor
              << " (струм знизити до " << (res.bundleDeratingFactor * 100.0) << "%)\n";
    std::cout << "Мін. радіус вигину (статика):    " << res.minBendRadiusStaticMm << " мм\n";
    std::cout << "Мін. радіус вигину (динаміка):   " << res.minBendRadiusDynamicMm << " мм\n";

    return 0;
}
