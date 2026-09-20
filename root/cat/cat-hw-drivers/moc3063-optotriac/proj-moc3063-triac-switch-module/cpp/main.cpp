#include "Moc3063.hpp"
#include <iostream>
#include <thread>
#include <chrono>

// Апаратна імітація GPIO для демонстрації роботи драйвера
namespace HardwareHal {
    static LogicLevel gpio_registers[256] = {LogicLevel::Low};
    static bool gpio_configured[256] = {false};

    bool initPin(uint8_t pin, LogicLevel inactive_level) {
        gpio_registers[pin] = inactive_level;
        gpio_configured[pin] = true;
        std::cout << "[HAL GPIO] Вивід GPIO_" << static_cast<int>(pin)
                  << " налаштовано як OUTPUT. Початковий рівень: "
                  << (inactive_level == LogicLevel::High ? "HIGH (1)" : "LOW (0)")
                  << std::endl;
        return true;
    }

    void writePin(uint8_t pin, LogicLevel level) {
        if (!gpio_configured[pin]) {
            std::cout << "[HAL ERROR] Спроба керування несконфігованим виводом GPIO_"
                      << static_cast<int>(pin) << std::endl;
            return;
        }
        gpio_registers[pin] = level;
        std::cout << "[HAL GPIO] Зміна стану виводу GPIO_" << static_cast<int>(pin)
                  << " -> " << (level == LogicLevel::High ? "HIGH (1)" : "LOW (0)")
                  << std::endl;
    }
}

// Конвертер статусу для зручного виводу у лог
const char* statusToString(Status status) {
    switch (status) {
        case Status::Ok:                 return "Успішно (Ok)";
        case Status::InvalidPin:         return "Помилка: невірний pin";
        case Status::NotInitialized:     return "Помилка: не ініціалізовано";
        case Status::AlreadyInitialized: return "Помилка: вже ініціалізовано";
        case Status::HardwareError:      return "Помилка апаратного рівня";
        default:                         return "Невідомий статус";
    }
}

int main() {
    std::cout << "========================================================\n";
    std::cout << "  Демонстрація C++ драйвера оптосимістора MOC3063\n";
    std::cout << "  (Zero-Cross оптопара для безпечної AC-комутації)\n";
    std::cout << "========================================================\n\n";

    // Конфігурація драйвера для керування потужним нагрівачем (ТЕН)
    Moc3063Config heater_config{
        .pin = 12,
        .active_level = ActiveLevel::ActiveHigh,
        .initial_state = LoadState::Disabled,
        .write_fn = HardwareHal::writePin,
        .init_fn = HardwareHal::initPin
    };

    std::cout << "[КРОК 1] Створення об'єкта драйвера MOC3063...\n";
    Moc3063 heater(heater_config);

    std::cout << "  - Стан ініціалізації: " << (heater.isInitialized() ? "Так" : "Ні") << "\n";
    std::cout << "  - Перевірка виклику turnOn() до ініціалізації: " 
              << statusToString(heater.turnOn()) << "\n";

    std::cout << "\n[КРОК 2] Безпечна ініціалізація периферії МК...\n";
    Status init_res = heater.init();
    std::cout << "  - Результат init(): " << statusToString(init_res) << "\n";
    std::cout << "  - Стан навантаження після ініціалізації: " 
              << (heater.isEnabled() ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n";

    std::cout << "\n[КРОК 3] Увімкнення силового навантаження (turnOn)...\n";
    Status turn_on_res = heater.turnOn();
    std::cout << "  - Результат turnOn(): " << statusToString(turn_on_res) << "\n";
    std::cout << "  - Логічний стан драйвера: " 
              << (heater.isEnabled() ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n";
    std::cout << "  - Пояснення Zero-Cross: Світлодіод оптопари увімкнено.\n"
              << "    Внутрішня схема MOC3063 відкриє силовий симістор у момент,\n"
              << "    коли напруга мережі 220V перетне 0V (мінімізація завад EMI).\n";

    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "\n[КРОК 4] Інвертування стану силового ключа (toggle)...\n";
    Status toggle_res = heater.toggle();
    std::cout << "  - Результат toggle(): " << statusToString(toggle_res) << "\n";
    std::cout << "  - Новий логічний стан драйвера: " 
              << (heater.isEnabled() ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n";
    std::cout << "  - Пояснення Zero-Cross: Світлодіод вимкнено.\n"
              << "    Силовий симістор закриється при переході струму навантаження через 0A.\n";

    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "\n[КРОК 5] Завершення роботи (демонстрація безпечного RAII вимкнення)...\n";
    heater.turnOn();
    std::cout << "  - Стан перед знищенням об'єкта: " 
              << (heater.isEnabled() ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n";

    std::cout << "\nВихід із main(): об'єкт heater виходить із зони видимості...\n";
    return 0;
}
