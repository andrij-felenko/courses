// bsp/bsp_bme280.hpp
#pragma once
#include "hal/hal_i2c.hpp"
#include <optional>

namespace bsp {

struct SensorReading {
    float temperature_c{0.0f};
    float humidity_percent{0.0f};
    float pressure_hpa{0.0f};
};

class Bme280 {
public:
    explicit Bme280(hal::II2cBus& bus, uint8_t address = 0x76) 
        : bus_(bus), address_(address) {}

    bool init();
    std::optional<SensorReading> read();

private:
    hal::II2cBus& bus_;
    uint8_t address_;
    uint16_t calib_t1_{0};
    int16_t calib_t2_{0};
    int16_t calib_t3_{0};
};

} // namespace bsp
