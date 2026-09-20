#include <iostream>
#include <iomanip>
#include "safety_types.hpp"
#include "safety_controller.hpp"

// Допоміжна функція для друку поточного стану контролера
void print_status(uint64_t time_ms, const safety::SafetyController& controller) {
    std::cout << "[" << std::setw(5) << time_ms << " мс] Стан: ";
    
    switch (controller.get_state()) {
        case safety::SafetyState::Safe:           std::cout << "БЕЗПЕЧНИЙ (Safe)"; break;
        case safety::SafetyState::Muting:         std::cout << "ПРИГЛУШЕННЯ (Muting)"; break;
        case safety::SafetyState::BlankingActive: std::cout << "МАСКУВАННЯ (Blanking)"; break;
        case safety::SafetyState::Tripped:        std::cout << "СПРАЦЮВАВ (Tripped)"; break;
        case safety::SafetyState::Fault:          std::cout << "АПАРАТНИЙ ЗБОЙ (Fault)"; break;
    }

    std::cout << " | Виходи: " << (controller.get_safety_outputs() ? "УВІМК" : "ВИМК");
    if (controller.get_fault_code() != safety::FaultCode::None) {
        std::cout << " | Помилка: " << safety::fault_code_to_string(controller.get_fault_code());
    }
    std::cout << "\n";
}

int main() {
    std::cout << "=== Промисловий контролер безпеки C++ (ISO 13849 / IEC 62061) ===\n\n";

    // Налаштування конфігурації
    safety::SafetyConfig config;
    config.discrepancy_time_ms = 150; // Час розходження 150 мс
    config.muting_timeout_ms = 1000;  // Таймаут Muting 1000 мс для тесту
    config.reset_mode = safety::ResetMode::Manual;

    safety::SafetyController controller(config);
    uint64_t time_ms = 0;

    // 1. Початковий стан — система у стані Tripped після подачі живлення
    controller.process_cycle(true, true, false, false, time_ms);
    print_status(time_ms, controller);

    // 2. Виконання ручного скидання (Reset) для переходу в нормальний режим Safe
    std::cout << "\n--- Натискання кнопки Reset ---\n";
    controller.request_reset();
    controller.process_cycle(true, true, false, false, time_ms += 10);
    print_status(time_ms, controller);

    // 3. Демонстрація роботи режиму Muting (проходження матеріалу через світлову завісу)
    std::cout << "\n--- Активація датчиків Muting (M1=1, M2=1) ---\n";
    controller.process_cycle(true, true, true, true, time_ms += 100);
    print_status(time_ms, controller);

    std::cout << "Переривання OSSD-променів під час активного Muting:\n";
    controller.process_cycle(false, false, true, true, time_ms += 50);
    print_status(time_ms, controller);

    std::cout << "Завершення проходження матеріалу (Muting вимкнено, OSSD відновлено):\n";
    controller.process_cycle(true, true, false, false, time_ms += 200);
    print_status(time_ms, controller);

    // 4. Демонстрація виявлення помилки розходження каналів (Discrepancy Fault)
    std::cout << "\n--- Симуляція розходження каналів (OSSD_A=0, OSSD_B=1) ---\n";
    controller.process_cycle(false, true, false, false, time_ms += 100);
    print_status(time_ms, controller);

    std::cout << "Очікування перевищення Discrepancy Time (150 мс):\n";
    controller.process_cycle(false, true, false, false, time_ms += 200);
    print_status(time_ms, controller);

    // 5. Відновлення сигналів OSSD та спроба скидання помилки (Fault Reset)
    std::cout << "\n--- Відновлення каналів OSSD_A=1, OSSD_B=1 та Fault Reset ---\n";
    controller.process_cycle(true, true, false, false, time_ms += 50);
    print_status(time_ms, controller);

    std::cout << "Спроба скидання апаратного збою (request_reset):\n";
    if (controller.request_reset()) {
        std::cout << "Помилку успішно скинуто в контролері.\n";
    }
    controller.process_cycle(true, true, false, false, time_ms += 10);
    print_status(time_ms, controller);

    std::cout << "Друге натискання Reset для увімкнення силових виходами:\n";
    controller.request_reset();
    controller.process_cycle(true, true, false, false, time_ms += 10);
    print_status(time_ms, controller);

    std::cout << "\n=== Демонстрацію роботи контролера завершено ===\n";
    return 0;
}
