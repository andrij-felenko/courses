#include <iostream>
#include "BatteryMonitor.h"

int main() {
    std::cout << "=== Тестування супервізора MT3608 на C++ ===\n";

    // EN пін 2, ADC пін A0, дільник 100k / 20k, Vref = 1.1V, Cutoff = 3.0V, Recovery = 3.3V
    BatteryMonitor batteryGuard(2, 0, 100000.0f, 20000.0f, 1.1f, 1023.0f, 3.0f, 3.3f, 0.3f);

    batteryGuard.onStateChange([](BatteryState state, float voltage) {
        std::string_view stateStr = "Номінальний";
        if (state == BatteryState::LowWarning) stateStr = "УВАГА: Низький заряд";
        if (state == BatteryState::CriticalCutoff) stateStr = "КРИТИЧНИЙ: Відсічка живлення";
        std::cout << "[СПОСТЕРІГАЧ] Новий статус: " << stateStr 
                  << " (Напруга: " << voltage << " В)\n";
    });

    batteryGuard.begin();

    // 1. Повний заряд акумулятора (4.15 В) -> сирий АЦП ~ 643
    std::cout << "\n>>> Режим 1: Робота від повністю зарядженого акумулятора 18650 <<<\n";
    for (int i = 0; i < 5; ++i) {
        batteryGuard.update(643);
    }
    std::cout << "Поточна напруга: " << batteryGuard.getVoltage() << " В\n";

    // 2. Глибокий розряд під навантаженням до 2.90 В -> сирий АЦП ~ 449
    std::cout << "\n>>> Режим 2: Глибокий розряд акумулятора (падіння напруги) <<<\n";
    for (int i = 0; i < 8; ++i) {
        batteryGuard.update(449);
    }
    std::cout << "Поточна напруга: " << batteryGuard.getVoltage() 
              << " В, стан підвищувача: " << (batteryGuard.isBoostActive() ? "ON" : "OFF") << "\n";

    // 3. Відскок напруги після відключення навантаження до 3.15 В -> сирий АЦП ~ 488
    std::cout << "\n>>> Режим 3: Відскок напруги без навантаження (3.15 В < 3.30 В) <<<\n";
    for (int i = 0; i < 5; ++i) {
        batteryGuard.update(488);
    }
    std::cout << "Поточна напруга: " << batteryGuard.getVoltage() 
              << " В, стан підвищувача: " << (batteryGuard.isBoostActive() ? "ON" : "OFF") 
              << " (захист утримує відсічку завдяки гістерезису)\n";

    // 4. Підключення зарядки TP4056 (підйом до 3.7 В) -> сирий АЦП ~ 573
    std::cout << "\n>>> Режим 4: Підключення зарядного пристрою <<<\n";
    for (int i = 0; i < 8; ++i) {
        batteryGuard.update(573);
    }
    std::cout << "Поточна напруга: " << batteryGuard.getVoltage() 
              << " В, стан підвищувача: " << (batteryGuard.isBoostActive() ? "ON" : "OFF") << "\n";

    std::cout << "\n=== Тест завершено успішно ===\n";
    return 0;
}
