#include "ApcLaserController.hpp"
#include <iostream>
#include <iomanip>

void printMetrics(const laser::ApcMetrics& metrics) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "  [СТАН]: " << (metrics.isLaserEnabled ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n";
    std::cout << "  Струм накачки: " << metrics.currentPumpmA << " мА\n";
    std::cout << "  Оптична потужність: " << metrics.opticalPowerMW << " мВт\n";
    std::cout << "  Струм фотодіода (APC): " << metrics.mpdCurrentuA << " мкА\n";
    std::cout << "  Температура: " << metrics.temperatureCelsius << " °C\n";
    std::cout << "  Стабільність випромінювання: " << metrics.powerStabilityPercent << " %\n";
    std::cout << "  Аварійні статуси: " << laser::faultReasonToString(metrics.lastFault) << "\n";
    std::cout << "----------------------------------------\n";
}

int main() {
    std::cout << "=== Система керування драйвером лазерного діода (APC) ===\n\n";

    // 1. Конфігурація параметрів лазерного діода та температурного захисту
    laser::CurrentConfig currentCfg;
    currentCfg.maxPumpCurrentmA = 140.0f;
    currentCfg.thresholdCurrentmA = 20.0f;
    currentCfg.targetPowerMW = 10.0f;
    currentCfg.slopeEfficiency = 0.45f;
    currentCfg.mpdResponsivity = 0.25f;

    laser::ThermalConfig thermalCfg;
    thermalCfg.minTempCelsius = 15.0f;
    thermalCfg.maxTempCelsius = 45.0f;
    thermalCfg.criticalTempCelsius = 55.0f;

    // 2. Створення екземпляра контролера
    laser::ApcLaserController controller(currentCfg, thermalCfg);

    // 3. Ініціалізація та перевірка початкового стану
    std::cout << "1. Ініціалізація драйвера лазера...\n";
    controller.updateTemperatureSensor(25.0f); // Нормальна початкова температура

    if (!controller.initialize()) {
        std::cerr << "Помилка ініціалізації контролера!\n";
        return 1;
    }
    std::cout << "Ініціалізація успішна.\n\n";

    // 4. Плавний запуск випромінювання (Soft-Start)
    std::cout << "2. Виконання плавності запуску (Soft-Start)...\n";
    if (controller.enableLaser()) {
        std::cout << "Лазер успішно виведено на робочий режим.\n";
    } else {
        std::cerr << "Помилка плавного запуску лазера!\n";
        return 1;
    }

    printMetrics(controller.getMetrics());

    // 5. Симуляція циклу регулювання APC у штатному режимі
    std::cout << "3. Симуляція роботи аналогового контуру APC...\n";
    for (int step = 1; step <= 5; ++step) {
        // Симуляція відгуку фотодіода на випромінювання з невеликим шумом
        auto currentMetrics = controller.getMetrics();
        float simulatedMpd = (currentMetrics.opticalPowerMW + (step % 2 == 0 ? 0.05f : -0.05f)) * currentCfg.mpdResponsivity;

        controller.updatePhotodiodeSensor(simulatedMpd);
        controller.processControlLoop(0.1f); // Kрок 100 мс

        std::cout << "Ітерація APC #" << step << ":\n";
        printMetrics(controller.getMetrics());
    }

    // 6. Симуляція аварійної ситуації (Тепловий перегрів)
    std::cout << "4. Симуляція перегріву корпусу (вивід за межі T_max)...\n";
    controller.updateTemperatureSensor(48.0f); // Температура перевищує maxTempCelsius (45 °C)
    controller.processControlLoop(0.1f);

    std::cout << "Реакція захисту на перегрів:\n";
    printMetrics(controller.getMetrics());

    // 7. Відновлення системи після переохолодження та скидання помилки
    std::cout << "5. Нормалізація температури та скидання аварії...\n";
    controller.updateTemperatureSensor(25.0f);
    controller.clearFault();
    controller.initialize();
    controller.enableLaser();

    // 8. Симуляція деградації кристала / загрози COD (раптове зникнення сигналу з моніторного фотодіода при високому струмі)
    std::cout << "6. Тестування апаратного захисту від COD (втрата зворотного зв'язку APC)...\n";
    controller.updatePhotodiodeSensor(0.00f); // Оптичний потік раптово впав у нуль при робочому струмі
    controller.processControlLoop(0.1f);

    std::cout << "Реакція апаратного захисту на загрозу COD:\n";
    printMetrics(controller.getMetrics());

    std::cout << "Демонстрацію роботи драйвера APC завершено.\n";
    return 0;
}
