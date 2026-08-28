/* sensor.hpp — публічний контракт на C++ */
#pragma once
#include <memory>
#include <expected>
#include <cstdint>

enum class SensorError { Timeout, InvalidCrc };

class Sensor {
public:
    explicit Sensor(uint8_t bus_id);
    ~Sensor();

    Sensor(Sensor &&) noexcept;
    Sensor& operator=(Sensor &&) noexcept;

    [[nodiscard]] std::expected<float, SensorError> read_temperature() noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};
