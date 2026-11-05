/**
 * @file main.cpp
 * @brief Точка входу для демонстрації роботи драйвера промислового пульта.
 */

#include "pendant_driver.hpp"
#include <iostream>
#include <thread>
#include <iomanip>

int main() {
    using namespace IndustrialPendant;

    std::cout << "=== Ініціалізація драйвера промислового підвісного пульта ==\n";
    
    PendantDriver driver(std::chrono::milliseconds(20));
    std::array<uint8_t, 16> txBuffer{};

    struct TestStep {
        bool up, down, left, right, start, estop;
        const char* description;
    };

    TestStep steps[] = {
        {false, false, false, false, false, true,  "Очікування / Спокійний стан (E-Stop замкнено)"},
        {true,  false, false, false, false, true,  "Натиснуто кнопку 'Вгору'"},
        {false, false, false, false, true,  true,  "Натиснуто кнопку 'Пуск'"},
        {false, false, false, false, false, true,  "Відпускання всіх кнопок"},
        {false, false, false, false, false, false, "АВАРІЯ: Обрив або розмикання лінії E-Stop (NC)"},
        {false, false, false, false, true,  false, "Спроба натиснути 'Пуск' під час аварії (має блокуватися)"}
    };

    for (int i = 0; i < 6; ++i) {
        const auto& step = steps[i];
        std::cout << "\n[Крок " << (i + 1) << "] " << step.description << "\n";

        for (int tick = 0; tick < 3; ++tick) {
            driver.update(step.up, step.down, step.left, step.right, step.start, step.estop);
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }

        auto state = driver.getState();
        size_t frameSize = driver.serializeFrame(txBuffer);

        std::cout << "  Статус системи: " 
                  << (state.status == SystemStatus::Normal ? "NORM" : "E-STOP / FAULT") << "\n"
                  << "  Кнопки -> UP: " << (state.up == ButtonState::Pressed ? "ON" : "OFF")
                  << " | DOWN: " << (state.down == ButtonState::Pressed ? "ON" : "OFF")
                  << " | START: " << (state.start == ButtonState::Pressed ? "ON" : "OFF")
                  << " | E-STOP NC: " << (state.estop == ButtonState::Pressed ? "CLOSED (OK)" : "OPEN (ALARM)") << "\n";

        std::cout << "  RS-485 Фрейм (" << frameSize << " байт): ";
        for (size_t b = 0; b < frameSize; ++b) {
            std::cout << "0x" << std::hex << std::setw(2) << std::setfill('0') 
                      << static_cast<int>(txBuffer[b]) << " ";
        }
        std::cout << std::dec << "\n";
    }

    std::cout << "\nРоботу демонстрації завершено успішно.\n";
    return 0;
}
