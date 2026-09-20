#include <iostream>
#include <iomanip>
#include "dip_config.hpp"

// Допоміжна функція для виводу масиву бітів
void printBinary(uint8_t byte) {
    std::cout << "0b";
    for (int i = 7; i >= 0; --i) {
        std::cout << ((byte >> i) & 1);
    }
}

// Допоміжна функція для текстового представлення швидкості
const char* baudRateToString(BaudRate baud) {
    switch (baud) {
        case BaudRate::Baud9600:   return "9600 baud";
        case BaudRate::Baud19200:  return "19200 baud";
        case BaudRate::Baud57600:  return "57600 baud";
        case BaudRate::Baud115200: return "115200 baud";
        default:                   return "Невідома";
    }
}

// Допоміжна функція для текстового представлення режиму
const char* modeToString(OperatingMode mode) {
    switch (mode) {
        case OperatingMode::Normal:      return "Normal (Робочий)";
        case OperatingMode::Diagnostic:  return "Diagnostic (Діагностика)";
        case OperatingMode::Calibration: return "Calibration (Калібрування)";
        case OperatingMode::Reserved:    return "Reserved (Зарезервовано / Помилка)";
        default:                         return "Невідомий";
    }
}

void testConfiguration(uint8_t rawByte, const char* testName) {
    std::cout << "=================================================\n";
    std::cout << "Тест: " << testName << "\n";
    std::cout << "Сирий конфігураційний байт: ";
    printBinary(rawByte);
    std::cout << " (0x" << std::hex << std::uppercase << (int)rawByte << std::dec << ")\n";

    DipConfig config(rawByte);
    ConfigSettings settings{};

    bool success = config.parse(settings);

    std::cout << "Результат валідації паритету: " 
              << (config.isParityValid() ? "УСПІХ (Parity OK)" : "ПОМИЛКА (Parity Mismatch)") << "\n";

    if (success) {
        std::cout << "-> Драйвер успішно зчитав конфігурацію:\n";
        std::cout << "   - Адреса пристрою: " << (int)settings.deviceAddress << "\n";
        std::cout << "   - Швидкість шини:  " << baudRateToString(settings.baudRate) << "\n";
        std::cout << "   - Режим роботи:    " << modeToString(settings.mode) << "\n";
    } else {
        std::cout << "-> ПОМИЛКА: Апаратна конфігурація некоректна або спотворена!\n";
        if (!settings.parityValid) {
            std::cout << "   Причина: Незбіг біта парності (можливе окиснення контактів DIP-перемикача).\n";
        } else if (settings.mode == OperatingMode::Reserved) {
            std::cout << "   Причина: Вибрано зарезервовану комбінацію важелів (OperatingMode::Reserved).\n";
        }
    }
    std::cout << "\n";
}

int main() {
    std::cout << "=== Демонстрація розбору конфігураційних DIP-перемикачів ===\n\n";

    // Тест 1: Валідна конфігурація
    // Біти: P=0 | Mode=00 (Normal) | Baud=11 (115200) | Addr=101 (5)
    // Інформаційні біти: 0b00011101 -> сума 1: 4 одиниці (парна). P_calc = 0.
    // P_recv = 0: 0b00011101 = 0x1D
    testConfiguration(0x1D, "Коректна конфігурація (Addr=5, Baud=115200, Normal)");

    // Тест 2: Помилка парності (збій контакту)
    // Змінимо P_recv на 1: 0b10011101 = 0x9D
    testConfiguration(0x9D, "Помилка цілісності (спотворений біт парності)");

    // Тест 3: Зарезервований режим роботи
    // Mode = 11 (Reserved), Baud = 01 (19200), Addr = 010 (2)
    // Інформаційні біти: 0b01101010 -> 4 одиниці. P_calc = 0. P_recv = 0 -> 0x6A
    testConfiguration(0x6A, "Зарезервований режим перемикачів (OperatingMode::Reserved)");

    return 0;
}
