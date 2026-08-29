#include "selection.hpp"

#include <array>
#include <format>
#include <iostream>

namespace {

using namespace drive;

// Кандидати з полиці. Числа — типові паспортні: струм і опір фази NEMA 17
// ті самі, з якими рахували тепловиділення в тексті.
constexpr std::array<Unit, 5> kCandidates{{
    {
        .motor = {
            .name = "N20 12В + планетарний 100:1",
            .family = Family::Brushed,
            .ratedTorqueNm = 0.0092,
            .noLoadSpeedRpm = 10000.0,
            .cornerSpeedRpm = 0.0,
            .ratedCurrentA = 0.8,
            .phaseResistanceOhm = 1.5,
            .rotorInertiaKgm2 = 1.0e-7,
            .thermalResistanceCPerW = 32.0,
            .supplyV = 12.0,
            .holdCurrentFraction = 1.0,
            .stepResolutionDeg = 0.0        // енкодера немає: положення привід не знає
        },
        .gear = { .ratio = 100.0, .efficiency = 0.60, .backlashDeg = 0.80 }
    },
    {
        .motor = {
            .name = "37GB520 12В + планетарний 30:1",
            .family = Family::Brushed,
            .ratedTorqueNm = 0.0215,
            .noLoadSpeedRpm = 8000.0,
            .cornerSpeedRpm = 0.0,
            .ratedCurrentA = 1.5,
            .phaseResistanceOhm = 1.0,
            .rotorInertiaKgm2 = 8.0e-6,
            .thermalResistanceCPerW = 8.0,
            .supplyV = 12.0,
            .holdCurrentFraction = 1.0,
            .stepResolutionDeg = 0.0
        },
        .gear = { .ratio = 30.0, .efficiency = 0.70, .backlashDeg = 0.50 }
    },
    {
        .motor = {
            .name = "NEMA 17 + TMC2209, 1/16 кроку",
            .family = Family::Stepper,
            .ratedTorqueNm = 0.59,          // момент утримання
            .noLoadSpeedRpm = 1000.0,
            .cornerSpeedRpm = 300.0,        // далі індуктивність не встигає
            .ratedCurrentA = 1.5,
            .phaseResistanceOhm = 1.6,
            .rotorInertiaKgm2 = 5.4e-6,
            .thermalResistanceCPerW = 6.0,
            .supplyV = 24.0,
            .holdCurrentFraction = 0.40,    // драйвер зрізає струм у спокої
            .stepResolutionDeg = 1.8 / 16.0
        },
        .gear = { .ratio = 1.0, .efficiency = 1.0, .backlashDeg = 0.0 }   // прямий привід
    },
    {
        .motor = {
            .name = "GM4108 + FOC, енкодер 14 біт",
            .family = Family::Brushless,
            .ratedTorqueNm = 0.18,
            .noLoadSpeedRpm = 2000.0,
            .cornerSpeedRpm = 800.0,
            .ratedCurrentA = 2.5,
            .phaseResistanceOhm = 6.0,
            .rotorInertiaKgm2 = 3.0e-5,
            .thermalResistanceCPerW = 8.0,
            .supplyV = 24.0,
            .holdCurrentFraction = 1.0,
            .stepResolutionDeg = 360.0 / 16384.0
        },
        .gear = { .ratio = 1.0, .efficiency = 1.0, .backlashDeg = 0.0 }
    },
    {
        // Паспорт шинного серво дано на ВИХІДНОМУ валу, тож зовнішньої передачі
        // немає, а k_t тут уже враховує внутрішній редуктор.
        .motor = {
            .name = "STS3215, шинний сервопривід",
            .family = Family::Servo,
            .ratedTorqueNm = 1.00,
            .noLoadSpeedRpm = 50.0,
            .cornerSpeedRpm = 0.0,
            .ratedCurrentA = 1.2,
            .phaseResistanceOhm = 3.0,
            .rotorInertiaKgm2 = 2.0e-6,
            .thermalResistanceCPerW = 20.0,
            .supplyV = 12.0,
            .holdCurrentFraction = 1.0,
            .stepResolutionDeg = 360.0 / 4096.0
        },
        .gear = { .ratio = 1.0, .efficiency = 1.0, .backlashDeg = 0.25 }  // люфт шестерень
    }
}};

constexpr std::array<Task, 2> kTasks{{
    {
        .label = "поворотна вісь дозатора",
        .loadTorqueNm = 0.35,
        .loadInertiaKgm2 = 5.0e-4,
        .targetSpeedRpm = 30.0,
        .accelTimeS = 0.10,
        .moveDuty = 0.30,
        .holdsUnderLoad = true,
        .positionToleranceDeg = 0.50,
        .ambientC = 25.0,
        .insulationLimitC = 105.0,
        .powerBudgetW = 12.0
    },
    {
        .label = "привідне колесо мобільного робота",
        .loadTorqueNm = 0.80,
        .loadInertiaKgm2 = 2.0e-3,
        .targetSpeedRpm = 120.0,
        .accelTimeS = 0.30,
        .moveDuty = 0.80,
        .holdsUnderLoad = false,       // у паузі привід знеструмлений
        .positionToleranceDeg = 0.0,   // позиціонування не потрібне
        .ambientC = 40.0,
        .insulationLimitC = 105.0,
        .powerBudgetW = 30.0
    }
}};

void printReport(const Unit& unit, const Task& task) {
    const auto result = evaluate(unit, task);
    if (!result) {
        std::cout << std::format("  {}\n    ПАСПОРТ      {}\n\n",
                                 unit.motor.name, result.error().what);
        return;
    }

    const Report& r = *result;
    std::cout << std::format("  {} ({})\n", unit.motor.name, familyName(unit.motor.family));
    std::cout << std::format(
        "    вал мотора   {:.0f} об/хв · треба {:.4f} Н·м · є {:.4f} Н·м (запас {:.2f} при нормі {:.2f})\n",
        r.motorSpeedRpm, r.peakTorqueNm, r.availableTorqueNm, r.margin, r.requiredMargin);
    std::cout << std::format("    струм        пік {:.2f} А · пусковий {:.2f} А\n",
                             r.peakCurrentA, r.stallCurrentA);
    std::cout << std::format(
        "    тепло        рух {:.2f} Вт · пауза {:.2f} Вт · середнє {:.2f} Вт · редуктор {:.2f} Вт -> обмотка {:.0f} °C\n",
        r.heat.moveW, r.heat.holdW, r.heat.averageW, r.heat.gearW, r.heat.windingC);
    std::cout << std::format("    живлення     {:.1f} Вт\n", r.electricalPowerW);

    if (r.outputResolutionDeg) {
        std::cout << std::format("    позиція      дискрет із люфтом {:.3f}°\n",
                                 *r.outputResolutionDeg);
    } else {
        std::cout << "    позиція      давача немає\n";
    }

    if (r.fits()) {
        std::cout << "    ВЕРДИКТ      підходить\n";
    } else {
        std::cout << std::format("    ВЕРДИКТ      не підходить: {}\n", join(r.failures));
    }
    if (!r.warnings.empty()) {
        std::cout << std::format("    УВАГА        {}\n", join(r.warnings));
    }
    std::cout << '\n';
}

}  // namespace

int main() {
    int unsolved = 0;

    for (const Task& task : kTasks) {
        std::cout << std::format("=== Задача: {} ===\n", task.label);
        std::cout << std::format(
            "{:.2f} Н·м · {:.0f} об/хв за {:.2f} с · рух {:.0f}% часу · допуск {:.2f}° · середовище {:.0f} °C\n\n",
            task.loadTorqueNm, task.targetSpeedRpm, task.accelTimeS,
            task.moveDuty * 100.0, task.positionToleranceDeg, task.ambientC);

        for (const Unit& unit : kCandidates) {
            printReport(unit, task);
        }

        if (const auto best = bestFit(kCandidates, task)) {
            const auto report = evaluate(kCandidates[*best], task);
            std::cout << std::format("  ВИБІР: {} — найбільший запас моменту ({:.2f})\n\n",
                                     kCandidates[*best].motor.name, report->margin);
        } else {
            std::cout << "  ВИБІР: жоден кандидат не проходить — вимоги треба переглядати\n\n";
            ++unsolved;
        }
    }

    return unsolved == 0 ? 0 : 1;
}
