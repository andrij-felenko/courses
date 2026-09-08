#include "PowerMonitor.h"

PowerMonitor::PowerMonitor(uint8_t alert_pin, uint8_t cutoff_pin, float max_current_ma, float max_voltage_v)
    : alert_pin_(alert_pin),
      cutoff_pin_(cutoff_pin),
      max_current_ma_(max_current_ma),
      max_voltage_v_(max_voltage_v) {}

PowerMonitor::~PowerMonitor() {
    // Безпечне розмикання кола живлення при знищенні об'єкта (RAII)
    output_enabled_ = false;
}

bool PowerMonitor::begin() {
    output_enabled_ = true;
    state_ = ProtectionState::Normal;
    last_sample_time_ms_ = 0;
    return true;
}

void PowerMonitor::pollSensors() {
    // Емуляція зчитування з реального сенсора INA219
    metrics_.voltage_v = 5.02f;
    metrics_.current_ma = 145.0f;
    metrics_.power_mw = metrics_.voltage_v * metrics_.current_ma;
}

void PowerMonitor::evaluateSafety() {
    if (metrics_.current_ma > max_current_ma_) {
        tripProtection(ProtectionState::TrippedOverCurrent);
    } else if (metrics_.voltage_v > max_voltage_v_) {
        tripProtection(ProtectionState::TrippedOverVoltage);
    } else if (metrics_.current_ma > (max_current_ma_ * 0.85f)) {
        state_ = ProtectionState::Warning;
    } else {
        state_ = ProtectionState::Normal;
    }
}

void PowerMonitor::tripProtection(ProtectionState reason) {
    state_ = reason;
    output_enabled_ = false; // Негайне аварійне відключення навантаження
}

void PowerMonitor::reset() {
    output_enabled_ = true;
    state_ = ProtectionState::Normal;
}

void PowerMonitor::update(uint32_t current_time_ms) {
    if (current_time_ms - last_sample_time_ms_ >= 50) { // Опитування кожні 50 мс
        last_sample_time_ms_ = current_time_ms;
        if (output_enabled_) {
            pollSensors();
            evaluateSafety();
        }
    }
}
