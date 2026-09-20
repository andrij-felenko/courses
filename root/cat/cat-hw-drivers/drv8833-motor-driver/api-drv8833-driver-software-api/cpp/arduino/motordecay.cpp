#include <Arduino.h>

enum class MotorDecay {
    Slow,
    Fast
};

class DRV8833Motor {
public:
    DRV8833Motor(uint8_t in1, uint8_t in2, uint8_t nsleep);
    void begin();
    void setSpeed(int16_t speed, MotorDecay decay = MotorDecay::Slow);
    void brake();
    void coast();

private:
    uint8_t _pinIN1;
    uint8_t _pinIN2;
    uint8_t _pinNSLEEP;
};
