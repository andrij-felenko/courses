#include "can_damper_actuator_adapter.hpp"
#include <algorithm>
#include <cmath>

CanDamperActuatorAdapter::CanDamperActuatorAdapter(ICanBusDriver& driver) noexcept
    : driver_(driver), rolling_counter_(0) {}

uint8_t CanDamperActuatorAdapter::rolling_counter() const noexcept {
    return rolling_counter_;
}

uint16_t CanDamperActuatorAdapter::quantize_angle(double degrees) noexcept {
    // Арифметика насичення (clamping): запобігаємо wrap-around переповненню розрядної сітки
    const double clamped = std::clamp(degrees, DamperAngle::kMinDegrees, DamperAngle::kMaxDegrees);

    // Пряме афінне перетворення за формулою DBC: raw = round((физ_величина - offset) / scale)
    const double raw = (clamped - can_dbc::kAngleOffset) / can_dbc::kAngleScale;
    const auto raw_int = static_cast<uint32_t>(std::round(raw));

    return static_cast<uint16_t>(std::clamp<uint32_t>(raw_int, can_dbc::kAngleRawMin, can_dbc::kAngleRawMax));
}

uint16_t CanDamperActuatorAdapter::quantize_speed(double speed) noexcept {
    const double clamped = std::clamp(speed, 0.0, 50.0);
    const double raw = (clamped - can_dbc::kSpeedOffset) / can_dbc::kSpeedScale;
    const auto raw_int = static_cast<uint32_t>(std::round(raw));

    return static_cast<uint16_t>(std::clamp<uint32_t>(raw_int, can_dbc::kSpeedRawMin, can_dbc::kSpeedRawMax));
}

CanFrame CanDamperActuatorAdapter::build_can_frame(const SetDamperCommand& command) {
    CanFrame frame;
    frame.id = can_dbc::kDamperCommandCanId; // CAN ID: 0x120
    frame.dlc = can_dbc::kPayloadLength;     // DLC: 8 байтів
    frame.data.fill(0x00);

    // Байт 0: Режим роботи заслінки (DamperMode)
    frame.data[0] = command.mode.raw_value() & can_dbc::kModeMask;

    // Байти 1..2: Цільовий кут заслінки (Little-Endian / Intel)
    // Молодший байт (LSB) розташовується у молодшому індексі (байт 1),
    // старший байт (MSB) — у наступному (байт 2).
    const uint16_t raw_angle = quantize_angle(command.target_angle.degrees());
    frame.data[1] = static_cast<uint8_t>(raw_angle & 0xFF);
    frame.data[2] = static_cast<uint8_t>((raw_angle >> 8) & 0xFF);

    // Байти 3..4: Швидкість переміщення (Big-Endian / Motorola)
    // Старший байт (MSB) розташовується першим (байт 3),
    // молодший байт (LSB) — другим (байт 4).
    const uint16_t raw_speed = quantize_speed(command.target_speed_deg_per_sec);
    frame.data[3] = static_cast<uint8_t>((raw_speed >> 8) & 0xFF);
    frame.data[4] = static_cast<uint8_t>(raw_speed & 0xFF);

    // Байт 5: Резервний байт (0x00)
    frame.data[5] = 0x00;

    // Байт 6: 4-бітний циклічний лічильник rolling counter [0..15]
    frame.data[6] = static_cast<uint8_t>(rolling_counter_ & can_dbc::kCounterMask);

    // Байт 7: Контрольна сума CRC-8 (SAE J1850) над байтами 0..6
    std::span<const uint8_t, 7> payload_span(frame.data.data(), 7);
    frame.data[7] = Crc8Calculator::calculate(payload_span);

    return frame;
}

std::expected<void, ActuatorError> CanDamperActuatorAdapter::send_command(
    const SetDamperCommand& command) {
    // 1. Формуємо бінарний кадр за специфікацією DBC
    const CanFrame frame = build_can_frame(command);

    // 2. Відправляємо двійковий пакет у шину через абстракцію драйвера
    const auto transmit_result = driver_.transmit(frame);
    if (!transmit_result) {
        // У разі відмови апаратної шини транслюємо специфічний збій у доменну помилку
        return std::unexpected(translate_bus_error(transmit_result.error()));
    }

    // 3. Інкрементуємо 4-бітний rolling counter (перехід 15 -> 0) лише після успішної передачі
    rolling_counter_ = static_cast<uint8_t>((rolling_counter_ + 1) & can_dbc::kCounterMask);

    return {};
}

ActuatorError CanDamperActuatorAdapter::translate_bus_error(CanBusError error) noexcept {
    switch (error) {
        case CanBusError::BusOff:
            return ActuatorError::BusFailure;
        case CanBusError::TxQueueFull:
        case CanBusError::TransmitTimeout:
            return ActuatorError::DeviceOffline;
        case CanBusError::HardwareFailure:
            return ActuatorError::BusFailure;
    }
    return ActuatorError::BusFailure;
}
