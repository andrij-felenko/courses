#include <iostream>
#include <iomanip>
#include <bitset>
#include <chrono>
#include <thread>
#include "ss41f_hall_decoder.hpp"
#include "stm32_gpio_exti.hpp"

// Допоміжна функція для виведення текстового опису сектора
const char* sector_to_string(bldc::RotorSector sector) {
    switch (sector) {
        case bldc::RotorSector::Sector1: return "Сектор 1 (0° - 60°)";
        case bldc::RotorSector::Sector2: return "Сектор 2 (60° - 120°)";
        case bldc::RotorSector::Sector3: return "Сектор 3 (120° - 180°)";
        case bldc::RotorSector::Sector4: return "Сектор 4 (180° - 240°)";
        case bldc::RotorSector::Sector5: return "Сектор 5 (240° - 300°)";
        case bldc::RotorSector::Sector6: return "Сектор 6 (300° - 360°)";
        default: return "Невідомий сектор";
    }
}

// Допоміжна функція для виведення напрямку обертання
const char* direction_to_string(bldc::RotationDirection dir) {
    switch (dir) {
        case bldc::RotationDirection::Forward: return "Прямий (CW)";
        case bldc::RotationDirection::Reverse: return "Зворотний (CCW)";
        default: return "Невизначений";
    }
}

int main() {
    std::cout << "==================================================================\n";
    std::cout << "  Декодер біполярних цифрових датчиків Холла SS41F (BLDC 120°)\n";
    std::cout << "==================================================================\n\n";

    constexpr uint8_t POLE_PAIRS = 4; // 4 пари полюсів двигуна
    bldc::Ss41fHallDecoder decoder(POLE_PAIRS);

    // 1. Реєстрація подійно-орієнтованих C++ callback-функцій
    decoder.set_sector_change_callback([](const bldc::RotorTelemetry& telemetry) {
        std::cout << "[Оновлення ротора] Поточний: " << sector_to_string(telemetry.current_sector)
                  << " | Напрямок: " << std::left << std::setw(15) << direction_to_string(telemetry.direction)
                  << " | Швидкість: " << std::right << std::setw(5) << telemetry.speed_rpm << " RPM"
                  << " | Переключень: " << telemetry.state_change_count << "\n";
    });

    decoder.set_error_callback([](bldc::DecoderError error, uint8_t raw_code) {
        std::cout << "  [!!! ДІАГНОСТИЧНА ПОМИЛКА !!!] Код: ";
        switch (error) {
            case bldc::DecoderError::InvalidHallState:
                std::cout << "Некоректний стан фаз (0b" 
                          << std::bitset<3>(raw_code) << ") - обрив або коротке замикання ліній SS41F\n";
                break;
            case bldc::DecoderError::IllegalStateTransition:
                std::cout << "Неприпустимий перехід фаз (0b" 
                          << std::bitset<3>(raw_code) << ") - пропущено сектор або дребезг контакту\n";
                break;
            case bldc::DecoderError::SensorTimeout:
                std::cout << "Таймаут датчиків - ротор зупинився\n";
                break;
            default:
                std::cout << "Невідома помилка\n";
                break;
        }
    });

    // 2. Створення апаратних портів та RAII-модуля GpioExtiGuard
    stm32::GpioRegisterMap port_a_regs{0, 0, 0, 0};
    stm32::GpioPinConfig pin_hall_a{&port_a_regs, 0}; // PA0 - Hall A
    stm32::GpioPinConfig pin_hall_b{&port_a_regs, 1}; // PA1 - Hall B
    stm32::GpioPinConfig pin_hall_c{&port_a_regs, 2}; // PA2 - Hall C

    stm32::GpioExtiGuard exti_guard(decoder, pin_hall_a, pin_hall_b, pin_hall_c);

    uint32_t current_time_us = 100000; // Початковий час 100 мс

    std::cout << "--- 1. Демонстрація нормального прямого обертання (Forward/CW) ---\n";
    // Послідовність станів для прямого обертання: 5 -> 4 -> 6 -> 2 -> 3 -> 1 -> 5...
    const uint8_t cw_sequence[] = {0b101, 0b100, 0b110, 0b010, 0b011, 0b001, 0b101, 0b100, 0b110, 0b010, 0b011, 0b001};
    constexpr uint32_t dt_step_us = 2500; // 2.5 мс між переключеннями (~1000 RPM для 4-полюсного двигуна)

    for (uint8_t hall_code : cw_sequence) {
        current_time_us += dt_step_us;
        exti_guard.simulate_pin_change(hall_code, current_time_us);
    }

    std::cout << "\n--- 2. Демонстрація прискорення двигуна (зменшення інтервалу) ---\n";
    constexpr uint32_t fast_dt_step_us = 1250; // 1.25 мс між переключеннями (~2000 RPM)
    for (size_t i = 0; i < 6; ++i) {
        current_time_us += fast_dt_step_us;
        exti_guard.simulate_pin_change(cw_sequence[i], current_time_us);
    }

    std::cout << "\n--- 3. Демонстрація реверсу обертання (Reverse/CCW) ---\n";
    // Зворотна послідовність станів: 1 -> 3 -> 2 -> 6 -> 4 -> 5 -> 1...
    const uint8_t ccw_sequence[] = {0b001, 0b011, 0b010, 0b110, 0b100, 0b101, 0b001};
    for (uint8_t hall_code : ccw_sequence) {
        current_time_us += dt_step_us;
        exti_guard.simulate_pin_change(hall_code, current_time_us);
    }

    std::cout << "\n--- 4. Тестування виявлення несправностей та діагностики помилок ---\n";
    std::cout << "4a. Імітація обриву ліній датчиків SS41F (код 0b000):\n";
    current_time_us += dt_step_us;
    exti_guard.simulate_pin_change(0b000, current_time_us);

    std::cout << "4b. Імітація короткого замикання на VCC (код 0b111):\n";
    current_time_us += dt_step_us;
    exti_guard.simulate_pin_change(0b111, current_time_us);

    std::cout << "4c. Імітація недозволеного стрибка (зі стану 0b101 одразу в 0b010, пропустивши 0b100):\n";
    current_time_us += dt_step_us;
    exti_guard.simulate_pin_change(0b101, current_time_us);
    current_time_us += dt_step_us;
    exti_guard.simulate_pin_change(0b010, current_time_us);

    std::cout << "\n--- 5. Демонстрація перевірки таймауту зупинки ротора ---\n";
    current_time_us += 1500000; // Пройшло 1.5 секунди без подій від датчиків
    decoder.check_timeout(current_time_us, 1000000);

    bldc::RotorTelemetry final_telemetry = decoder.get_telemetry();
    std::cout << "\nПідсумкова телеметрія ротора:\n";
    std::cout << "  - Стан по поточній швидкості: " << final_telemetry.speed_rpm << " RPM\n";
    std::cout << "  - Загальна кількість успішних переключень: " << final_telemetry.state_change_count << "\n";
    std::cout << "  - Всього зафіксовано апаратних/фазових помилок: " << final_telemetry.error_count << "\n";

    std::cout << "\nДемонстрація декодера сигналів SS41F успішно завершена.\n";
    return 0;
}
