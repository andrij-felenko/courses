#include <Arduino.h>

class PiezoDriver {
private:
    uint8_t _pin;
    uint32_t _sample_rate;
    uint16_t _baseline;
    bool _initialized;

public:
    PiezoDriver(uint8_t pin) : _pin(pin), _sample_rate(10000), _baseline(0), _initialized(false) {}

    bool begin(uint32_t sample_rate_hz = 10000) {
        pinMode(_pin, INPUT);
        _sample_rate = sample_rate_hz;
        _baseline = analogRead(_pin);
        _initialized = true;
        return true;
    }
};
