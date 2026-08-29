#pragma once

#include <cstdint>
#include <expected>

namespace bringup {

// Помилка транзакції. Замість -1 та errno — тип, який неможливо не перевірити.
enum class BusError : std::uint8_t {
    Nack,    // ведений не підтвердив адресу або байт
    Timeout  // лінія зайнята, START фізично не сформувався
};

using WriteResult = std::expected<void, BusError>;
using ReadResult = std::expected<std::uint8_t, BusError>;

// Контракт шини. На залізі — периферія I2C, на стенді — SimulatedSensor.
class I2cBus {
public:
    virtual ~I2cBus() = default;

    virtual WriteResult write(std::uint8_t dev_addr, std::uint8_t reg, std::uint8_t value) = 0;
    virtual ReadResult read(std::uint8_t dev_addr, std::uint8_t reg) = 0;

    // Дев'ять тактів SCL: звільняє SDA, затиснуту веденим посеред байта.
    virtual void recover() = 0;
};

}  // namespace bringup
