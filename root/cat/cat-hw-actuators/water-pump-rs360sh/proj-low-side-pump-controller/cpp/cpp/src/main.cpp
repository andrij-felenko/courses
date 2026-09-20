#include "WaterPumpController.h"
#include <iostream>
#include <thread>
#include <chrono>

// Приклад реалізації ШІМ для тестування на ПК (вивід у консоль)
class MockPwmChannel : public IPwmChannel {
public:
    void setDutyCycle(uint8_t duty) override {
        std::cout << "[PWM] Duty cycle set to " << static_cast<int>(duty) << std::endl;
    }
};

int main() {
    MockPwmChannel pwm;
    WaterPumpController::Config config {
        std::chrono::milliseconds(2000), // Плавний пуск 2 секунди
        std::chrono::milliseconds(5000), // Сторожовий таймер 5 секунд
        50,  // Мінімальний ШІМ
        255  // Максимальний ШІМ
    };

    WaterPumpController pump(pwm, config);

    std::cout << "Starting pump..." << std::endl;
    pump.start();

    // Головний неблокуючий цикл
    auto startTime = std::chrono::steady_clock::now();
    while (true) {
        pump.update();

        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime).count();

        // Імітація надходження води (скидання сторожового таймера)
        // Припиняємо скидати таймер після 6 секунд, щоб викликати помилку сухого ходу
        if (elapsed % 1000 == 0 && elapsed < 6000) {
            std::cout << "[Sensor] Water flow detected, resetting watchdog." << std::endl;
            pump.resetWatchdog();
        }

        if (pump.isFault()) {
            std::cout << "Pump FAULT! Dry run detected." << std::endl;
            break;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    return 0;
}
