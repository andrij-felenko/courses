#include <iostream>
#include "pir_sensor.hpp"
#include "power_management.hpp"
#include "lighting_controller.hpp"

// Глобальне посилання на об'єкт давача для обробника апаратного переривання ISR
static PirSensor* g_sensor_ptr = nullptr;

/**
 * @brief Симуляція векторного обробника апаратного переривання EXTI від HC-SR505.
 * 
 * У реальній прошивці це функція на зразок `void EXTI0_IRQHandler(void)` або callback `attachInterrupt()`.
 */
void simulated_EXTI_IRQHandler(bool pin_high, uint32_t current_time_ms) {
    if (g_sensor_ptr != nullptr) {
        g_sensor_ptr->handleInterrupt(pin_high, current_time_ms);
    }
}

int main() {
    std::cout << "=== Демонстрація енергоефективної автоматики освітлення на HC-SR505 ===\n\n";

    // 1. Конфігурація виводів та параметрів
    constexpr uint8_t PIR_PIN = 2;          // Вивід OUT HC-SR505 підключено до GPIO2
    constexpr uint8_t RELAY_PIN = 13;       // Вивід реле підключено до GPIO13
    constexpr uint32_t HOLD_TIME_MS = 3000;    // 3 секунди затримки освітлення для демонстрації

    // 2. Створення системних компонентів
    PirSensor pir_sensor(PIR_PIN, 50);
    PowerManager power_manager(LowPowerMode::DeepSleep);
    LightingController controller(pir_sensor, power_manager, RELAY_PIN, HOLD_TIME_MS);

    g_sensor_ptr = &pir_sensor;

    pir_sensor.init();
    power_manager.configureWakeupSource(PIR_PIN);
    controller.init();

    std::cout << "\n--- Запуск головного циклу обробки подій ---\n";

    uint32_t system_time_ms = 1000;

    // Крок 1: Початковий стан Idle (відсутність руху)
    controller.update(system_time_ms);

    // Крок 2: Виявлення руху (сигнал HIGH від HC-SR505)
    std::cout << "\n--- Подія: Об'єкт входить у зону дії HC-SR505 ---\n";
    system_time_ms += 200;
    simulated_EXTI_IRQHandler(true, system_time_ms);
    controller.update(system_time_ms);

    // Крок 3: Рух триває, повторне оновлення
    std::cout << "\n--- Проходження часу (рух триває) ---\n";
    system_time_ms += 1000;
    controller.update(system_time_ms);

    // Крок 4: Рух припиняється (HC-SR505 опускає OUT у LOW)
    std::cout << "\n--- Подія: Об'єкт залишає зону дії HC-SR505 ---\n";
    system_time_ms += 500;
    simulated_EXTI_IRQHandler(false, system_time_ms);
    controller.update(system_time_ms);

    // Крок 5: Відлік часу затримки утримання освітлення
    std::cout << "\n--- Проходження часу: 1.5 сек (в межах затримки " << HOLD_TIME_MS << " мс) ---\n";
    system_time_ms += 1500;
    controller.update(system_time_ms);

    // Крок 6: Закінчення таймауту та перехід у сон
    std::cout << "\n--- Проходження часу: ще 2.0 сек (таймаут вичерпано) ---\n";
    system_time_ms += 2000;
    controller.update(system_time_ms);

    // Крок 7: Новий рух пробуджує мікроконтролер від EXTI
    std::cout << "\n--- Подія: Новий рух пробуджує мікроконтролер від EXTI ---\n";
    system_time_ms += 5000;
    simulated_EXTI_IRQHandler(true, system_time_ms);
    controller.update(system_time_ms);

    std::cout << "\n=== Демонстрацію завершено успішно ===\n";
    return 0;
}
