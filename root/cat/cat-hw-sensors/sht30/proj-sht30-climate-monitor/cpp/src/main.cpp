#include "i2c_bus.hpp"
#include "sht30.hpp"
#include "climate_monitor.hpp"

#include <iostream>
#include <iomanip>
#include <thread>
#include <chrono>

int main() {
    std::cout << "=== Система моніторингу мікроклімату SHT30 (I2C) ===" << std::endl;

    // Ініціалізація RAII-обгортки шини I2C
    sensors::I2CBus i2c_bus("/dev/i2c-1");
    if (!i2c_bus.is_open()) {
        std::cerr << "Помилка: не вдалося відкрити шину I2C!" << std::endl;
        return 1;
    }

    // Створення драйвера SHT30
    sensors::SHT30 sht30(i2c_bus, sensors::SHT30::Address::Default);

    // Програмне скидання давача перед запуском
    if (sht30.soft_reset()) {
        std::cout << "[ОК] Скидання (Soft Reset) SHT30 виконано." << std::endl;
    }

    // Модуль вищого рівня для аналізу мікроклімату (поріг конденсації 85%)
    sensors::ClimateMonitor monitor(sht30, 85.0f);

    constexpr int iterations = 3;
    for (int i = 1; i <= iterations; ++i) {
        std::cout << "\n--- Цикл опитування #" << i << " ---" << std::endl;

        sensors::ClimateStatus status = monitor.update();

        if (!status.crc_ok) {
            std::cerr << "[Помилка] Невірний CRC-8! Зчитаний пакунок пошкоджено." << std::endl;
        } else {
            std::cout << std::fixed << std::setprecision(2);
            std::cout << "Температура:   " << status.temperature_c << " °C" << std::endl;
            std::cout << "Вологість:     " << status.humidity_percent << " %" << std::endl;
            std::cout << "Точка роси:    " << status.dew_point_c << " °C" << std::endl;

            if (status.condensation_risk) {
                std::cout << "[УВАГА] Виявлено ризик конденсації! Запуск сушки нагрівачем..." << std::endl;
                if (monitor.perform_decondensation_cycle(std::chrono::milliseconds(1000))) {
                    std::cout << "[ОК] Сушку завершено успішно." << std::endl;
                }
            } else {
                std::cout << "[Інфо] Стан довкілля стабільний." << std::endl;
            }
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    // Переведення в енергоефективний режим сну
    std::cout << "\nЗавершення роботи. Переведення SHT30 в режим сну (Sleep)..." << std::endl;
    if (monitor.enter_sleep_mode()) {
        std::cout << "[ОК] Давач переведено в сон." << std::endl;
    }

    return 0;
}
