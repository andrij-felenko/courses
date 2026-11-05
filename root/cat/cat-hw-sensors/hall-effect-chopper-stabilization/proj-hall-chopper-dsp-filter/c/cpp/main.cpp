#include <cstdint>
#include "chopper.hpp"

namespace hw {
    volatile uint32_t* const kAdcResult  = reinterpret_cast<uint32_t*>(0x40012440);
    volatile uint32_t* const kTimerStat  = reinterpret_cast<uint32_t*>(0x40000000);
    volatile uint32_t* const kSensorCtrl = reinterpret_cast<uint32_t*>(0x40020000);

    void init() {
        // Налаштування АЦП та таймерів
    }
    
    void setSensorPhase(uint8_t phase) {
        *kSensorCtrl = (phase == 0) ? 0x01 : 0x02;
    }
    
    void delay() {
        for (volatile int i = 0; i < 150; i++) {}
    }
    
    uint32_t readAdc() {
        return *kAdcResult;
    }
    
    bool timerTicked() {
        if (*kTimerStat & 0x01) {
            *kTimerStat &= ~0x01;
            return true;
        }
        return false;
    }
}

int main() {
    hw::init();
    ChopperProcessor processor;
    
    while (true) {
        if (hw::timerTicked()) {
            hw::setSensorPhase(0);
            hw::delay();
            int32_t phase0 = hw::readAdc();
            
            hw::setSensorPhase(1);
            hw::delay();
            int32_t phase1 = hw::readAdc();
            
            int32_t hall_field = processor.process(phase0, phase1);
            
            bool is_magnet_near = (hall_field > 1000) || (hall_field < -1000);
            if (is_magnet_near) {
                // Дії при виявленні магніту
            }
        }
    }
    return 0;
}
