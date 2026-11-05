#include <iostream>
#include <iomanip>
#include "iec60751.hpp"

using namespace iec60751;

int main() {
    // Створюємо конвертер для Pt100 з діапазоном від -50 до 200 градусів та кроком 1 градус
    // Таблиця LUT генерується повністю під час компіляції, не витрачаючи час у runtime
    constexpr IEC60751Convert<100, -50, 200, 1> pt100Converter;

    std::cout << "--- Демонстрація розрахунку температури за стандартом IEC 60751 ---\n\n";

    // Тестуємо кілька значень опору
    double testResistances[] = { 80.31, 100.0, 138.51, 175.86 }; 

    std::cout << std::fixed << std::setprecision(3);
    for (double r : testResistances) {
        double tempLut = pt100Converter.temperatureFromResistance(r);
        std::cout << "Опір: " << std::setw(7) << r << " Ом -> Температура (LUT інтерполяція): " 
                  << std::setw(7) << tempLut << " °C\n";
    }

    std::cout << "\n--- Аналіз похибки (Клас A) ---\n";
    ToleranceClass sensorClass = ToleranceClass::A;
    double currentTemp = 100.0;
    
    // Розрахуємо допуск для 100 градусів
    double sensorTol = getToleranceCelsius(sensorClass, currentTemp);
    std::cout << "Допуск датчика класу A при " << currentTemp << " °C: +/- " << sensorTol << " °C\n";

    // Складаємо бюджет похибок для вимірювального каналу
    ErrorBudget budget = {
        .sensorErrorC = sensorTol,
        .adcErrorC = 0.05,       // Приклад: шум АЦП і похибка квантування дають 0.05 C
        .wireErrorC = 0.02,      // Для 3- або 4-провідної схеми похибка дротів мінімальна
        .selfHeatingC = 0.01     // При невеликому струмі вимірювання (наприклад, 1 мА) нагрів мінімальний
    };

    std::cout << "Комбінована похибка вимірювального каналу: +/- " 
              << budget.combinedError() << " °C\n";

    return 0;
}
