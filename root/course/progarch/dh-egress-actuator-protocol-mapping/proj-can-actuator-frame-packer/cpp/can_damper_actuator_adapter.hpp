#pragma once

#include "can_bus.hpp"
#include "damper_domain.hpp"

// ============================================================================
// ВИХІДНИЙ АДАПТЕР ДОМЕННОГО ПОРТУ (OUTBOUND ADAPTER)
// ============================================================================

/// @brief Вихідний протокольний адаптер сервоприводу заслінки.
/// Реалізує інтерфейс доменного порту IDamperActuatorPort (C++20).
/// Відповідає за:
/// 1. Квантування доменних величин за коефіцієнтами scale та offset з арифметикою насичення.
/// 2. Побітове розміщення Little-Endian та Big-Endian сигналів у 8-байтному кадрі CAN.
/// 3. Ведення 4-бітного лічильника послідовності (rolling counter 0..15).
/// 4. Обчислення контрольної суми CRC-8 (SAE J1850) над кадровим навантаженням.
/// 5. Трансляцію технічних помилок шини CAN у доменний тип ActuatorError через std::expected.
class CanDamperActuatorAdapter final : public IDamperActuatorPort {
public:
    /// @brief Конструктор адаптера з інжекцією абстрактного драйвера шини CAN.
    /// @param driver Посилання на реалізацію драйвера ICanBusDriver.
    explicit CanDamperActuatorAdapter(ICanBusDriver& driver) noexcept;

    /// @brief Реалізація методу вихідного порту IDamperActuatorPort.
    [[nodiscard]] std::expected<void, ActuatorError> send_command(
        const SetDamperCommand& command) override;

    /// @brief Поточне значення 4-бітного лічильника rolling counter (для перевірки у тестах).
    [[nodiscard]] uint8_t rolling_counter() const noexcept;

private:
    /// @brief Квантування фізичного кута в цілочисельний raw-код за DBC зі saturation.
    [[nodiscard]] static uint16_t quantize_angle(double degrees) noexcept;

    /// @brief Квантування швидкості в цілочисельний raw-код за DBC зі saturation.
    [[nodiscard]] static uint16_t quantize_speed(double speed) noexcept;

    /// @brief Збирання двійкового 8-байтного кадру CanFrame за правилами DBC.
    [[nodiscard]] CanFrame build_can_frame(const SetDamperCommand& command);

    /// @brief Мапінг технічних помилок шини у доменний код ActuatorError.
    [[nodiscard]] static ActuatorError translate_bus_error(CanBusError error) noexcept;

    ICanBusDriver& driver_;
    uint8_t rolling_counter_{0}; ///< 4-бітний циклічний лічильник [0..15]
};
