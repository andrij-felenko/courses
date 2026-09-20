#include "WaterPump.hpp"

WaterPump::WaterPump(IWaterPumpHardware& hw, const WaterPumpConfig& config)
    : hardware(hw), config(config), currentState(State::Idle), 
      startTimeMs(0), softStartStartMs(0), currentDuty(0) {
    hardware.SetPWM(0);
}

void WaterPump::Start() {
    if (currentState != State::Idle) return;
    
    uint32_t currentTime = hardware.GetTimeMs();
    
    currentState = State::Starting;
    softStartStartMs = currentTime;
    startTimeMs = currentTime;
    currentDuty = 0;
}

void WaterPump::Stop() {
    currentState = State::Idle;
    currentDuty = 0;
    hardware.SetPWM(0);
}

void WaterPump::Update() {
    if (currentState == State::Idle) return;
    
    uint32_t currentTime = hardware.GetTimeMs();
    
    // Перевірка захисного таймера
    if (currentTime - startTimeMs >= config.maxRunTimeMs) {
        Stop();
        return;
    }
    
    // Кінцевий автомат плавного пуску
    if (currentState == State::Starting) {
        uint32_t elapsed = currentTime - softStartStartMs;
        
        if (elapsed >= config.softStartDurationMs) {
            currentDuty = config.targetDutyCycle;
            currentState = State::Running;
        } else {
            // Пропорційне збільшення ШІМ
            currentDuty = static_cast<uint8_t>((elapsed * config.targetDutyCycle) / config.softStartDurationMs);
        }
        hardware.SetPWM(currentDuty);
    }
}
