#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <cstdlib>
#include "liquid_level_controller.hpp"

// Симуляція стану апаратного середовища мікроконтролера
namespace MockHardware {
    static bool pinAState = false;
    static bool pinBState = false;
    static bool relayPinState = false;
    static float simulatedLiquidLevel = 15.0f; // Початковий рівень рідини у резервуарі (15%)

    void digitalWrite(uint8_t pin, bool state) {
        if (pin == 2) pinAState = state;
        else if (pin == 3) pinBState = state;
        else if (pin == 8) relayPinState = state;
    }

    uint16_t analogRead(uint8_t pin) {
        (void)pin;
        // Симуляція завад поверхні (шум ±2%)
        float noise = (std::rand() % 400 - 200) / 100.0f;
        float noisyLevel = simulatedLiquidLevel + noise;
        if (noisyLevel < 0.0f) noisyLevel = 0.0f;
        if (noisyLevel > 100.0f) noisyLevel = 100.0f;

        // Перетворення відсотків у 10-бітне значення ADC (0..1023)
        return static_cast<uint16_t>((noisyLevel / 100.0f) * 1023.0f);
    }

    void delayMicroseconds(uint16_t microseconds) {
        // У реальному МК тут викликається апаратна затримка delayMicroseconds(us)
        (void)microseconds;
    }
}

int main() {
    std::cout << "=========================================================\n";
    std::cout << "  СИСТЕМА КОНТРОЛЮ РІВНЯ РІДИНИ МІКРОКОНТРОЛЕРА (C++)\n";
    std::cout << "=========================================================\n\n";

    // Налаштування конфігурації контролера
    ControllerConfig config;
    config.pinExcitationA = 2;       // Пін A збудження
    config.pinExcitationB = 3;       // Пін B збудження
    config.pinAnalogRead = 0;        // Аналоговий вхід A0
    config.pinRelay = 8;             // Пін реле насоса
    config.thresholds.lowThreshold = 25.0f;   // Нижній поріг увімкнення насоса (25%)
    config.thresholds.highThreshold = 75.0f;  // Верхній поріг вимкнення насоса (75%)
    config.mode = ControlMode::Fill;          // Режим підкачування
    config.filterWindowSize = 5;              // Розмір вікна ковзного середнього
    config.pulseDelayUs = 150;                // Тривалість імпульсу 150 мкс
    config.activeLowRelay = true;             // Силове реле активне низьким рівнем

    // Ініціалізація екземпляра контролера із передачею апаратних функцій
    LiquidLevelController controller(
        config,
        MockHardware::digitalWrite,
        MockHardware::analogRead,
        MockHardware::delayMicroseconds
    );

    controller.begin();

    std::cout << "Конфігурація запущена:\n";
    std::cout << " - Режим: Наповнення (Fill)\n";
    std::cout << " - Поріг увімкнення (Low): " << config.thresholds.lowThreshold << "%\n";
    std::cout << " - Поріг вимкнення (High): " << config.thresholds.highThreshold << "%\n";
    std::cout << " - Захист від електролізу: Прямокутні імпульси полярності A/B (" << config.pulseDelayUs << " мкс)\n";
    std::cout << " - Фільтрація: Ковзне середнє, вікно = " << config.filterWindowSize << "\n\n";

    std::cout << std::setw(6) << "Крок" 
              << std::setw(18) << "Рівень (сирий, %)" 
              << std::setw(20) << "Рівень (фільтр, %)" 
              << std::setw(16) << "Стан реле" 
              << std::setw(20) << "Статус насоса" << "\n";
    std::cout << "-------------------------------------------------------------------------------\n";

    // Симуляція циклу роботи системи протягом 25 кроків
    for (int step = 1; step <= 25; ++step) {
        // Виконання одного циклу контролера
        float filteredLevel = controller.update();
        bool relayOn = controller.isRelayActive();

        // Імітація зміни рівня рідини залежно від стану насоса
        if (relayOn) {
            // Насос працює -> рівень зростає
            MockHardware::simulatedLiquidLevel += 4.5f;
        } else {
            // Насос вимкнений -> рідина споживається, рівень падає
            MockHardware::simulatedLiquidLevel -= 3.0f;
        }

        std::cout << std::setw(6) << step
                  << std::setw(17) << std::fixed << std::setprecision(1) << MockHardware::simulatedLiquidLevel << "%"
                  << std::setw(19) << std::fixed << std::setprecision(1) << filteredLevel << "%"
                  << std::setw(16) << (relayOn ? "АКТИВНЕ" : "ВИМКНЕНЕ")
                  << std::setw(20) << (relayOn ? "НАКАЧУВАННЯ..." : "ОЧІКУВАННЯ") << "\n";
    }

    std::cout << "\n=========================================================\n";
    std::cout << "Симуляцію успішно завершено.\n";
    std::cout << "Захист електродів від електролізу виконано безперервно.\n";
    std::cout << "=========================================================\n";

    return 0;
}
