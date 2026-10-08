#include "dc130_motor_driver.hpp"
#include <iostream>

using namespace embedded;

int main() {
    std::cout << "--------------------------------------------------------\n";
    std::cout << " Керування колекторним двигуном 130 через C++ H-Bridge Драйвер\n";
    std::cout << "--------------------------------------------------------\n";

    // Конфігурація підключення двигуна типорозміру 130
    MotorConfig config;
    config.pinIn1 = 12;
    config.pinIn2 = 13;
    config.pinEnable = 14;
    config.pwmFrequencyHz = 20000; // 20 кГц беззвучний режим
    config.deadTimeMs = 50;        // 50 мс захисна затримка скрізного струму
    config.minDutyCycle = 12;      // 12% поріг подолання тертя спокою

    DC130MotorDriver motor(config);
    if (!motor.init()) {
        std::cerr << "Помилка ініціалізації драйвера мотора!\n";
        return 1;
    }

    // 1. Плавне збільшення швидкості
    std::cout << "\n=== КРОК 1: Плавне розганяння мотора (Forward) ===\n";
    motor.setDirection(Direction::Forward);
    for (uint8_t speed = 20; speed <= 100; speed += 40) {
        std::cout << "\n--> Запит швидкості: " << static_cast<int>(speed) << "%\n";
        motor.setSpeed(speed);
        PwmTimer::delayMs(30);
    }

    // 2. Безпечний реверс напрямку з Dead Time
    std::cout << "\n=== КРОК 2: Зміна напрямку на Reverse під час руху ===\n";
    motor.setDirection(Direction::Reverse);

    // 3. Порівняння активного гальмування brake() та інерційного вибігу coast()
    std::cout << "\n=== КРОК 3: Порівняльний аналіз режимів зупинки ===\n";

    std::cout << "\n[Тест 1] Встановлення 75% швидкості -> Активне електродинамічне гальмування (brake):\n";
    motor.setSpeed(75);
    PwmTimer::delayMs(20);
    motor.brake();

    std::cout << "\n[Тест 2] Встановлення 75% швидкості -> Інерційний вибіг (coast):\n";
    motor.setDirection(Direction::Forward);
    motor.setSpeed(75);
    PwmTimer::delayMs(20);
    motor.coast();

    // 4. Демонстрація гарантованої зупинки RAII-обгорткою MotorGuard
    std::cout << "\n=== КРОК 4: Використання RAII MotorGuard у робочому блоці ===\n";
    {
        motor.setSpeed(50);
        MotorGuard guard(motor, StopMode::Brake);
        std::cout << "Двигун обертається під захистом RAII. Вихід з блоку...\n";
    }

    std::cout << "\nДемонстрацію повністю завершено успішно.\n";
    return 0;
}
