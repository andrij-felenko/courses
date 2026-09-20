#include <iostream>
#include <vector>
#include "cable_pull_switch.hpp"

// Допоміжна функція для виводу назви стану FSM
const char* stateToString(CablePullSwitch::State state) {
    switch (state) {
        case CablePullSwitch::State::Normal:           return "Норма (Готовий до роботи)";
        case CablePullSwitch::State::EmergencyStop:    return "Аварійне зупинення (E-STOP)";
        case CablePullSwitch::State::DiscrepancyFault: return "Апаратна аварія (Розсинхрон каналів)";
        case CablePullSwitch::State::WaitForReset:    return "Очікування ручного скидання (Reset)";
    }
    return "Невідомий";
}

int main() {
    std::cout << "=== Драйвер двоканального тросового вимикача (IEC 60947-5-5) ===\n\n";

    CablePullSwitch::Config config{
        .debounce_ms = 10,
        .max_discrepancy_ms = 40
    };

    CablePullSwitch safety_switch(config);

    // Моделювання послідовності подій у часі (час мс, NC1, NC2, Опис)
    struct SimulationStep {
        uint32_t time_ms;
        bool nc1;
        bool nc2;
        const char* description;
    };

    std::vector<SimulationStep> steps = {
        {   0, true,  true,  "Нормальний натяг троса (обидва контакти замкнені)" },
        {  50, true,  true,  "Робота конвеєра без перешкод" },
        { 100, false, false, "Оператор потягнув трос: синхронне розмикання NC1 та NC2" },
        { 120, false, false, "Аварійний стан утримується засувом" },
        { 200, true,  true,  "Трос відпущено, натяг відновлено (обидва контакти замкнено)" },
        { 250, true,  true,  "Спроба запуску до виклику reset (має залишатися заблокованим)" },
        { 300, true,  true,  "Тест розсинхронізації: розмикаємо NC1, NC2 залишаємо замкненим" },
        { 310, false, true,  "Розсинхрон 10 мс (в межах допуску 40 мс)" },
        { 360, false, true,  "Розсинхрон 60 мс (перевищено 40 мс -> апаратний дефект)" },
        { 400, true,  true,  "Замикаємо обидва контакти для усунення дефекту" }
    };

    uint32_t current_time_ms = 0;

    for (const auto& step : steps) {
        current_time_ms = step.time_ms;
        safety_switch.update(current_time_ms, step.nc1, step.nc2);

        std::cout << "[" << current_time_ms << " мс] " << step.description << "\n";
        std::cout << "  Стан FSM: " << stateToString(safety_switch.getState())
                  << " | Дозвіл роботи: " << (safety_switch.isSafeToOperate() ? "ТАК" : "НІ") << "\n\n";

        // На кроці 250 мс пробуємо виконати ручне скидання reset()
        if (current_time_ms == 250) {
            std::cout << "--- Виконання команди ручного скидання reset() ---\n";
            bool reset_ok = safety_switch.reset();
            std::cout << "  Результат скидання: " << (reset_ok ? "УСПІШНО" : "ВІДХИЛЕНО") << "\n";
            std::cout << "  Новий стан FSM: " << stateToString(safety_switch.getState()) << "\n\n";
        }
    }

    // Остаточне скидання після апаратної аварії розсинхрону
    std::cout << "--- Виконання остаточного ручного скидання після відновлення каналів ---\n";
    bool final_reset = safety_switch.reset();
    std::cout << "  Результат скидання: " << (final_reset ? "УСПІШНО" : "ВІДХИЛЕНО") << "\n";
    std::cout << "  Підсумковий стан FSM: " << stateToString(safety_switch.getState()) << "\n";

    return 0;
}
