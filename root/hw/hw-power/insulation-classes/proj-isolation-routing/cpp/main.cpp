#include <iostream>
#include <iomanip>
#include <string_view>
#include <expected>

namespace safety {

enum class PollutionDegree {
    CleanDry = 1,     // PD 1: герметичні модулі або лаковані плати
    NormalIndoor = 2, // PD 2: офісна та побутова електроніка
    Industrial = 3    // PD 3: промислове пилове середовище
};

enum class MaterialGroup {
    GroupI,   // CTI >= 600 (фторопласт, кераміка)
    GroupII,  // 400 <= CTI < 600 (спеціальний текстоліт)
    GroupIIIa // 175 <= CTI < 400 (стандартний FR-4 / CEM-1)
};

enum class InsulationClass {
    Functional,
    Basic,
    Reinforced
};

struct IsolationSpec {
    double voltageRms{250.0};
    double altitudeMeters{0.0};
    InsulationClass insulation{InsulationClass::Reinforced};
    PollutionDegree pollution{PollutionDegree::NormalIndoor};
    MaterialGroup material{MaterialGroup::GroupIIIa};
};

struct IsolationRequirements {
    double clearanceMm{0.0};
    double creepageMm{0.0};
    double altitudeMultiplier{1.0};
};

class IsolationCalculator {
public:
    [[nodiscard]] static constexpr double getAltitudeMultiplier(double altitudeMeters) noexcept {
        if (altitudeMeters <= 2000.0) return 1.00;
        if (altitudeMeters <= 3000.0) return 1.14;
        if (altitudeMeters <= 4000.0) return 1.29;
        if (altitudeMeters <= 5000.0) return 1.48;
        return 1.70;
    }

    [[nodiscard]] static std::expected<IsolationRequirements, std::string_view>
    compute(const IsolationSpec& spec) noexcept {
        if (spec.voltageRms <= 0.0) {
            return std::unexpected("Робоча напруга повинна бути більшою за нуль");
        }

        double baseClr = 0.0;
        if (spec.voltageRms <= 150.0) {
            baseClr = 1.0;
        } else if (spec.voltageRms <= 300.0) {
            baseClr = (spec.insulation == InsulationClass::Reinforced) ? 3.0 : 1.5;
        } else {
            baseClr = (spec.insulation == InsulationClass::Reinforced) ? 6.0 : 3.0;
        }

        if (spec.insulation == InsulationClass::Functional) {
            baseClr = 0.5;
        }

        const double altMult = getAltitudeMultiplier(spec.altitudeMeters);
        const double finalClr = baseClr * altMult;

        double baseCrp = 0.0;
        if (spec.pollution == PollutionDegree::CleanDry) {
            baseCrp = (spec.insulation == InsulationClass::Reinforced) ? 1.4 : 0.7;
        } else if (spec.pollution == PollutionDegree::NormalIndoor) {
            switch (spec.material) {
                case MaterialGroup::GroupI:
                    baseCrp = (spec.insulation == InsulationClass::Reinforced) ? 3.6 : 1.8;
                    break;
                case MaterialGroup::GroupII:
                    baseCrp = (spec.insulation == InsulationClass::Reinforced) ? 4.4 : 2.2;
                    break;
                case MaterialGroup::GroupIIIa:
                default:
                    baseCrp = (spec.insulation == InsulationClass::Reinforced) ? 5.0 : 2.5;
                    break;
            }
        } else { // Industrial PD 3
            baseCrp = (spec.insulation == InsulationClass::Reinforced) ? 8.0 : 4.0;
        }

        return IsolationRequirements{
            .clearanceMm = finalClr,
            .creepageMm = baseCrp,
            .altitudeMultiplier = altMult
        };
    }
};

} // namespace safety

int main() {
    using namespace safety;

    constexpr IsolationSpec spec{
        .voltageRms = 250.0,
        .altitudeMeters = 3500.0,
        .insulation = InsulationClass::Reinforced,
        .pollution = PollutionDegree::NormalIndoor,
        .material = MaterialGroup::GroupIIIa
    };

    const auto result = IsolationCalculator::compute(spec);

    if (!result) {
        std::cerr << "Помилка розрахунку: " << result.error() << '\n';
        return 1;
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Розрахунок зазорів безпеки друкованої плати (C++23) ===\n";
    std::cout << "Робоча напруга мережі:        " << spec.voltageRms << " В RMS\n";
    std::cout << "Висота над рівнем моря:       " << spec.altitudeMeters << " м\n";
    std::cout << "Висотний множник k_d:         " << result->altitudeMultiplier << "x\n";
    std::cout << "------------------------------------------------------\n";
    std::cout << "Повітряний зазор (Clearance): " << result->clearanceMm << " мм\n";
    std::cout << "Шлях витоку (Creepage):       " << result->creepageMm << " мм\n";

    return 0;
}
