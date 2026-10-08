#include <iostream>
#include <iomanip>
#include "pwm_timer.hpp"
#include "continuous_servo.hpp"

// Допоміжна функція для демонстраційного друку стану сервопривода
static void printServoStatus(const char* step_name, const ContinuousServo& servo) {
    std::cout << std::left << std::setw(32) << step_name
              << " | Швидкість: " << std::right << std::setw(6) << std::fixed << std::setprecision(1)
              << servo.getCurrentSpeed() << "%"
              << " | Імпульс: " << std::setw(4) << servo.getCurrentPulseUs() << " мкс"
              << " | Стан: " << (servo.isStopped() ? "ЗУПИНЕНО" : "ОБЕРТАННЯ")
              << "\n";
}

int main() {
    std::cout << "=== Керування сервоприводом постійного обертання (C++) ===\n\n";

    // 1. Створення та ініціалізація апаратного ШІМ-таймера на GPIO 18
    constexpr uint8_t SERVO_PIN = 18;
    PwmTimer pwm_timer(SERVO_PIN, 50); // 50 Гц (період 20 мс)

    // 2. Конфігурація часових параметрів ШІМ
    ServoPwmConfig config;
    config.min_pulse_us = 1000;     // -100% (максимальна швидкість CCW)
    config.neutral_pulse_us = 1500; // 0% (початкова нейтраль)
    config.max_pulse_us = 2000;     // +100% (максимальна швидкість CW)
    config.trim_offset_us = 0;      // Початковий зсув відсутній

    ContinuousServo servo(pwm_timer, config);

    if (!servo.init()) {
        std::cerr << "Помилка ініціалізації модулів ШІМ!\n";
        return 1;
    }
    printServoStatus("Ініціалізація (нейтраль)", servo);

    // 3. Калібрування нейтральної точки для усунення механічного/електронного дрейфу
    std::cout << "\n--- Крок 1: Калібрування зсуву нейтралі (Trim Offset) ---\n";
    servo.setTrimOffset(25); // Дійсна нейтраль стає 1525 мкс
    printServoStatus("Після калібрування (+25 мкс)", servo);

    // 4. Демонстрація плавної зміни напрямку та швидкості обертання
    std::cout << "\n--- Крок 2: Обертання за годинниковою стрілкою (CW) ---\n";
    servo.setSpeed(ServoDirection::Clockwise, 30.0f);
    printServoStatus("CW 30% швидкості", servo);

    servo.setSpeed(ServoDirection::Clockwise, 100.0f);
    printServoStatus("CW 100% макс. швидкість", servo);

    std::cout << "\n--- Крок 3: Обертання проти годинникової стрілки (CCW) ---\n";
    servo.setSpeed(-50.0f); // Від'ємне значення означає CCW
    printServoStatus("CCW 50% швидкості", servo);

    servo.setSpeed(ServoDirection::CounterClockwise, 100.0f);
    printServoStatus("CCW 100% макс. швидкість", servo);

    std::cout << "\n--- Крок 4: Повна зупинка ---\n";
    servo.stop();
    printServoStatus("Зупинено (подача нейтралі)", servo);

    // 5. Демонстрація гарантованої автоматичної зупинки через RAII ServoGuard
    std::cout << "\n--- Крок 5: Безпечна робота через RAII (ServoGuard) ---\n";
    {
        std::cout << "[Область видимості] Створення ServoGuard та запуск обертання...\n";
        ServoGuard guard(servo);

        servo.setSpeed(75.0f);
        printServoStatus("Рух у локальному блоці", servo);

        std::cout << "[Область видимості] Вихід з локального блоку...\n";
        // При виході з блоку деструктор guard автоматично повертає сервопривід у стан зупинки
    }
    printServoStatus("Після виходу з ServoGuard", servo);

    std::cout << "\n=== Демонстрацію успішно завершено ===\n";
    return 0;
}
