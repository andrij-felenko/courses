// Конфігурація та клас помпи на C++
struct PumpConfig {
    uint8_t  gpioPin;
    uint8_t  pwmChannel;
    uint32_t pwmFreqHz;
    uint8_t  deadbandDuty;
    float    flowRateMaxMlS;
    uint32_t maxContinuousMs;
};

class WaterPump {
public:
    enum class Error { Ok = 0, InvalidParam };
    Error init(const PumpConfig &config);
};
