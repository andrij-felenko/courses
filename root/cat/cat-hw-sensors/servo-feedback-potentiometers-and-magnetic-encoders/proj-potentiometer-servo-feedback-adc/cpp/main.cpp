#include "servo_feedback.hpp"
#include <iostream>
#include <iomanip>
#include <random>
#include <cmath>

/**
 * @file main.cpp
 * @brief Демонстрація використання модуля ServoFeedback з імітацією завад АЦП.
 */

int main() {
    std::cout << "=== Модуль кутового зворотного зв'язку сервоприводу (EMA + Калібрування) ===\n\n";

    // 1. Конфігурація калібрувальних параметрів для 12-бітного АЦП (0..4095)
    // Допустимий робочий діапазон потенціометра або магнітного енкодера: 200..3895 відліків
    // Це відповідає діапазону повороту сервоприводу від 0.0° до 270.0°
    CalibrationParams calib{
        .raw_min = 200,
        .raw_max = 3895,
        .min_angle_deg = 0.0f,
        .max_angle_deg = 270.0f,
        .raw_zero_offset = 15 // Монтажне зміщення нуля на 15 відліків
    };

    // 2. Ініціалізація класу зворотного зв'язку з коефіцієнтом EMA alpha = 0.15f
    // alpha = 0.15 забезпечує чудове придушення високочастотного шуму АЦП
    ServoFeedback feedback(calib, 0.15f);

    std::cout << "[ІНІЦІАЛІЗАЦІЯ]\n";
    std::cout << "Калібрування: raw_min=" << calib.raw_min 
              << ", raw_max=" << calib.raw_max
              << ", кути=[" << calib.min_angle_deg << "° .. " << calib.max_angle_deg << "°]"
              << ", зміщення нуля=" << calib.raw_zero_offset << "\n";
    std::cout << "Коефіцієнт EMA alpha = 0.15\n\n";

    // Генератор випадкового шуму АЦП (імітація завад живлення та наведень)
    std::mt19937 rng(42);
    std::normal_distribution<float> noise(0.0f, 18.0f); // Шум із СКО = 18 відліків

    std::cout << "[СИМУЛЯЦІЯ РУХУ СЕРВОПРИВОДУ З ЗАВАДАМИ]\n";
    std::cout << std::setw(6) << "Крок"
              << std::setw(12) << "Ідеальний"
              << std::setw(12) << "Сирий АЦП"
              << std::setw(14) << "Фільтр. АЦП"
              << std::setw(14) << "Кут (°)"
              << std::setw(14) << "Статус" << "\n";
    std::cout << std::string(72, '-') << "\n";

    // Симуляція плавного повороту від 0° до 270° за 20 кроків
    for (int step = 0; step <= 20; ++step) {
        float progress = static_cast<float>(step) / 20.0f;
        
        // Ідеальний відлік АЦП без шуму
        float ideal_raw = static_cast<float>(calib.raw_min) + 
                          progress * static_cast<float>(calib.raw_max - calib.raw_min) +
                          static_cast<float>(calib.raw_zero_offset);

        // Додаємо високочастотний шум АЦП
        float noisy_val = ideal_raw + noise(rng);
        uint16_t raw_adc = static_cast<uint16_t>(std::clamp(noisy_val, 0.0f, 4095.0f));

        // Оновлюємо стан модуля зворотного зв'язку
        SensorStatus status = feedback.update_raw(raw_adc);

        std::cout << std::setw(6) << step
                  << std::setw(12) << static_cast<int>(ideal_raw)
                  << std::setw(12) << raw_adc
                  << std::setw(14) << std::fixed << std::setprecision(1) << feedback.filtered_raw()
                  << std::setw(14) << std::fixed << std::setprecision(2) << feedback.angle_degrees()
                  << std::setw(14) << status_to_string(status) << "\n";
    }

    // 3. Тестування аварійних ситуацій (вихід АЦП за межі калібрувального діапазону)
    std::cout << "\n[ТЕСТУВАННЯ АВАРІЙНИХ СИТУАЦІЙ]\n";

    // Обрив лінії / підтяжка до GND (raw_adc = 50 < raw_min = 200)
    uint16_t fault_underflow = 50;
    SensorStatus status_under = feedback.update_raw(fault_underflow);
    std::cout << "Сирий АЦП = " << fault_underflow 
              << " -> Статус: " << status_to_string(status_under)
              << " | Кут: " << feedback.angle_degrees() << "°\n";

    // Замикання на VCC / насичення АЦП (raw_adc = 4050 > raw_max = 3895)
    uint16_t fault_overflow = 4050;
    SensorStatus status_over = feedback.update_raw(fault_overflow);
    std::cout << "Сирий АЦП = " << fault_overflow 
              << " -> Статус: " << status_to_string(status_over)
              << " | Кут: " << feedback.angle_degrees() << "°\n";

    std::cout << "\nДемонстрація роботи модуля зворотного зв'язку успішно завершена.\n";
    return 0;
}
