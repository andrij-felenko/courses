#include <iostream>
#include <iomanip>
#include "enabling_switch.hpp"

// Допоміжна функція для виводу опису стану українською мовою
const char* state_to_string(EnablingState state) {
    switch (state) {
        case EnablingState::Released: return "Released (Вимкнено)";
        case EnablingState::Enabled:  return "Enabled (Дозвіл увімкнено)";
        case EnablingState::Panic:    return "Panic (Панічний перетиск)";
        case EnablingState::Fault:    return "Fault (Апаратна несправність)";
    }
    return "Невідомий";
}

const char* vigilance_to_string(VigilanceStatus status) {
    switch (status) {
        case VigilanceStatus::Normal:  return "Норма";
        case VigilanceStatus::Warning: return "ПОПЕРЕДЖЕННЯ! Потрібно перевідпустити важіль";
        case VigilanceStatus::Expired: return "ТАЙМ-АУТ! Дозвіл заблоковано";
    }
    return "Невідомий";
}

int main() {
    DriverConfig config;
    config.debounce_ms = 10;
    config.discrepancy_ms = 30;
    config.hold_max_ms = 100; // Скорочено для наочності симуляції
    config.warn_ms = 40;
    config.react_ms = 30;

    EnablingSwitchController controller(config);

    std::cout << "=========================================================\n";
    std::cout << " Демонстрація роботи драйвера трипозиційної кнопки дозволу \n";
    std::cout << "=========================================================\n\n";

    uint32_t current_time_ms = 0;

    auto step_simulation = [&](bool pin_a, bool pin_b, uint32_t dt_ms, const char* description) {
        current_time_ms += dt_ms;
        controller.update(pin_a, pin_b, current_time_ms);

        std::cout << "Час: " << std::setw(4) << current_time_ms << " мс | "
                  << "Подія: " << std::setw(45) << std::left << description << " | "
                  << "Стан: " << std::setw(25) << state_to_string(controller.get_state()) << " | "
                  << "Вихід: " << (controller.is_enabled() ? "УВІМК" : "ВИМК") << "\n";
    };

    // Крок 1: Початковий стан — важіль відпущено
    step_simulation(false, false, 0, "Важіль відпущено");

    // Крок 2: Натискання до проміжного положення (Enabled)
    step_simulation(true, true, 20, "Натискання у робоче положення (Enabled)");

    // Крок 3: Тримаємо важіль у робочому стані
    step_simulation(true, true, 50, "Утримання у робочому стані");

    // Крок 4: Наближення тайм-ауту vigilance control (попередження)
    step_simulation(true, true, 40, "Таймер досяг межі t_hold_max (Warning)");
    std::cout << "   -> Статус пильності: " << vigilance_to_string(controller.get_vigilance_status()) << "\n";

    // Крок 5: Перевищення часу реакції (Expired)
    step_simulation(true, true, 80, "Таймер пильності вичерпано (Expired)");
    std::cout << "   -> Статус пильності: " << vigilance_to_string(controller.get_vigilance_status()) << "\n";

    // Крок 6: Важіль продовжують тримати, але вихід заблоковано
    step_simulation(true, true, 20, "Утримання після тайм-ауту (Блокування)");

    // Крок 7: Оператор повністю відпускає важіль для скидання
    step_simulation(false, false, 20, "Повне відпускання важеля для скидання");

    // Крок 8: Повторне правильне натискання
    step_simulation(true, true, 20, "Повторне натискання у робочий стан");

    // Крок 9: Симуляція апаратної несправності (розсинхронізація ліній > 30 мс)
    step_simulation(true, false, 40, "Розсинхронізація каналів CH_A=1, CH_B=0");

    // Крок 10: Повне відпускання для відновлення після Fault
    step_simulation(false, false, 20, "Відпускання після Fault");

    std::cout << "\nТестування успішно завершено.\n";
    return 0;
}
