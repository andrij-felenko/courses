#include <iostream>
#include <iomanip>
#include "servo_driver.hpp"
#include "motion_profile.hpp"
#include "servo_tester.hpp"

int main() {
    std::cout << "=========================================================\n";
    std::cout << " Симуляція системи керування RC-сервоприводом (C++)\n";
    std::cout << "=========================================================\n\n";

    // 1. Ініціалізація апаратного драйвера сервоприводу (Канал 0, межі 500..2500 мкс)
    rc_servo::ServoDriver driver(0, 500, 2500);
    driver.enableOutput(true);

    // 2. Налаштування профайлера плавної динаміки (макс. швидкість 120°/с, прискорення 480°/с²)
    rc_servo::MotionProfiler profiler(120.0f, 480.0f);

    // 3. Ініціалізація сервотестера
    rc_servo::ServoTester tester(driver, profiler);

    std::cout << "[ІНІЦІАЛІЗАЦІЯ] Драйвер та профайлер успішно налаштовані.\n";
    std::cout << "Частота кадру ШІМ: 50 Гц (період 20000 мкс).\n\n";

    // Тест 1: Режим нейтралі (90°, 1500 мкс)
    std::cout << "--- Тест 1: Режим Neutral (Калібрування вала) ---\n";
    tester.setMode(rc_servo::TesterMode::Neutral);
    
    // Моделюємо кілька кроків дискретизації (dt = 20 мс, відповідає частоті кадрів 50 Гц)
    constexpr float DT = 0.020f; 
    for (int i = 0; i < 5; ++i) {
        tester.update(DT);
        std::cout << "Крок " << i + 1 
                  << " | Кут: " << std::fixed << std::setprecision(1) << driver.getAngleDeg() << "°"
                  << " | ШІМ: " << driver.getPulseWidthUs() << " мкс"
                  << " | Тактів таймера: " << driver.pulseToTimerTicks(driver.getPulseWidthUs())
                  << "\n";
    }

    // Тест 2: Перехід у ручний режим (Manual) до 150° з плавною динамікою
    std::cout << "\n--- Тест 2: Режим Manual (Плавне переміщення до 150°) ---\n";
    tester.setMode(rc_servo::TesterMode::Manual);
    tester.setManualTarget(150.0f);

    for (int i = 0; i < 12; ++i) {
        tester.update(DT);
        std::cout << "Час: " << std::setprecision(3) << (i + 1) * DT << " с"
                  << " | Кут: " << std::setprecision(1) << driver.getAngleDeg() << "°"
                  << " | ШІМ: " << driver.getPulseWidthUs() << " мкс"
                  << " | Швидкість: " << profiler.getCurrentVelocity() << " °/с"
                  << "\n";
    }

    // Тест 3: Автоматичне сканування (AutoSweep) між 20° та 160°
    std::cout << "\n--- Тест 3: Режим AutoSweep (Сканування 20° <-> 160°) ---\n";
    tester.setSweepRange(20.0f, 160.0f);
    tester.setMode(rc_servo::TesterMode::AutoSweep);

    for (int i = 0; i < 10; ++i) {
        tester.update(DT);
        std::cout << "Крок сканування " << i + 1
                  << " | Ціль: " << profiler.getTargetAngle() << "°"
                  << " | Поточний кут: " << driver.getAngleDeg() << "°"
                  << " | ШІМ: " << driver.getPulseWidthUs() << " мкс"
                  << "\n";
    }

    // Тест 4: Перевірка захисного бар'єру безпеки (симуляція спроби невалідного імпульсу)
    std::cout << "\n--- Тест 4: Симуляція захисного відключення при некоректних параметрах ---\n";
    rc_servo::DriverStatus status = driver.setPulseWidthUs(300); // 300 мкс - поза безпечними межами
    if (status != rc_servo::DriverStatus::Ok) {
        std::cout << "[ЗАХИСТ] Спроба встановити ШІМ 300 мкс відхилена драйвером (Код: " 
                  << static_cast<int>(status) << ").\n";
    }

    std::cout << "\nДемонстрація завершена успішно.\n";
    return 0;
}
