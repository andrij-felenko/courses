#ifndef HUMIDITY_SENSOR_HPP
#define HUMIDITY_SENSOR_HPP

#include <cstdint>
#include <chrono>
#include <expected>
#include <span>
#include <functional>

namespace hardware {

enum class Precision : uint8_t {
    Low = 0,
    Medium,
    High
};

enum class DriverError : int8_t {
    CommunicationFailed = -1,
    ChecksumMismatch    = -2,
    OutOfBounds         = -3,
    HeaterFault         = -4,
    Timeout             = -5
};

struct SensorReadings {
    float temperature_c;
    float relative_humidity;
    float dew_point_c;
    float vapor_pressure_pa;
    float absolute_humidity_g_m3;
};

using I2CWriteFn = std::function<int(uint8_t addr, std::span<const uint8_t> data)>;
using I2CReadFn  = std::function<int(uint8_t addr, std::span<uint8_t> data)>;
using DelayFn    = std::function<void(std::chrono::milliseconds d)>;

class HumiditySensorDevice {
public:
    struct Config {
        uint8_t i2c_address{0x44};
        std::chrono::milliseconds timeout{100};
        Precision precision{Precision::High};
        bool auto_heater{true};
        I2CWriteFn write_fn{};
        I2CReadFn  read_fn{};
        DelayFn    delay_fn{};
    };

    explicit HumiditySensorDevice(Config cfg) : cfg_(std::move(cfg)) {}

    [[nodiscard]] std::expected<void, DriverError> initialize() noexcept;
    [[nodiscard]] std::expected<SensorReadings, DriverError> read_metrics() noexcept;
    [[nodiscard]] std::expected<void, DriverError> set_heater_state(bool enable) noexcept;

    [[nodiscard]] static bool verify_crc8(std::span<const uint8_t, 2> bytes, uint8_t checksum) noexcept;

private:
    Config cfg_;
};

} // namespace hardware

#endif // HUMIDITY_SENSOR_HPP
