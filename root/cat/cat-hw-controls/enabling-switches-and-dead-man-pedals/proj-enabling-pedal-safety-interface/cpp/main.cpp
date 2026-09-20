/**
 * @file main.cpp
 * @brief Приклад асинхронного опитування педалі дозволу з колбеками та індикацією.
 */

#include <iostream>
#include <vector>
#include "EnablingPedal.hpp"

int main() {
    PedalConfig config;
    config.debounceMs = 20;
    config.discrepancyTimeoutMs = 100;
    config.maxStuckTimeMs = 5000; // Для тестування встановимо 5 секунд

    EnablingPedal pedal(config);

    // Реєстрація зворотного виклику при зміні стану FSM
    pedal.setOnStateChanged([](SafetyState newState) {
        std::cout << "[FSM Callback] Новий стан: " << EnablingPedal::stateToString(newState) << '\n';
    });

    // Реєстрація аварійного зворотного виклику
    pedal.setOnFault([](std::string_view reason) {
        std::cout << "[CRITICAL ALARM] Аварія педалі: " << reason << '\n';
    });

    std::cout << "=== Система моніторингу педалі дозволу запущена ===\n";

    struct Step {
        std::uint32_t timeMs;
        bool chA;
        bool chB;
        std::string_view info;
    };

    std::vector<Step> steps = {
        {   0, false, false, "Педаль відпущена" },
        { 100, true,  true,  "Педаль затиснута в Положення 2 (Дозвіл роботи)" },
        { 5200, true, true,  "Тривале тримання педалі понад 5000 мс (Перевірка заклинювання)" },
        { 5300, false, false, "Відпущення педалі оператором" },
        { 5500, true,  true,  "Повторна спроба натискання після аварії" },
        { 5600, false, false, "Відпущення для повного скидання" },
        { 5800, true,  true,  "Відновлення нормальної роботи" }
    };

    std::uint32_t currentTimeMs = 0;
    std::size_t stepIdx = 0;

    while (stepIdx < steps.size()) {
        currentTimeMs += 10;

        if (currentTimeMs >= steps[stepIdx].timeMs) {
            std::cout << "\n--- Час: " << currentTimeMs << " мс | " << steps[stepIdx].info << " ---\n";
            stepIdx++;
        }

        std::size_t activeIdx = (stepIdx > 0) ? stepIdx - 1 : 0;
        pedal.update(steps[activeIdx].chA, steps[activeIdx].chB, currentTimeMs);
    }

    std::cout << "\n=== Моделювання роботи педалі завершено успішно ===\n";
    return 0;
}
