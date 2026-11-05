#include <iostream>
#include <iomanip>
#include <vector>
#include "tank_gauge.hpp"

int main() {
    std::cout << "=========================================================\n";
    std::cout << "  МОНІТОРИНГ ОБ'ЄМУ РЕЗЕРВУАРА НА БАЗІ УЛЬТРАЗВУКУ (C++)\n";
    std::cout << "=========================================================\n\n";

    TankMonitoring::TankConfig config;
    config.sensorHeightMm = 2000.0f;
    config.maxVolumeLiters = 1000.0f;
    config.calibrationTable = {
        {0.0f, 0.0f},
        {200.0f, 45.0f},
        {500.0f, 180.0f},
        {1000.0f, 500.0f},
        {1500.0f, 820.0f},
        {1800.0f, 955.0f},
        {2000.0f, 1000.0f}
    };

    TankMonitoring::TankGaugeController controller(config, 5);

    float ambientTemperature = 22.5f;
    std::vector<uint32_t> echoPulsesUs = {
        5800, 5810, 5795, 2500 /* сплеск від хвилі */, 5805, 5800, 9500 /* хибна луна */, 5798, 5802
    };

    std::cout << "Температура довкілля: " << ambientTemperature << " °C\n";
    std::cout << "Швидкість звуку: " << TankMonitoring::TankGaugeController::calculateSoundSpeed(ambientTemperature) << " м/с\n\n";

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Крок | ToF (мкс) | Сира дист. (мм) | Фільтр. дист. (мм) | Рівень (мм) | Об'єм (л) | Заповнення\n";
    std::cout << "----------------------------------------------------------------------------------------\n";

    for (size_t i = 0; i < echoPulsesUs.size(); ++i) {
        controller.update(echoPulsesUs[i], ambientTemperature);

        std::cout << " #" << std::setw(2) << (i + 1) << " | "
                  << std::setw(9) << echoPulsesUs[i] << " | "
                  << std::setw(15) << controller.getRawDistanceMm() << " | "
                  << std::setw(18) << controller.getFilteredDistanceMm() << " | "
                  << std::setw(11) << controller.getLiquidLevelMm() << " | "
                  << std::setw(9) << controller.getVolumeLiters() << " | "
                  << std::setw(9) << controller.getPercentage() << "%\n";
    }

    std::cout << "----------------------------------------------------------------------------------------\n";
    std::cout << "Система успішно нівелювала імпульсні викиди хвилювання резервуара.\n";
    return 0;
}
