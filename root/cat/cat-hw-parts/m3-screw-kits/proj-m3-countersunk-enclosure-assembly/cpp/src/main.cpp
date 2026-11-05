#include "EnclosureJointCalculator.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=== Запуск верифікації з'єднання кришки та гвинтів М3 DIN 7991 ==-\n\n";

    EnclosureJointCalculator calculator;

    // Приклад 1: Алюміній 6061-T6, товщина пластини 4.0 мм, гвинт класу 10.9
    {
        std::cout << "--- Варіант 1: Алюміній 6061, товщина 4.0 мм, клас 10.9 ---\n";
        auto report = calculator.calculate(4.0, MaterialType::Aluminum6061, FastenerGrade::Grade10_9);
        calculator.printReport(report);
    }

    std::cout << "\n";

    // Приклад 2: Нержавіюча сталь, товщина пластини 3.0 мм, гвинт A2-70
    {
        std::cout << "--- Варіант 2: Сталь, товщина 3.0 мм, клас A2-70 ---\n";
        auto report = calculator.calculate(3.0, MaterialType::Steel, FastenerGrade::A2_70);
        calculator.printReport(report);
    }

    std::cout << "\n";

    // Приклад 3: Термопластик (ABS/PC), товщина 5.0 мм, гвинт A2-70
    {
        std::cout << "--- Варіант 3: Термопластик, товщина 5.0 мм, клас A2-70 ---\n";
        auto report = calculator.calculate(5.0, MaterialType::Thermoplastic, FastenerGrade::A2_70);
        calculator.printReport(report);
    }

    return 0;
}
