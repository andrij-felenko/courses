#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>
#include <span>

namespace PowerAudit {

constexpr double CopperRho20C   = 1.724e-8; // Ом * м
constexpr double CopperAlpha20C = 0.00393;  // 1 / °C
constexpr double CopperKcu      = 5.091e4;  // А^2 * с / мм^4

enum class ElementType {
    Connector,
    Trace,
    ViaArray,
    Mosfet,
    Fuse,
    Shunt
};

struct ElementParams {
    std::string name;
    ElementType type;
    double nominalResistanceOhm{0.0};
    double tempCoefficient{0.0};
    
    // Доріжка
    double lengthMm{0.0};
    double widthMm{0.0};
    double thicknessUm{0.0};
    bool hasGroundPlane{true};
    
    // Переходи (via)
    int viaCount{1};
    double drillDiameterMm{0.4};
    double platingThicknessUm{25.0};
    
    // MOSFET
    double rThJa{0.0};
    
    // Захист
    double i2tRatingA2s{0.0};
};

struct ElementResult {
    double opResistanceOhm{0.0};
    double voltageDropV{0.0};
    double powerLossW{0.0};
    double tempRiseC{0.0};
    double finalTempC{0.0};
    bool isSafe{true};
    std::string defectReason{};
};

struct AuditReport {
    double totalResistanceNom{0.0};
    double totalResistanceHot{0.0};
    double totalVDropCont{0.0};
    double totalVDropPeak{0.0};
    double vLoadMinWorstCase{0.0};
    double totalPowerDissipatedW{0.0};
    bool systemPass{true};
    std::vector<ElementResult> elementResults;
};

class PowerPathAuditor {
public:
    struct Config {
        double vSourceNom{24.0};
        double vSourceMin{18.0};
        double iLoadContinuous{5.0};
        double iLoadPeak{10.0};
        double tAmbientC{55.0};
        double vUvloThreshold{17.0};
    };

    explicit PowerPathAuditor(Config cfg) : cfg_(cfg) {}

    [[nodiscard]] AuditReport evaluate(std::span<const ElementParams> elements) const {
        AuditReport report{};
        report.elementResults.reserve(elements.size());

        for (const auto& elem : elements) {
            ElementResult res{};
            double rNom = elem.nominalResistanceOhm;
            double alpha = elem.tempCoefficient;

            if (elem.type == ElementType::Trace) {
                rNom = calculateTraceResistance20C(elem.lengthMm, elem.widthMm, elem.thicknessUm);
                alpha = CopperAlpha20C;
            } else if (elem.type == ElementType::ViaArray) {
                rNom = calculateViaArrayResistance20C(elem.viaCount, elem.drillDiameterMm, elem.platingThicknessUm, 1.6);
                alpha = CopperAlpha20C;
            }

            // Оцінка перегріву
            const double current = cfg_.iLoadContinuous;
            const double pEst = current * current * rNom;

            if (elem.type == ElementType::Trace) {
                res.tempRiseC = calculateTraceTempRise(current, elem.widthMm, elem.thicknessUm, elem.hasGroundPlane);
            } else if (elem.type == ElementType::Mosfet && elem.rThJa > 0.0) {
                res.tempRiseC = pEst * elem.rThJa;
            } else {
                res.tempRiseC = pEst * 15.0;
            }

            res.finalTempC = cfg_.tAmbientC + res.tempRiseC;
            const double deltaT = res.finalTempC - 20.0;
            res.opResistanceOhm = rNom * (1.0 + alpha * deltaT);
            res.voltageDropV = current * res.opResistanceOhm;
            res.powerLossW = current * current * res.opResistanceOhm;

            // Верифікація безпеки
            if (res.finalTempC > 105.0) {
                res.isSafe = false;
                res.defectReason = "Перегрів > 105 °C (межа FR-4)";
            }

            if (elem.type == ElementType::Trace) {
                const double areaMm2 = elem.widthMm * (elem.thicknessUm * 1e-3);
                const double lnTerm = std::log((1.0 + CopperAlpha20C * (150.0 - 20.0)) /
                                               (1.0 + CopperAlpha20C * (res.finalTempC - 20.0)));
                const double i2tTraceLimit = CopperKcu * areaMm2 * areaMm2 * lnTerm;

                for (const auto& other : elements) {
                    if (other.type == ElementType::Fuse && other.i2tRatingA2s > 0.0) {
                        if (other.i2tRatingA2s >= i2tTraceLimit) {
                            res.isSafe = false;
                            res.defectReason = "I²t запобіжника перевищує поріг руйнування міді";
                        }
                    }
                }
            }

            if (!res.isSafe) {
                report.systemPass = false;
            }

            report.totalResistanceNom += rNom;
            report.totalResistanceHot += res.opResistanceOhm;
            report.totalPowerDissipatedW += res.powerLossW;
            report.elementResults.push_back(res);
        }

        report.totalVDropCont = cfg_.iLoadContinuous * report.totalResistanceHot;
        report.totalVDropPeak = cfg_.iLoadPeak * report.totalResistanceHot;
        report.vLoadMinWorstCase = cfg_.vSourceMin - report.totalVDropPeak;

        if (report.vLoadMinWorstCase < cfg_.vUvloThreshold) {
            report.systemPass = false;
        }

        return report;
    }

private:
    Config cfg_;

