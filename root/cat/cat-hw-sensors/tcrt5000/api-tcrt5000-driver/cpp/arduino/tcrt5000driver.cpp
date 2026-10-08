#include <Arduino.h>

class Tcrt5000Driver {
public:
    enum Status {
        OK = 0,
        ERR_INVALID_ARG,
        ERR_ADC_FAIL,
        ERR_SATURATION,
        ERR_DISCONNECTED
    };

    struct Config {
        uint8_t analogPin;
        int8_t digitalPin;
        int8_t emitterPin;
        uint16_t thresholdLow;
        uint16_t thresholdHigh;
    };

private:
    Config config_;
    uint16_t lastRawValue_;
    uint16_t filteredValue_;
    bool isCalibrated_;
    bool isInitialized_;

public:
    Tcrt5000Driver() 
        : lastRawValue_(0), filteredValue_(0), isCalibrated_(false), isInitialized_(false) {}

    Status begin(const Config& cfg) {
        config_ = cfg;
        pinMode(config_.analogPin, INPUT);
        
        if (config_.digitalPin >= 0) {
            pinMode(config_.digitalPin, INPUT);
        }
        if (config_.emitterPin >= 0) {
            pinMode(config_.emitterPin, OUTPUT);
            digitalWrite(config_.emitterPin, HIGH); // Вмикаємо світлодіод за замовчуванням
        }
        
        isInitialized_ = true;
        return OK;
    }

    bool isInitialized() const { return isInitialized_; }
};
