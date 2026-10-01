#include "swd_interface.hpp"
#include "daplink_programmer.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=== Архітектура програматора DAPLink та захист SWD від фантомного живлення ===\n\n";

    // 1. Створення підсистем низькорівневого SWD та PowerGuard
    daplink::SwdInterface swd;
    daplink::PowerGuard powerGuard(swd);

    // 2. Створення об'єкта програматора DAPLink
    daplink::DapLinkProgrammer programmer(swd, powerGuard);

    // 3. Первинна ініціалізація системи (перевірка High-Z стану)
    std::cout << "1. Ініціалізація програматора DAPLink...\n";
    programmer.initialize();
    std::cout << "Поточний стан: " << daplink::programmerStateToString(programmer.getState()) << "\n\n";

    // 4. Моделювання підключення цільової плати (V_TARGET = 3.3 В)
    std::cout << "2. Подача живлення на цільову плату (V_TARGET = 3.3 В)...\n";
    programmer.updatePowerState(3.3f);

    std::cout << "\n3. Встановлення підключення SWD з MCU...\n";
    if (programmer.connectTarget()) {
        std::cout << "Підключення успішне!\n";
        if (auto targetOpt = programmer.getTargetInfo(); targetOpt.has_value()) {
            const auto& target = *targetOpt;
            std::cout << "  IDCODE: 0x" << std::hex << std::uppercase << target.idcode << std::dec << "\n";
            std::cout << "  Designer ID: 0x" << std::hex << target.designerID << std::dec << " (ARM)\n";
            std::cout << "  Part Number: 0x" << std::hex << target.partNumber << std::dec << " (Cortex-M4)\n";
            std::cout << "  Revision: " << static_cast<int>(target.revision) << "\n";
        }
    } else {
        std::cerr << "Помилка підключення до цільової плати!\n";
        return 1;
    }

    std::cout << "\n4. Запуск сесії зневадження (Debug Session)...\n";
    if (programmer.startDebugSession()) {
        std::cout << "Сесію зневадження активовано.\n";
    }

    // 5. Виконання відлагоджувальних операцій (читання/запис регістрів Core Debug)
    std::cout << "\n5. Читання регістрів зневадження MCU через SWD...\n";
    auto dhcsr = programmer.readRegister(0xE000EDF0);
    if (dhcsr) {
        std::cout << "  Значення DHCSR: 0x" << std::hex << std::uppercase << *dhcsr << std::dec << "\n";
    }

    std::cout << "\n6. Запис у регістр DEMCR (0xE000EDFC)...\n";
    programmer.writeRegister(0xE000EDFC, 0x01000000);

    // 6. Симуляція аварійного відключення живлення цільової плати (Фантомне живлення)
    std::cout << "\n7. СИМУЛЯЦІЯ АВАРІЇ: Несподіване зникнення живлення V_TARGET (падіння до 0.3 В)...\n";
    std::cout << "   (Без захисту струм з SWCLK/SWDIO жив би MCU через захисні діоди GPIO!)\n";
    programmer.updatePowerState(0.3f);

    std::cout << "\nПоточний стан після аварії: " << daplink::programmerStateToString(programmer.getState()) << "\n";

    // 7. Спроба виконання операцій у стані Error
    std::cout << "\n8. Спроба виконання читання у стані Error...\n";
    auto failedRead = programmer.readRegister(0xE000EDF0);
    if (!failedRead.has_value()) {
        std::cout << "  Операцію читання відхилено, обладнання захищено.\n";
    }

    // 8. Відновлення живлення та скидання помилки
    std::cout << "\n9. Відновлення V_TARGET (3.3 В) та скидання стану помилки...\n";
    programmer.updatePowerState(3.3f);
    programmer.clearError();

    // 9. Повторне підключення та штатне завершення
    std::cout << "\n10. Повторне штатне підключення та безпечне відключення...\n";
    programmer.connectTarget();
    programmer.disconnectTarget();

    std::cout << "\nОстаточний стан програматора: " << daplink::programmerStateToString(programmer.getState()) << "\n";
    std::cout << "Демонстрацію роботи DAPLink завершено успішно.\n";

    return 0;
}
