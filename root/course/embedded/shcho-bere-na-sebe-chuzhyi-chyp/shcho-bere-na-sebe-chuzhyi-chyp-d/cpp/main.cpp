#include <cstdint>
#include <span>
#include <expected>
#include <optional>
#include <array>

namespace embedded {

enum class DriverError : uint8_t {
    BusError,
    InvalidDevice,
    Timeout,
    NoEvent
};

enum class EventType : uint8_t {
    None        = 0x00,
    Touch       = 1 << 0,
    LowBattery  = 1 << 1,
    CryptoDone  = 1 << 2
};

struct Point2D {
    uint16_t x{0};
    uint16_t y{0};
};

struct DeviceReport {
    std::optional<Point2D> touch_position;
    std::optional<uint8_t> battery_soc_percent;
    bool                   crypto_operation_complete{false};
};

class CompanionDriver {
public:
    static constexpr uint8_t I2C_ADDRESS = 0x55 << 1;

    struct Registers {
        static constexpr uint8_t Status     = 0x00;
        static constexpr uint8_t TouchData  = 0x01;
        static constexpr uint8_t BatterySoc = 0x05;
        static constexpr uint8_t IntClear   = 0x0F;
    };

    CompanionDriver() = default;

    /* Викликається з апаратного ISR переривання піна INT */
    void notify_interrupt_asserted() noexcept {
        event_pending_ = true;
    }

    [[nodiscard]] bool has_pending_events() const noexcept {
        return event_pending_;
    }

    /**
     * @brief Неблокуюче опитування та зчитування пакетної телеметрії
     */
    [[nodiscard]] std::expected<DeviceReport, DriverError> process_events() noexcept {
        if (!event_pending_) {
            return std::unexpected(DriverError::NoEvent);
        }

        event_pending_ = false;

        uint8_t status_raw{0};
        if (!i2c_read(Registers::Status, std::span<uint8_t, 1>(&status_raw, 1))) {
            return std::unexpected(DriverError::BusError);
        }

        DeviceReport report{};

        /* Обробка сенсорних координат */
        if (status_raw & static_cast<uint8_t>(EventType::Touch)) {
            std::array<uint8_t, 4> raw_buf{};
            if (i2c_read(Registers::TouchData, raw_buf)) {
                uint16_t x = static_cast<uint16_t>((raw_buf[0] << 8) | raw_buf[1]);
                uint16_t y = static_cast<uint16_t>((raw_buf[2] << 8) | raw_buf[3]);
                report.touch_position = Point2D{x, y};
            }
        }

        /* Обробка заряду АКБ */
        if (status_raw & static_cast<uint8_t>(EventType::LowBattery)) {
            uint8_t soc{0};
            if (i2c_read(Registers::BatterySoc, std::span<uint8_t, 1>(&soc, 1))) {
                report.battery_soc_percent = soc;
            }
        }

        report.crypto_operation_complete = (status_raw & static_cast<uint8_t>(EventType::CryptoDone)) != 0;

        /* Квитування переривання (Ack) */
        const uint8_t clear_cmd{0x01};
        std::ignore = i2c_write(Registers::IntClear, std::span<const uint8_t, 1>(&clear_cmd, 1));

        return report;
    }

private:
    volatile bool event_pending_{false};

    /* Апаратні виклики I2C з використанням безпечних std::span */
    bool i2c_read(uint8_t reg, std::span<uint8_t> dest) noexcept;
    bool i2c_write(uint8_t reg, std::span<const uint8_t> src) noexcept;
};

} // namespace embedded
