#include "pyrometer.hpp"
#include <iostream>
#include <iomanip>
#include <vector>

// Допоміжна функція для виведення текстового опису статусу
std::string statusToString(pyrometer::ThermalStatus status) {
    switch (status) {
        case pyrometer::ThermalStatus::Safe:
            return "НОРМА (Safe)";
        case pyrometer::ThermalStatus::Warning:
            return "УВАГА (Warning - наближення до межі)";
        case pyrometer::ThermalStatus::CriticalOverheat:
            return "КРИТИЧНИЙ ПЕРЕГРІВ (Critical Overheat!)";
        case pyrometer::ThermalStatus::InvalidReading:
            return "ПОХИБКА ВИМІРЮВАННЯ (Invalid Reading)";
    }
    return "НЕВІДОМО";
}

int main() {
    std::cout << "=========================================================\n";
    std::cout << "  МОДУЛЬ ОБРОБКИ ДАНИХ ІЧ-ПІРОМЕТРА MESTEK IR01B (C++)\n";
    std::cout << "=========================================================\n\n";

    pyrometer::PyrometerSensor sensor;
    pyrometer::ThermalToleranceEvaluator evaluator(15.0); // Попередження при запасі < 15 °C

    const double backgroundTempC = 23.5;

    struct MeasurementScenario {
        std::string componentName;
        double emissivity;
        double sensorVoltageVolt;
        double maxTempC;
    };

    std::vector<MeasurementScenario> scenarios = {
        {"Силовий MOSFET транзистор (пластиковий корпус)", 0.95, 3.42e-7, 125.0},
        {"Випрямляльний діод Шотткі (пластик TO-220)",      0.95, 2.95e-7, 110.0},
        {"Анодований алюмінієвий радіатор",                 0.82, 1.85e-7,  85.0},
        {"Оголена мідна доріжка силової плати",             0.05, 1.10e-8, 105.0},
        {"Силовий індуктивний дросель",                     0.92, 4.15e-7, 100.0}
    };

    std::cout << std::fixed << std::setprecision(2);

    for (const auto& item : scenarios) {
        std::cout << "---------------------------------------------------------\n";
        std::cout << "Об'єкт вимірювання: " << item.componentName << "\n";
        
        if (!sensor.setEmissivity(item.emissivity)) {
            std::cout << " [ПОМИЛКА] Некоректне значення емісивності: " << item.emissivity << "\n";
            continue;
        }

        std::cout << "Налаштована емісивність (ε): " << sensor.getEmissivity() << "\n";
        std::cout << "Вхідна напруга сенсора:      " << item.sensorVoltageVolt * 1e6 << " мкВ\n";

        auto tempOpt = sensor.calculateTargetTemperature(item.sensorVoltageVolt, backgroundTempC);

        if (!tempOpt.has_value()) {
            std::cout << " [ПОМИЛКА] Не вдалося обчислити температуру (вихід за межі діапазону)\n";
            continue;
        }

        const double measuredTemp = tempOpt.value();
        auto eval = evaluator.evaluate(item.componentName, measuredTemp, item.maxTempC);

        std::cout << "Розрахована температура:     " << measuredTemp << " °C\n";
        std::cout << "Максимальна припустима T:    " << eval.maxAllowedTempCelsius << " °C\n";
        std::cout << "Температурний запас:         " << eval.thermalMarginCelsius << " °C\n";
        std::cout << "Статус безпеки:              " << statusToString(eval.status) << "\n";
    }

    std::cout << "=========================================================\n";
    return 0;
}
