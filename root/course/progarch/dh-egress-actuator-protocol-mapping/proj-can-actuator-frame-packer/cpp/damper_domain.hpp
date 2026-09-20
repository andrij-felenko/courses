#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <expected>
#include <string_view>

// ============================================================================
// ДОМЕННІ ПОМИЛКИ ТА СТАТУСИ АКТУАТОРА
// ============================================================================

/// @brief Доменні коди помилок актуатора заслінки.
/// Доменне ядро оперує виключно цими поняттями, нічого не знаючи
/// про апаратні статуси контролера CAN, помилки арбітражу чи тайм-аути сокетів.
enum class ActuatorError {
    BusFailure,       ///< Апаратна відмова шини зв'язку (стан Bus-Off контролера)
    DeviceOffline,    ///< Пристрій не відповідає або буфер відправки переповнений
    MechanicalStall,  ///< Механічне заклинювання або аварійний перегрів сервоприводу
    ProtocolCorrupt,  ///< Порушення цілісності протоколу (збій CRC або послідовності)
    InvalidParameter  ///< Неприпустиме значення параметра (вихід за фізичні межі)
};

/// @brief Текстовий опис доменної помилки для логування та діагностики.
[[nodiscard]] constexpr std::string_view to_string(ActuatorError error) noexcept {
    switch (error) {
        case ActuatorError::BusFailure:
            return "BusFailure (Апаратна відмова шини зв'язку CAN)";
        case ActuatorError::DeviceOffline:
            return "DeviceOffline (Актуатор недосяжний або буфер передавача переповнено)";
        case ActuatorError::MechanicalStall:
            return "MechanicalStall (Механічне блокування заслінки / аварійне навантаження)";
        case ActuatorError::ProtocolCorrupt:
            return "ProtocolCorrupt (Порушення цілісності кадру або розсинхронізація лічильника)";
        case ActuatorError::InvalidParameter:
            return "InvalidParameter (Параметр виходить за допустимі межі безпеки)";
    }
    return "UnknownError";
}

// ============================================================================
// ТИПІЗОВАНІ ОБ'ЄКТИ-ЗНАЧЕННЯ (VALUE OBJECTS)
// ============================================================================

/// @brief Об'єкт-значення (Value Object) цільового кута повороту повітряної заслінки.
/// Забезпечує фундаментальний інваріант: кут завжди перебуває в межах [0.0°, 90.0°]
/// та квантується з кроком 0.1° для запобігання похибкам неперервних чисел з плаваючою комою.
class DamperAngle {
public:
    static constexpr double kMinDegrees = 0.0;    ///< Повністю перекрита заслінка
    static constexpr double kMaxDegrees = 90.0;   ///< Повністю відкрита заслінка
    static constexpr double kStepDegrees = 0.1;   ///< Фізичний крок квантування кута

    /// @brief Безпечний конструктор з автоматичним насиченням (clamping) до діапазону [0°, 90°].
    explicit constexpr DamperAngle(double degrees) noexcept
        : degrees_(quantize(std::clamp(degrees, kMinDegrees, kMaxDegrees))) {}

    /// @brief Фабричний метод зі строгою валідацією без неявного насичення.
    /// Повертає ActuatorError::InvalidParameter, якщо передано некоректне значення або NaN.
    [[nodiscard]] static std::expected<DamperAngle, ActuatorError> create(double degrees) noexcept {
        if (std::isnan(degrees) || degrees < kMinDegrees || degrees > kMaxDegrees) {
            return std::unexpected(ActuatorError::InvalidParameter);
        }
        return DamperAngle(degrees);
    }

    /// @brief Отримати значення кута у градусах.
    [[nodiscard]] constexpr double degrees() const noexcept {
        return degrees_;
    }

    [[nodiscard]] constexpr bool operator==(const DamperAngle& other) const noexcept {
        return std::abs(degrees_ - other.degrees_) < (kStepDegrees / 2.0);
    }

private:
    [[nodiscard]] static constexpr double quantize(double val) noexcept {
        // Квантування до найближчого дискрету kStepDegrees (0.1°)
        const auto discrete_steps = static_cast<int64_t>(val * 10.0 + 0.5);
        return static_cast<double>(discrete_steps) / 10.0;
    }

    double degrees_{kMinDegrees};
};

/// @brief Типізований об'єкт-значення режиму роботи заслінки.
/// Захищає від некоректних конфігурацій протоколу на рівні системи типів C++.
class DamperMode {
public:
    enum class Type : uint8_t {
        Normal = 0x01,        ///< Штатне регулювання повітряного потоку
        Calibration = 0x02,   ///< Калібрування кінцевих положень вихідного вала
        EmergencyStop = 0x03  ///< Аварійна зупинка у поточному положенні
    };

    constexpr DamperMode() noexcept : type_(Type::Normal) {}
    constexpr explicit DamperMode(Type type) noexcept : type_(type) {}

    [[nodiscard]] static constexpr DamperMode normal() noexcept {
        return DamperMode(Type::Normal);
    }

    [[nodiscard]] static constexpr DamperMode calibration() noexcept {
        return DamperMode(Type::Calibration);
    }

    [[nodiscard]] static constexpr DamperMode emergency_stop() noexcept {
        return DamperMode(Type::EmergencyStop);
    }

    [[nodiscard]] constexpr Type type() const noexcept { return type_; }
    [[nodiscard]] constexpr uint8_t raw_value() const noexcept { return static_cast<uint8_t>(type_); }
    [[nodiscard]] constexpr bool is_normal() const noexcept { return type_ == Type::Normal; }
    [[nodiscard]] constexpr bool is_calibration() const noexcept { return type_ == Type::Calibration; }
    [[nodiscard]] constexpr bool is_emergency() const noexcept { return type_ == Type::EmergencyStop; }

    [[nodiscard]] constexpr std::string_view name() const noexcept {
        switch (type_) {
            case Type::Normal: return "Normal";
            case Type::Calibration: return "Calibration";
            case Type::EmergencyStop: return "EmergencyStop";
        }
        return "Unknown";
    }

    [[nodiscard]] constexpr bool operator==(const DamperMode& other) const noexcept = default;

private:
    Type type_{Type::Normal};
};

/// @brief Доменна команда керування сервоприводом заслінки.
/// Формується логікою мікроклімату і не містить жодних апаратних чи протокольних деталей.
struct SetDamperCommand {
    DamperAngle target_angle;              ///< Цільовий кут повороту [0.0°, 90.0°]
    DamperMode mode{DamperMode::normal()}; ///< Режим роботи сервоприводу
    double target_speed_deg_per_sec{15.0}; ///< Швидкість переміщення заслінки (град/с)
};

// ============================================================================
// ВИХІДНИЙ КЕРОВАНИЙ ПОРТ (DRIVEN PORT)
// ============================================================================

/// @brief Інтерфейс вихідного порту для взаємодії з актуатором заслінки.
/// Визначає контракт передачі команд позиціонування без прив'язки до типу шини
/// (CAN, Modbus, BACnet) та повертає монадичний результат std::expected.
class IDamperActuatorPort {
public:
    virtual ~IDamperActuatorPort() = default;

    /// @brief Відправити доменну команду актуатору.
    /// @param command Валідована доменна команда позиціонування.
    /// @return Успіх (void) або типізована доменна помилка ActuatorError.
    [[nodiscard]] virtual std::expected<void, ActuatorError> send_command(
        const SetDamperCommand& command) = 0;
};
