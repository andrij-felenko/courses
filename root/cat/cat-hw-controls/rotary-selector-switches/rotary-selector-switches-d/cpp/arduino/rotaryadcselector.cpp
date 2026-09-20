#include <Arduino.h>

class RotaryAdcSelector {
private:
    uint8_t _pin;
    static constexpr uint8_t _positions = 12;
    static constexpr uint16_t _maxAdc = 1023;

public:
    explicit RotaryAdcSelector(uint8_t pin) : _pin(pin) {}

    int readPosition() const {
        uint16_t rawAdc = analogRead(_pin);
        uint16_t step = _maxAdc / (_positions - 1);
        uint16_t halfStep = step / 2;

        for (uint8_t i = 0; i < _positions; ++i) {
            uint16_t target = i * step;
            int32_t minVal = static_cast<int32_t>(target) - halfStep;
            int32_t maxVal = target + halfStep;
            
            if (rawAdc >= (minVal < 0 ? 0 : minVal) && rawAdc <= maxVal) {
                return i + 1;
            }
        }
        return -1;
    }
};
