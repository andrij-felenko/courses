/*
 * Системний контракт для C++-прошивки. Ті самі дві речі, що й у C-версії:
 * абстракція шини та результат у величинах SI — і жодного вендорського типу.
 */
#pragma once

#include <cstdint>
#include <span>

namespace sensor {

enum class SensorStatus : std::uint8_t {
    Ok,
    InvalidParameter,
    CommunicationError,
    InvalidDevice,
    Timeout,
    CalibrationInvalid,
    NoResources
};

constexpr const char* to_string(SensorStatus st) noexcept
{
    switch (st) {
    case SensorStatus::Ok:                 return "Ok";
    case SensorStatus::InvalidParameter:   return "InvalidParameter";
    case SensorStatus::CommunicationError: return "CommunicationError";
    case SensorStatus::InvalidDevice:      return "InvalidDevice";
    case SensorStatus::Timeout:            return "Timeout";
    case SensorStatus::CalibrationInvalid: return "CalibrationInvalid";
    case SensorStatus::NoResources:        return "NoResources";
    }
    return "Unknown";
}

struct EnvironmentReading {
    float temperature_celsius{};
    float pressure_hpa{};
};

/*
 * Довжина буфера їде разом із вказівником: std::span не дає драйверу
 * прочитати чи записати за межі виділеної пам'яті, а саме там ховаються
 * найдорожчі помилки у вендорських колбеках.
 */
class II2cBus {
public:
    virtual ~II2cBus() = default;

    II2cBus(const II2cBus&) = delete;
    II2cBus& operator=(const II2cBus&) = delete;

    virtual bool read_registers(std::uint8_t dev_addr, std::uint8_t reg,
                                std::span<std::uint8_t> buffer) = 0;
    virtual bool write_registers(std::uint8_t dev_addr, std::uint8_t reg,
                                 std::span<const std::uint8_t> buffer) = 0;

protected:
    II2cBus() = default;
};

}  // namespace sensor
