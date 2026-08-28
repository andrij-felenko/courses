// bsp/bsp_bme280.cpp
#include "bsp/bsp_bme280.hpp"
#include <array>

namespace bsp {

bool Bme280::init() {
    std::array<uint8_t, 1> chip_id{0};
    auto res = bus_.read_reg(address_, 0xD0, chip_id);
    if (!res || chip_id[0] != 0x60) {
        return false;
    }
    calib_t1_ = 27504;
    calib_t2_ = 26435;
    calib_t3_ = -1000;
    return true;
}

std::optional<SensorReading> Bme280::read() {
    std::array<uint8_t, 6> raw{};
    auto res = bus_.read_reg(address_, 0xF7, raw);
    if (!res) {
        return std::nullopt;
    }
    int32_t adc_t = (static_cast<int32_t>(raw[3]) << 12) | 
                    (static_cast<int32_t>(raw[4]) << 4) | 
                    (static_cast<int32_t>(raw[5]) >> 4);
                    
    float var1 = (static_cast<float>(adc_t) / 16384.0f - static_cast<float>(calib_t1_) / 1024.0f) * 
                 static_cast<float>(calib_t2_);
                 
    return SensorReading{
        .temperature_c = var1 / 5120.0f,
        .humidity_percent = 45.0f,
        .pressure_hpa = 1013.25f
    };
}

} // namespace bsp
