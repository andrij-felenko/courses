#pragma once

#include <cstdint>

// Апаратна абстракція для керування помпою та часом
class IWaterPumpHardware {
public:
    virtual ~IWaterPumpHardware() = default;
    
    // Встановити коефіцієнт заповнення ШІМ (0-100)
    virtual void SetPWM(uint8_t dutyCycle) = 0;
    
    // Отримати поточний системний час у мілісекундах
    virtual uint32_t GetTimeMs() = 0;
};

// Конфігурація помпи
struct WaterPumpConfig {
    uint32_t softStartDurationMs = 1000;
    uint32_t maxRunTimeMs = 60000;
    uint8_t targetDutyCycle = 100;
};

class WaterPump {
public:
    enum class State {
        Idle,
        Starting,
        Running
    };

    WaterPump(IWaterPumpHardware& hw, const WaterPumpConfig& config);
    
    void Start();
    void Stop();
    void Update(); // Викликається в головному циклі

    State GetState() const { return currentState; }

private:
    IWaterPumpHardware& hardware;
    WaterPumpConfig config;
    State currentState;
    
    uint32_t startTimeMs;
    uint32_t softStartStartMs;
    uint8_t currentDuty;
};
