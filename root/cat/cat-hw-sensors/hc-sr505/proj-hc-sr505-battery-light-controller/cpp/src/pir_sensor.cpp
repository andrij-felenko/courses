#include "pir_sensor.hpp"
#include <iostream>

PirSensor::PirSensor(uint8_t gpio_pin, uint32_t debounce_ms)
    : pin_(gpio_pin), debounce_ms_(debounce_ms) {}

void PirSensor::init() {
    // Налаштування цифрового виводу GPIO як входу з апаратним EXTI за обома фронтами
    is_active_.store(false, std::memory_order_relaxed);
    motion_event_pending_.store(false, std::memory_order_relaxed);
    last_interrupt_time_.store(0, std::memory_order_relaxed);
    
    std::cout << "[PirSensor] Ініціалізовано GPIO pin " << static_cast<int>(pin_)
              << " для HC-SR505 (EXTI RISING/FALLING, debounce=" << debounce_ms_ << "ms)\n";
}

void PirSensor::handleInterrupt(bool current_pin_level, uint32_t current_time_ms) {
    uint32_t last_time = last_interrupt_time_.load(std::memory_order_relaxed);
    
    // Програмна фільтрація коротких імпульсів дребезгу
    if ((current_time_ms - last_time) < debounce_ms_) {
        return;
    }
    
    last_interrupt_time_.store(current_time_ms, std::memory_order_relaxed);
    
    if (current_pin_level) {
        // Високий рівень сигналу OUT — виявлено ІЧ-випромінювання рухомого об'єкта
        is_active_.store(true, std::memory_order_release);
        motion_event_pending_.store(true, std::memory_order_release);
    } else {
        // Сигнал OUT опустився у LOW — власна затримка HC-SR505 завершилася
        is_active_.store(false, std::memory_order_release);
    }
}

bool PirSensor::isMotionDetected() const {
    return is_active_.load(std::memory_order_acquire);
}

bool PirSensor::consumeMotionEvent() {
    // Атомарна перевірка та скидання прапорця нової події для ISR-безпеки
    return motion_event_pending_.exchange(false, std::memory_order_acq_rel);
}
