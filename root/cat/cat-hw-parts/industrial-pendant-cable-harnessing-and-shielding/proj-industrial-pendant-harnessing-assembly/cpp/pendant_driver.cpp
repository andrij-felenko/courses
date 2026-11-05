/**
 * @file pendant_driver.cpp
 * @brief Реалізація методів класу PendantDriver.
 */

#include "pendant_driver.hpp"

namespace IndustrialPendant {

PendantDriver::PendantDriver(DebounceTime debounceInterval)
    : debounce_interval_(debounceInterval) {}

bool PendantDriver::filterButton(DebounceEntry& entry, bool rawInput, std::chrono::steady_clock::time_point now) {
    if (rawInput != entry.last_raw_state) {
        entry.last_raw_state = rawInput;
        entry.last_change_time = now;
    }

    if (std::chrono::duration_cast<DebounceTime>(now - entry.last_change_time) >= debounce_interval_) {
        entry.stable_state = rawInput;
    }

    return entry.stable_state;
}

void PendantDriver::update(bool rawUp, bool rawDown, bool rawLeft, bool rawRight, bool rawStart, bool rawEstop) {
    const auto now = std::chrono::steady_clock::now();

    // Застосування фільтра антибрязкання до звичайних кнопок
    current_state_.up = filterButton(db_up_, rawUp, now) ? ButtonState::Pressed : ButtonState::Released;
    current_state_.down = filterButton(db_down_, rawDown, now) ? ButtonState::Pressed : ButtonState::Released;
    current_state_.left = filterButton(db_left_, rawLeft, now) ? ButtonState::Pressed : ButtonState::Released;
    current_state_.right = filterButton(db_right_, rawRight, now) ? ButtonState::Pressed : ButtonState::Released;
    current_state_.start = filterButton(db_start_, rawStart, now) ? ButtonState::Pressed : ButtonState::Released;

    // Моніторинг лінії аварійної зупинки (NC ланцюг: true = нормально замкнено, false = обрив/натиснуто)
    bool stableEstop = filterButton(db_estop_, rawEstop, now);
    current_state_.estop = stableEstop ? ButtonState::Pressed : ButtonState::Released;

    if (!stableEstop) {
        // Якщо ланцюг розімкнувся (аварія або обрив дільниці кабелю), переводимо систему в E-Stop
        current_state_.status = SystemStatus::EstopTriggered;
        // При аварії примусово скидаємо команди руху
        current_state_.up = ButtonState::Released;
        current_state_.down = ButtonState::Released;
        current_state_.left = ButtonState::Released;
        current_state_.right = ButtonState::Released;
        current_state_.start = ButtonState::Released;
    } else {
        current_state_.status = SystemStatus::Normal;
    }
}

PendantState PendantDriver::getState() const noexcept {
    return current_state_;
}

bool PendantDriver::isEstopActive() const noexcept {
    return current_state_.status == SystemStatus::EstopTriggered;
}

uint16_t PendantDriver::calculateCRC16(const uint8_t* data, size_t length) noexcept {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= static_cast<uint16_t>(data[i]);
        for (uint8_t j = 0; j < 8; ++j) {
            if ((crc & 0x0001) != 0) {
                crc = static_cast<uint16_t>((crc >> 1) ^ 0xA001);
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

size_t PendantDriver::serializeFrame(std::array<uint8_t, 16>& buffer) const noexcept {
    // Формат фрейму RS-485:
    // [0]: Синхронізація (Header) = 0xAA
    // [1]: Адреса пристрою = 0x01
    // [2]: Байт стану кнопок (біт 0: Up, біт 1: Down, біт 2: Left, біт 3: Right, біт 4: Start, біт 5: E-Stop)
    // [3]: Статус системи (SystemStatus)
    // [4..5]: CRC-16 (Modbus)
    
    buffer[0] = 0xAA;
    buffer[1] = 0x01;

    uint8_t buttonsByte = 0;
    if (current_state_.up == ButtonState::Pressed) buttonsByte |= (1 << 0);
    if (current_state_.down == ButtonState::Pressed) buttonsByte |= (1 << 1);
    if (current_state_.left == ButtonState::Pressed) buttonsByte |= (1 << 2);
    if (current_state_.right == ButtonState::Pressed) buttonsByte |= (1 << 3);
    if (current_state_.start == ButtonState::Pressed) buttonsByte |= (1 << 4);
    if (current_state_.estop == ButtonState::Pressed) buttonsByte |= (1 << 5);

    buffer[2] = buttonsByte;
    buffer[3] = static_cast<uint8_t>(current_state_.status);

    uint16_t crc = calculateCRC16(buffer.data(), 4);
    buffer[4] = static_cast<uint8_t>(crc & 0xFF);
    buffer[5] = static_cast<uint8_t>((crc >> 8) & 0xFF);

    return 6;
}

} // namespace IndustrialPendant
