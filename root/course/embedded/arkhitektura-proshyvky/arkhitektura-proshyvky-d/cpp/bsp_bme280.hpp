// bsp/bsp_bme280.hpp
#pragma once
#include "hal/hal_i2c.hpp"
#include <optional>

namespace bsp {

struct EnvironmentalData {
    float temperature_c{0.0f};
    float humidity_rh{0.0f};
    float pressure_hpa{0.0f};
};

class Bme280Driver {
public:
    Bme280Driver(hal::II2cBus& bus, uint8_t address = 0x76)
        : bus_(bus), address_(address) {}

    bool init();
    std::optional<EnvironmentalData> measure();

private:
    hal::II2cBus& bus_;
    uint8_t address_;
    uint16_t dig_t1_{0};
    int16_t dig_t2_{0};
    int16_t dig_t3_{0};
};

} // namespace bsp
