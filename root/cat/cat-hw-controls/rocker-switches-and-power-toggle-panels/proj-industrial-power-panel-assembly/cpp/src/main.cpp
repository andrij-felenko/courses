#include "../include/power_panel_calculator.hpp"
#include <iostream>

int main() {
    std::cout << "=== C++ СИМУЛЯТОР СИЛОВИХ РОКЕРНИХ ПАНЕЛЕЙ КОМУТАЦІЇ ===\n\n";

    using namespace PowerPanel;

    // Сценарій 1: Номінальний режим роботи рокерної панелі (230V AC, 10A, 1.5 мм²)
    std::cout << ">>> СЦЕНАРІЙ 1: Стандартна промислова мережа 230V AC <<<\n";
    PowerCircuitConfig config1{
        .voltageV = 230.0,
        .currentA = 10.0,
        .wireLengthM = 15.0,
        .wireSectionMm2 = 1.5,
        .wireResistivityOhmMm2M = COPPER_RESISTIVITY,
        .switchContactResistanceMohm = 15.0,
        .switchThermalResistanceCw = 16.0,
        .ambientTempC = 30.0,
        .maxAllowedTempC = 85.0,
        .maxAllowedVoltageDropPercent = 3.0
    };

    PowerPanelCalculator calc1(config1);
    CalculationResult res1 = calc1.analyze();
    calc1.printReport(res1);

    if (res1.isOverallSafe) {
        std::cout << "ВИСНОВОК: Сценарій 1 цілком безпечний для експлуатації.\n\n";
    } else {
        std::cout << "УВАГА: Сценарій 1 містить небезпечні параметри!\n\n";
    }

    // Сценарій 2: Низьковольтне силове коло 12V DC (Високий струм 25A, зношені контакти 40 мОм)
    std::cout << ">>> СЦЕНАРІЙ 2: Низьковольтне коло 12V DC з високим навантаженням <<<\n";
    PowerCircuitConfig config2{
        .voltageV = 12.0,
        .currentA = 25.0,
        .wireLengthM = 6.0,
        .wireSectionMm2 = 2.5,
        .wireResistivityOhmMm2M = COPPER_RESISTIVITY,
        .switchContactResistanceMohm = 40.0, // Зношені контакти
        .switchThermalResistanceCw = 22.0,
        .ambientTempC = 35.0,
        .maxAllowedTempC = 85.0,
        .maxAllowedVoltageDropPercent = 5.0
    };

    PowerPanelCalculator calc2(config2);
    CalculationResult res2 = calc2.analyze();
    calc2.printReport(res2);

    if (!res2.isOverallSafe) {
        std::cout << "УВАГА: Сценарій 2 НЕБЕЗПЕЧНИЙ! Необхідна корекція параметрів:\n";
        if (!res2.isThermalSafe) {
            std::cout << " - Перегрів рокера! Замініть перемикач на екземпляр із меншим перехідним опором.\n";
        }
        if (!res2.isVoltageDropSafe || !res2.isCurrentDensitySafe) {
            std::cout << " - Збільшіть переріз кабелю з " << config2.wireSectionMm2 
                      << " мм² до " << res2.recommendedSectionMm2 << " мм².\n";
        }
        std::cout << "\n";
    }

    return 0;
}
