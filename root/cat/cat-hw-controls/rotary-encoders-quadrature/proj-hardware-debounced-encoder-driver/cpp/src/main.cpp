#include <iostream>
#include <iomanip>
#include "encoder_types.hpp"
#include "quadrature_encoder.hpp"

int main() {
    std::cout << "=== Об'єктно-орієнтований драйвер енкодера C++17 (Callbacks & Async) ===\n\n";

    // Створення драйвера енкодера з роздільною здатністю 500 PPR у режимі 4X
    encoder::QuadratureEncoder encoder_driver(500, encoder::DecodingMode::X4, 10);

    // Реєстрація подійної лямбда-функції (Callback)
    encoder_driver.set_event_callback([](encoder::EncoderEvent event, const encoder::EncoderState& state) {
        switch (event) {
            case encoder::EncoderEvent::PositionChanged:
                std::cout << "[ПОДІЯ: Крок] Позиція: " << std::setw(4) << state.position
                          << " | Напрямок: " << encoder::direction_to_string(state.direction) << "\n";
                break;
            case encoder::EncoderEvent::IndexTriggered:
                std::cout << "[ПОДІЯ: INDEX] Досягнуто нульову мітку Z! Скидання лічильника.\n";
                break;
            case encoder::EncoderEvent::VelocityUpdated:
                std::cout << "[ПОДІЯ: Швидкість] RPM: " << std::fixed << std::setprecision(2) << state.velocity_rpm << "\n";
                break;
        }
    });

    uint64_t current_time_us = 0;

    // 1. Початковий стан
    encoder_driver.update(false, false, false, current_time_us);

    // 2. Симуляція обертання за годинниковою стрілкою (CW: 00 -> 10 -> 11 -> 01 -> 00)
    std::cout << "--- 1. Симуляція обертання за годинниковою стрілкою (CW) ---\n";
    current_time_us += 20; encoder_driver.update(true,  false, false, current_time_us);
    current_time_us += 20; encoder_driver.update(true,  true,  false, current_time_us);
    current_time_us += 20; encoder_driver.update(false, true,  false, current_time_us);
    current_time_us += 20; encoder_driver.update(false, false, false, current_time_us);

    // 3. Симуляція обертання проти годинникової стрілки (CCW)
    std::cout << "\n--- 2. Симуляція обертання проти годинникової стрілки (CCW) ---\n";
    current_time_us += 20; encoder_driver.update(false, true,  false, current_time_us);
    current_time_us += 20; encoder_driver.update(true,  true,  false, current_time_us);
    current_time_us += 20; encoder_driver.update(true,  false, false, current_time_us);
    current_time_us += 20; encoder_driver.update(false, false, false, current_time_us);

    // 4. Симуляція спрацьовування індексної мітки Index (Z)
    std::cout << "\n--- 3. Симуляція проходження індексної мітки Z ---\n";
    current_time_us += 50; encoder_driver.update(false, false, true, current_time_us);
    current_time_us += 50; encoder_driver.update(false, false, false, current_time_us);

    // 5. Симуляція таймера для перевірки розрахунку швидкості (10 мс)
    std::cout << "\n--- 4. Симуляція періодичного виклику обчислення швидкості ---\n";
    for (int i = 0; i < 5; ++i) {
        current_time_us += 2500;
        encoder_driver.update(true, true, false, current_time_us);
        current_time_us += 2500;
        encoder_driver.update(false, false, false, current_time_us);
    }

    // 6. Отримання поточного стану через std::optional
    auto opt_state = encoder_driver.get_state();
    if (opt_state.has_value()) {
        std::cout << "\nФінальна позиція: " << opt_state->position
                  << " | Підсумкова швидкість: " << opt_state->velocity_rpm << " RPM\n";
    }

    std::cout << "\n=== Демонстрацію робочого драйвера C++17 завершено ===\n";
    return 0;
}
