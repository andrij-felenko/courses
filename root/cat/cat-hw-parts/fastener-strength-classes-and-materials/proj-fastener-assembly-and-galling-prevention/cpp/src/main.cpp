#include <iostream>
#include <iomanip>
#include "FastenerCalculator.hpp"

/**
 * @file main.cpp
 * @brief Точка входу з демонстрацією обчислення параметрів кріплення для сталі 10.9, A4-70 із шаром Anti-Seize та титану Grade 5.
 */

void printFastenerAnalysis(const FastenerCalculator& calc, double clampedLengthMm) {
    std::cout << "========================================================\n";
    std::cout << " Матеріал кріплення: " << calc.getMaterialName() << "\n";
    std::cout << " Умови змащення:    " << calc.getLubricationName() << "\n";
    std::cout << " Геометрія різьби:  M" << std::fixed << std::setprecision(1) << calc.getNominalDiameter() 
              << " x " << calc.getPitch() << " мм\n";
    std::cout << "--------------------------------------------------------\n";
    
    double As = calc.calculateStressArea();
    double Fp = calc.calculatePreload(0.75);
    double T = calc.calculateTighteningTorque();
    double elongation = calc.calculateElongation(clampedLengthMm);
    
    std::cout << std::setprecision(2);
    std::cout << " Розрахункова площа перерізу (As): " << As << " мм²\n";
    std::cout << " Зусилля попереднього натягу (Fp): " << (Fp / 1000.0) << " кН (за 75% плинності)\n";
    std::cout << " Необхідний момент затягування (T): " << T << " Н·м\n";
    std::cout << " Пружне подовження на довжині " << clampedLengthMm << " мм: " << std::setprecision(4) << elongation << " мм\n";
    std::cout << " Аналіз ризику задирання:          " << calc.assessGallingRisk() << "\n";
    std::cout << "========================================================\n\n";
}

int main() {
    std::cout << "=== Демонстрація інженерного калькулятора нарізних з'єднань ===\n\n";

    try {
        // 1. Високоміцна легована сталь 10.9 (болт M12x1.75 з легким мастилом)
        FastenerCalculator boltSteel10_9(12.0, 1.75, MaterialGrade::Steel_10_9, LubricationCondition::LightlyOiled);
        printFastenerAnalysis(boltSteel10_9, 50.0);

        // 2. Кислотостійка нержавіюча сталь A4-70 із протизадирним шаром Anti-Seize (болт M10x1.5)
        FastenerCalculator boltStainlessA4(10.0, 1.5, MaterialGrade::Stainless_A4_70, LubricationCondition::AntiSeize);
        printFastenerAnalysis(boltStainlessA4, 40.0);

        // 3. Титановий сплав Grade 5 (Ti-6Al-4V) із захисним шаром Anti-Seize (болт M10x1.5)
        FastenerCalculator boltTitanium(10.0, 1.5, MaterialGrade::Titanium_Grade5, LubricationCondition::AntiSeize);
        printFastenerAnalysis(boltTitanium, 40.0);

        // 4. Демонстрація критичної небезпеки сухого тертя для титану Grade 5 (той самий болт без мастила)
        std::cout << "--- Демонстрація аварійного режиму: Титан Grade 5 на сухому терті ---\n";
        FastenerCalculator boltTitaniumDry(10.0, 1.5, MaterialGrade::Titanium_Grade5, LubricationCondition::Dry);
        printFastenerAnalysis(boltTitaniumDry, 40.0);

    } catch (const std::exception& e) {
        std::cerr << "Помилка обчислень: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
