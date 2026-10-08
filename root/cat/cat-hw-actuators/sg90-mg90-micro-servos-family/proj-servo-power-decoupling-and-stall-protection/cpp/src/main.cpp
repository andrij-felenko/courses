#include "towerpro_servo.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=========================================================\n";
    std::cout << "  Демонстрація керування Tower Pro MG90S із АЦП-моніторингом\n";
    std::cout << "=========================================================\n\n";

    towerpro::TowerProServo servo;

    towerpro::ServoConfig config;
    config.model = towerpro::ServoModel::MG90S;
    config.pwmPin = 9;
    
    // Налаштування струмового датчика (50 мОм шунт, підсилення 20x, АЦП 12-біт, Vref=3.3V)
    config.adcConfig.adcPin = 34;
    config.adcConfig.referenceVoltageV = 3.3f;
    config.adcConfig.adcResolution = 4096;
    config.adcConfig.shuntResistanceOhm = 0.05f;
    config.adcConfig.ampGain = 20.0f;
    config.adcConfig.sampleIntervalUs = 1000; // 1 мс

    if (!servo.begin(config)) {
        std::cerr << "Помилка ініціалізації сервоприводу та АЦП!\n";
        return 1;
    }

    const auto& profile = servo.getActiveProfile();
    std::cout << "Модель сервоприводу    : " << profile.modelName << "\n";
    std::cout << "Діапазон ШІМ-імпульсів : " << profile.minPulseUs << " - " << profile.maxPulseUs << " мкс\n";
    std::cout << "Поріг струму заклинення: " << profile.stallCurrentThresholdmA << " мА\n";
    std::cout << "Ліміт часу заклинення  : " << profile.stallTimeoutMs << " мс\n";
    std::cout << "Редуктор               : " << (profile.isMetalGear ? "Металевий" : "Пластиковий") << "\n\n";

    // Реєстрація лямбда-функції обробки аварійного зупину (Emergency Stop Callback)
    servo.setEmergencyCallback([](towerpro::ServoModel model, float currentmA, uint32_t overloadDurationMs) {
        std::cout << "\n---------------------------------------------------------\n";
        std::cout << " [АВАРИЙНИЙ СТОП!] Спрацював струмовий захист!\n";
        std::cout << " Струм споживання : " << std::fixed << std::setprecision(1) << currentmA << " мА\n";
        std::cout << " Тривалість затору: " << overloadDurationMs << " мс\n";
        std::cout << " Дії: ШІМ знято, привід знеструмлено для збереження редуктора.\n";
        std::cout << "---------------------------------------------------------\n\n";
    });

    uint32_t currentTimeMs = 0;
    uint32_t currentTimeUs = 0;

    // 1. Нормальний режим руху
    std::cout << "--- 1. Нормальна робота без механічних перешкод ---\n";
    float targetAngles[] = {0.0f, 45.0f, 90.0f, 135.0f, 180.0f};

    for (float angle : targetAngles) {
        servo.setAngle(angle);
        
        // Симуляція нормального струму під час руху (~200 мА -> rawAdc = 250)
        servo.setSimulatedAdcRaw(250);

        for (int i = 0; i < 20; ++i) {
            currentTimeMs += 10;
            currentTimeUs += 10000;
            servo.update(currentTimeMs, currentTimeUs);
        }

        std::cout << "Кут: " << std::setw(5) << servo.getAngle() << " deg | "
                  << "ШІМ: " << servo.readMicroseconds() << " us | "
                  << "Струм: " << std::fixed << std::setprecision(1) << servo.getCurrentmA() << " мА | "
                  << "ШІМ активний: " << (servo.isAttached() ? "ТАК" : "НІ") << "\n";
    }

    // 2. Симуляція механічного заклинювання (Stall Condition)
    std::cout << "\n--- 2. Імітація механічного заклинювання редуктора (Stall) ---\n";
    servo.setAngle(180.0f);
    
    // Симуляція струму заклинювання (~967 мА -> rawAdc = 1200, перевищує 750 мА)
    servo.setSimulatedAdcRaw(1200);

    for (int step = 0; step <= 12; ++step) {
        currentTimeMs += 50;
        currentTimeUs += 50000;
        
        servo.update(currentTimeMs, currentTimeUs);

        std::cout << "Час: " << std::setw(4) << currentTimeMs << " ms | "
                  << "Струм: " << std::fixed << std::setprecision(1) << std::setw(6) << servo.getCurrentmA() << " мА | "
                  << "Перевантаження: " << (servo.isOverloaded() ? "ТАК" : "НІ ") << " | "
                  << "Аварія: " << (servo.isEmergencyStopped() ? "ТАК" : "НІ ") << "\n";
    }

    // 3. Спроба подачі нових команд під час аварійного стану
    std::cout << "\n--- 3. Перевірка блокування команд у режимі Emergency Stop ---\n";
    std::cout << "Спроба встановити кут 0 deg...\n";
    servo.setAngle(0.0f);
    std::cout << "Поточний кут у системі: " << servo.getAngle() << " deg (команда відхилена)\n";

    // 4. Скидання аварії та повернення до штатного режиму
    std::cout << "\n--- 4. Усунення перешкоди та скидання аварійного стану ---\n";
    servo.setSimulatedAdcRaw(250); // Струм повернувся до норми
    servo.resetEmergency();
    std::cout << "Стан аварії скинуто. ШІМ відновлено: " << (servo.isAttached() ? "ТАК" : "НІ") << "\n";
    
    servo.setAngle(45.0f);
    std::cout << "Новий кут встановлено: " << servo.getAngle() << " deg | ШІМ: " << servo.readMicroseconds() << " us\n";

    std::cout << "\nТестування успішно завершено.\n";
    return 0;
}
