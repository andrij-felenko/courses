#include "mcu_periph.hpp"
#include "foc.hpp"
#include <iostream>

int main() {
    // Екземпляри об'єктів системної периферії та FOC-контролера
    sys::McuPeripherals periph;
    control::FocController foc;

    // Конфігурація платформи STM32G431
    const sys::PeripheralsConfig config{
        .pwmFrequencyHz   = 20000,
        .deadTimeNs       = 1000,
        .shuntResistorOhm = 0.010f,
        .opampGain        = 16.0f,
        .adcVref          = 3.3f
    };

    if (!periph.init(config)) {
        return -1;
    }

    // Автоматичне виправлення зсуву нуля струмових вимірювачів
    periph.calibrateOffsets();

    // Ініціалізація параметрів FOC
    foc.init(24.0f, periph.getPwmPeriod());
    foc.setTargetSpeed(150.0f); // Бажана швидкість 150 рад/с

    // Активація генерації ШІМ у таймері TIM1
    periph.enablePwm(true);

    constexpr float dtCurrent = 0.00005f; // 20 кГц
    constexpr float dtSpeed   = 0.001f;   // 1 кГц

    float speedTimer = 0.0f;
    float electricalAngle = 0.0f;

    // Головний цикл виконання програми
    for (int step = 0; step < 10000; ++step) {
        // Оновлення контуру регулювання струму
        foc.updateCurrentLoop(electricalAngle, dtCurrent, periph);

        // Симуляція зміни позиції ротора
        electricalAngle += foc.getMeasuredSpeed() * dtCurrent;
        if (electricalAngle > 6.28318530718f) {
            electricalAngle -= 6.28318530718f;
        }

        // Крок контуру регулювання швидкості
        speedTimer += dtCurrent;
        if (speedTimer >= dtSpeed) {
            speedTimer = 0.0f;
            const float simulatedSpeed = foc.getMeasuredSpeed() + (foc.getIq() * 1.5f - 0.05f * foc.getMeasuredSpeed()) * dtSpeed;
            foc.updateSpeedLoop(simulatedSpeed, dtSpeed);
        }
    }

    return 0;
}
