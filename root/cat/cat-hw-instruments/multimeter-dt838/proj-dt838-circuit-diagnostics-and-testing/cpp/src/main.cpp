#include "dt838_processor.hpp"
#include <iostream>
#include <vector>
#include <iomanip>

int main() {
    std::cout << "=== Модуль обробки вимірювальних даних мультиметра DT-838 ===\n\n";

    dt838::AdcConvertor convertor;
    dt838::DiodeTester diodeTester;
    dt838::TemperatureEvaluator tempEvaluator(15.0, 75.0);

    // 1. Демонстрація конвертації вимірювань напруги та опору
    std::cout << "--- 1. Перетворення вимірювальних режимів (АЦП ICL7106) ---\n";
    struct Sample {
        int16_t adc;
        dt838::MeasurementMode mode;
    };

    std::vector<Sample> samples = {
        {1250, dt838::MeasurementMode::VoltageDC_20V},      // 12.50 В
        { 450, dt838::MeasurementMode::Resistance_200Ohm},   // 45.0 Ом
        {1999, dt838::MeasurementMode::VoltageDC_1000V},    // Зашкалювання (Overflow)
        { 580, dt838::MeasurementMode::DiodeTest}            // 580 мВ (діодний тест)
    };

    for (const auto& sample : samples) {
        auto result = convertor.processRawAdc(sample.adc, sample.mode);
        std::cout << "Відлік АЦП: " << std::setw(5) << sample.adc << " | ";
        if (result.overflow) {
            std::cout << "ПОМИЛКА: " << result.description << "\n";
        } else {
            std::cout << result.description << ": " 
                      << result.value << " " << result.unit << "\n";
        }
    }

    // 2. Демонстрація тестування напівпровідникових p-n переходів
    std::cout << "\n--- 2. Автоматична діагностика напівпровідників ---\n";
    std::vector<double> diodeVoltages = {45.0, 320.0, 650.0, 1850.0};

    for (double vDrop : diodeVoltages) {
        auto state = diodeTester.evaluateJunction(vDrop);
        std::cout << "Падіння напруги: " << std::setw(6) << vDrop << " мВ -> "
                  << dt838::DiodeTester::getStateDescription(state) << "\n";
    }

    // 3. Демонстрація контролю температури та допусків
    std::cout << "\n--- 3. Оцінка температури з термопари K-типу та перевірка допусків ---\n";
    double ambientTemp = 22.5;
    std::vector<double> tcVoltages = {0.82, 2.35, 3.10};

    for (double vTc : tcVoltages) {
        auto status = tempEvaluator.evaluate(vTc, ambientTemp);
        std::cout << "Сигнал термопари: " << vTc << " мВ | " << status.message << "\n";
    }

    std::cout << "\nОпрацювання вимірювальних даних DT-838 успішно завершено.\n";
    return 0;
}
