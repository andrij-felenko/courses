#include "g3mb202p.hpp"
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    std::cout << "=== Демонстрація роботи драйвера твердотільного реле G3MB-202P (240 В) ===\n\n";

    // Налаштування GPIO: Пін 12, активний високий рівень
    drivers::GpioConfig gpio_cfg{
        .pin_number = 12,
        .active_level = drivers::LogicLevel::ActiveHigh
    };

    // Налаштування безпеки: мінімальний інтервал між комутаціями 200 мс
    drivers::SafetyConfig safety_cfg{
        .min_switch_interval = std::chrono::milliseconds(200)
    };

    // Створення та ініціалізація об'єкта драйвера реле
    drivers::G3MB202P ssr(gpio_cfg, safety_cfg);
    if (!ssr.init()) {
        std::cerr << "Не вдалося ініціалізувати драйвер G3MB-202P\n";
        return 1;
    }

    std::cout << "\n--- Спроба 1: Увімкнення реле ---\n";
    if (ssr.turn_on() == drivers::SwitchResult::Success) {
        std::cout << "Успіх: Навантаження 240 В підключено.\n";
    }

    std::cout << "\n--- Спроба 2: Швидка спроба вимкнути реле (без паузи) ---\n";
    // Реле не повинно перемикатися через часовий захист
    if (ssr.turn_off() == drivers::SwitchResult::Throttled) {
        std::cout << "Часовий захист спрацював коректно. Перемикання відхилено.\n";
    }

    std::cout << "\n--- Очікування витримки захисного інтервалу (250 мс) ---\n";
    std::this_thread::sleep_for(std::chrono::milliseconds(250));

    std::cout << "\n--- Спроба 3: Вимкнення реле після затримки ---\n";
    if (ssr.turn_off() == drivers::SwitchResult::Success) {
        std::cout << "Успіх: Навантаження 240 В відключено.\n";
    }

    std::cout << "\n--- Спроба 4: Безпечне інвертування стану (toggle) ---\n";
    std::this_thread::sleep_for(std::chrono::milliseconds(250));
    ssr.toggle();

    std::cout << "\n--- Поточний стан реле: "
              << (ssr.is_on() ? "УВІМКНЕНО" : "ВИМКНЕНО") << " ---\n";

    std::cout << "\n--- Завершення роботи програми (автоматичне вимкнення в деструкторі) ---\n";
    return 0;
}
