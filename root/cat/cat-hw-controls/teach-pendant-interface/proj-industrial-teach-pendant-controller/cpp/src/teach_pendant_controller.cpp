#include "teach_pendant_controller.hpp"
#include <cstring>

TeachPendantController::TeachPendantController() = default;

void TeachPendantController::set_state_callback(StateCallback callback) {
    state_callback_ = std::move(callback);
}

void TeachPendantController::set_emergency_callback(EmergencyCallback callback) {
    emergency_callback_ = std::move(callback);
}

EnablingState TeachPendantController::evaluate_enabling_switch(uint8_t pin1, uint8_t pin2) noexcept {
    // Двоканальне декодування трипозиційного вимикача дозволу
    // pin1 = Channel A (NO1), pin2 = Channel B (NO2)
    // 0 = контакт розімкнено, 1 = контакт замкнено
    if (pin1 == 0 && pin2 == 0) {
        return EnablingState::Released; // Стан 1: Вільний
    } 
    if (pin1 == 1 && pin2 == 1) {
        return EnablingState::Enabled;  // Стан 2: Натиснуто до середини (Робота)
    }
    // Будь-яка невідповідність каналів або повне стискання до упору відповідає стану Паніка
    return EnablingState::Panic;         // Стан 3: Панічне стискання (Аварійне розмикання)
}

void TeachPendantController::update(uint32_t current_time_ms,
                                    uint8_t raw_enabling_pin1,
                                    uint8_t raw_enabling_pin2,
                                    uint8_t raw_estop_pin,
                                    const std::array<int16_t, 6>& raw_axes,
                                    uint16_t raw_buttons) {
    // Перевірка інтервалу для цифрового згладжування контактного брязкоту
    if (current_time_ms - last_debounce_time_ms_ < DEBOUNCE_DELAY_MS) {
        return;
    }
    last_debounce_time_ms_ = current_time_ms;

    PendantState previous_state = current_state_;

    // Декодування аварійної кнопки E-Stop (Normally Closed контакт: 0 = тригер/натиснуто)
    current_state_.estop_button = (raw_estop_pin == 0) ? EmergencyState::Triggered : EmergencyState::Normal;

    // Декодування стану трипозиційної кнопки дозволу
    current_state_.enabling_switch = evaluate_enabling_switch(raw_enabling_pin1, raw_enabling_pin2);

    // Оновлення осей джойстика та кнопок
    current_state_.joystick_axes = raw_axes;
    current_state_.button_mask = raw_buttons;
    current_state_.timestamp_ms = current_time_ms;

    // Генерація сповіщення у разі зміни стану E-Stop
    if (previous_state.estop_button != current_state_.estop_button && emergency_callback_) {
        emergency_callback_(current_state_.estop_button);
    }

    // Сповіщення про оновлення стану телеметрії
    if (state_callback_) {
        state_callback_(current_state_);
    }
}

const PendantState& TeachPendantController::get_current_state() const noexcept {
    return current_state_;
}

uint16_t TeachPendantController::calculate_crc16(const uint8_t* data, size_t length) noexcept {
    // Алгоритм CRC16-CCITT (Поліном: 0x1021, Ініціалізація: 0xFFFF)
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= static_cast<uint16_t>(data[i]) << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

PendantPacket TeachPendantController::build_packet() const noexcept {
    PendantPacket packet{};
    packet.header = 0xAA;
    packet.enabling_status = static_cast<uint8_t>(current_state_.enabling_switch);
    packet.estop_status = static_cast<uint8_t>(current_state_.estop_button);
    packet.button_mask = current_state_.button_mask;
    
    for (size_t i = 0; i < 6; ++i) {
        packet.axes[i] = current_state_.joystick_axes[i];
    }
    packet.timestamp_ms = current_state_.timestamp_ms;

    // Обчислення CRC16 для всього кадру за винятком самого поля crc16
    constexpr size_t data_len = sizeof(PendantPacket) - sizeof(uint16_t);
    packet.crc16 = calculate_crc16(reinterpret_cast<const uint8_t*>(&packet), data_len);

    return packet;
}
