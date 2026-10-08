#include <Arduino.h>

class AnalogAngleSensor {
private:
    uint16_t _adcMin;
    uint16_t _adcMax;
    uint16_t _resolution;

public:
    AnalogAngleSensor(uint16_t adcMin, uint16_t adcMax, uint16_t resolution)
        : _adcMin(adcMin), _adcMax(adcMax), _resolution(resolution) {}

    bool readAngle(uint8_t pin, uint16_t &angleOut) {
        uint16_t rawAdc = analogRead(pin);
        if (rawAdc < _adcMin || rawAdc > _adcMax) {
            return false; // Помилка: вихід за межі мертвих зон
        }
        uint32_t normalized = rawAdc - _adcMin;
        angleOut = static_cast<uint16_t>((normalized * _resolution) / (_adcMax - _adcMin));
        return true;
    }
};
