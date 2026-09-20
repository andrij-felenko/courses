#include "GuardedToggleSwitch.h"
#include <iostream>

// Функція обробки подій панелі керування (імітація реєстратора подій в Arduino / вбудованій системі)
void handleSafetyEvent(const ToggleEventData& event) {
    std::cout << "[ПОДІЯ " << event.timestamp_ms << " мс] "
              << safetyEventToString(event.event_type)
              << " | Статус ковпачка: " << (event.guard_state == GuardState::Open ? "ВІДКРИТО" : "ЗАКРИТО")
              << " | Тумблер: " << (event.switch_position == SwitchPosition::On ? "УВІМК" : "ВИМК")
              << " | Дозвіл дій: " << (event.action_allowed ? "ДОЗВОЛЕНО" : "БЛОКОВАНО")
              << std::endl;
}

int main() {
    std::cout << "=== Панель керування: Тумблер із захисним ковпачком Mollie ===" << std::endl;

    // Ініціалізація драйвера тумблера з часом дебаунсу 20 мс
    GuardedToggleSwitch toggle_switch(20);
    toggle_switch.setEventCallback(handleSafetyEvent);

    uint32_t current_time = 0;

    // 1. Початковий стан: Ковпачок закритий (LOW = false), тумблер вимкнений (LOW = false)
    std::cout << "\n--- Крок 1: Ініціалізація органів керування ---" << std::endl;
    toggle_switch.update(false, false, current_time);

    // 2. Спроба виконання критичної дії при закритому ковпачку
    std::cout << "\n--- Крок 2: Спроба виконання команди при закритому ковпачку ---" << std::endl;
    current_time += 100;
    bool success = toggle_switch.executeCriticalAction(current_time);
    std::cout << "Результат спроби виконання: " << (success ? "УСПІХ" : "БЛОКОВАНО БЕЗПЕКОЮ") << std::endl;

    // 3. Відкриття захисного ковпачка Mollie (guard = true / HIGH)
    std::cout << "\n--- Крок 3: Відкриття захисного ковпачка Mollie ---" << std::endl;
    current_time += 50;
    // Імітація стабільного сигналу після дебаунсу (20 мс)
    toggle_switch.update(false, true, current_time);
    current_time += 25;
    toggle_switch.update(false, true, current_time);

    // 4. Перемикання тумблера в стан УВІМКНЕНО (switch = true / HIGH)
    std::cout << "\n--- Крок 4: Перемикання важеля в стан УВІМКНЕНО ---" << std::endl;
    current_time += 50;
    toggle_switch.update(true, true, current_time);
    current_time += 25;
    toggle_switch.update(true, true, current_time);

    // 5. Виконання критичної дії при відкритому ковпачку та увімкненому тумблері
    std::cout << "\n--- Крок 5: Повторна спроба виконання критичної команди ---" << std::endl;
    current_time += 10;
    success = toggle_switch.executeCriticalAction(current_time);
    std::cout << "Результат спроби виконання: " << (success ? "УСПІХ (Команда виконана)" : "БЛОКОВАНО") << std::endl;

    // 6. Закриття захисного ковпачка Mollie при включеному тумблері
    std::cout << "\n--- Крок 6: Закриття ковпачка (захисне повернення важеля) ---" << std::endl;
    current_time += 100;
    toggle_switch.update(true, false, current_time);
    current_time += 25;
    toggle_switch.update(true, false, current_time);

    return 0;
}
