#include <iostream>
#include "servo_tester.hpp"

int main() {
    hw::ServoTester tester;
    tester.init();

    std::cout << "=== Сервотестер та калібратор ESC (C++17) ===\n";
    std::cout << "Початковий режим: Neutral (1500 мкс)\n";

    uint32_t mockSystemMs = 0;
    constexpr uint16_t mockAdcPot = 3000; // Положення ручки потенціометра

    for (int i = 0; i < 20; ++i) {
        mockSystemMs += 10;

        // Симуляція натискання кнопки перемикання режимів
        const bool btnPressed = (mockSystemMs >= 40 && mockSystemMs <= 60);
        tester.handleButton(btnPressed, mockSystemMs);

        if (tester.getMode() == hw::Mode::Manual) {
            tester.updateManual(mockAdcPot);
        } else if (tester.getMode() == hw::Mode::AutoSweep) {
            tester.updateSweep(mockSystemMs);
        }

        tester.updateEscCalibration(mockSystemMs);

        std::cout << "[" << mockSystemMs << " мс] Режим: "
                  << static_cast<int>(tester.getMode())
                  << " | Тривалість імпульсу ШІМ: " << tester.getPulseUs() << " мкс\n";
    }

    return 0;
}
