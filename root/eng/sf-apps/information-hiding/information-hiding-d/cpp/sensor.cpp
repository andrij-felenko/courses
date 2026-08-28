/* sensor.cpp — прихована таємниця на C++ */
#include "sensor.hpp"
#include <array>

struct Sensor::Impl {
    uint8_t bus_id;
    std::array<uint32_t, 16> calibration_raw{};
    float last_reading{0.0f};

    explicit Impl(uint8_t id) : bus_id(id) {}
};

Sensor::Sensor(uint8_t bus_id) : pimpl_(std::make_unique<Impl>(bus_id)) {}
Sensor::~Sensor() = default;
Sensor::Sensor(Sensor &&) noexcept = default;
Sensor& Sensor::operator=(Sensor &&) noexcept = default;

std::expected<float, SensorError> Sensor::read_temperature() noexcept {
    if (!pimpl_) return std::unexpected(SensorError::Timeout);
    return pimpl_->last_reading;
}
