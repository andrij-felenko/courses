#include <iostream>
#include "SmartRelay.h"

int main() {
    std::cout << "=== Вузол автоматизації 220 В (HLK-PM01 + ESP32) ===\n";

    // Пін реле 18, пін кнопки 4, dead-time 3000 мс, debounce 40 мс, ліміт роботи 10000 мс
    SmartRelay smartRelay(18, 4, 3000, 40, 10000);

    // Підписка на події сповіщення (Observer)
    smartRelay.onStateChanged([](RelayState state, std::string_view reason) {
        std::string_view stateStr = "Невідомо";
        switch (state) {
            case RelayState::Off: stateStr = "OFF (Вимкнено)"; break;
            case RelayState::On: stateStr = "ON (Увімкнено)"; break;
            case RelayState::DeadTime: stateStr = "DEADTIME (Пауза безпеки)"; break;
            case RelayState::Fault: stateStr = "FAULT (Аварія)"; break;
        }
        std::cout << "[ПОДІЯ] Стан змінено на: " << stateStr 
                  << " | Причина: " << reason << "\n";
    });

    smartRelay.begin();

    // 1. Фізичне натискання кнопки
    std::cout << "\n>>> Симуляція натискання клавіші вимикача <<<\n";
    smartRelay.updateButton(true, 50);
    smartRelay.update(50);

    // 2. Спроба негайного перемикання назад через 500 мс
    std::cout << "\n>>> Симуляція швидкого вимкнення через 500 мс <<<\n";
    smartRelay.updateButton(false, 550);
    smartRelay.updateButton(true, 600); // Знову натиснули
    smartRelay.update(600);

    // 3. Спроба негайного увімкнення під час активного dead-time (700 мс)
    std::cout << "\n>>> Спроба негайного повторного ввімкнення під час паузи (700 мс) <<<\n";
    smartRelay.turnOn(700);
    smartRelay.update(700);

    // 4. Завершення dead-time (3700 мс) та виконання відкладеного увімкнення
    std::cout << "\n>>> Настання часу t = 3700 мс (dead-time вичерпано) <<<\n";
    smartRelay.update(3700);

    std::cout << "\nФінальний статус виходу: " 
              << (smartRelay.isActive() ? "АКТИВНЕ НАВАНТАЖЕННЯ" : "ЗНЕСТРУМЛЕНО") << "\n";
    return 0;
}
