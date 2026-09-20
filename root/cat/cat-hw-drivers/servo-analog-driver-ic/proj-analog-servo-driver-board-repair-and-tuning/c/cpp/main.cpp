#include "ServoTester.hpp"
#include <iostream>
#include <iomanip>

namespace {

void delayMs(std::uint32_t ms) {
    (void)ms;
}

} // namespace

int main() {
    std::cout << "=== Тестування аналогових серводрайверів AA5188 / KC0032 (C++) ===\n";

    // Екземпляр тестера з тактовою частотою 72 МГц (наприклад, STM32F103)
    ServoControl::ServoTester tester(72000000U);

    if (!tester.init()) {
        std::cerr << "Не вдалося ініціалізувати таймер!\n";
        return 1;
    }

    const auto& regs = tester.timerRegisters();
    std::cout << "Таймер настроєно: Prescaler=" << regs.PSC
              << ", ARR=" << regs.ARR << " (Частота кадру: 50 Гц)\n";

    tester.start();
    std::cout << "ШІМ-сигнал активовано.\n\n";

    // 1. Калібрування центрального положення
    std::cout << "--- 1. Калібрування нейтралі (1500 мкс / 90.0 deg) ---\n";
    tester.calibrateNeutral();
    std::cout << "Поточний імпульс: " << tester.pulseWidthUs() << " мкс, "
              << "Кут: " << std::fixed << std::setprecision(1) << tester.angleDeg() << " deg\n";
    delayMs(1000);

    // 2. Сканування позицій з кроком 45 градусів
    std::cout << "\n--- 2. Перевірка кутових позицій (0 -> 45 -> 90 -> 135 -> 180 deg) ---\n";
    const float testAngles[] = {0.0f, 45.0f, 90.0f, 135.0f, 180.0f};
    for (float angle : testAngles) {
        tester.setAngleDeg(angle);
        std::cout << "Задано кут: " << std::setw(5) << angle << " deg | "
                  << "CCR1 імпульс: " << tester.pulseWidthUs() << " мкс | "
                  << "Зчитаний кут: " << tester.angleDeg() << " deg\n";
        delayMs(250);
    }

    // 3. Перевірка коректності при виході за допустимі межі
    std::cout << "\n--- 3. Перевірка валідації діапазонів (Safety Clamping) ---\n";
    std::cout << "Встановлення кута -20.0 deg...\n";
    tester.setAngleDeg(-20.0f);
    std::cout << "Результат: імпульс " << tester.pulseWidthUs() << " мкс (кут " << tester.angleDeg() << " deg)\n";

    std::cout << "Встановлення кута 220.0 deg...\n";
    tester.setAngleDeg(220.0f);
    std::cout << "Результат: імпульс " << tester.pulseWidthUs() << " мкс (кут " << tester.angleDeg() << " deg)\n";

    // 4. Завершення випробування
    tester.stop();
    std::cout << "\nШІМ вимкнено. Випробування серводрайверів AA5188 / KC0032 завершено.\n";

    return 0;
}
