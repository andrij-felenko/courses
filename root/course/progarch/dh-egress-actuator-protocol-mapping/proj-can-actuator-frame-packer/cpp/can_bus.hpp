#pragma once

#include <array>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

// ============================================================================
// СТРУКТУРИ ТА ТИПИ ШИНИ CAN
// ============================================================================

/// @brief Двійковий кадр класичної шини CAN (CAN 2.0A/B).
struct CanFrame {
    uint32_t id{0};                ///< Ідентифікатор кадру CAN (11 або 29 бітів)
    uint8_t dlc{8};                ///< Довжина корисного навантаження (Data Length Code)
    std::array<uint8_t, 8> data{}; ///< Фіксований 8-байтний буфер корисного навантаження
};

/// @brief Апаратні коди помилок контролера та шини CAN.
enum class CanBusError {
    BusOff,          ///< Контролер перейшов у стан Bus-Off через переповнення лічильника помилок
    TxQueueFull,     ///< Черга відправки драйвера (TX FIFO) заповнена
    TransmitTimeout, ///< Сплив граничний час очікування передачі кадру в шину
    HardwareFailure  ///< Апаратний збій периферійного трансивера або контролера
};

/// @brief Текстовий опис апаратної помилки шини.
[[nodiscard]] constexpr std::string_view to_string(CanBusError error) noexcept {
    switch (error) {
        case CanBusError::BusOff:
            return "BusOff (Критична кількість помилок на лінії, контролер ізольовано)";
        case CanBusError::TxQueueFull:
            return "TxQueueFull (Буфер передачі переповнено, кадр відхилено)";
        case CanBusError::TransmitTimeout:
            return "TransmitTimeout (Сплив таймаут передачі кадру актуатору)";
        case CanBusError::HardwareFailure:
            return "HardwareFailure (Апаратна відмова контролера або трансивера)";
    }
    return "UnknownCanBusError";
}

/// @brief Абстрактний інтерфейс драйвера шини CAN.
/// Ізолює вихідний адаптер від специфіки платформи (Linux SocketCAN, FreeRTOS HAL, bxCAN).
class ICanBusDriver {
public:
    virtual ~ICanBusDriver() = default;

    /// @brief Відправити двійковий кадр CanFrame у шину.
    /// @param frame Сформований двійковий пакет.
    /// @return Успіх або апаратна помилка CanBusError.
    [[nodiscard]] virtual std::expected<void, CanBusError> transmit(
        const CanFrame& frame) = 0;
};

// ============================================================================
// КОНСТАНТИ СПЕЦИФІКАЦІЇ СИГНАЛІВ DBC (CAN DATABASE)
// ============================================================================

namespace can_dbc {
    /// @brief CAN ID повідомлення керування актуатором заслінки.
    inline constexpr uint32_t kDamperCommandCanId = 0x120;

    /// @brief Довжина корисного навантаження кадру (завжди 8 байтів).
    inline constexpr uint8_t kPayloadLength = 8;

    // --- Параметри кодування цільового кута (Little-Endian / Intel) ---
    inline constexpr double kAngleScale = 0.1;    ///< Крок квантування: 0.1° / LSB
    inline constexpr double kAngleOffset = 0.0;   ///< Адитивне зміщення: 0.0°
    inline constexpr uint16_t kAngleRawMin = 0;   ///< Raw-код для 0.0°: 0
    inline constexpr uint16_t kAngleRawMax = 900; ///< Raw-код для 90.0°: 900

    // --- Параметри кодування швидкості (Big-Endian / Motorola) ---
    inline constexpr double kSpeedScale = 0.1;    ///< Крок квантування швидкості: 0.1 (град/с) / LSB
    inline constexpr double kSpeedOffset = 0.0;   ///< Зміщення: 0.0
    inline constexpr uint16_t kSpeedRawMin = 0;   ///< Raw-код для 0.0 град/с
    inline constexpr uint16_t kSpeedRawMax = 500; ///< Raw-код для 50.0 град/с: 500

    // --- Маски полів кадру ---
    inline constexpr uint8_t kModeMask = 0x0F;    ///< Маска режиму (байт 0, молодші 4 біти)
    inline constexpr uint8_t kCounterMask = 0x0F; ///< 4-бітний rolling counter (діапазон 0..15)
}

// ============================================================================
// РОЗРАХУНОК КОНТРОЛЬНОЇ СУМИ CRC-8 (SAE J1850)
// ============================================================================

/// @brief Обчислення 8-бітної циклічної контрольної суми над корисним навантаженням CAN.
/// Використовує промисловий стандартний поліном SAE J1850 (x^8 + x^4 + x^3 + x^2 + 1 -> 0x1D)
/// для гарантованого виявлення спотворень бітів у фізичній лінії.
class Crc8Calculator {
public:
    static constexpr uint8_t kPolynomial = 0x1D; ///< Твірний поліном SAE J1850
    static constexpr uint8_t kInitValue = 0xFF;  ///< Початкове значення регістра
    static constexpr uint8_t kXorOut = 0xFF;     ///< Фінальна маска інверсії XOR

    /// @brief Обчислити контрольну суму над послідовністю байтів.
    /// @param data Неволодіюче вікно байтів std::span.
    /// @return 8-бітна контрольна сума CRC-8.
    [[nodiscard]] static uint8_t calculate(std::span<const uint8_t> data) noexcept {
        uint8_t crc = kInitValue;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int bit = 0; bit < 8; ++bit) {
                if ((crc & 0x80) != 0) {
                    crc = static_cast<uint8_t>((crc << 1) ^ kPolynomial);
                } else {
                    crc = static_cast<uint8_t>(crc << 1);
                }
            }
        }
        return crc ^ kXorOut;
    }
};
