// Клас драйвера рівня рідини (C++)
#ifndef LIQUID_LEVEL_SENSOR_HPP
#define LIQUID_LEVEL_SENSOR_HPP

#include <cstdint>

enum class SensorStatus {
    Ok = 0,
    InvalidArg = -1,
    LineBreak = -2,
    ShortCircuit = -3
};

struct SensorConfig {
    uint16_t adcEmpty;
    uint16_t adcFull;
    uint16_t maxHeightMm;
    uint8_t  medianWindow;
    uint8_t  movingAvgWindow;
    float    tempCoef;
    float    tempCalibCelsius;
};

class LiquidLevelSensor {
public:
    LiquidLevelSensor() = default;
    SensorStatus begin(const SensorConfig& config);
private:
    SensorConfig config_;
    bool initialized_{false};
    bool validateConfig(const SensorConfig& config) const;
};

#endif // LIQUID_LEVEL_SENSOR_HPP
