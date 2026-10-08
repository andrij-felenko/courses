#include <Arduino.h>

enum class MQ7State {
    Uninit,
    HighHeat,
    LowHeat,
    Fault
};

enum class MQ7Error {
    None,
    InvalidArg,
    HeaterFault,
    TimingJitter
};

class MQ7Driver {
public:
    struct Config {
        uint8_t adcPin;
        uint8_t pwmPin;
        float vRefMv;
        uint32_t adcMax;
        float rlKohm;
        float r0Kohm;
        uint32_t highHeatMs;
        uint32_t lowHeatMs;
    };

private:
    Config config_;
    MQ7State state_;
    uint32_t lastStateChangeMs_;
    uint32_t lastTickMs_;
    uint16_t rawAdc_;
    float rsKohm_;
    float coPpm_;
    bool dataReady_;
    MQ7Error error_;

public:
    MQ7Driver() : state_(MQ7State::Uninit), dataReady_(false), error_(MQ7Error::None) {}

    bool begin(const Config& cfg) {
        config_ = cfg;
        pinMode(config_.pwmPin, OUTPUT);
        // Запускаємо фазу високого нагріву (100% ШІМ = 255)
        analogWrite(config_.pwmPin, 255);
        
        state_ = MQ7State::HighHeat;
        lastStateChangeMs_ = millis();
        lastTickMs_ = millis();
        dataReady_ = false;
        return true;
    }
};
