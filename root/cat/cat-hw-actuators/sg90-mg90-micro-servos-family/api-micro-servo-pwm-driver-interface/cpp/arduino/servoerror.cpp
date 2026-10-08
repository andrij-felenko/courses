// C++ (Arduino / Object-Oriented Framework)
#include <stdint.h>

enum class ServoError {
    Ok = 0,
    InvalidArg = -1,
    HwInitFail = -2
};

struct ServoConfig {
    uint8_t pin;
    uint16_t usMin = 500;
    uint16_t usMax = 2500;
    float angleMin = 0.0f;
    float angleMax = 180.0f;
    int16_t trimOffsetUs = 0;
};

class ServoDriver {
private:
    ServoConfig config_;
    bool isInitialized_ = false;
    uint16_t currentUs_ = 1500;

public:
    ServoDriver() = default;

    ServoError begin(const ServoConfig& config) {
        if (config.usMin >= config.usMax || config.usMin < 400 || config.usMax > 2600) {
            return ServoError::InvalidArg;
        }
        if (config.angleMin >= config.angleMax) {
            return ServoError::InvalidArg;
        }

        config_ = config;
        uint16_t neutralUs = config_.usMin + (config_.usMax - config_.usMin) / 2;
        currentUs_ = neutralUs + config_.trimOffsetUs;

        // Конфігурування апаратного таймера ШІМ для обраного піна
        // pinMode(config_.pin, OUTPUT);
        // hardware_pwm_write_us(config_.pin, currentUs_);

        isInitialized_ = true;
        return ServoError::Ok;
    }

    bool isInitialized() const { return isInitialized_; }
};
