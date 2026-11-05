#include "LvcBuffer.hpp"
#include <iostream>
#include <exception>

int main() {
    std::cout << "=== Демонстрація роботи тристабільного буфера 74LVC1G125 із RAII ===\n\n";

    try {
        // Створюємо два буфери, що керують різними лініями /OE (наприклад, пін 10 та пін 11)
        LvcBuffer sensor_buffer(10);
        LvcBuffer display_buffer(11);

        std::cout << "\n--- Крок 1: Увімкнення першого пристрою (Sensor) ---\n";
        sensor_buffer.enable();

        std::cout << "\n--- Крок 2: Безпечне перемикання на другий пристрій (Display) з паузою ---\n";
        // Використовуємо метод switch_to для реалізації патерну break-before-make
        sensor_buffer.switch_to(display_buffer, std::chrono::microseconds(50));

        std::cout << "\n--- Крок 3: Перевірка стану буферів ---\n";
        std::cout << "Sensor активний? " << (sensor_buffer.is_enabled() ? "Так" : "Ні") << "\n";
        std::cout << "Display активний? " << (display_buffer.is_enabled() ? "Так" : "Ні") << "\n";

        std::cout << "\n--- Крок 4: Вихід із блоку видимості (тестування RAII) ---\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }

    std::cout << "\n=== Програма завершила роботу успішно, усі шинні буфери ізольовані (Hi-Z). ===\n";
    return 0;
}
