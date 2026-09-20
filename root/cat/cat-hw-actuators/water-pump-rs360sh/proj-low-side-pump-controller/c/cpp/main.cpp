#include <iostream>
#include <thread>
#include <chrono>
#include "WaterPump.hpp"

// Реалізація апаратного рівня
class HardwareSimulation : public IWaterPumpHardware {
public:
    void SetPWM(uint8_t dutyCycle) override {
        std::cout << "[АПАРАТУРА] ШІМ встановлено: " << static_cast<int>(dutyCycle) << "%\n";
    }
    
    uint32_t GetTimeMs() override {
        return sysTimeMs;
    }

    void AdvanceTime(uint32_t ms) {
        sysTimeMs += ms;
    }

private:
    uint32_t sysTimeMs = 0;
};

int main() {
    HardwareSimulation hw;
    WaterPumpConfig config;
    config.softStartDurationMs = 1000;
    config.maxRunTimeMs = 5000;
    config.targetDutyCycle = 80;
    
    WaterPump pump(hw, config);
    
    std::cout << "--- Запуск помпи (Soft-Start) ---\n";
    pump.Start();
    
    // Головний цикл симуляції
    for (int i = 0; i < 60; ++i) {
        pump.Update();
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        hw.AdvanceTime(100);
        
        if (hw.GetTimeMs() % 500 == 0) {
            auto state = pump.GetState();
            if (state == WaterPump::State::Idle) {
                std::cout << "Час: " << hw.GetTimeMs() << " мс. Стан: Зупинено (Спрацював захист?)\n";
                break;
            } else if (state == WaterPump::State::Starting) {
                std::cout << "Час: " << hw.GetTimeMs() << " мс. Стан: Розгін\n";
            } else {
                std::cout << "Час: " << hw.GetTimeMs() << " мс. Стан: Робота\n";
            }
        }
    }
    
    return 0;
}
