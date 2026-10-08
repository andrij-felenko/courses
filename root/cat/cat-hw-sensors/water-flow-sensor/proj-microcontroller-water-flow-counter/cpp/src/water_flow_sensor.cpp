#include "water_flow_sensor.hpp"

// Ініціалізація статичних членів класу
std::atomic<uint32_t> WaterFlowSensor::pulse_count_{0};
WaterFlowSensor* WaterFlowSensor::instance_ = nullptr;

WaterFlowSensor::WaterFlowSensor(uint8_t gpio_pin, float k_factor)
    : pin_(gpio_pin), k_factor_(k_factor > 0.0f ? k_factor : 7.5f) {
    instance_ = this;
}

void WaterFlowSensor::begin() {
    pulse_count_.store(0, std::memory_order_relaxed);
    last_update_ms_ = 0;
    current_flow_rate_ = 0.0f;
    total_volume_liters_ = 0.0;
    total_pulse_accumulator_ = 0;
}

void IRAM_ATTR WaterFlowSensor::handle_interrupt() {
    // Атомарне збільшення лічильника імпульсів при кожному зрізі сигналу турбіни
    pulse_count_.fetch_add(1, std::memory_order_relaxed);
}

void WaterFlowSensor::update(uint32_t current_time_ms) {
    if (last_update_ms_ == 0) {
        last_update_ms_ = current_time_ms;
        return;
    }

    uint32_t elapsed_ms = current_time_ms - last_update_ms_;
    // Розраховуємо витрату не частіше ніж раз на 1000 мс для усереднення та стабільності
    if (elapsed_ms < 1000) {
        return;
    }

    // Атомарно отримуємо накопичену кількість імпульсів за інтервал та скидаємо лічильник ISR
    uint32_t current_pulses = pulse_count_.exchange(0, std::memory_order_relaxed);
    total_pulse_accumulator_ += current_pulses;

    // Розрахунок частоти імпульсів F (Гц) = імпульси / секунди
    float elapsed_seconds = static_cast<float>(elapsed_ms) / 1000.0f;
    float pulse_frequency = static_cast<float>(current_pulses) / elapsed_seconds;

    // Формула витрати: Q (л/хв) = F / K-factor
    current_flow_rate_ = pulse_frequency / k_factor_;

    // Розрахунок накопиченого об'єму за інтервал:
    // Об'єм (літри) = імпульси / (K-factor * 60 сек)
    double liters_this_interval = static_cast<double>(current_pulses) / (k_factor_ * 60.0);
    total_volume_liters_ += liters_this_interval;

    last_update_ms_ = current_time_ms;
}

FlowMetrics WaterFlowSensor::get_metrics() const {
    return FlowMetrics{
        current_flow_rate_,
        total_volume_liters_,
        total_pulse_accumulator_
    };
}

void WaterFlowSensor::set_k_factor(float k_factor) {
    if (k_factor > 0.0f) {
        k_factor_ = k_factor;
    }
}

void WaterFlowSensor::reset_total_volume() {
    total_volume_liters_ = 0.0;
    total_pulse_accumulator_ = 0;
}