    static double calculateTraceResistance20C(double lenMm, double widthMm, double thickUm) noexcept {
        const double areaM2 = (widthMm * 1e-3) * (thickUm * 1e-6);
        if (areaM2 <= 0.0) return 0.0;
        return CopperRho20C * ((lenMm * 1e-3) / areaM2);
    }

    static double calculateViaArrayResistance20C(int count, double drillMm, double platingUm, double boardThickMm) noexcept {
        if (count <= 0 || drillMm <= 0.0 || platingUm <= 0.0) return 0.0;
        const double meanDiamM = (drillMm - platingUm * 1e-3) * 1e-3;
        const double wallAreaM2 = std::numbers::pi * meanDiamM * (platingUm * 1e-6);
        const double singleViaR = CopperRho20C * (boardThickMm * 1e-3 / wallAreaM2);
        return singleViaR / static_cast<double>(count);
    }

    static double calculateTraceTempRise(double current, double widthMm, double thickUm, bool hasPlane) noexcept {
        const double areaMm2 = widthMm * (thickUm * 1e-3);
        if (areaMm2 <= 0.0) return 999.0;
        const double k = hasPlane ? 14.5 : 9.95;
        const double term = current / (k * std::pow(areaMm2, 0.725));
        if (term <= 0.0) return 0.0;
        return std::pow(term, 1.0 / 0.44);
    }
};

} // namespace PowerAudit

int main() {
    using namespace PowerAudit;

    const std::vector<ElementParams> powerElements = {
        { .name = "XT30 Роз'єм",       .type = ElementType::Connector, .nominalResistanceOhm = 0.005,  .tempCoefficient = 0.002 },
        { .name = "SMD Запобіжник 7A", .type = ElementType::Fuse,      .nominalResistanceOhm = 0.015,  .tempCoefficient = 0.001, .i2tRatingA2s = 18.0 },
        { .name = "P-MOS FET Захист",  .type = ElementType::Mosfet,    .nominalResistanceOhm = 0.008,  .tempCoefficient = 0.006, .rThJa = 45.0 },
        { .name = "Шина живлення (2oz)",.type = ElementType::Trace,     .lengthMm = 80.0, .widthMm = 4.0, .thicknessUm = 70.0, .hasGroundPlane = true },
        { .name = "Масив переходів (4x)",.type = ElementType::ViaArray, .viaCount = 4, .drillDiameterMm = 0.4, .platingThicknessUm = 25.0 },
        { .name = "Вимірювальний шунт", .type = ElementType::Shunt,     .nominalResistanceOhm = 0.010,  .tempCoefficient = 0.0001 }
    };

    PowerPathAuditor::Config cfg{
        .vSourceNom = 24.0,
        .vSourceMin = 18.0,
        .iLoadContinuous = 5.0,
        .iLoadPeak = 10.0,
        .tAmbientC = 55.0,
        .vUvloThreshold = 17.0
    };

    PowerPathAuditor auditor(cfg);
    const auto report = auditor.evaluate(powerElements);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "================================================================================\n";
    std::cout << "             ЗВІТ НАСКРІЗНОГО АУДИТУ СИЛОВОГО ТРАКТУ (C++20)                    \n";
    std::cout << "================================================================================\n";
    std::cout << "Загальний опір (гарячий):          " << report.totalResistanceHot * 1e3 << " мОм\n";
    std::cout << "Сумарний спад напруги (пік 10A):  " << report.totalVDropPeak << " В\n";
    std::cout << "Мінімальна напруга на шині:       " << report.vLoadMinWorstCase << " В (UVLO: " << cfg.vUvloThreshold << " В)\n";
    std::cout << "Сумарні втрати потужності:        " << report.totalPowerDissipatedW << " Вт\n";
    std::cout << "Статус системи:                   " << (report.systemPass ? "ВІДПОВІДАЄ НОРМАМ" : "ДЕФЕКТ") << "\n";
    std::cout << "================================================================================\n";

    return 0;
}
