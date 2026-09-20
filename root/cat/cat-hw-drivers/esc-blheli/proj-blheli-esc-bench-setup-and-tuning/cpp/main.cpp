#include "blheli_esc.hpp"
#include <iostream>

int main() {
    std::cout << "--- Запуск системи керування BLDC мотором (BLHeli 30A ESC) ---" << std::endl;

    // Конфігурація пінів: ШІМ = Pin 9, АЦП = Pin A0, дільник напруги BEC = 2.0
    constexpr uint8_t PWM_PIN = 9;
    constexpr uint8_t BEC_ADC_PIN = 0;
    constexpr float VOLTAGE_DIVIDER = 2.0f;

    BLHeliESC esc(PWM_PIN, BEC_ADC_PIN, VOLTAGE_DIVIDER);

    // 1. Ініціалізація модулів
    if (!esc.init()) {
        std::cerr << "Помилка ініціалізації периферії ESC!" << std::endl;
        return 1;
    }

    // 2. Виконання процедури автокалібрування діапазону газу
    esc.calibrate();

    // 3. Перевірка живлення BEC перед запуском
    float initial_bec_v = esc.readBECVoltage();
    std::cout << "[BEC Monitor] Початкова напруга BEC: " << initial_bec_v << " В" << std::endl;

    if (!esc.isBECVoltageSafe()) {
        std::cerr << "[УВАГА] Небезпечна напруга BEC! Запуск скасовано." << std::endl;
        esc.emergencyStop();
        return 1;
    }

    // 4. Демонстраційний цикл плавного розгону та моніторингу
    std::cout << "\n--- Початок тестування розгону двигуна ---" << std::endl;
    
    // Плавне збільшення газу від 0% до 50%
    for (float throttle = 0.0f; throttle <= 50.0f; throttle += 10.0f) {
        esc.setThrottlePercent(throttle);
        float bec_v = esc.readBECVoltage();

        std::cout << "Газ: " << throttle << "% | Імпульс: " 
                  << esc.getPulseWidthUs() << " мкс | Напруга BEC: " 
                  << bec_v << " В" << std::endl;

        // Постійний контроль просідання живлення
        if (!esc.isBECVoltageSafe()) {
            std::cerr << "[КРИТИЧНО] Просідання напруги BEC (" << bec_v 
                      << " В < " << BLHeliESC::BEC_SAFE_VOLTAGE_MIN << " В)!" << std::endl;
            esc.emergencyStop();
            break;
        }
    }

    // 5. Безпечне уповільнення та вимкнення мотора
    std::cout << "\n--- Завершення робочого циклу ---" << std::endl;
    esc.setThrottlePercent(0.0f);
    std::cout << "Двигун зупинено. ШІМ-імпульс: " << esc.getPulseWidthUs() << " мкс." << std::endl;

    return 0;
}
